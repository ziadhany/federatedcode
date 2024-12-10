#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#

from traceback import format_exc as traceback_format_exc

import requests
from django.core.management.base import BaseCommand

from fedcode.models import FederateRequest
from fedcode.signatures import FEDERATEDCODE_PRIVATE_KEY
from fedcode.signatures import HttpSignature


def send_fed_req_task():
    """Send activity request to the target and save the status."""

    for rq in FederateRequest.objects.all().order_by("created_at"):
        if not rq.done:
            try:
                headers = {"Content-Type": "application/json"}
                requests.post(rq.target, json=rq.body, headers=headers)
                rq.done = True
                rq.save()
            except Exception as e:
                rq.error_message = f"Failed to federate {rq!r} {e!r} \n {traceback_format_exc()}"
            finally:
                rq.save()


class Command(BaseCommand):
    def handle(self, *args, **options):
        send_fed_req_task()
