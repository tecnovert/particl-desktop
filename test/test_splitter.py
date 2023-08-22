#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2023 tecnovert
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

'''
Notes
 - Use without docker image, see notes.txt

'''

__version__ = '0.1'


import os
import json
import time
import signal
import decimal
import argparse
import threading
import subprocess

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC


BINARY_PATH = os.path.join(os.path.dirname(__file__), '../', 'packages/linux-unpacked/particl-desktop-testing')
DATADIR = os.path.expanduser('~/.particl')
PARTICL_CLIDIR = os.path.expanduser(os.getenv('PARTICL_CLIDIR', '~/tmp/particl-23.0.3.0/bin/'))
delay_event = threading.Event()


def cli1(cmd, wallet=None):
    args = os.path.join(PARTICL_CLIDIR, 'particl-cli') + ' --regtest' + ' --rpcport=51835' + f' --datadir={DATADIR} '
    if wallet:
        args += ' --rpcwallet=' + wallet
    args += ' ' + cmd
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out = p.communicate()
    r = out[0]
    re = out[1]
    if re and len(re) > 0:
        raise ValueError('RPC error ' + str(re))
    try:
        return json.loads(r)
    except Exception:
        pass
    return r.decode('utf-8').strip()


def jsonDecimal(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError


def dumpje(jin, replace_with='\\"'):
    return json.dumps(jin, default=jsonDecimal).replace('"', replace_with)


def waitForHeight(nHeight, delay_event, nTries=60):
    for i in range(nTries):
        delay_event.wait(1)
        if delay_event.is_set():
            raise ValueError('waitForHeight stopped.')
        ro = cli1('getblockchaininfo')
        if ro['blocks'] >= nHeight:
            return True
    raise ValueError('waitForHeight timed out.')


def stakeToHeight(height, delay_event):
    cli1('walletsettings stakelimit "%s"' % (dumpje({'height': height})), 'main')
    cli1('reservebalance false', 'main')
    waitForHeight(height, delay_event)


def stakeBlocks(num_blocks, delay_event):
    height = int(cli1('getblockcount'))
    stakeToHeight(height + num_blocks, delay_event)


def run_loop():
    while not delay_event.is_set():
        stakeBlocks(1, delay_event)
        delay_event.wait(5.0)


def signalHandler(sig, frame):
    print('Signal {} detected, ending.'.format(sig))
    delay_event.set()


def acceptTerms(remote_app):
    cbx = remote_app.find_element(By.ID, "mat-checkbox-1-input")
    actions = webdriver.ActionChains(remote_app)
    actions.move_to_element(cbx)
    actions.click(cbx)
    actions.perform()

    btn = remote_app.find_element(By.CLASS_NAME, "mat-raised-button")
    btn.click()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('--delayafter', dest='delayafter', help='Seconds to delay for once complete (default=0)', type=int, default=0, required=False)

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
            delay_event.wait(2)

    delay_event.wait(2)

    try:
        heading = remote_app.find_element(By.XPATH, "//h2[contains(text(),'Terms & Conditions')]")
        print('\nAccept terms node 1')
        acceptTerms(remote_app)
    except Exception as e:
        if 'no such element' in str(e):
            print("Terms appear accepted")
        else:
            print("Check / accept terms failed", e)

    for i in range(16):
        print('Waiting for core to respond')
        delay_event.wait(2)
        try:
            wallets = cli1('listwallets')
        except Exception:
            continue
        break

    print('\nPreparing staking wallet')
    wallets = cli1('listwallets')
    print('wallets', wallets)
    if 'main' not in wallets:
        try:
            cli1('loadwallet main')
        except Exception:
            cli1('createwallet main')
            cli1('walletsettings stakingoptions "{\\"stakecombinethreshold\\":100,\\"stakesplitthreshold\\":200}"', 'main')
            cli1('walletsettings stakelimit "{}"'.format(dumpje({'height': 1})), 'main')
            cli1('reservebalance true 10000000', 'main')
            cli1('extkeyimportmaster "abandon baby cabbage dad eager fabric gadget habit ice kangaroo lab absorb"', 'main')

    try:
        print('Installing signal handler, ctrl+c to quit')
        signal.signal(signal.SIGINT, signalHandler)
        stake_thread = threading.Thread(target=run_loop)
        stake_thread.start()

        print('Click "Wallet"')
        WebDriverWait(remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'wallet')]"))).click()

        print('Click "Send/Convert"')
        WebDriverWait(remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'wallet/active/send')]"))).click()

        print('Click "Convert Public & Private"')
        WebDriverWait(remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class,'mat-tab-label') and @aria-posinset='2']"))).click()

        delay_event.wait(2)
        print('Select "Anon"')
        cbxs = remote_app.find_elements(By.XPATH, "//mat-radio-button")
        for cbx in cbxs:
            inner_html = cbx.get_attribute('innerHTML')
            if 'Offers the highest privacy' in inner_html:
                actions = webdriver.ActionChains(remote_app)
                actions.move_to_element(cbx)
                actions.click(cbx)
                actions.perform()
                break

        if args.delayafter > 0:
            print(f'Delaying for {args.delayafter} seconds')
            print('Ctrl+c to quit')
            delay_event.wait(args.delayafter)
    finally:
        delay_event.set()
        stake_thread.join()

    print('Done.')


if __name__ == '__main__':
    main()
