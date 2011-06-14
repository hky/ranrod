========
 Models
========

Models define how we extract information from a specific type of device, they
should be generic to a (line of) vendor model(s).

All models should consist of re-usable code.


Syntax
======

The model configuration are Python modules, we try to follow the
:pep:`8` guidelines where possible.


Functions and variables
=======================

capture
-------

.. function:: capture(pattern : regexp[, name1 : string[, nameN : string]])

Captures text in the device output to a local variable. One can either use
named Python Regular Expression groups or provide the variable names as
arguments::

    >>> capture(r'version: (?P<version>\S+)')

Is equivalent to::

    >>> capture(r'version: (\S+)', 'version')


command
-------

.. function:: command(line : string)

Executes the command on the device returning the output::

    >>> output = command('show version')


connect
-------

.. function:: command(device : object) -> context

Connect to the device::

    >>> with connect(device) as remote:
    ...     log('Connected to %s' % (remote,))
    ...


device
------

.. data:: device
.. data:: device.config

This holds a reference to the current device and its configuration.


dumper
------

.. function:: dumper(device : object) -> context

Repository logger for the device, takes a ``device`` as parameter::

    >>> with dumper(device) as output:
    ...     record(output, 'Starting dump...')
    ...


expect
------

.. function:: expect(pattern : regexp, callback : string or function)

Fires a callback as soon as the expected string is seen::

    >>> expect(r'login:', device.config.username)
    >>> def callback(*args, **kwargs):
    ...     return 'testing'
    ...
    >>> expect(r'password:', callback)


filter
------

.. function:: filter(pattern : regexp[, replace : string])

Replace text in the device output with the given ``replace`` string, this
defaults to ``<removed>>`` if not provided.


header
------

.. function:: header(text : string) -> string

Generate a header, which can be used as header in the recorded output::

    >>> record(output, header('Dumping our border router'))


ignore
------

.. function:: ignore(pattern : regexp)

Ignores lines in the device output that match the output.


log
---

.. function:: log(text : string)

Put a line in the general RANROD log::

    >>> log('Hello world!')


record
------

.. function:: record(output : object, data : string)

Record data to the device ``output``, where ``output`` is a :func:`dumper`
instance.


pattern
-------

.. function:: pattern(pattern : string)

Compiles a pattern into a regular expression object::

    >>> ignore(pattern(r'rx packets: .*'))


prompt
------

.. function:: prompt([pattern : regexp])

If no arguments are provided, we wait until the device returns a prompt::

    >>> prompt()
    
Otherwise, we can specify what pattern is used to recognise the device's
prompt::

    >>> prompt(pattern(r'^[>#$]$'))
    
Keep in mind that the pattern is matched against stripped lines (no leading
or trailing spaces/tabs are provided).
