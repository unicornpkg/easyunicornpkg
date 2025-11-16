# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import unittest

from easyunicornpkg.easyunicornpkg import automatic_resolver, gen_from_gists


def this_test(self, package_table: list[str]):
    self.assertIsInstance(package_table, list)
    self.assertIn('package.unicornSpec = "v1.0.0"', package_table)
    self.assertIn('package.pkgType = "com.github.gist"', package_table)
    self.assertIn(
        'package.name = "com-github-gist-test.lua"',
        package_table,
    )
    self.assertIn(
        'package.instdat.repo_owner = "tomodachi94"',
        package_table,
    )
    self.assertIn(
        'package.instdat.repo_name = "6b121766ef4ec1e5c97e6834879d90c3"',
        package_table,
    )
    self.assertIn(
        'package.instdat.repo_ref = "f374449bc05821b453e4cc09bfd7f02e68edeb2f"',
        package_table,
    )
    self.assertIn(
        'package.instdat.filemaps["com-github-gist-test.lua"] = "com-github-gist-test.lua"',
        package_table,
    )


class TestGitHubGist(unittest.TestCase):
    def test_automatic_resolution(self):
        package_table = automatic_resolver(
            "https://gist.github.com/tomodachi94/6b121766ef4ec1e5c97e6834879d90c3", True
        )
        this_test(self, package_table)

    def test_gen_from_github(self):
        package_table = gen_from_gists(
            "tomodachi94", "6b121766ef4ec1e5c97e6834879d90c3", "", True
        )
        this_test(self, package_table)
