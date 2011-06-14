.. RANROD documentation master file, created by
   sphinx-quickstart on Wed Jun  8 19:35:43 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RANROD
======

RANROD is a router config differ and collector inspired by RANCID_. While RANCID_
is a cool product, it just lacks the flexibility and ease of extending it for
other purposes than grabbing Cisco configurations. Also, it's mostly written in
Perl and Bash, compiled into a giant pile of seperate scripts to do a relative
easy job. RANROD intends to be more flexible, yet easier to maintain and use.

All you need to run RANROD is a Python_ interpreter, Paramiko_ SSH client
libraries and some version control tools of your choice!

.. _RANCID: http://www.shrubbery.net/rancid/
.. _Python: http://python.org/
.. _Paramiko: http://www.lag.net/paramiko/

Download
========

There are no official releases of RANROD yet, we first want to implement and
test more devices before we put out an official release. You can, however, get
a tarball from the repository and run a development release:

  * `ranrod.tgz`_
 
  * `ranrod.zip`_

  * `ranrod-models.tgz`_

  * `ranrod-models.zip`_
  

.. _ranrod.tgz: https://github.com/tehmaze/ranrod/tarball/master
.. _ranrod.zip: https://github.com/tehmaze/ranrod/zipball/master
.. _ranrod-models.tgz: https://github.com/tehmaze/ranrod-models/tarball/master
.. _ranrod-models.zip: https://github.com/tehmaze/ranrod-models/zipball/master


Documentation
=============

Contents:

.. toctree::
   :maxdepth: 2

   usage
   config/index
   models/index
   api/modules
