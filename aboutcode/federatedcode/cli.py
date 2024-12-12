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

from aboutcode.federatedcode import client


@click.group()
def handler():
    pass


@click.command()
@click.argument("purl")
def scan(purl):
    """
    Get package scan for PURL from FederatedCode git repository.

    PURL: PURL to fetch scan result
    """
    click.echo(client.get_package_scan(purl=purl))


@click.command()
@click.argument("purl")
def discover(purl):
    """
    Discover existing Packages in the FederatedCode AP server.

    PURL: PURL to find in AP server
    """
    if response := client.discover_package_in_ap_server(purl=purl):
        click.echo(click.style(response, fg="green", bold=True))
    else:
        click.echo(
            click.style(
                f"Error: {purl} not available on {client.FEDERATEDCODE_AP_HOST} AP server.",
                fg="red",
                bold=True,
            )
        )


handler.add_command(scan)
handler.add_command(discover)

if __name__ == "__main__":
    handler()
