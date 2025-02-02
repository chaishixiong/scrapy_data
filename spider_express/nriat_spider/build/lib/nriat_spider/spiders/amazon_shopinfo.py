optimization level was requested by
    # the caller.
    if direct is None:
        direct = (__debug__ and optimize == 0)

    # "Indirect" byte-compilation: write a temporary script and then
    # run it with the appropriate flags.
    if not direct:
        try:
            from tempfile import mkstemp
            (script_fd, script_name) = mkstemp(".py")
        except ImportError:
            from tempfile import mktemp
            (script_fd, script_name) = None, mktemp(".py")
        log.info("writing byte-compilation script '%s'", script_name)
        if not dry_run:
            if script_fd is not None:
                script = os.fdopen(script_fd, "w")
            else:
                script = open(script_name, "w")

            with script:
                script.write("""\
from distutils.util import byte_compile
files = [
""")

                # XXX would be nice to write absolute filenames, just for
                # safety's sake (script should be more robust in the face of
                # chdir'ing before running it).  But this requires abspath'ing
                # 'prefix' as well, and that breaks the hack in build_lib's
                # 'byte_compile()' method that carefully tacks on a trailing
                # slash (os.sep really) to make sure the prefix here is "just
                # right".  This whole prefix business is rather delicate -- the
                # problem is that it's really a directory, but I'm treating it
                # as a dumb string, so trailing slashes and so forth matter.

                #py_files = map(os.path.abspath, py_files)
                #if prefix:
                #    prefix = os.path.abspath(prefix)

                script.write(",\n".join(map(repr, py_files)) + "]\n")
                script.write("""
byte_compile(files, optimize=%r, force=%r,
             prefix=%r, base_dir=%r,
             verbose=%r, dry_run=0,
             direct=1)
""" % (optimize, force, prefix, base_dir, verbose))

        cmd = [sys.executable]
        cmd.extend(_optim_args_from_interpreter_flags())
        cmd.append(script_name)
        spawn(cmd, dry_run=dry_run)
        execute(os.remove, (script_name,), "removing %s" % script_name,
                dry_run=dry_run)

    # "Direct" byte-compilation: use the py_compile module to compile
    # right here, right now.  Note that the script generated in indirect
    # mode simply calls 'byte_compile()' in direct mode, a weird sort of
    # cross-process recursion.  Hey, it works!
    else:
        from py_compile import compile

        for file in py_files:
            if file[-3:] != ".py":
                # This lets us be lazy and not filter filenames in
                # the "install_lib" command.
                continue

            # Terminology from the py_compile module:
            #   cfile - byte-compiled file
            #   dfile - purported source filename (same as 'file' by default)
            if optimize >= 0:
                opt = '' if optimize == 0 else optimize
                cfile = importlib.util.cache_from_source(
                    file, optimization=opt)
            else:
                cfile = importlib.util.cache_from_source(file)
            dfile = file
            if prefix:
                if file[:len(prefix)] != prefix:
                    raise ValueError("invalid prefix: filename %r doesn't start with %r"
                           % (file, prefix))
                dfile = dfile[len(prefix):]
            if base_dir:
                dfile = os.path.join(base_dir, dfile)

            cfile_base = os.path.basename(cfile)
            if direct:
                if force or newer(file, cfile):
                    log.info("byte-compiling %s to %s", file, cfile_base)
                    if not dry_run:
                        compile(file, cfile, dfile)
                else:
                    log.debug("skipping byte-compilation of %s to %s",
                              file, cfile_base)

# byte_compile ()

