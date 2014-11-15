import argh
import logging
import sys
import time

from redis import StrictRedis
from tabulate import tabulate

from .utils import (
    create_package_with_ttl,
    DEFAULT_REDIS_KEY,
    extract_package,
)

LOG = logging.getLogger(__name__)


def push(payload, ttl, priority, redis_host='localhost', redis_port=6379):
    """
    Push a package to the queue
    """
    connection = StrictRedis(host=redis_host, port=redis_port)
    package = create_package_with_ttl(
        payload=payload, ttl=float(ttl), score=float(priority))
    connection.zadd(DEFAULT_REDIS_KEY, package.score, package.raw_entry)
    connection.publish(DEFAULT_REDIS_KEY, 'new_message')


def remove(payload, redis_host='localhost', redis_port=6379):
    """
    Remove a package (or packages if the payload matches multiple) from the
    queue
    """
    connection = StrictRedis(host=redis_host, port=redis_port)
    packages = _get_packages_in_queue(connection)

    packages_to_remove = [
        package for package in packages if package.payload == payload]

    if packages_to_remove:
        LOG.debug(
            'Removing the following packages: {}'.format(packages_to_remove))
        entries_to_remove = [
            package.raw_entry for package in packages_to_remove]
        connection.zrem(DEFAULT_REDIS_KEY, *entries_to_remove)
        connection.publish(DEFAULT_REDIS_KEY, 'new_message')


@argh.named('list')
def list_(redis_host='localhost', redis_port=6379):
    """
    Prints out the contents of the queue

    The output is pretty for humans but machine parseable if been piped
    """
    connection = StrictRedis(host=redis_host, port=redis_port)
    packages = _get_packages_in_queue(connection)

    now = time.time()
    table = [
        [package.score,
         package.payload,
         _time_to_str(package.expire_time),
         '{0:.3f}'.format(package.ttl(now))]
        for package in sorted(packages)]

    if sys.stdout.isatty():
        # Pretty print
        tablefmt = "simple"
        headers = ['Score', 'Payload', 'Expire Time', 'TTL (secs)']
    else:
        tablefmt = "plain"
        headers = []

    print(tabulate(table, headers=headers, tablefmt=tablefmt))


def _time_to_str(time_val):
    return time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(time_val))


def _get_packages_in_queue(connection):
    queue_contents = connection.zscan_iter(DEFAULT_REDIS_KEY)
    return [extract_package(entry) for entry in queue_contents]
