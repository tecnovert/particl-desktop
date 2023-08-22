#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) 2023 tecnovert
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.

'''
Notes
 - Use with docker-compose.yml
 - Close any modals before rerunning
 - Killing the docker container is likely to lose the chain.

'''

__version__ = '0.1'

import os
import time
import json
import random
import signal
import decimal
import argparse
import threading
import subprocess
import xmlrpc.client


PARTICL_CLIDIR = os.path.expanduser(os.getenv('PARTICL_CLIDIR', '~/tmp/particl-23.1.5.0/bin/'))
delay_event = threading.Event()


def cli1(cmd, wallet=None):
    args = os.path.join(PARTICL_CLIDIR, 'particl-cli') + ' --regtest' + ' --rpcport=51937' + ' --datadir=/tmp/pdtests/node1/.particl '
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


def cli2(cmd, wallet=None):
    args = os.path.join(PARTICL_CLIDIR, 'particl-cli') + ' --regtest' + ' --rpcport=51938' + ' --datadir=/tmp/pdtests/node2/.particl'
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


def randomFirstName():
    return random.choice(('Liam', 'Olivia', 'Noah', 'Emma', 'Oliver', 'Charlotte', 'Elijah', 'Amelia', 'James', 'Ava'))


def randomLastName():
    return random.choice(('Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez'))


def acceptTerms(server):
    code = '''
cbx = self.remote_app.find_element(By.ID, "mat-checkbox-1-input")
#cbx.click()
actions = webdriver.ActionChains(self.remote_app)
actions.move_to_element(cbx)
actions.click(cbx)
actions.perform()

btn = self.remote_app.find_element(By.CLASS_NAME, "mat-raised-button")
btn.click()
    '''
    result = server.run_exec(code)


