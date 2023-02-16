 resource_name), 'rb')

    def _get(self, path):
        with open(path, 'rb') as stream:
            return stream.read()

    @classmethod
    def _register(cls):
        loader_cls = getattr(
            importlib_machinery,
            'SourceFileLoader',
            type(None),
        )
        register_loader_type(loader_cls, cls)


DefaultProvider._register()


class EmptyProvider(NullProvider):
    """Provider that returns nothing for all requests"""

    module_path = None

    _isdir = _has = lambda self, path: False

    def _get(self, path):
        return ''

    def _listdir(self, path):
        return []

    def __init__(self):
        pass


empty_provider = EmptyProvider()


class ZipManifests(dict):
    """
    zip manifest builder
    """

    @classmethod
    def build(cls, path):
        """
        Build a dictionary similar to the zipimport directory
        caches, except instead of tuples, store ZipInfo objects.

        Use a platform-specific path separator (os.sep) for the path keys
        for compatibility with pypy on Windows.
        """
        with zipfile.ZipFile(path) as zfile:
            items = (
                (
                    name.replace('/', os.sep),
                    zfile.getinfo(name),
                )
                for name in zfile.namelist()
            )
            return dict(items)

    load = build


class MemoizedZipManifests(ZipManifests):
    """
    Memoized zipfile manifests.
    """
    manifest_mod = collections.namedtuple('manifest_mod', 'manifest mtime')

    def load(self, path):
        """
        Load a manifest at path or return a suitable manifest already loaded.
        """
        path = os.path.normpath(path)
        mtime = os.stat(path).st_mtime

        if path not in self or self[path].mtime != mtime:
            manifest = self.build(path)
            self[path] = self.manifest_mod(manifest, mtime)

        return self[path].manifest


