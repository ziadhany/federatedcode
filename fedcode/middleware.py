#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#

import zoneinfo

from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Activate local timezone for user using cookies
            tzname = request.COOKIES.get("user_timezone")
            if tzname:
                timezone.activate(zoneinfo.ZoneInfo(tzname))
            else:
                timezone.deactivate()
        except Exception as e:
            timezone.deactivate()

        return self.get_response(request)
