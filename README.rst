===============================
Kamikaze
===============================

.. image:: https://badge.fury.io/py/kamikaze.png
    :target: http://badge.fury.io/py/kamikaze

.. image:: https://travis-ci.org/brendanmaguire/kamikaze.png?branch=master
        :target: https://travis-ci.org/brendanmaguire/kamikaze

A service for placing prioritised packages with expiry times on a queue and
having a consumer notified of the packages

How it works
------------

This service monitors a Redis sorted set and calls a consumer function
when a new package arrives or the current highest priority package
expires. The consumer function must be a Python `asyncio
coroutine <https://docs.python.org/3/library/asyncio-task.html>`__.

How to install
--------------

::

    pip install kamikaze

The consumer function
---------------------

The consumer function is the function that is called when a new message
comes to the top of the queue. The function should be of the format:

::

    def consumer_function(package, *args):
        """
        Does stuff with packages and optional args passed from the command line
        """

Long running consumer functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the consumer function is long running then it should yield control of
the loop when possible. Otherwise the kamikaze service will be slow to
react to changes in the queue.

Fast running consumer function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the consumer function is fast then there will be no need to yield
control to the main loop until it is complete.

Running the service
-------------------

Start the service by running the following:

::

    kamikaze service <consumer-function-path> --consumer-function-args

The consumer function should be the full path to the python coroutine.
It must be in your ``$PYTHONPATH``.

Give the ``--help`` flag for a full list of options.

Tools
-----

Pushing a Package
~~~~~~~~~~~~~~~~~

Use the ``push`` command to add a package to the queue:

::

    kamikaze push <payload> <ttl> <priority>

Removing a Package
~~~~~~~~~~~~~~~~~~

Use the ``remove`` command to remove a package from the queue:

::

    kamikaze remove <payload>

View Queue
~~~~~~~~~~

Use the ``view-queue`` command to list all packages on the queue:

::

    kamikaze view-queue

Running the examples
--------------------

Yielding example
~~~~~~~~~~~~~~~~

An example of a yielding function can be run like so:

::

    kamikaze service example_consumer.consumer.yielding_consumer_func

Blocking example
~~~~~~~~~~~~~~~~

An example of a blocking function can be run like so:

::

    kamikaze service example_consumer.consumer.blocking_consumer_func
