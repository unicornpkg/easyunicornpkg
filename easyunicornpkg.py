#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Commandcracker

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

# built-in modules
from re import (
    RegexFlag,
    compile as re_compile,
    search as re_search
)
from urllib.request import urlopen
from argparse import ArgumentParser
from json import loads
from sys import exit as sys_exit
from typing import Union
from pathlib import Path

# pylint: disable=missing-function-docstring

# pylint: disable-next=pointless-string-statement
""" Todos:
TODO: Add providers:
    - com.github.release
    - com.github.gist
    - com.gitlab
    - local.generic
    - org.bitbucket
TODO: Multiple URL support
TODO: Error Codes
"""

pastebin_pattern = re_compile(r"pastebin\.com/(?P<id>[0-9a-zA-Z]+)")
git_pattern = re_compile(r'''
(?P<host>(git@|https://)([\w\.@]+)(/|:))
(?P<owner>[\w,\-,\_]+)/
(?P<repo>[\w,\-,\_]+)(.git){0,1}((/){0,1})
''', RegexFlag.VERBOSE)


def http_get_dict(url: str) -> dict:
    return loads(urlopen(url, timeout=10).read())


# pylint: disable-next=too-many-arguments
def generate_package_table(
    filemaps: dict,
    # pylint: disable-next=invalid-name
    pkgType: str,
    url: str = None,
    name: str = "<Unknown>",
    desc: str = "<Unknown>",
    repo_owner: str = None,
    repo_name: str = None,
    repo_ref: str = None,
    generated_notice: bool = True
) -> list:
    out = []

    if generated_notice:
        out.append("-- Generated with easyunicornpkg, (c) 2022 Commandcracker")

    if url:
        out.append(f'-- {url}')

    out.append("")
    out.append("local package = {}")
    out.append(f'package.name = "{name}"')
    out.append(f'package.desc = "{desc}"')
    out.append("package.instdat = {}")

    if repo_owner:
        out.append(f'package.instdat.repo_owner = "{repo_owner}"')
    if repo_name:
        out.append(f'package.instdat.repo_name = "{repo_name}"')
    if repo_ref:
        out.append(f'package.instdat.repo_ref = "{repo_ref}"')

    out.append("package.instdat.filemaps = {}")

    for remote, local in filemaps.items():
        out.append(f'package.instdat.filemaps["{remote}"] = "{local}"')

    out.append(f'package.pkgType = "{pkgType}"')
    out.append('package.unicornSpec = "v1.0.0"')
    out.append("")
    out.append("return package")

    return out


def gen_from_pastebin(pastebin_id: str, target_location: str) -> list:
    return generate_package_table(
        filemaps={
            pastebin_id: f"{target_location}{pastebin_id}.lua"
        },
        pkgType="com.pastebin",
        url=f"https://pastebin.com/{pastebin_id}"
    )


def gen_from_github(
    repo_owner: str,
    repo_name: str,
    target_location: str,
    whitelist: list = True
) -> list:
    if whitelist is True:
        whitelist = [".lua"]

    reposinfo = http_get_dict(
        f"https://api.github.com/repos/{repo_owner}/{repo_name}",
    )
    branch = reposinfo.get("default_branch")

    tree = http_get_dict(
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/trees/{branch}?recursive=1"
    )

    filemaps = {}

    for item in tree.get("tree"):
        if item.get("type") == "blob":
            path = item.get("path")

            if whitelist:
                suffix = Path(path).suffix
                if suffix not in whitelist:
                    continue

            filemaps[path] = f'{target_location}{path}'

    return generate_package_table(
        filemaps=filemaps,
        pkgType="com.github",
        url=f"https://github.com/{repo_owner}/{repo_name}",
        name=reposinfo.get("name").lower(),
        desc=reposinfo.get("description"),
        repo_owner=reposinfo.get("owner").get("login"),
        repo_name=reposinfo.get("name"),
        repo_ref=branch
    )


def git_resolver(url: str, no_whitelist: bool) -> Union[list, None]:
    result = re_search(git_pattern, url)

    # the resolver is not made for this url
    if result is None:
        return None

    groups = result.groupdict()
    host = groups.get("host")

    if "github.com" in host:
        if no_whitelist:
            return gen_from_github(
                groups.get("owner"),
                groups.get("repo"),
                "",
                whitelist=None
            )
        return gen_from_github(
            groups.get("owner"),
            groups.get("repo"),
            ""
        )

    if "gitlab.com" in host:
        sys_exit("GitLab is currently not supported")

    # The resolver dos not support this git provider
    return None


def pastebin_resolver(url: str, _unused) -> Union[list, None]:
    result = re_search(pastebin_pattern, url)

    # the resolver is not made for this url
    if result is None:
        return None

    groups = result.groupdict()
    pastebin_id = groups.get("id")

    return gen_from_pastebin(pastebin_id, "")


def automatic_resolver(url: str, no_whitelist: bool) -> list:
    resolvers = [
        git_resolver,
        pastebin_resolver
    ]

    for resolver in resolvers:
        result = resolver(url, no_whitelist)
        if result:
            return result

    sys_exit("URL not supported")


def main():
    parser = ArgumentParser(
        prog='easyunicornpkg',
        description='Python utility to build a unicornpkg package table.'
    )

    parser.add_argument(
        'URL',
        type=str,
        help='the URL that the package table should be generated from.'
    )

    parser.add_argument(
        '-W', '--no-whitelist',
        action='store_true',
        help="disables the file type whitelist."
    )

    args = parser.parse_args()

    print("\n".join(automatic_resolver(
        args.URL,
        args.no_whitelist
    )))


if __name__ == "__main__":
    main()
