#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2023 tecnovert
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.


__version__ = '0.1'


import os
import time
import argparse

import xmlrpc.server

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC


BINARY_PATH = os.path.join(os.path.dirname(__file__), '../', 'packages/linux-unpacked/particl-desktop-testing')


class MyServer:
    def __init__(self, remote_app):
        self.remote_app = remote_app
        self.output = ''

    def run_exec(self, code: str):
        # Using a local output variable doesn't seem to work
        self.output = ''
        exec(code)
        return self.output

    def pagesource(self):
        return self.remote_app.page_source.encode("utf-8")


def test_particldesktop():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('--host', dest='host', help='RPC host (default=127.0.0.1)', type=str, default='127.0.0.1', required=False)
    parser.add_argument('--port', dest='port', help='RPC port to host on (default=8000)', type=int, default=8000, required=False)

    args = parser.parse_args()

    options = webdriver.ChromeOptions()
    options.binary_location = BINARY_PATH
    options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=7070')
    options.add_argument('--devtools')

    for i in range(10):
        try:
            remote_app = webdriver.remote.webdriver.WebDriver(
                command_executor='http://localhost:9515',
                options=options,)
            break
        except Exception as e:
            print('Error connecting to webdriver', e)
            time.sleep(2)

    try:
        server = xmlrpc.server.SimpleXMLRPCServer((args.host, args.port))
        server.register_instance(MyServer(remote_app))
        server.serve_forever()
    finally:
        remote_app.quit()

    print('Done.')


if __name__ == '__main__':
    test_particldesktop()
