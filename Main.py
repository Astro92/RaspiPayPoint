import requests
import json
import lnpay_py
import pyqrcode
import pygame
import png
import time
from lnpay_py.wallet import LNPayWallet
from lnpay_py.lntx import LNPayLnTx

# fetch current price of bitcoin

def opennode(currency='GBP',fiat=5):
    url='https://api.opennode.com/v1/rates'
    r=requests.get(url)
    current_price = json.loads(r.text)["data"]['BTC'+currency][currency]
    satoshi = current_price/1000000
    cost = int(fiat/satoshi)
    return cost

lnpay_py.initialize('LNPAY_API_KEY')
Wallet_Admin = 'LNPAY_ADMIN_KEY'
Wallet_Invoice = 'LNPAY_INVOICE_KEY'
Wallet_Read = 'LNPAY_READ_KEY'

fiat_amount = opennode('GBP',1)

while True:

    my_wallet_invoice = LNPayWallet(Wallet_Invoice)
    invoice_params = {'num_satoshis': 0,'memo': 'Coffee'}
    invoice_params['num_satoshis'] = fiat_amount
    LN_invoice_request = my_wallet_invoice.create_invoice(invoice_params)
    LN_invoice = LN_invoice_request['payment_request']
    
    invoice_QR = pyqrcode.create(LN_invoice) 
    invoice_QR.png("/PATH/TO/myinvoice.png", scale = 8)

    lntx_id = LN_invoice_request['id']
    ln_tx = LNPayLnTx(lntx_id)
    invoice_result = ln_tx.get_info()
    invoice_state = invoice_result['settled']
    
    pygame.init()
    white = (255, 255, 255) 
    display_surface = pygame.display.set_mode((480, 320)) # sets the size of the screen in use
    pygame.display.set_caption('Lightning') 
    invoice = pygame.image.load(r'/PATH/TO/myinvoice.png')
    invoice = pygame.transform.scale(invoice, (300, 300))
    coffee = pygame.image.load(r'/PATH/TO/lightning.png')
    coffee = pygame.transform.scale(coffee, (150, 227))
    display_surface.fill(white)
    display_surface.blit(invoice, (0, 10))
    display_surface.blit(coffee, (310,50))

    #invoice is live for 86400 seconds
    expiary = 0
    while invoice_state != 1 or expiary == 80000:
        #print('waiting for payment')
        ln_tx = LNPayLnTx(lntx_id)
        invoice_result = ln_tx.get_info()
        invoice_state = invoice_result['settled']
        expiary = expiary + 1
        for event in pygame.event.get() : 
		# if event object type is QUIT 
		# then quitting the pygame 
		# and program both. 
	        if event.type == pygame.QUIT : 
			# deactivates the pygame library 
		        pygame.quit() 
			# quit the program. 
		        quit()
		# Draws the surface object to the screen. 
	        pygame.display.update() 
        time.sleep(1)

    # Optional trigger for use with IFTTT
    
    params={"value1":"none","value2":"none","value3":"none"}
    params['value1']=fiat_amount
    pay_trigger = requests.post('https://maker.ifttt.com/trigger/invoice_payed/with/key/IFTTT_API_KEY',params)
    pygame.quit()
