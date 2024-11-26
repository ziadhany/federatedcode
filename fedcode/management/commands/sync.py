#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#
from django.core.management import BaseCommand

from fedcode.importer import Importer
from fedcode.models import SyncRequest


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        The Sync Command is responsible for running the Importer and updating the status of pending sync requests.
        """
        for sync_r in SyncRequest.objects.all().order_by("created_at"):
            if sync_r.done:
                continue

            try:
                repo = sync_r.repo
                repo.git_repo_obj.remotes.origin.pull()
                importer = Importer(repo, repo.admin)
                importer.run()
                sync_r.done = True
            except Exception as e:
                sync_r.error_message = e
            finally:
                sync_r.save()
