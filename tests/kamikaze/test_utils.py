import unittest

from kamikaze.utils import (
    create_package_with_ttl,
    extract_package,
    Package,
)


class TestUtils(unittest.TestCase):

    def test_get_sorted_packages(self):
        package1 = Package(payload='saucepans', expire_time=10, score=22)
        package2 = Package(payload='chairs', expire_time=11, score=23)
        package3 = Package(payload='baloons', expire_time=12, score=21)
        self.assertEqual(
            [package3, package1, package2],
            sorted([package1, package2, package3]))

    def test_create_package_with_ttl(self):
        package = create_package_with_ttl(
            payload='saucepans', ttl=10, score=22, now=3610)
        self.assertPackageEqual(
            package, payload='saucepans', expire_time=3620,
            raw_entry='3620.0:saucepans', score=22)

    def test_extract_package(self):
        package = extract_package(('10:cactus', 3.5))
        self.assertPackageEqual(
            package, payload='cactus', expire_time=10,
            raw_entry='10.0:cactus', score=3.5)

    def test_extract_package_with_byte_value(self):
        package = extract_package((b'10:cactus', 3.5))
        self.assertPackageEqual(
            package, payload='cactus', expire_time=10,
            raw_entry='10.0:cactus', score=3.5)

    def test_extract_package_with_no_expire_time(self):
        package = extract_package((b':cactus', 3.5))
        self.assertPackageEqual(
            package, payload='cactus', expire_time=None,
            raw_entry=':cactus', score=3.5)

    def test_package_ttl(self):
        package = Package(payload='saucepans', expire_time=10, score=22)
        self.assertEqual(8, package.ttl(now=2))

    def test_package_expired(self):
        package = Package(payload='saucepans', expire_time=10, score=22)
        self.assertTrue(package.expired(now=12))

    def test_package_not_expired(self):
        package = Package(payload='saucepans', expire_time=10, score=22)
        self.assertFalse(package.expired(now=2))

    def test_package_repr(self):
        package = Package(payload='saucepans', expire_time=10, score=22)
        self.assertEqual(
            'Package(payload=saucepans,score=22,expire_time=10.0)',
            str(package))

    def assertPackageEqual(self, package, payload, expire_time, raw_entry,
                           score):
        self.assertEqual(payload, package.payload)
        self.assertEqual(expire_time, package.expire_time)
        self.assertEqual(raw_entry, package.raw_entry)
        self.assertEqual(score, package.score)
