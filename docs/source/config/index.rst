===============
 Configuration
===============

Syntax
======

The configuration syntax supports different types and directives.

Sections
--------

The configuration sections are indicated by using square brackets:


.. code-block:: cfg

   [section]


Including files
---------------

You can include one template from a second one:


.. code-block:: cfg

   < other.cfg


Including sections
------------------

There is an inheritance system in the templates, one template can inherit
directives from a second section:


.. code-block:: cfg

   [first]
   foo    = bar
   
   [second]
   @first
   biz    = 42


This will expand to:


.. code-block:: cfg

   [first]
   foo    = bar
   
   [second]
   foo    = bar
   biz    = 42


Definitions
-----------

You can define key-value pairs by using the equals sign (``=``), there are 
different types the parser may evaluate:

   ====== ========================================================
   Type   Example
   ====== ========================================================
   bool   ``yes``, ``true``, ``enable``
          ``no``, ``false``, ``disabled``
   none   ``none``, ``null``
   int    ``42`` [#]_
   long   ``42``
   float  ``42.23``
   regexp ``/test/``, ``/test/igm``
   list   ``42, /test/``
   ====== ========================================================


.. [#]  Integer always converts to long

Comments
--------

You can either use a semi-colon ``;`` or a hash ``#`` to put remarks or
comments in the configuration files:


.. code-block:: cfg

   ; This will be ignored
   # and so will this


etc/ranrod.cfg
==============

This is the main configuration file, all file locations will be relative to
this file if the given path is a relative path.

An example configuration may read:


.. code-block:: cfg
   :linenos:

   ; Load repository templates
   < repository.cfg
   
   ;
   ; Locations
   ;
   [paths]
   ; Path to logging directory
   log       = ../log
   
   ;
   ; Devices configuration
   ;
   [devices]
   ; Path to model definitions
   models     = models/
   ; Path to devices definitions (will be expanded by glob)
   load      = device/*.cfg
   
   ;
   ; Repository configuration
   ;
   [repository]
   ; Use mercurial template
   @template:mercurial
   ; Path to repository
   path      = ../repository


etc/devices/*.cfg
=================

These are the device configurations which specify all parameters to connect
to a device.