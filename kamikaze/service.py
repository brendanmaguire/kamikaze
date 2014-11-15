"""
This service monitors
"""
import asyncio
import json
import logging
import time

from asyncio_redis import Connection as RedisConnection
from collections import namedtuple
from importlib import import_module

from .utils import (
    DEFAULT_REDIS_KEY,
    extract_package,
)

LOG = logging.getLogger(__name__)


QueueUpdates = namedtuple(
    'QueueUpdates', ['expired_packages', 'highest_priority_package'])

# Very small initial timeout so we read the queue
_INITIAL_TIMEOUT = 0.01


@asyncio.coroutine
def _get_queue_updates(connection, now, redis_key):
    cursor = yield from connection.zscan(redis_key)
    results = yield from cursor.fetchall()
    return _entries_to_queue_updates(results.items(), now=now)


def _entries_to_queue_updates(entries, now):
    packages = [extract_package(entry) for entry in entries]

    expired_packages = []
    highest_priority_package = None

    for package in sorted(packages):
        if package.expired(now):
            expired_packages.append(package)
        else:
            highest_priority_package = package
            # We don't bother with the rest of the packages once we've found a
            # valid non expired one
            break

    return QueueUpdates(
        expired_packages=expired_packages,
        highest_priority_package=highest_priority_package)


def _time_until_package_expires(package, now):
    if package is not None:
        return package.ttl(now)
    else:
        return None


@asyncio.coroutine
def _get_subscription(redis_host, redis_port, redis_key):
    connection = yield from RedisConnection.create(
        host=redis_host, port=redis_port)
    subscriber = yield from connection.start_subscribe()
    yield from subscriber.subscribe([redis_key])

    return subscriber


@asyncio.coroutine
def _remove_expire_packages(connection, packages, redis_key):
    if packages:
        LOG.info('Removing packages from "{key}": {packages}'.format(
            key=redis_key, packages=packages))
        yield from asyncio.wait([connection.zrem(
            redis_key, [package.raw_entry for package in packages])])


@asyncio.coroutine
def _main_loop(consumer_function, consumer_function_kwargs, redis_host=None,
               redis_port=6379, redis_key=DEFAULT_REDIS_KEY):
    LOG.info('Connecting to {host} on port {port}'.format(
        host=redis_host, port=redis_port))
    connection = yield from RedisConnection.create(
        host=redis_host, port=redis_port)
    LOG.info('Subscribing to key "{key}"'.format(key=redis_key))
    subscriber = yield from _get_subscription(
        redis_host=redis_host, redis_port=redis_port, redis_key=redis_key)

    timeout = _INITIAL_TIMEOUT
    consumer_future = None
    while True:
        try:
            LOG.debug('Waiting for a published message with timeout of '
                      '{}'.format(timeout))
            message = yield from asyncio.wait_for(
                subscriber.next_published(), timeout)
            LOG.debug('Notified of new message: {}'.format(message))
        except asyncio.TimeoutError:
            LOG.debug('Timed out after {} seconds'.format(timeout))

        # Cancel the currently running consumer as soon as possible
        if consumer_future is not None:
            LOG.debug('Cancelling future')
            consumer_future.cancel()

        now = time.time()
        queue_updates = yield from _get_queue_updates(
            connection, now, redis_key)
        yield from _remove_expire_packages(
            connection=connection,
            packages=queue_updates.expired_packages,
            redis_key=redis_key)

        highest_priority_package = queue_updates.highest_priority_package
        timeout = _time_until_package_expires(highest_priority_package, now)

        if asyncio.iscoroutinefunction(consumer_function):
            consumer_future = asyncio.async(consumer_function(
                highest_priority_package, **consumer_function_kwargs))
        else:
            consumer_function(
                highest_priority_package, **consumer_function_kwargs)
            consumer_future = None


def service(consumer_function_path: 'The import path of the function',
            consumer_function_kwargs: 'Arguments passed to the function'=None,
            redis_host='localhost', redis_port=6379):
    """
    Run the kamikaze service and invoke the specified python function every
    time a new message comes to the top of the queue
    """
    module_name, function_name = consumer_function_path.rsplit('.', 1)

    module = import_module(module_name)
    consumer_function = getattr(module, function_name)

    if consumer_function_kwargs:
        consumer_function_kwargs = json.loads(consumer_function_kwargs)
    else:
        consumer_function_kwargs = {}
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main_loop(
        consumer_function=consumer_function,
        consumer_function_kwargs=consumer_function_kwargs,
        redis_host=redis_host, redis_port=redis_port))
