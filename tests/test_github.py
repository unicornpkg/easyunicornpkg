# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import unittest

from easyunicornpkg.easyunicornpkg import automatic_resolver, gen_from_github


def this_test(self, package_table: list[str]):
    self.assertIsInstance(package_table, list)
    self.assertIn('package.unicornSpec = "v1.0.0"', package_table)
    self.assertIn('package.pkgType = "com.github"', package_table)
    # pylint: disable=duplicate-code
    self.assertIn(
        'package.name = "test-repo"',
        package_table,
    )
    self.assertIn(
        'package.instdat.repo_owner = "unicornpkg"',
        package_table,
    )
    self.assertIn(
        'package.instdat.repo_name = "test-repo"',
        package_table,
    )
    # pylint: enable=duplicate-code
    self.assertIn(
        'package.licensing = "CC0-1.0"',
        package_table,
    )
    self.assertIn(
        'package.instdat.filemaps["com-github-test.lua"] = "com-github-test.lua"',
        package_table,
    )


class TestGitHub(unittest.TestCase):
    def test_automatic_resolution(self):
        package_table = automatic_resolver(
            "https://github.com/unicornpkg/test-repo", True
        )
        this_test(self, package_table)

    def test_gen_from_github(self):
        package_table = gen_from_github("unicornpkg", "test-repo", "", True)
        this_test(self, package_table)