def createMarket(server):
    # Create new market

    # Market Module
    print('Click "Market Module"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'market')]"))).click()
    '''
    result = server.run_exec(code)

    print('Click "Manage Markets"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'management')]"))).click()
    '''
    result = server.run_exec(code)

    print('Click "Create New Market"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[@routerlink='create']"))).click()
    '''
    result = server.run_exec(code)

    # Name input
    print('Fill name input')
    code = '''
input = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='name']")))
input.send_keys("Best Market")
    '''
    result = server.run_exec(code)

    print('Check "Community Market"')
    code = '''
cbx = self.remote_app.find_elements(By.XPATH, "//mat-radio-button")[1]
actions = webdriver.ActionChains(self.remote_app)
actions.move_to_element(cbx)
actions.click(cbx)
actions.perform()
    '''
    result = server.run_exec(code)

    print('Click "Confirm & Create"')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@color='primary']"))).click()
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)

    print('Get market id from span')
    code = '''
market_id_span = WebDriverWait(self.remote_app, 10).until(EC.presence_of_element_located((By.XPATH, "//span[@class='market-type']")))
self.output = market_id_span.get_attribute('innerHTML')
    '''
    result = server.run_exec(code)
    print("run_exec", result)
    market_id = result.split(':')[1].strip()
    print("market_id", market_id)
    return market_id


def joinMarket(server, market_id):
    # Market Module
    print('Click "Market Module"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'market')]"))).click()
    '''
    result = server.run_exec(code)

    # Manage Markets
    print('Click "Manage Markets"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'management')]"))).click()
    '''
    result = server.run_exec(code)

    # Browser
    print('Select Browser tab')
    code = '''
#WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.ID, "mat-tab-label-7-1"))).click()
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-posinset='2']"))).click()
    '''
    result = server.run_exec(code)

    print('Click "Join via Market ID"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'join-button-toggle')]"))).click()
    '''
    result = server.run_exec(code)

    print('Fill name input')
    code = '''
input = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='name']")))
input.send_keys("Best Market")
    '''
    result = server.run_exec(code)

    print('Fill inviteCode input')
    code = f'''
input2 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='inviteCode']")))
input2.send_keys("{market_id}:::{market_id}")
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)
    print('Click "Join This Market" button (hack takes long)')
    # occluded button is also found, no idea why only the worst idea works
    code = '''
#WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Join this Market')]"))).click()
#btns = self.remote_app.find_elements(By.XPATH, "//button")
btns = self.remote_app.find_elements(By.XPATH, "//button[@color='primary']")
for btn in btns:
    try:
        WebDriverWait(self.remote_app, 5).until(EC.element_to_be_clickable(btn)).click()
        break
    except Exception:
        continue

    #inner_html = btn.get_attribute('innerHTML')
    #if 'Join this Market' in inner_html:
    #    #btn.click()
    #    WebDriverWait(self.remote_app, 5).until(EC.element_to_be_clickable(btn)).click()
    #    break
    '''
    result = server.run_exec(code)

    print('Select "Your Markets" tab')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-posinset='1']"))).click()
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)
    print('Get market id from span')
    code = '''
market_id_span = self.remote_app.find_element(By.XPATH, "//span[@class='market-type']")
self.output = market_id_span.get_attribute('innerHTML')
    '''
    result = server.run_exec(code)
    market_id = result.split(':')[1].strip()
    print("market_id", market_id)

    return market_id


def getMarketID(server):
    print('Click "Market Module"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'market')]"))).click()
    '''
    result = server.run_exec(code)

    print('Click "Manage Markets"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'management')]"))).click()
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)
    print('Get market id from span')
    code = '''
market_id_span = self.remote_app.find_element(By.XPATH, "//span[@class='market-type']")
self.output = market_id_span.get_attribute('innerHTML')
    '''
    result = server.run_exec(code)
    market_id = result.split(':')[1].strip()
    print("market_id", market_id)

    return market_id


def addListing(server, listing_data={}):
    print('Click "Market Module"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'market')]"))).click()
    '''
    result = server.run_exec(code)

    print('Click "Sell"')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'market/sell')]"))).click()
    '''
    result = server.run_exec(code)

    print('Select "Inventory & Products" tab')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-posinset='3']"))).click()
    '''
    result = server.run_exec(code)

    print('Click "New"')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[@routerlink='new-listing']"))).click()
    '''
    result = server.run_exec(code)

    print('Fill productCode input')
    product_code = listing_data.get('product_code', 'nft_course_001')
    code = f'''
input1 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='productCode']")))
input1.send_keys("{product_code}")
    '''
    result = server.run_exec(code)

    print('Fill title input')
    title = listing_data.get('title', 'Best NFT course')
    code = f'''
input2 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='title']")))
input2.send_keys("{title}")
    '''
    result = server.run_exec(code)

    print('Fill summary input')
    summary = listing_data.get('summary', 'Make moni from jpg')
    code = f'''
input3 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//textarea[@formcontrolname='summary']")))
input3.send_keys("{summary}")
    '''
    result = server.run_exec(code)

    print('Fill description input')
    description = listing_data.get('description', 'Long description very text')
    code = f'''
input4 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//textarea[@formcontrolname='description']")))
input4.send_keys("{description}")
    '''
    result = server.run_exec(code)

    print('Fill basePrice input')
    base_price = listing_data.get('base_price', 1)
    code = f'''
input5 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='basePrice']")))
input5.send_keys("{base_price}")
    '''
    result = server.run_exec(code)

    print('Select Shipping From country')
    shipping_from = listing_data.get('shipping_from', 'Afghanistan')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//tree-select[contains(@placeholderlabel,'Shipping from')]"))).click()
    '''
    result = server.run_exec(code)

    code = f'''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'{shipping_from}')]"))).click()
    '''
    result = server.run_exec(code)

    print('Fill priceShipLocal input')
    price_ship_local = listing_data.get('price_ship_local', 1)
    code = f'''
input6 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='priceShipLocal']")))
input6.send_keys("{price_ship_local}")
    '''
    result = server.run_exec(code)

    print('Fill priceShipIntl input')
    price_ship_intl = listing_data.get('price_ship_intl', 1)
    code = f'''
