import requests
import telebot
# import sys
# sys.path.append("/")
from tokens import ChatId
from tokens import TeleBotToken

print(type(ChatId))
print(type(TeleBotToken))

## Direcciones a monitorear

address = ['3PEEsRmcWspCxhKqobvKY3axW1846AMRwzr']

## Typos de operaciones a monitorear

types = [4,16]

## Punto de partida en la revision de las cuentas (aprox 1-5-2022)

lastId = ['F46uUCkrHZKyvhvRw5DkGLGaASXU5Ufz4RDkHMQb2HLz']

## Otros parametros

limit = 50

bot = telebot.TeleBot(TeleBotToken, parse_mode=None)

bot.send_message(ChatId, "Iniciando...")

def height():
     headers = {
     'accept': 'application/json',
     }

     response = requests.get('http://nodes.wavesnodes.com/blocks/height', headers=headers).json()
     return response['height']


def monitor(address,lastId,limit):
        node_url = 'http://nodes.wavesnodes.com'
        address = address
        limit = limit

        resp = requests.get(f'{node_url}/transactions/address/{address}/limit/{limit}') 
        
        if resp.status_code == 200:
            resp = resp.json()
            resp = resp[0]
            responseFilter = []

            for i in range(len(resp)):
                if resp[i]['type'] in types:
                    responseFilter.append(resp[i])

            retorno = ultimo(responseFilter, lastId, len(responseFilter))
          
            return retorno
        else:
            print(response.status_code)
            print("Error en dirección "+str(address))
            return "error"

def ultimo(responseR,lastIdR,limitR):
        for i in range(limitR):
            if responseR[i]['id'] == lastIdR: 
                if i > 0:
                    return responseR[i-1]
                elif i == 0:
                    return responseR[0]
        print("no se encontro el ultimo en la lista")
        print(i)
        ## print(responseR[0])
        print(lastIdR)
        return responseR[0]

id=lastId[0]
after=lastId[0]

while True:
    for x in range(len(address)):
        (a,id)=(address[x],lastId[x])

        while True:
            response = monitor(a,id,limit)

            id = response['id']

            if response =="error":
                print("Error Server - FIN")
                break
           
            # Transferencias

            if response['type'] == 4 and id != lastId[x]:
                if response['assetId']=="34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ":
                    monto = round(response['amount']/1000000,0)
                    cuenta = response['sender']
                    if response['recipient']==a:
                        message = "Trans entrante de {} USDT a la cuenta {}".format(str(monto),str(a))
                        print(message)
                        bot.send_message(ChatId, message)
                    elif response['sender']==a:
                        message = "Trans saliente de {} USDT desde la cuenta {}".format(str(monto),str(a))
                        print(message)
                        bot.send_message(ChatId, message)
                    else:
                        print("error USDT")
                elif response['assetId']=="6XtHjpXbs9RRJP2Sr9GUyVqzACcby9TkThHXnjVC5CDJ":
                    monto = round(response['amount']/1000000,0)
                    cuenta = response['sender']
                    if response['recipient']==a:
                        message = "Trans entrante de {} USDC a la cuenta {}".format(str(monto),str(a))
                        print(message)
                        bot.send_message(ChatId, message)
                    elif response['sender']==a:
                        message = "Trans saliente de {} USDC desde la cuenta {}".format(str(monto),str(a))
                        print(message)
                        bot.send_message(ChatId, message)
                    else:
                        print("error USDC")
                else:
                    print("Trans en otra moneda diferente a USDC/T")

            # Scripts

            if (response['type'] == 16 and id != lastId[x] and response['dApp'] == '3PAZv9tgK1PX7dKR7b4kchq5qdpUS3G5sYT' and (response['call']['function']=='repay' or response['call']['function']=='deposit')):
               
                if response['payment'][0]['assetId']=="34N9YcEETLWn93qYQ64EsP1x89tSruJU44RrEMSXXEPJ":
                    monto = round(response['payment'][0]['amount']/1000000,0)
                    cuenta = response['sender']
                    message = "A Vires de {} USDT desde la cuenta {}".format(str(monto),str(cuenta))
                    print(message)
                    bot.send_message(ChatId, message)
                elif response['payment'][0]['assetId']=="6XtHjpXbs9RRJP2Sr9GUyVqzACcby9TkThHXnjVC5CDJ":
                    monto = round(response['payment'][0]['amount']/1000000,0)
                    cuenta = response['sender']
                    message = "A Vires de {} USDC desde la cuenta {}".format(str(monto),str(cuenta))
                    print(message)
                    bot.send_message(ChatId, message)
                else:
                    print("Script en moneda diferente a USDC/T")
           
            if id == lastId[x]:
                break
            else:
                lastId[x] = id