=======================
aboutcode.federatedcode
=======================

|license| |build| |release|

.. |license| image:: https://img.shields.io/badge/License-Apache--2.0-blue.svg?style=for-the-badge
    :target: https://opensource.org/licenses/Apache-2.0

.. |build| image:: https://img.shields.io/github/actions/workflow/status/aboutcode-org/federatedcode/pypi-release-aboutcode-federatedcode.yml?style=for-the-badge&logo=github

.. |release| image:: https://img.shields.io/pypi/v/aboutcode.federatedcode?style=for-the-badge&logo=pypi&color=%23a569bd
    :target: https://pypi.org/project/aboutcode.federatedcode/
    :alt: PyPI - Version


This is a CLI and library of FederatedCode client utilities for fetching and subscribing to package metadata, and utilities for managing activity streams.

Installation
============

To install the FederatedCode client, use the following command:

.. code-block:: bash

    pip install aboutcode.federatedcode


CLI Usage
=========

Use the ``federatedcode`` CLI to discover and fetch scans using the PURL:

.. code-block:: bash

    # Display the general help for federatedcode
    federatedcode --help

    # Display help for a specific command
    federatedcode [command] --help

Example
-------

Discover a PURL in the FederatedCode AP Server:

.. code-block:: bash

    ❯ federatedcode discover pkg:npm/%40angular/animation
    http://<Your-FederatedCode-Host>/purls/@pkg:npm/%2540angular/animation


Library Usage
=============

Use the ``client`` module to fetch scan results, subscribe to packages, or discover packages
in the AP server.

.. code-block:: python

    from aboutcode.federatedcode import client

Use the ``contrib`` module to get the Django mixin and various utilities to manage activity streams.

.. code-block:: python

    from aboutcode.federatedcode.contrib import django

License
=======

Copyright (c) nexB Inc. and others. All rights reserved.

SPDX-License-Identifier: Apache-2.0

See https://aboutcode.org for more information about AboutCode OSS projects.

.. code-block:: none

    You may not use this software except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.