class ZipProvider(EggProvider):
    """Resource support for zips and eggs"""

    eagers = None
    _zip_manifests = MemoizedZipManifests()

    def __init__(self, module):
        EggProvider.__init__(self, module)
        self.zip_pre = self.loader.archive + os.sep

    def _zipinfo_name(self, fspath):
        # Convert a virtual filename (full path to file) into a zipfile subpath
        # usable with the zipimport directory cache for our target archive
        fspath = fspath.rstrip(os.sep)
        if fspath == self.loader.archive:
            return ''
        if fspath.startswith(self.zip_pre):
            return fspath[len(self.zip_pre):]
        raise AssertionError(
            "%s is not a subpath of %s" % (fspath, self.zip_pre)
        )

    def _parts(self, zip_path):
        # Convert a zipfile subpath into an egg-relative path part list.
        # pseudo-fs path
        fspath = self.zip_pre + zip_path
        if fspath.startswith(self.egg_root + os.sep):
            return fspath[len(self.egg_root) + 1:].split(os.sep)
        raise AssertionError(
            "%s is not a subpath of %s" % (fspath, self.egg_root)
        )

    @property
    def zipinfo(self):
        return self._zip_manifests.load(self.loader.archive)

    def get_resource_filename(self, manager, resource_name):
        if not self.egg_name:
            raise NotImplementedError(
                "resource_filename() only supported for .egg, not .zip"
            )
        # no need to lock for extraction, since we use temp names
        zip_path = self._resource_to_zip(resource_name)
        eagers = self._get_eager_resources()
        if '/'.join(self._parts(zip_path)) in eagers:
            for name in eagers:
                self._extract_resource(manager, self._eager_to_zip(name))
        return self._extract_resource(manager, zip_path)

    @staticmethod
    def _get_date_and_size(zip_stat):
        size = zip_stat.file_size
        # ymdhms+wday, yday, dst
        date_time = zip_stat.date_time + (0, 0, -1)
        # 1980 offset already done
        timestamp = time.mktime(date_time)
        return timestamp, size

    def _extract_resource(self, manager, zip_path):

        if zip_path in self._index():
            for name in self._index()[zip_path]:
                last = self._extract_resource(
                    manager, os.path.join(zip_path, name)
                )
            # return the extracted directory name
            return os.path.dirname(last)

        timestamp, size = self._get_date_and_size(self.zipinfo[zip_path])

        if not WRITE_SUPPORT:
            raise IOError('"os.rename" and "os.unlink" are not supported '
                          'on this platform')
        try:

            real_path = manager.get_cache_path(
                self.egg_name, self._parts(zip_path)
            )

            if self._is_current(real_path, zip_path):
                return real_path

            outf, tmpnam = _mkstemp(
                ".$extract",
                dir=os.path.dirname(real_path),
            )
            os.write(outf, self.loader.get_data(zip_path))
            os.close(outf)
            utime(tmpnam, (timestamp, timestamp))
            manager.postprocess(tmpnam, real_path)

            try:
                rename(tmpnam, real_path)

            except os.error:
                if os.path.isfile(real_path):
                    if self._is_current(real_path, zip_path):
                        # the file became current since it was checked above,
                        #  so proceed.
                        return real_path
                    # Windows, del old file and retry
                    elif os.name == 'nt':
                        unlink(real_path)
                        rename(tmpnam, real_path)
                        return real_path
                raise

        except os.error:
            # report a user-friendly error
            manager.extraction_error()

        return real_path

    def _is_current(self, file_path, zip_path):
        """
        Return True if the file_path is current for this zip_path
        """
        timestamp, size = self._get_date_and_size(self.zipinfo[zip_path])
        if not os.path.isfile(file_path):
            return False
        stat = os.stat(file_path)
        if stat.st_size != size or stat.st_mtime != timestamp:
            return False
        # check that the contents match
        zip_contents = self.loader.get_data(zip_path)
        with open(file_path, 'rb') as f:
            file_contents = f.read()
        return zip_contents == file_contents

    def _get_eager_resources(self):
        if self.eagers is None:
            eagers = []
            for name in ('native_libs.txt', 'eager_resources.txt'):
                if self.has_metadata(name):
                    eagers.extend(self.get_metadata_lines(name))
            self.eagers = eagers
        return self.eagers

    def _index(self):
        try:
            return self._dirindex
        except AttributeError:
            ind = {}
            for path in self.zipinfo:
                parts = path.split(os.sep)
                while parts:
                    parent = os.sep.join(parts[:-1])
                    if parent in ind:
                        ind[parent].append(parts[-1])
                        break
                    else:
                        ind[parent] = [parts.pop()]
            self._dirindex = ind
            return ind

    def _has(self, fspath):
        zip_path = self._zipinfo_name(fspath)
        return zip_path in self.zipinfo or zip_path in self._index()

    def _isdir(self, fspath):
        return self._zipinfo_name(fspath) in self._index()

    def _listdir(self, fspath):
        return list(self._index().get(self._zipinfo_name(fspath), ()))

    def _eager_to_zip(self, resource_name):
        return self._zipinfo_name(self._fn(self.egg_root, resource_name))

    def _resource_to_zip(self, resource_name):
        return self._zipinfo_name(self._fn(self.module_path, resource_name))


register_loader_type(zipimport.zipimporter, ZipProvider)


class FileMetadata(EmptyProvider):
    """Metadata handler for standalone PKG-INFO files

    Usage::

        metadata = FileMetadata("/path/to/PKG-INFO")

    This provider rejects all data and metadata requests except for PKG-INFO,
    which is treated as existing, and will be the contents of the file at
    the provided location.
    """

    def __init__(self, path):
        self.path = path

    def has_metadata(self, name):
        return name == 'PKG-INFO' and os.path.isfile(self.path)

    def get_metadata(self, name):
        if name != 'PKG-INFO':
            raise KeyError("No metadata except PKG-INFO is available")

        with io.open(self.path, encoding='utf-8', errors="replace") as f:
            metadata = f.read()
        self._warn_on_replacement(metadata)
        return metadata

    def _warn_on_replacement(self, metadata):
        # Python 2.7 compat for: replacement_char = '�'
        replacement_char = b'\xef\xbf\xbd'.decode('utf-8')
        if replacement_char in metadata:
            tmpl = "{self.path} could not be properly decoded in UTF-8"
            msg = tmpl.format(**locals())
            warnings.warn(msg)

    def get_metadata_lines(self, name):
        return yield_lines(self.get_metadata(name))


