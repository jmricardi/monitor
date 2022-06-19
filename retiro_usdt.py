from time import sleep
from tokens import TeleBotToken
from tokens import myApiKey
from tokens import sender
from tokens import senderPublicKey
from tokens import dApp
from tokens import ChatId
import requests
import telebot

# from tokens import TeleBotToken

def sign(myApiKey,sender,senderPublicKey,dApp):
    
    nodeUrl = 'http://164.92.69.234:6870'
    dApp=dApp
    senderPublicKey=senderPublicKey
    myApiKey=myApiKey 
    sender=sender
    amount=1000000000
    # assetId='6XtHjpXbs9RRJP2Sr9GUyVqzACcby9TkThHXnjVC5CDJ' #USDC
    assetId='34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ' #USDT

    # Step 1 (Optional). Calculate Fee

    headers = {
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
    }
    json_data = {
        'type': 16,
        'senderPublicKey': senderPublicKey,
        'call': {
            'function': 'withdraw',
            'args': [
                    {
            "type": "string",
            "value": assetId
                    },
                    {
            "type": "integer",
            "value": amount
                    }

            ],
        },
        'payment': [],
        'dApp': dApp,
    }

    response = requests.post(nodeUrl+'/transactions/calculateFee', headers=headers, json=json_data)

    feeAmount = response.json()['feeAmount']

    # Step 2. Sign Transaction

    headers = {
        'X-API-Key': myApiKey,
        # Already added when you pass json=
        # 'Content-Type': 'application/json',
    }
    json_data = {
        'type': 16,
        'sender': sender,
        'call': {
            'function': 'withdraw',
            'args': [
                    {
            "type": "string",
            "value": assetId
                    },
                    {
            "type": "integer",
            "value": amount
                    }

            ],
        },
        'payment': [],
        'dApp': dApp,
        'feeAssetId': None,
        'fee': feeAmount,
    }

    response = requests.post(nodeUrl+'/transactions/sign', headers=headers, json=json_data)

    signed = response.json()

    # Step 3 (optional). Pre-validate Transaction

    headers = {
        # Already added when you pass json= but not when you pass data=
        # 'Content-Type': 'application/json',
    }
    json_data = signed

    response = requests.post(nodeUrl+'/debug/validate', headers=headers, json=json_data)

    if (response.json()['valid']==False):
        print(list(response.json()['error'].split(","))[1])
        return False

    # Step 4. Broadcast Transaction

    headers = {
        # Already added when you pass json= but not when you pass data=
        # 'Content-Type': 'application/json',
    }
    json_data = signed

    response = requests.post(nodeUrl+'/transactions/broadcast', headers=headers, json=json_data)

    id = response.json()['id']

    return id

def monitor():
    resp = requests.get("https://api.vires.finance/state")
        
    if resp.status_code != 200:
        print("Error del servidor Vires")
        return "error"
    else:
        resp = resp.json()
    # condicional saldo USDC

    USDC_supply = resp['markets'][3]['supply']
    USDC_debt = resp['markets'][3]['totalDebt']
    USDC_saldo = USDC_supply - USDC_debt

    # condicional saldo USDT

    USDT_supply = resp['markets'][2]['supply']
    USDT_debt = resp['markets'][2]['totalDebt']
    USDT_saldo = USDT_supply - USDT_debt

    return (USDT_saldo, USDC_saldo)

def formatNumber(number, decimals, espanol=True):
    if type(number) != int and type(number) != float:
        return number
    
    d={'.':',',',':'.'}
    return ''.join(d.get(s, s) for s in f"{number:,.{decimals}f}") \
        if espanol \
        else f"{number:,.{decimals}f}"    

bot = telebot.TeleBot(TeleBotToken, parse_mode=None)

bot.send_message(ChatId, "Iniciando...")

USDT = ""
USDC = ""
estado_USDT = "-"
estado_USDC = "-"
    
while True:
    sleep(3)
    response = monitor()

    if response =="error":
        print("Error Server - FIN")
        break

    estado_USDT = USDT
    estado_USDC = USDC

    if response[0] < 0:
        USDT = "sin"
    else:
        USDT = "con"

    if response[1] < 0:
        USDC = "sin"
    else:
        USDC = "con"

    if estado_USDT != USDT or estado_USDC != USDC:
        bot.send_message(ChatId,"Saldo USDT -> USD " + str(formatNumber(response[0],2,True)) + " " + USDT + " saldo")
        bot.send_message(ChatId,"Saldo USDC -> USD " + str(formatNumber(response[1],2,True)) + " " + USDC + " saldo")

    if USDT=="con" and response[0]>1000:
        res=sign(myApiKey, sender, senderPublicKey, dApp)
        if res!=False:
            bot.send_message(ChatId,"Retiro USDT Exitoso ID " + str(res))
            break
        else:
            bot.send_message(ChatId,"Error al retirar")