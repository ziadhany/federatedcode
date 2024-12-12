#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#

from django.db import models
from django.utils.translation import gettext_lazy as _


class FederatedCodePackageActivityMixin(models.Model):
    """Abstract Model for FederatedCode package activity."""

    author = models.CharField(
        max_length=300,
        null=False,
        blank=False,
        help_text=_("Author of package activity."),
    )

    content = models.JSONField(
        null=False,
        blank=False,
        help_text=_("Package activity content."),
    )

    activity_update_date = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Timestamp indicating when original activity was last updated."),
    )

    class Meta:
        abstract = True
