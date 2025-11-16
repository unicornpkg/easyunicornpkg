# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import unittest

from easyunicornpkg.easyunicornpkg import automatic_resolver, pastebin_resolver


def this_test(self, package_table: list[str]):
    self.assertIsInstance(package_table, list)
    self.assertIn('package.unicornSpec = "v1.0.0"', package_table)
    self.assertIn('package.pkgType = "com.pastebin"', package_table)
    self.assertIn(
        'package.instdat.filemaps["p4zeq7Ma"] = "p4zeq7Ma.lua"', package_table
    )


class TestPastebin(unittest.TestCase):
    def test_automatic_resolution(self):
        package_table = automatic_resolver("https://pastebin.com/p4zeq7Ma", True)
        this_test(self, package_table)

    def test_pastebin_resolver(self):
        package_table = pastebin_resolver("https://pastebin.com/p4zeq7Ma", True)
        this_test(self, package_table)
