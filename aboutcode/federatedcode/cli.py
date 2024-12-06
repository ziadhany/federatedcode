#!/usr/bin/env python3
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# FederatedCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/federatedcode for support or download.
# See https://aboutcode.org for more information about AboutCode.org OSS projects.
#

import click
from aboutcode.federatedcode.client import get_package_scan

@click.command()
@click.argument('purl')
def handler(purl):
    """
    Get package scan for PURL from FederatedCode git repository.
    
    PURL: PURL to fetch scan result
    """
    click.echo(get_package_scan(purl=purl))

if __name__ == '__main__':
    handler()
