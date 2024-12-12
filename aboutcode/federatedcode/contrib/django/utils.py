#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#


import saneyaml


def get_package_activity_type(activity: dict) -> str:
    return activity.get("type")


def get_package_activity_object(activity: dict) -> dict:
    return activity.get("object")


def get_package_activity_author(activity: dict) -> str:
    activity_object = get_package_activity_object(activity)
    return activity_object.get("author")


def get_package_activity_content(activity: dict) -> dict:
    activity_object = get_package_activity_object(activity)
    content = activity_object.get("content")
    return saneyaml.load(content)


def get_package_activity_update_date(activity: dict) -> str:
    activity_object = get_package_activity_object(activity)
    return activity_object.get("update_date")
