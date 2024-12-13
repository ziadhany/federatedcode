#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#

from unittest.mock import patch

from aboutcode.federatedcode.client import discover_package_in_ap_server


def test_discover_package_in_ap_server():
    with patch("requests.head") as mock_head:
        mock_response = mock_head.return_value
        mock_response.status_code = 200

        result = discover_package_in_ap_server("pkg:foo/bar")
        expected = "http://localhost:8000/purls/@pkg:npm/foo/bar"
        result == expected
