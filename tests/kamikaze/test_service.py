import unittest

from kamikaze.service import (
    _entries_to_queue_updates,
    _time_until_package_expires,
)
from kamikaze.utils import Package


class TestService(unittest.TestCase):

    def test_entries_to_queue_updates(self):
        entries = [
            ('12:yellow', 1),
            ('10:orange', 2),
            ('21:red', 3),
            ('22:blue', 5),
            ('23:green', 7),
        ]
        queue_updates = _entries_to_queue_updates(entries, now=20)
        self.assertEqual(
            ['yellow', 'orange'],
            [package.payload for package in queue_updates.expired_packages])
        self.assertEqual('red', queue_updates.highest_priority_package.payload)

    def test_time_until_package_expires(self):
        package = Package(payload='saucepans', expire_time=10, score=22)
        self.assertEqual(1, _time_until_package_expires(package, now=9))
        self.assertEqual(-1, _time_until_package_expires(package, now=11))
        self.assertEqual(None, _time_until_package_expires(None, now=11))