def rfc822_escape (header):
    """Return a version of the string escaped for inclusion in an
    RFC-822 header, by ensuring there are 8 spaces space after each newline.
    """
    lines = header.split('\n')
    sep = '\n' + 8 * ' '
    return sep.join(lines)
                                                                                                                                                                                                                                                                                                                                                  'summImageUrl': 'https://ae04.alicdn.com/kf/S78242b1e21cf4f2c92ae4df51610991cz.jpg_120x120.jpg'， 'tagResult': ''， 'unit': 'piece'}， {'averageStar': 5.0， 'averageStarRate': 100.0， 'bigSaleProduct': False， 'feedbacks': 1， 'formatedPiecePriceStr': 'US $6.48'， 'formatedPromotionPiecePriceStr': 'US $4.41'， 'id': 1005004270675346， 'image350Url': 'https://ae04.alicdn.com/kf/S4af5dcc044de43e6b805a073ad312195E.jpg_350x350.jpg'， 'inPromotion': True， 'lot': False， 'mediaId': '1100005993095'， 'orders': 1， 'originPrice': {'currencyCode': 'USD'， 'formattedPrice': 'US $6.48'， 'minPrice': 6.48}， 'pcDetailUrl': '//www.aliexpress.com/store/product/Vase-Still-Life-Diamond-Painting-Fruit-Flower-Picture-Rhinestones-Diamond-Embroidery-Kitchen-Landscape-Mosaic-Cross-Stitch/1100177073_1005004270675346.html?pdp_npi=2%40dis%21USD%21US%20%246.48%21US%20%244.41%21%21%21%21%21%400b0fdc6a16666185795207321e0f08%2112000028582858086%21sh'， 'piecePriceMoney': {'amount': 6.48， 'cent': 648， 'centFactor': 100， 'currency': 'USD'， 'currencyCode': 'USD'}， 'pieceUnit': 'piece'， 'piecesPerLot': 1， 'previewPrice': {'currencyCode': 'USD'}， 'promotionDiscount': 32， 'promotionPiecePriceMoney': {'amount': 4.41， 'cent': 441， 'centFactor': 100， 'currency': 'USD'， 'currencyCode': 'USD'}， 'salePrice': {'currencyCode': 'USD'， 'discount': 32， 'formattedPrice': 'US $4.41'， 'minPrice': 4.41}， 'scaleImageUrl': 'https://ae04.alicdn.com/kf/S4af5dcc044de43e6b805a073ad312195E.jpg_200x200.jpg'， 'seoTitle': 'Vase Still Life Diamond Painting Fruit Flower Picture Rhinestones Diamond Embroidery Kitchen Landscape Mosaic Cross Stitch Home'， 'subject': 'Vase Still Life Diamond Painting Fruit Flower Picture Rhinestones Diamond Embroidery Kitchen Landscape Mosaic Cross Stitch Home'， 'summImageUrl': 'https://ae04.alicdn.com/kf/S4af5dcc044de43e6b805a073ad312195E.jpg_120x120.jpg'， 'tagResult': ''， 'unit': 'piece'}， {'averageStar': 0.0， 'bigSaleProduct': False， 'feedbacks': 0， 'formatedPiecePriceStr': 'US $6.48'， 'formatedPromotionPiecePriceStr': 'US $4.41'， 'id': 1005004129915519， 'image350Url': 'https://ae04.alicdn.com/kf/S1a667041b7c9446a84350cb450088463s.jpg_350x350.jpg'， 'inPromotion': True， 'lot': False， 'mediaId': '1100005993095'， 'orders': 1， 'originPrice': {'currencyCode': 'USD'， 'formattedPrice': 'US $6.48'， 'minPrice': 6.48}， 'pcDetailUrl': '//www.aliexpress.com/store/product/5D-Diamond-Painting-Kit-Unicorn-Animal-Mosaic-Flower-Castle-Landscape-Beach-Diamond-Embroidery-Rhinestone-Cartoon-Fantasy/1100177073_1005004129915519.html?pdp_npi=2%40dis%21USD%21US%20%246.48%21US%20%244.41%21%21%21%21%21%400b0fdc6a16666185795207321e0f08%2112000028133645787%21sh'， 'piecePriceMoney': {'amount': 6.48， 'cent': 648， 'centFactor': 100， 'currency': 'USD'， 'currencyCode': 'USD'}， 'pieceUnit': 'piece'， 'piecesPerLot': 1， 'previewPrice': {'currencyCode': 'USD'}， 'promotionDiscount': 32， 'promotionPiecePriceMoney': {'amount': 4.41， 'cent': 441， 'centFactor': 100， 'currency': 'USD'， 'currencyCode': 'USD'}， 'salePrice': {'currencyCode': 'USD'， 'discount': 32， 'for