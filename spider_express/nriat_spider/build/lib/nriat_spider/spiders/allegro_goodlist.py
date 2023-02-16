 itself should not pay attention to
        # this flag: it is the business of 'ensure_finalized()', which
        # always calls 'finalize_options()', to respect/update it.
        self.finalized = 0

    # XXX A more explicit way to customize dry_run would be better.
    def __getattr__(self, attr):
        if attr == 'dry_run':
            myval = getattr(self, "_" + attr)
            if myval is None:
                return getattr(self.distribution, attr)
            else:
                return myval
        else:
            raise AttributeError(attr)

    def ensure_finalized(self):
        if not self.finalized:
            self.finalize_options()
        self.finalized = 1

    # Subclasses must define:
    #   initialize_options()
    #     provide default values for all options; may be customized by
    #     setup script, by options from config file(s), or by command-line
    #     options
    #   finalize_options()
    #     decide on the final values for all options; this is called
    #     after all possible intervention from the outside world
    #     (command-line, option file, etc.) has been processed
    #   run()
    #     run the command: do whatever it is we're here to do,
    #     controlled by the command's various option values

    def initialize_options(self):
        """Set default values for all the options that this command
        supports.  Note that these defaults may be overridden by other
        commands, by the setup script, by config files, or by the
        command-line.  Thus, this is not the place to code dependencies
        between options; generally, 'initialize_options()' implementations
        are just a bunch of "self.foo = None" assignments.

        This method must be implemented by all command classes.
        """
        raise RuntimeError("abstract method -- subclass %s must override"
                           % self.__class__)

    def finalize_options(self):
        """Set final values for all the options that this command supports.
        This is always called as late as possible, ie.  after any option
        assignments from the command-line or from other commands have been
        done.  Thus, this is the place to code option dependencies: if
        'foo' depends on 'bar', then it is safe to set 'foo' from 'bar' as
        long as 'foo' still has the same value it was assigned in
        'initialize_options()'.

        This method must be implemented by all command classes.
        """
        raise RuntimeError("abstract method -- subclass %s must override"
                           % self.__class__)


    def dump_options(self, header=None, indent=""):
        from distutils.fancy_getopt import longopt_xlate
        if header is None:
            header = "command options for '%s':" % self.get_command_name()
        self.announce(indent + header, level=log.INFO)
        indent = indent + "  "
        for (option, _, _) in self.user_options:
            option = option.translate(longopt_xlate)
            if option[-1] == "=":
                option = option[:-1]
            value = getattr(self, option)
            self.announce(indent + "%s = %s" % (option, value),
                          level=log.INFO)

    def run(self):
        """A command's raison d'etre: carry out the action it exists to
        perform, controlled by the options initialized in
        'initialize_options()', customized by other commands, the setup
        script, the command-line, and config files, and finalized in
        'finalize_options()'.  All terminal output and filesystem
        interaction should be done by 'run()'.

        This method must be implemented by all command classes.
        """
        raise RuntimeError("abstract method -- subclass %s must override"
                           % self.__class__)

    def announce(self, msg, level=1):
        """If the current verbosity level is of greater than or equal to
        'level' print 'msg' to stdout.
        """
        log.log(level, msg)

    def debug_print(self, msg):
        """Print 'msg' to stdout if the global DEBUG (taken from the
        DISTUTILS_DEBUG environment variable) flag is true.
        """
        from distutils.debug import DEBUG
        if DEBUG:
            print(msg)
            sys.stdout.flush()


    # -- Option validation methods -------------------------------------
    # (these are very handy in writing the 'finalize_options()' method)
    #
    # NB. the general philosophy here is to ensure that a particular option
    # value meets certain type and value constraints.  If not, we try to
    # force it into conformance (eg. if we expect a list but have a string,
    # split the string on comma and/or whitespace).  If we can't force the
    # option into conformance, raise DistutilsOptionError.  Thus, command
    # classes need do nothing more than (eg.)
    #   self.ensure_string_list('foo')
    # and they can be 