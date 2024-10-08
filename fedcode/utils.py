#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#

import io
import json
import os
from urllib.parse import urlparse

import requests
from django.urls import resolve
from django.urls import reverse
from git.repo.base import Repo
from packageurl import PackageURL

from federatedcode.settings import FEDERATEDCODE_DOMAIN


def parse_webfinger(subject):
    """
    get the username and host from webfinger acct:user@host
    >>> parse_webfinger("acct:ziadhany@example.com")
    ('ziadhany', 'example.com')
    >>> parse_webfinger("acct:")
    ('', '')
    >>> parse_webfinger("ziadhany@example.com")
    ('ziadhany', 'example.com')
    """
    if subject.startswith("acct"):
        acct = subject[5:]
        result = acct.split("@")
        user_part, host = "", ""
        if len(result) == 2:
            user_part, host = result
        return user_part, host
    else:
        return tuple(subject.split("@"))


def generate_webfinger(username, domain=FEDERATEDCODE_DOMAIN):
    return username + "@" + domain


def clone_git_repo(repo_path, repo_url):
    """
    Clone Git repository in ${repo_path}/repo_name.git
    """
    repo_name = str(hash(repo_url))
    abspath = os.path.join(repo_path, repo_name)
    repo = Repo.clone_from(repo_url, str(abspath))
    return repo


def full_reverse(page_name, *args, **kwargs):
    web_page = reverse(page_name, args=args, kwargs=kwargs)
    return f'{"https://"}{FEDERATEDCODE_DOMAIN}{web_page}'


def full_resolve(full_path):
    parser = urlparse(full_path)
    resolver = resolve(parser.path)
    return resolver.kwargs, resolver.url_name


def check_purl_actor(purl_string):
    """
    Purl actor is a purl without a version
    """
    purl = PackageURL.from_string(purl_string)
    if not (purl.version or purl.qualifiers or purl.subpath):
        return True
    return False


def ap_collection(objects):
    """
    accept the result of the query like filter and Add all objects in activitypub collection format
    https://www.w3.org/TR/activitystreams-vocabulary/#dfn-orderedcollection
    """
    return {
        "type": "OrderedCollection",
        "totalItems": objects.count(),
        "orderedItems": [obj.to_ap for obj in objects.all()],
    }


def webfinger_actor(domain, user):
    """"""
    acct = generate_webfinger(user, domain)
    url = f"http://{domain}/.well-known/webfinger?resource=acct:{acct}"  # TODO http -> https
    headers = {"User-Agent": ""}  # TODO
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()["links"][1][
                "href"
            ]  # TODO please check if type = "application/activity+json"
    except requests.exceptions.RequestException as e:
        return f"Failed to fetch the actor {e}"


def fetch_actor(url):
    """
    fetch actor profile URL and return profile Json-LD
    """
    headers = {"User-Agent": ""}  # TODO
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()

    except requests.exceptions.HTTPError as e:
        return f"Http Error: {e}"
    except requests.exceptions.ConnectionError as e:
        return f"Error Connecting: {e}"
    except requests.exceptions.Timeout as e:
        return f"Timeout Error:{e}"
    except requests.exceptions.RequestException as e:
        return f"OOps: Something Else {e}"

    return "Failed to fetch the actor"


def file_data(file_name):
    with open(file_name) as file:
        data = file.read()
        return json.loads(data)


def load_git_file(git_repo_obj, filename, commit_id):
    """
    Get file data from a specific git commit using gitpython
    copied from https://stackoverflow.com/a/54900961/9871531
    """
    commit = git_repo_obj.commit(commit_id)
    target_file = commit.tree / filename

    with io.BytesIO(target_file.data_stream.read()) as f:
        return f.read().decode("utf-8")
