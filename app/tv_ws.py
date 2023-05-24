import websocket
import random
import string
import json
import re

def generateSession(is_chart=False):
    arr = [random.choice(string.ascii_lowercase + string.digits) for i in range(12)]
    arr = [i if random.randint(1, 3) == 2 else i.upper() for i in arr]
    return ("cs_" if is_chart else "qs_") + ''.join(arr)

def prependHeader(st):
    return "~m~" + str(len(st)) + "~m~" + st

def constructMessage(func, paramList):
    return json.dumps({"m":func, "p":paramList}, separators=(',', ':'))

def createMessage(func, paramList):
    return prependHeader(constructMessage(func, paramList))

def sendMessage(ws, func, args):
    ws.send(createMessage(func, args))

def sendMessageSimple(ws, msg):
    ws.send(prependHeader(msg))

def getPriceData(sym, tf):
    tf = {
        '1m': '1',
        '5m': '5',
        '15m': '15',
        '30m': '30',
        '1h': '60',
        '4h': '240',
        '1D': '1D',
        '1W': '1W'
    }[tf]
    ws = websocket.create_connection('wss://data.tradingview.com/socket.io/websocket?from=chart%2F&date=2030_01_11-11_27&type=chart')
    sendMessage(ws, 'set_auth_token', ['unauthorized_user_token'])
    csid = generateSession(True)
    sendMessage(ws, 'chart_create_session', [csid, ''])
    sendMessage(ws, 'switch_timezone', [csid, 'Etc/UTC'])
    qsid = generateSession()
    sendMessage(ws, 'quote_create_session', [qsid])
    sendMessage(ws, 'resolve_symbol', [csid, 'sds_sym_1', sym])
    sendMessage(ws, "create_series", [csid, "sds_1", "s1", "sds_sym_1", tf, 1000, ""])
    while True:
        data = re.split('~m~\d+~m~', ws.recv())
        price_data = []
        for i in data:
            if '"m":"timescale_update"' in i:
                json_data = json.loads(i)
                price_data_raw = json_data['p'][1]['sds_1']['s']
                for i in price_data_raw:
                    price_data.append({
                        'time': i['v'][0],
                        'open': i['v'][1],
                        'high': i['v'][2],
                        'low': i['v'][3],
                        'close': i['v'][4],
                        'volume': i['v'][5]
                    })
                ws.close()
                return price_data

# Get Daily volume from TV
def getDailyVolume(asset_names):
    asset_names = list(set(asset_names))
    ws = websocket.create_connection('wss://data.tradingview.com/socket.io/websocket?from=chart%2F&date=2030_01_11-11_27&type=chart')
    sendMessage(ws, 'set_auth_token', ['unauthorized_user_token'])
    csid = generateSession(True)
    sendMessage(ws, 'chart_create_session', [csid, ''])
    qsid = generateSession()
    sendMessage(ws, 'quote_create_session', [qsid])
    sendMessage(ws, 'quote_set_fields', [qsid, "short_name", "volume"])
    asset_names.insert(0, qsid)
    sendMessage(ws, 'quote_add_symbols', asset_names)
    res = {}
    for j in range(2):
        data = re.split('~m~\d+~m~', ws.recv())
        for i in data:
            try:
                i_ = json.loads(i)
                if i_['m'] == 'qsd':
                    sym_ = i_['p'][1]['n']
                    vol_ = i_['p'][1]['v']['volume']
                    res[sym_] = vol_
            except:
                pass
    sendMessage(ws, 'quote_remove_symbols', asset_names)
    sendMessage(ws, 'quote_hibernate_all', [qsid])
    ws.close()
    return res