class PathMetadata(DefaultProvider):
    """Metadata provider for egg directories

    Usage::

        # Development eggs:

        egg_info = "/path/to/PackageName.egg-info"
        base_dir = os.path.dirname(egg_info)
        metadata = PathMetadata(base_dir, egg_info)
        dist_name = os.path.splitext(os.path.basename(egg_info))[0]
        dist = Distribution(basedir, project_name=dist_name, metadata=metadata)

        # Unpacked egg directories:

        egg_path = "/path/to/PackageName-ver-pyver-etc.egg"
        metadata = PathMetadata(egg_path, os.path.join(egg_path,'EGG-INFO'))
        dist = Distribution.from_filename(egg_path, metadata=metadata)
    """

    def __init__(self, path, egg_info):
        self.module_path = path
        self.egg_info = egg_info


class EggMetadata(ZipProvider):
    """Metadata provider for .egg files"""

    def __init__(self, importer):
        """Create a metadata provider from a zipimporter"""

        self.zip_pre = importer.archive + os.sep
        self.loader = importer
        if importer.prefix:
            self.module_path = os.path.join(importer.archive, importer.prefix)
        else:
            self.module_path = importer.archive
        self._setup_prefix()


_declare_state('dict', _distribution_finders={})


def register_finder(importer_type, distribution_finder):
    """Register `distribution_finder` to find distributions in sys.path items

    `importer_type` is the type or class of a PEP 302 "Importer" (sys.path item
    handler), and `distribution_finder` is a callable that, passed a path
    item and the importer instance, yields ``Distribution`` instances found on
    that path item.  See ``pkg_resources.find_on_path`` for an example."""
    _distribution_finders[importer_type] = distribution_finder


def find_distributions(path_item, only=False):
    """Yield distributions accessible via `path_item`"""
    importer = get_importer(path_item)
    finder = _find_adapter(_distribution_finders, importer)
    return finder(importer, path_item, only)


def find_eggs_in_zip(importer, path_item, only=False):
    """
    Find eggs in zip files; possibly multiple nested eggs.
    """
    if importer.archive.endswith('.whl'):
        # wheels are not supported with this finder
        # they don't have PKG-INFO metadata, and won't ever contain eggs
        return
    metadata = EggMetadata(importer)
    if metadata.has_metadata('PKG-INFO'):
        yield Distribution.from_filename(path_item, metadata=metadata)
    if only:
        # don't yield nested distros
        return
    for subitem in metadata.resource_listdir('/'):
        if _is_egg_path(subitem):
            subpath = os.path.join(path_item, subitem)
            dists = find_eggs_in_zip(zipimport.zipimporter(subpath), subpath)
            for dist in dists:
                yield dist
        elif subitem.lower().endswith('.dist-info'):
            subpath = os.path.join(path_item, subitem)
            submeta = EggMetadata(zipimport.zipimporter(subpath))
            submeta.egg_info = subpath
            yield Distribution.from_location(path_item, subitem, submeta)


register_finder(zipimport.zipimporter, find_eggs_in_zip)


def find_nothing(importer, path_item, only=False):
    return ()


register_finder(object, find_nothing)


