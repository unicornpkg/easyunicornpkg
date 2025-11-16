#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Copyright 2022 Commandcracker

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# built-in modules
from re import RegexFlag, compile as re_compile, search as re_search
from urllib.request import urlopen
from argparse import ArgumentParser
from json import loads
from typing import Union
from pathlib import Path

# pylint: disable=missing-function-docstring

# pylint: disable-next=pointless-string-statement
""" Todos:
TODO: Add providers:
    - com.github.release
    - org.bitbucket
TODO: Multiple URL support
TODO: Error Codes
"""

pastebin_pattern = re_compile(r"pastebin\.com/(?P<id>[0-9a-zA-Z]+)")
git_pattern = re_compile(
    r"""
(?P<host>(git@|https://)([\w\.@]+)(/|:))
(?P<owner>[\w,\-,\_]+)/
(?P<repo>[\w,\-,\_]+)(.git){0,1}((/){0,1})
""",
    RegexFlag.VERBOSE,
)

gist_raw_url_pattern = re_compile(
    r"""
^(?P<protocol>.*):\/\/
(?P<host>.*)\/
(?P<owner>.*)\/
(?P<gistid>.*)
\/raw\/
(?P<fileid>.*)\/
(?P<filename>.*)$
""",
    RegexFlag.VERBOSE,
)


def http_get_dict(url: str) -> dict:
    return loads(urlopen(url, timeout=10).read())


# pylint: disable-next=too-many-arguments,too-many-positional-arguments
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
    licensing: str | None = None,
    generated_notice: bool = True,
) -> list:
    out = []

    if generated_notice:
        out.append("-- Generated with https://github.com/unicornpkg/easyunicornpkg")

    if url:
        out.append(f"-- {url}")

    out.append("")
    out.append("local package = {}")
    out.append(f'package.name = "{name}"')
    out.append(f'package.desc = "{desc}"')
    if licensing:
        out.append(f'package.licensing = "{licensing}"')
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
        filemaps={pastebin_id: f"{target_location}{pastebin_id}.lua"},
        pkgType="com.pastebin",
        url=f"https://pastebin.com/{pastebin_id}",
    )


def gen_from_github(
    repo_owner: str, repo_name: str, target_location: str, whitelist: list = True
) -> list:
    if whitelist is True:
        whitelist = [".lua"]

    repos_url = "https://api.github.com/repos/"
    reposinfo = http_get_dict(
        f"{repos_url}{repo_owner}/{repo_name}",
    )

    license_: str | None = None
    if reposinfo["license"]:
        license_ = reposinfo["license"]["spdx_id"]

    branch = reposinfo.get("default_branch")
    tree = http_get_dict(
        f"{repos_url}{repo_owner}/{repo_name}/git/trees/{branch}?recursive=1"
    )
    filemaps = {}

    for item in tree.get("tree"):
        if item.get("type") == "blob":
            path = item.get("path")

            if whitelist:
                suffix = Path(path).suffix
                if suffix not in whitelist:
                    continue

            filemaps[path] = f"{target_location}{path}"

    return generate_package_table(
        filemaps=filemaps,
        pkgType="com.github",
        url=f"https://github.com/{repo_owner}/{repo_name}",
        name=reposinfo.get("name").lower(),
        desc=reposinfo.get("description"),
        licensing=license_,
        repo_owner=reposinfo.get("owner").get("login"),
        repo_name=reposinfo.get("name"),
        repo_ref=branch,
    )


def gen_from_gitlab(
    repo_owner: str, repo_name: str, target_location: str, whitelist: list = True
) -> list:
    if whitelist is True:
        whitelist = [".lua"]

    projects_url = "https://gitlab.com/api/v4/projects/"
    reposinfo = http_get_dict(f"{projects_url}{repo_owner}%2F{repo_name}")
    tree = http_get_dict(
        f"{projects_url}{repo_owner}%2F{repo_name}/repository/tree?recursive=1"
    )
    filemaps = {}

    for item in tree:
        if item.get("type") == "blob":
            path = item.get("path")

            if whitelist:
                suffix = Path(path).suffix
                if suffix not in whitelist:
                    continue

            filemaps[path] = f"{target_location}{path}"

    return generate_package_table(
        filemaps=filemaps,
        pkgType="com.gitlab",
        url=f"https://gitlab.com/{repo_owner}/{repo_name}",
        name=reposinfo.get("path"),
        desc=reposinfo.get("description"),
        repo_owner=repo_owner,
        repo_name=reposinfo.get("path"),
        repo_ref=reposinfo.get("default_branch"),
    )


def gen_from_gists(
    repo_owner: str,
    repo_name: str,
    target_location: str,
    # pylint: disable-next=unused-argument
    whitelist: list = True,
) -> list:
    git = http_get_dict(f"https://api.github.com/gists/{repo_name}")
    files = git.get("files")

    fileid = "<Unknown>"
    filename = "<Unknown>"

    filemaps = {}

    for file_name in files:
        raw_url = files.get(file_name).get("raw_url")

        result = re_search(gist_raw_url_pattern, raw_url)
        groups = result.groupdict()

        fileid = groups.get("fileid")
        filename = groups.get("filename")
        filemaps[filename] = f"{target_location}{filename}"
        break

    return generate_package_table(
        filemaps=filemaps,
        pkgType="com.github.gist",
        url=f"https://gist.github.com/{repo_owner}/{repo_name}",
        desc=git.get("description"),
        name=filename,
        repo_owner=repo_owner,
        repo_name=repo_name,
        repo_ref=fileid,
    )


# pylint: disable-next=too-many-return-statements
def git_resolver(url: str, no_whitelist: bool) -> Union[list, None]:
    result = re_search(git_pattern, url)

    # the resolver is not made for this url
    if result is None:
        return None

    groups = result.groupdict()
    host = groups.get("host")

    if "gist.github.com" in host:
        return gen_from_gists(
            groups.get("owner"),
            groups.get("repo"),
            "",
        )

    if "github.com" in host:
        if no_whitelist:
            return gen_from_github(
                groups.get("owner"), groups.get("repo"), "", whitelist=None
            )
        return gen_from_github(groups.get("owner"), groups.get("repo"), "")

    if "gitlab.com" in host:
        if no_whitelist:
            return gen_from_gitlab(
                groups.get("owner"), groups.get("repo"), "", whitelist=None
            )
        return gen_from_gitlab(groups.get("owner"), groups.get("repo"), "")

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
    resolvers = [git_resolver, pastebin_resolver]

    for resolver in resolvers:
        result = resolver(url, no_whitelist)
        if result:
            return result

    return generate_package_table(
        filemaps={url: "<Unknown>"}, pkgType="local.generic", url=url
    )


def main():
    parser = ArgumentParser(
        prog="easyunicornpkg",
        description="Python utility to build a unicornpkg package table.",
    )

    parser.add_argument(
        "URL", type=str, help="the URL that the package table should be generated from."
    )

    parser.add_argument(
        "-W",
        "--no-whitelist",
        action="store_true",
        help="disables the file type whitelist.",
    )

    args = parser.parse_args()

    print("\n".join(automatic_resolver(args.URL, args.no_whitelist)))


if __name__ == "__main__":
    main()