input7 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='priceShipIntl']")))
input7.send_keys("{price_ship_intl}")
    '''
    result = server.run_exec(code)

    print('Click Publishing Settings')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//mat-expansion-panel[contains(@class,'publishing-settings')]"))).click()
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)
    print('Click Publish To')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//div[@class='mat-form-field-flex']")
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    if 'Select Market' in inner_html:
        btn.click()
        break
    '''
    result = server.run_exec(code)

    print('Set Market')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Best Market')]"))).click()
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)

    print('Click Product Category')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//div[@class='mat-form-field-flex']")
#self.output = str(len(btns))
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    #self.output += "     BTN" + inner_html
    if 'Select a category' in inner_html:
        #self.output += "     BTN" + inner_html
        btn.click()
        break
    '''
    result = server.run_exec(code)
    print('result', result)

    print('Set Product Category')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Automotive')]"))).click()
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)
    print('Click "Save and Publish"')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//button[@color='primary']")
#self.output = str(len(btns))
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    #self.output += "     BTN" + inner_html
    if 'Save and Publish' in inner_html:
        #self.output += "     BTN" + inner_html
        btn.click()
        break
    '''
    result = server.run_exec(code)
    print('result', result)

    print('Waiting 2 seconds')
    time.sleep(2)
    print('Click "Select Duration"')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//div[@class='mat-form-field-flex']")
#self.output = str(len(btns))
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    #self.output += "     BTN" + inner_html
    if 'Select duration' in inner_html:
        #self.output += "     BTN" + inner_html
        btn.click()
        break
    '''
    result = server.run_exec(code)
    print('result', result)

    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'2 days')]"))).click()
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)
    print('Click "Publish Listing"')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//button[@color='primary']")
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    if 'Publish Listing' in inner_html:
        btn.click()
        break
    '''
    result = server.run_exec(code)
    print('result', result)


def countListings(server, name=None):
    print('Click "Market Module"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'market')]"))).click()
    '''
    result = server.run_exec(code)

    print('Click "Browse"')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'market/listings')]"))).click()
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)

    print('Count listings')
    code = '''
cards = self.remote_app.find_elements(By.XPATH, "//mat-card[contains(@class,'listing')]")
listings = 0
for card in cards:
    listings += 1
self.output = listings
    '''
    result = server.run_exec(code)
    return result


def addListingToCart(server, name):
    print('Click "Market Module"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'market')]"))).click()
    '''
    result = server.run_exec(code)

    print('Click "Browse"')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'market/listings')]"))).click()
    '''
    result = server.run_exec(code)

    # If the MP starts syncing all open modals seem to close!
    print('Waiting 1 second')
    time.sleep(1)

    print('Click listing')
    code = f'''
cards = self.remote_app.find_elements(By.XPATH, "//mat-card[contains(@class,'listing')]")
for card in cards:
    inner_html = card.get_attribute('innerHTML')
    if '{name}' in inner_html:
        #card.click()
        actions = webdriver.ActionChains(self.remote_app)
        actions.move_to_element(card)
        actions.click(card)
        actions.perform()
        break
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)

    print('Click Add to Cart')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//button[@color='primary']")
self.output = str(len(btns)) + ' '
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    if 'Add to Cart' in inner_html:
        self.output += 'click'
        btn.click()
        break
    '''
    result = server.run_exec(code)
    print('result', result)

    print('Waiting 1 second')
    time.sleep(1)

    print('Close modal')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'modal-close')]"))).click()
    '''
    result = server.run_exec(code)


