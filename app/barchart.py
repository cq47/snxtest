import requests_html


def getOptionsData():
    headers = {
        'authority': 'www.barchart.com',
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.barchart.com/options/options-screener',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    ses = requests_html.HTMLSession()
    ses.get('https://www.barchart.com/options/options-screener')
    res = ses.cookies.get_dict()
    cookies = {
        'laravel_token': res['laravel_token'][:-3]
    }
    headers['x-xsrf-token'] = ses.cookies.get_dict()['XSRF-TOKEN'][:-3]

    all_data = []

    for i in range(1, 20):
        query = {
            "fields":"symbol,baseSymbol,baseLastPrice,symbolType,strikePrice,moneyness,expirationDate,daysToExpiration,bidPrice,askPrice,lastPrice,volume,openInterest,volatility,tradeTime,expirationDate",
            "hasOptions":"true",
            "raw":"1",
            "page": str(i),
            "meta":"field.shortName,field.type,field.description",
            "in(symbolType,(call,put))":"",
            "in(baseSymbolType,(1))":"",
            "between(daysToExpiration,0,60)":"",
            "in(expirationType,(weekly))":"",
            "between(volume,100,)":"",
            "between(openInterest,500,)":"",
            "in(exchange,(AMEX,NYSE,NASDAQ,INDEX-CBOE))":""
        }

        try:
            response = ses.get(
                'https://www.barchart.com/proxies/core-api/v1/options/get',
                cookies=cookies,
                headers=headers,
                params=query
            )
            data_ = response.json()['data']
            if data_:
                all_data.extend(data_)
            else:
                break
        except:
            break

    return all_data