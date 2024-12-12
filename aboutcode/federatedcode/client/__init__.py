#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#

import os
from typing import Union
from urllib.parse import quote
from urllib.parse import urljoin

import requests
from aboutcode.hashid import get_package_base_dir
from dotenv import load_dotenv
from packageurl import PackageURL

load_dotenv()

FEDERATEDCODE_GIT_RAW_URL = os.getenv(
    "FEDERATEDCODE_GIT_RAW_URL",
    "https://raw.githubusercontent.com/aboutcode-org/",
)

FEDERATEDCODE_AP_HOST = os.getenv(
    "FEDERATEDCODE_AP_HOST",
    "http://localhost:8000/",
)


class ScanNotAvailableError(Exception):
    pass


def get_package_scan(purl: Union[PackageURL, str]):
    """Return the package scan result for a PURL from the FederatedCode Git repository."""

    if not FEDERATEDCODE_GIT_RAW_URL:
        raise ValueError("Provide ``FEDERATEDCODE_GIT_RAW_URL`` in .env file.")

    if isinstance(purl, str):
        purl = PackageURL.from_string(purl)

    if not purl.version:
        raise ValueError("Missing version in PURL.")

    package_path = get_package_base_dir(purl=purl)
    package_path_parts = package_path.parts

    repo_name = f"{package_path_parts[0]}/refs/heads/main"
    package_dir_path = "/".join(package_path_parts[1:])
    version = purl.version
    file_name = "scancodeio.json"

    url_parts = [repo_name, package_dir_path, version, file_name]

    file_url = urljoin(FEDERATEDCODE_GIT_RAW_URL, "/".join(url_parts))

    try:
        response = requests.get(file_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        if response.status_code == 404:
            raise ScanNotAvailableError(f"No scan available for {purl!s}")
        raise err


def subscribe_package(federatedcode_host, remote_username, purl):
    """Subscribe package for their metadata update from FederatedCode."""

    url_path = f"api/v0/users/@{remote_username}/subscribe/?purl={quote(purl)}"
    return requests.get(urljoin(federatedcode_host, url_path))


def discover_package_in_ap_server(purl: Union[str, PackageURL]):
    """Return package profile if PURL exists in AP server."""

    if not FEDERATEDCODE_AP_HOST:
        raise ValueError("Provide ``FEDERATEDCODE_AP_HOST`` in .env file.")

    if isinstance(purl, str):
        purl = PackageURL.from_string(purl)

    if purl.version or purl.subpath or purl.qualifiers:
        purl = PackageURL(
            type=purl.type,
            namespace=purl.name,
            name=purl.name,
        )

    package = quote(str(purl), safe=":/")
    url = urljoin(FEDERATEDCODE_AP_HOST, f"/purls/@{package}")
    response = requests.head(url, allow_redirects=True)
    if response.status_code == 200:
        return url