def checkoutCart(server, data={}):
    print('Click "Market Module"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'market')]"))).click()
    '''
    result = server.run_exec(code)

    print('Click "Cart"')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'market/cart')]"))).click()
    '''
    result = server.run_exec(code)

    print('Fill firstName input')
    first_name = data.get('first_name', randomFirstName())
    code = f'''
input1 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='firstName']")))
input1.send_keys("{first_name}")
    '''
    result = server.run_exec(code)

    print('Fill lastName input')
    last_name = data.get('last_name', randomLastName())
    code = f'''
input2 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='lastName']")))
input2.send_keys("{last_name}")
    '''
    result = server.run_exec(code)

    print('Fill addressLine1 input')
    addr_line_1 = data.get('addr_line_1', '99 Ninety Nine St')
    code = f'''
input3 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='addressLine1']")))
input3.send_keys("{addr_line_1}")
    '''
    result = server.run_exec(code)

    print('Fill zipCode input')
    zip_code = data.get('zip_code', '9999')
    code = f'''
input4 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='zipCode']")))
input4.send_keys("{zip_code}")
    '''
    result = server.run_exec(code)

    print('Fill city input')
    city = data.get('city', 'Tirana')
    code = f'''
input5 = WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//input[@formcontrolname='city']")))
input5.send_keys("{city}")
    '''
    result = server.run_exec(code)

    print('Select country')
    country = data.get('country', 'Albania')
    code = f'''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//tree-select[contains(@placeholderlabel,'Select your country')]"))).click()
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'{country}')]"))).click()
    '''
    result = server.run_exec(code)

    print('Uncheck save profile')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//div[@class='mat-checkbox-inner-container']")
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    if 'save-shipping-profile' in inner_html:
        btn.click()
        break
    '''
    result = server.run_exec(code)

    print('Click "Review & Submit this Order"')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//button[@color='primary']")
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    if 'Submit this Order' in inner_html:
        btn.click()
        break
    '''
    result = server.run_exec(code)
    print('result', result)

    print('Waiting 1 second')
    time.sleep(1)

    print('Click "Confirm Order & Submit"')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//button[@color='primary']")
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    if 'Confirm Order' in inner_html:
        btn.click()
        break
    '''
    result = server.run_exec(code)
    print('result', result)


def countOrders(server, name=None):
    print('Click "Market Module"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'market')]"))).click()
    '''
    result = server.run_exec(code)

    print('Click "Sell"')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'market/sell')]"))).click()
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)

    print('Count orders')
    code = '''
divs = self.remote_app.find_elements(By.XPATH, "//div[@class='hash']")
orders = []
for div in divs:
    inner_html = div.get_attribute('innerHTML')
    orders.append(inner_html)
self.output = orders
    '''
    result = server.run_exec(code)
    print('result', result)
    return result


def acceptOrder(server, order_hash):
    print('Click "Market Module"')
    code = '''
WebDriverWait(self.remote_app, 20).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'market')]"))).click()
    '''
    result = server.run_exec(code)

    print('Click "Sell"')
    code = '''
WebDriverWait(self.remote_app, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href,'market/sell')]"))).click()
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)

    print('Click order')
    code = f'''

cards = self.remote_app.find_elements(By.XPATH, "//mat-expansion-panel-header[contains(@class,'header')]")
for card in cards:
    inner_html = card.get_attribute('innerHTML')
    if '{order_hash}' in inner_html:
        card.click()
        break
    '''
    result = server.run_exec(code)

    print('Waiting 1 second')
    time.sleep(1)

    print('Click "Accept order request"')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//button[contains(@class,'mat-raised-button')]")
self.output += str(len(btns))
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    self.output += '    inner_html ' + inner_html
    if 'Accept order request' in inner_html:
        btn.click()
        self.output += ' clicked'
        break
    '''
    result = server.run_exec(code)
    print('result', result)

    print('Waiting 1 second')
    time.sleep(1)

    print('Click "Yes, accept order"')
    code = '''
btns = self.remote_app.find_elements(By.XPATH, "//button[@color='primary']")
for btn in btns:
    inner_html = btn.get_attribute('innerHTML')
    if 'Yes, accept' in inner_html:
        btn.click()
        break
    '''
    result = server.run_exec(code)
    print('result', result)


def run_loop():
    while not delay_event.is_set():
        stakeBlocks(1, delay_event)
        delay_event.wait(5.0)