def _by_version_descending(names):
    """
    Given a list of filenames, return them in descending order
    by version number.

    >>> names = 'bar', 'foo', 'Python-2.7.10.egg', 'Python-2.7.2.egg'
    >>> _by_version_descending(names)
    ['Python-2.7.10.egg', 'Python-2.7.2.egg', 'foo', 'bar']
    >>> names = 'Setuptools-1.2.3b1.egg', 'Setuptools-1.2.3.egg'
    >>> _by_version_descending(names)
    ['Setuptools-1.2.3.egg', 'Setuptools-1.2.3b1.egg']
    >>> names = 'Setuptools-1.2.3b1.egg', 'Setuptools-1.2.3.post1.egg'
    >>> _by_version_descending(names)
    ['Setuptools-1.2.3.post1.egg', 'Setuptools-1.2.3b1.egg']
    """
    def _by_version(name):
        """
        Parse each component of the filename
        """
        name, ext = os.path.splitext(name)
        parts = itertools.chain(name.split('-'), [ext])
        return [packaging.version.parse(part) for part in parts]

    return sorted(names, key=_by_version, reverse=True)


def find_on_path(importer, path_item, only=False):
    """Yield distributions accessible on a sys.path directory"""
    path_item = _normalize_cached(path_item)

    if _is_unpacked_egg(path_item):
        yield Distribution.from_filename(
            path_item, metadata=PathMetadata(
                path_item, os.path.join(path_item, 'EGG-INFO')
            )
        )
        return

    entries = safe_listdir(path_item)

    # for performance, before sorting by version,
    # screen entries for only those that will yield
    # distributions
    filtered = (
        entry
        for entry in entries
        if dist_factory(path_item, entry, only)
    )

    # scan for .egg and .egg-info in directory
    path_item_entries = _by_version_descending(filtered)
    for entry in path_item_entries:
        fullpath = os.path.join(path_item, entry)
        factory = dist_factory(path_item, entry, only)
        for dist in factory(fullpath):
            yield dist


def dist_factory(path_item, entry, only):
    """
    Return a dist_factory for a path_item and entry
    """
    lower = entry.lower()
    is_meta = any(map(lower.endswith, ('.egg-info', '.dist-info')))
    return (
        distributions_from_metadata
        if is_meta else
        find_distributions
        if not only and _is_egg_path(entry) else
        resolve_egg_link
        if not only and lower.endswith('.egg-link') else
        NoDists()
    )


class NoDists:
    """
    >>> bool(NoDists())
    False

    >>> list(NoDists()('anything'))
    []
    """
    def __bool__(self):
        return False
    if six.PY2:
        __nonzero__ = __bool__

    def __call__(self, fullpath):
        return iter(())


def safe_listdir(path):
    """
    Attempt to list contents of path, but suppress some exceptions.
    """
    try:
        return os.listdir(path)
    except (PermissionError, NotADirectoryError):
        pass
    except OSError as e:
        # Ignore the directory if does not exist, not a directory or
        # permission denied
        ignorable = (
            e.errno in (errno.ENOTDIR, errno.EACCES, errno.ENOENT)
            # Python 2 on Windows needs to be handled this way :(
            or getattr(e, "winerror", None) == 267
        )
        if not ignorable:
            raise
    return ()


def distributions_from_metadata(path):
    root = os.path.dirname(path)
    if os.path.isdir(path):
        if len(os.listdir(path)) == 0:
            # empty metadata dir; skip
            return
        metadata = PathMetadata(root, path)
    else:
        metadata = FileMetadata(path)
    entry = os.path.basename(path)
    yield Distribution.from_location(
        root, entry, metadata, precedence=DEVELOP_DIST,
    )


def non_empty_lines(path):
    """
    Yield non-empty lines from file at path
    """
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield line


def resolve_egg_link(path):
    """
    Given a path to an .egg-link, resolve distributions
    present in the referenced path.
    """
    referenced_paths = non_empty_lines(path)
    resolved_paths = (
        os.path.join(os.path.dirname(path), ref)
        for ref in referenced_paths
  