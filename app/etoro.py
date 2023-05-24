import random
import requests
import datetime
from .models import Asset
from .barchart import getOptionsData


# Generate client request id for eToro API
def generateCRID():
    s = '0123456789abcdefghijklmnopqrstuvwxyz'
    res = ''
    for j in [8, 4, 4, 4, 12]:
        res += ''.join([random.choice(s) for i in range(8)])
    return res

# There's a parameter "cv" in many requests which is changed every now and the; this seems to return a value that can be used as that parameter
def getCV():
    try:
        data = 'LS_op2=create&LS_phase=6601&LS_cause=new.api&LS_polling=true&LS_polling_millis=0&LS_idle_millis=0&LS_cid=tqGko0tg4pkpW3CAK3T4hwLri8LBO7d&LS_adapter_set=PROXY_PUSH&LS_password=%7B%22UserAgent%22%3A%22Mozilla%2F5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F108.0.0.0%20Safari%2F537.36%22%2C%22ApplicationVersion%22%3A%22508.0.3%22%2C%22ApplicationName%22%3A%22ReToro%22%2C%22AccountType%22%3A%22Demo%22%2C%22ApplicationIdentifier%22%3A%22ReToro%22%7D&LS_container=lsc&'
        response = requests.post('https://push-demo-lightstreamer.cloud.etoro.com/lightstreamer/create_session.js',data=data)
        data = response.text.replace('\n', '').replace(' ', '')
        sid = data.split(');start(')[1].split(',')[0][1:-1]
        return sid
    except:
        return None

# Get assets metadata like precision
def getAssetMetadata():
    try:
        cv = getCV()
        params = {
            'bulkNumber': '1',
            'totalBulks': '1',
            'cv': cv
        }
        response = requests.get('https://api.etorostatic.com/sapi/trade-real/instruments/bulk-slim', params=params)
        data = response.json()['Instruments']
        for i in data:
            try:
                a = Asset.objects.get(instrument_id=i['InstrumentID'])
                a.precision = i['AboveDollarPrecision']
                a.save()
            except:
                pass
    except Exception as e:
        print(e)

# Get price data of all instruments
def getAllPriceData(cv, assets):
    params = {'cv': cv}
    response = requests.get('https://api.etorostatic.com/sapi/candles/closingprices.json', params=params)
    data = response.json()
    final = {}
    for i in data:
        for j in assets:
            if j.instrument_id == i['InstrumentId']:
                final[j.instrument_id] = i
    return final

# Get data of all instruments
def getAllAssets():
    params = {
        'bulkNumber': '1',
        'cv': '87e373a1d29fda48fcd17b1872da0f84_adc7999519b7c2a7859f08acc7d094ae',
        'totalBulks': '1',
    }

    response = requests.get('https://api.etorostatic.com/sapi/instrumentsmetadata/V1.1/instruments/bulk', params=params)

    try:
        data = response.json()
        if data:
            # All except for options
            data = data.get('InstrumentDisplayDatas')
            if data:
                stocks, etfs, opts, comms = [], [], [], []
                for i in data:
                    if i['InstrumentTypeID'] == 5:
                        stocks.append(i)
                    elif i['InstrumentTypeID'] == 6:
                        etfs.append(i)
                    elif i['InstrumentTypeID'] == 2:
                        comms.append(i)
            # Options
            data = getOptionsData()
            for i in data:
                opts.append({
                    'Symbol': i['baseSymbol'],
                    'Description': 'Option',
                    'BaseLastPrice': i['raw']['baseLastPrice'],
                    'LastPrice': i['raw']['lastPrice'],
                    'StrikePrice': i['raw']['strikePrice'],
                    'BidPrice': i['raw']['bidPrice'],
                    'AskPrice': i['raw']['askPrice'],
                    'Type': i['raw']['symbolType'],
                    'Moneyness': i['raw']['moneyness'],
                    'ExpDate': datetime.datetime.strptime(i['raw']['expirationDate'], "%Y-%m-%d"),
                    'Vol': i['raw']['volume'],
                    'OI': i['raw']['openInterest'],
                    'IV': i['raw']['volatility']
                })

            return {
                's': stocks,
                'e': etfs,
                'o': opts,
                'c': comms
            }
    except: 
        pass

    return {}

# Get close prices (daily) and isMarketOpen
def addClosePriceData(assets):
    aids = ','.join([str(i.instrument_id) for i in assets])
    data = requests.get('https://api.etorostatic.com/sapi/candles/closingprices.json/?instruments=%5B' + aids + '%5D', params={'cv': getCV()})
    try:
        data = data.json()
        for i in range(len(data)):
            assets[i].is_market_open = data[i]['IsMarketOpen']
            assets[i].close_price = data[i]['OfficialClosingPrice']
    except:
        pass