def signalHandler(sig, frame):
    print('Signal {} detected, ending.'.format(sig))
    delay_event.set()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    parser.add_argument('--port', dest='port', help='RPC port (default=8001)', type=int, default=8001, required=False)
    parser.add_argument('--port2', dest='port2', help='RPC port (default=8002)', type=int, default=8002, required=False)
    parser.add_argument('--delayafter', dest='delayafter', help='Seconds to delay for once complete  (default=0)', type=int, default=0, required=False)

    args = parser.parse_args()
    server = xmlrpc.client.ServerProxy('http://localhost:{}'.format(args.port))

    server2 = xmlrpc.client.ServerProxy('http://localhost:{}'.format(args.port2))

    code = '''
heading = self.remote_app.find_element(By.XPATH, "//h2[contains(text(),'Terms & Conditions')]")
    '''
    try:
        server.run_exec(code)
        print('\nAccept terms node 1')
        acceptTerms(server)
    except Exception as e:
        if 'no such element' in str(e):
            print("Terms appear accepted")
        else:
            print("Check / accept terms failed", e)

    try:
        server2.run_exec(code)
        print('\nAccept terms node 2')
        acceptTerms(server2)
    except Exception as e:
        if 'no such element' in str(e):
            print("Terms appear accepted")
        else:
            print("Check / accept terms failed", e)

    try:
        print('\nFind market id on node 1')
        market_id = getMarketID(server)
    except Exception as e:
        print("getMarketID from node 1 failed", e)
        print('\nCreate market node 1')
        market_id = createMarket(server)

    try:
        print('\nFind market id on node 2')
        market_id2 = getMarketID(server2)
    except Exception as e:
        print("getMarketID from node 2 failed", e)
        print('\nJoin market node2', market_id)
        market_id2 = joinMarket(server2, market_id)

    print('\nPreparing staking wallets')
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

    wallets = cli2('listwallets')
    print('wallets', wallets)
    if 'main' not in wallets:
        try:
            cli2('loadwallet main')
        except Exception:
            cli2('createwallet main')
            cli2('walletsettings stakingoptions "{\\"stakecombinethreshold\\":100,\\"stakesplitthreshold\\":200}"', 'main')
            cli2('walletsettings stakelimit "{}"'.format(dumpje({'height': 1})), 'main')
            cli2('reservebalance true 10000000', 'main')
            cli2('extkeyimportmaster "pact mammal barrel matrix local final lecture chunk wasp survey bid various book strong spread fall ozone daring like topple door fatigue limb olympic" "" true "" "" 0 "{\\"createextkeys\\":1}"', 'main')

    addrs1 = cli1('liststealthaddresses', 'profiles/DEFAULT/particl-market')
    print('addrs1', addrs1)
    if len(addrs1) < 1:
        addr1 = cli1('getnewstealthaddress', 'profiles/DEFAULT/particl-market')
    else:
        addr1 = addrs1[0]['Stealth Addresses'][0]['Address']

    addrs2 = cli2('liststealthaddresses', 'profiles/DEFAULT/particl-market')
    print('addrs2', addrs2)
    if len(addrs1) < 1:
        addr2 = cli2('getnewstealthaddress', 'profiles/DEFAULT/particl-market')
    else:
        addr2 = addrs2[0]['Stealth Addresses'][0]['Address']

    balances1 = cli1('getbalances', 'profiles/DEFAULT/particl-market')
    print('balances1', balances1)

    # TODO: Staking should be disabled for market wallet
    cli1('walletsettings stakingoptions "{\\"enabled\\":\\"false\\"}"', 'profiles/DEFAULT/particl-market')
    cli2('walletsettings stakingoptions "{\\"enabled\\":\\"false\\"}"', 'profiles/DEFAULT/particl-market')

    if balances1['mine']['anon_trusted'] < 100:
        print('Sending anon outputs to node 1')
        outputs = [{'address': addr1, 'amount': 100}, ]
        for i in range(11):
            txid = cli2('sendtypeto part anon "{}"'.format(dumpje(outputs)), 'main')
            # Faster than waiting to sync
            raw_tx = cli2('gettransaction {}'.format(txid), 'main')['hex']
            cli1('sendrawtransaction "{}"'.format(raw_tx))

        print('stake 12 blocks')
        stakeBlocks(12, delay_event)
        balances1 = cli1('getbalances', 'profiles/DEFAULT/particl-market')
        print('balances1', balances1)

    if balances1['mine']['trusted'] < 100:
        print('Sending outputs to node 1')
        outputs = [{'address': addr1, 'amount': 10}, ]
        for i in range(11):
            txid = cli2('sendtypeto part part "{}"'.format(dumpje(outputs)), 'main')
            # Faster than waiting to sync
            raw_tx = cli2('gettransaction {}'.format(txid), 'main')['hex']
            cli1('sendrawtransaction "{}"'.format(raw_tx))

        print('stake 2 blocks')
        stakeBlocks(2, delay_event)
        balances1 = cli1('getbalances', 'profiles/DEFAULT/particl-market')
        print('balances1', balances1)

    balances2 = cli2('getbalances', 'profiles/DEFAULT/particl-market')
    print('balances2', balances2)

    if balances2['mine']['anon_trusted'] < 100:
        print('Sending anon outputs to node 2')
        outputs = [{'address': addr2, 'amount': 100}, ]
        for i in range(10):
            txid = cli2('sendtypeto part anon "{}"'.format(dumpje(outputs)), 'main')
            # Faster than waiting to sync
            raw_tx = cli2('gettransaction {}'.format(txid), 'main')['hex']
            cli1('sendrawtransaction "{}"'.format(raw_tx))

        print('stake 12 blocks')
        stakeBlocks(12, delay_event)
        balances2 = cli1('getbalances', 'profiles/DEFAULT/particl-market')
        print('balances2', balances2)

    if balances2['mine']['trusted'] < 100:
        print('Sending outputs to node 2')
        outputs = [{'address': addr2, 'amount': 10}, ]
        for i in range(10):
            txid = cli2('sendtypeto part part "{}"'.format(dumpje(outputs)), 'main')
            # Faster than waiting to sync
            raw_tx = cli2('gettransaction {}'.format(txid), 'main')['hex']
            cli1('sendrawtransaction "{}"'.format(raw_tx))

        print('stake 2 blocks')
        stakeBlocks(2, delay_event)
        balances1 = cli2('getbalances', 'profiles/DEFAULT/particl-market')
        print('balances2', balances2)

    try:
        print('Installing signal handler, ctrl+c to quit')
        signal.signal(signal.SIGINT, signalHandler)
        stake_thread = threading.Thread(target=run_loop)
        stake_thread.start()

        print('Count listings on node 1')
        num_listings1 = countListings(server)
        print('node 1 listings', num_listings1)

        if num_listings1 < 1:
            print('Add listing from node 1')
            addListing(server)

            num_listings1_expect = num_listings1 + 1
            print('Wait for listings on node 1')
            for i in range(16):
                delay_event.wait(2)
                num_listings1 = countListings(server)
                if num_listings1 >= num_listings1_expect:
                    break
            assert (num_listings1 >= num_listings1_expect)

        print('Wait for listings on node 2')
        for i in range(16):
            delay_event.wait(2)
            num_listings2 = countListings(server2)
            if num_listings1 >= num_listings2:
                break
        assert (num_listings1 >= num_listings2)

        print('Add Listing to Cart')
        addListingToCart(server2, 'Best NFT course')
        checkoutCart(server2)

        print('Wait for orders on node 1')
        for i in range(16):
            delay_event.wait(2)
            orders1 = countOrders(server)
            if len(orders1) >= 1:
                break
        assert (len(orders1) >= 1)
        print('node 1 orders', len(orders1))

        acceptOrder(server, orders1[0])

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
