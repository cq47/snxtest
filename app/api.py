import json
import random
import datetime
import requests
import threading
from multiprocessing.pool import Pool
from django.utils import dateformat, formats
from .etoro import *
from .tv_ws import *
from pprint import pprint
from asgiref.sync import async_to_sync
from paper.asgi import channel_layer
from django.contrib.sessions.models import Session
from .models import CustomUser, Asset, Chart, Order, Position, Option
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseNotFound


price_update_threads = {}
iid_updates = []
updates_started = False

def update_daily_volume():
    while True:
        # Get daily volume for listed assets
        a = Asset.objects.filter(listed=True)
        a = [i.asset for i in a]
        data = getDailyVolume(a)   
        upd_res = {}
        dtn = datetime.datetime.now()
        dtnf = dateformat.format(dtn, formats.get_format('DATETIME_FORMAT'))
        # Save data to model to display it fast when the list of assets is loaded
        for k, v in data.items():
            try:
                a = Asset.objects.get(asset=k)
                a.daily_volume = v
                a.last_update_daily_volume = dtn
                a.save()
                upd_res[a.instrument_id] = dtnf
            except:
                pass
        # Send to websocket
        async_to_sync(channel_layer.group_send)('updates_list', {'type': 'send_to_client', 'm': {
            't': 'dv',
            'd': data,
            'lu': upd_res
        }})

def update_market_state():
    while True:
        a = Asset.objects.filter(listed=True)
        a = [i.instrument_id for i in a]
        
        dtn = datetime.datetime.now()
        dtnf = dateformat.format(dtn, formats.get_format('DATETIME_FORMAT'))

        data = requests.get('https://api.etorostatic.com/sapi/candles/closingprices.json')
        for i in data.json():
            iid = i['InstrumentId']
            # Updates for charts
            if iid in iid_updates:
                async_to_sync(channel_layer.group_send)('updates_' + str(iid), {'type': 'send_to_client', 'm': {
                    't': 'm',
                    'd': {
                        'mo': i['IsMarketOpen'],
                        'c': i['ClosingPrices']['Daily']['Price'],
                        'oc': i['OfficialClosingPrice']
                    }
                }})
            # Updates for list of assets
            if iid in a:
                cp = i['ClosingPrices']['Daily']['Price']
                imo = i['IsMarketOpen']
                ocp = i['OfficialClosingPrice']

                try:
                    asset = Asset.objects.get(instrument_id=iid)
                    asset.is_market_open = imo
                    asset.close_price = cp
                    asset.official_close_price = ocp
                    asset.last_update_is_market_open = dtn
                    asset.save()
                except:
                    pass

                async_to_sync(channel_layer.group_send)('updates_list', {'type': 'send_to_client', 'm': {
                    't': 'm',
                    'd': {
                        'i': iid,
                        'mo': imo,
                        'c': cp,
                        'oc': ocp,
                        'lu': dtnf
                    }
                }})

def update_rates():
    while True:
        a = Asset.objects.filter(listed=True)
        a = [i.instrument_id for i in a]

        dtn = datetime.datetime.now()
        dtnf = dateformat.format(dtn, formats.get_format('DATETIME_FORMAT'))

        all_users = CustomUser.objects.filter(is_admin=False)

        try:
            data = requests.get('https://api.etorostatic.com/sapi/trade-real/instruments?InstrumentDataFilters=Rates&cv=' + str(random.randint(1, 1000000000)))
            for i in data.json()['Rates']:
                iid = i['InstrumentID']
                # Prices
                bid_price = i['Bid']
                ask_price = i['Ask']
                # 0.15% of spread on top of what's already there
                if ask_price >= bid_price:
                    ask_price = ask_price + bid_price * 0.15 / 100
                else:
                    bid_price = bid_price + ask_price * 0.15 / 100
                # Updates for charts
                if iid in iid_updates:
                    async_to_sync(channel_layer.group_send)('updates_' + str(iid), {'type': 'send_to_client', 'm': {
                        't': 'p',
                        'd': {
                            'b': bid_price,
                            'a': ask_price
                        }
                    }})
                # Updates for list of assets
                if iid in a:
                    # Update asset object
                    try:
                        asset = Asset.objects.get(instrument_id=iid)
                        asset.bid_price = bid_price
                        asset.ask_price = ask_price
                        asset.last_update_current_price = dtn
                        asset.save()
                    except:
                        pass

                    # Update / create positions
                    try:    
                        # If market is open
                        if asset.is_market_open:
                            # Iterate over each user
                            for user_ in all_users:
                                # Websocket name to send updates to
                                ws_name = 'account_' + str(user_.id)

                                # Get list of open positions to update PnL
                                positions_ = Position.objects.filter(user_id=user_.id, iid=asset.instrument_id, status='o')
                                for pos_ in positions_:
                                    if pos_.side == 'l':
                                        if pos_.calc_price > 0:
                                            pos_.pnl = (bid_price / pos_.calc_price - 1) * 100 * pos_.leverage
                                    else:
                                        if ask_price > 0:
                                            pos_.pnl = (pos_.calc_price / ask_price - 1) * 100 * pos_.leverage
                                    pos_.save()

                                # Get list of pending orders
                                orders_ = Order.objects.filter(user_id=user_.id, iid=asset.instrument_id, status='p')
                                # Iterate over each order
                                for order_ in orders_:
                                    ods_ = order_.size if order_.size_type == 't' else order_.size * bid_price
                                    # If price reached -> fill order and open new position
                                    if (bid_price >= order_.price) if order_.side == 'l' else (bid_price <= order_.price):
                                        # Check if order size not more than user's balance
                                        if ods_ <= user_.balance:
                                            # Fill order
                                            order_.status = 'f'
                                            order_.save()
                                            # Open new position
                                            pos = Position()
                                            pos.user_id = user_.id
                                            pos.date = datetime.datetime.now()
                                            pos.status = 'o'
                                            pos.iid = asset.instrument_id
                                            pos.asset_name = asset.asset
                                            pos.side = order_.side
                                            pos.calc_price = round(ask_price if order_.side == 'l' else bid_price, asset.precision)
                                            pos.entry_price = bid_price  # if we use <bid_price> -> we use current price (as if we had slippage); we can use <order_.price> to "have no slippage" and open position at the SAME EXACT price as was the order
                                            pos.exit_price = 0
                                            pos.dollar_size = ods_
                                            pos.size = order_.size
                                            pos.size_type = order_.size_type
                                            # Calculate PnL
                                            if pos.side == 'l':
                                                pnl_ = (bid_price / pos.calc_price - 1) * 100 * pos.leverage
                                            else:
                                                pnl_ = (pos.calc_price / ask_price - 1) * 100 * pos.leverage
                                            pos.pnl = pnl_
                                            pos.save()

                                            # User balance
                                            user_.balance -= ods_
                                            user_.save()

                                            # Send msg to ws to update order and create a new position item
                                            async_to_sync(channel_layer.group_send)(ws_name, {'type': 'send_to_client', 'm': {
                                                't': 'co_',
                                                's': 'ok',
                                                'd': {
                                                    'id': order_.id,
                                                    'ot': order_.order_type,
                                                    'os': order_.size,
                                                    'ost': order_.size_type,
                                                    'si': order_.side,
                                                    'l': order_.leverage,
                                                    'pid': pos.id,
                                                    'pnl': pnl_,
                                                    'osdollar': pos.dollar_size,
                                                    'calcp': pos.calc_price,
                                                    'ep': pos.entry_price
                                                },
                                                'os': 'f'  # f -> filled
                                            }})
                                        else:
                                            # Reject order
                                            order_.status = 'r'
                                            order_.save()
                                            # 
                                            async_to_sync(channel_layer.group_send)(ws_name, {'type': 'send_to_client', 'm': {
                                                't': 'co_',
                                                's': 'ok',
                                                'd': {
                                                    'id': order_.id,
                                                    'ot': order_.order_type,
                                                    'os': order_.size,
                                                    'ost': order_.size_type,
                                                    'si': order_.side,
                                                    'l': order_.leverage,
                                                    'pid': -1,
                                                    'pnl': 0,
                                                    'osdollar': ods_,
                                                    'calcp': -1,
                                                    'ep': -1
                                                },
                                                'os': 'r'
                                            }})
                    except Exception as e:
                        print(e)

                    # Send update to websocket
                    async_to_sync(channel_layer.group_send)('updates_list', {'type': 'send_to_client', 'm': {
                        't': 'p',
                        'd': {
                            'i': iid,
                            'b': i['Bid'],
                            'a': i['Ask'],
                            'lu': dtnf
                        }
                    }})
        except Exception as e:
            print(e)

        # Update total PnL and PnL of all open positions
        for user_ in all_users:
            ws_name = 'account_' + str(user_.id)
            # 
            total_pnl = 0
            total_pnl_open = 0
            all_pos = Position.objects.filter(user_id=user_.id)
            if len(all_pos) > 0:
                for i in all_pos:
                    total_pnl += i.pnl * i.dollar_size
                    if i.status == 'o':
                        total_pnl_open += i.pnl * i.dollar_size
                total_pnl /= 100
                total_pnl_open /= 100
                # 
                async_to_sync(channel_layer.group_send)(ws_name, {'type': 'send_to_client', 'm': {
                    't': 'bal_',
                    's': 'ok',
                    'pnl': total_pnl,
                    'pnlo': total_pnl_open,
                    'b': user_.balance
                }})

if not updates_started:
    updates_started = True
    t1 = threading.Thread(target=update_rates, daemon=True)
    t1.start()
    t2 = threading.Thread(target=update_market_state, daemon=True)
    t2.start()
    t3 = threading.Thread(target=update_daily_volume, daemon=True)
    t3.start()

class UpdatesTarget:
    def __init__(self, instrument_id, tf, asset_name):
        self.t = [
            threading.Thread(target=self.f_price, args=(instrument_id, tf,), daemon=True),
            threading.Thread(target=self.f_volume, args=(instrument_id, tf, asset_name,), daemon=True)
        ]
        self.must_stop = False
        self.counter = 1
        for i in range(len(self.t)):
            self.t[i].start()

    def f_volume(self, instrument_id, tf, asset_name):
        tf_tv = {
            'OneMinute': '1',
            'FiveMinutes': '5',
            'FifteenMinutes': '15',
            'ThirtyMinutes': '30',
            'OneHour': '60',
            'FourHours': '240',
            'OneDay': '1D'
        }[tf]
        ws = websocket.create_connection('wss://data.tradingview.com/socket.io/websocket?from=chart%2F&date=2030_01_11-11_27&type=chart')
        sendMessage(ws, 'set_auth_token', ['unauthorized_user_token'])
        csid = generateSession(True)
        sendMessage(ws, 'chart_create_session', [csid, ''])
        qsid = generateSession()
        sendMessage(ws, 'quote_create_session', [qsid])
        sendMessage(ws, 'resolve_symbol', [csid, 'sds_sym_1', asset_name])
        sendMessage(ws, "create_series", [csid, "sds_1", "s1", "sds_sym_1", tf_tv, 1, ""])
        vol_ = 0
        cur_h = 0
        while True:
            try:
                if self.must_stop:
                    ws.close()
                    return
                data = re.split('~m~\d+~m~', ws.recv())
                for i in data:
                    try:
                        i_ = json.loads(i)
                        if i_['m'] in ['timescale_update', 'du']:
                            vol_ = i_['p'][1]['sds_1']['s'][0]['v'][5]
                            async_to_sync(channel_layer.group_send)('updates_' + str(instrument_id) + '_' + tf, {'type': 'send_to_client', 'm': {
                                't': 'v',
                                'd': vol_
                            }})
                    except:
                        if i.startswith('~h~'):
                            sendMessageSimple(ws, i)
            except:
                return

    def f_price(self, instrument_id, tf):
        while True:
            try:
                if self.must_stop:
                    return
                data = requests.get('https://candle.etoro.com/candles/desc.json/' + tf + '/1/' + str(instrument_id)).json()
                ic = data['Candles']
                if len(ic) > 0:
                    c = ic[0]['Candles'][0]
                    async_to_sync(channel_layer.group_send)('updates_' + str(instrument_id) + '_' + tf, {'type': 'send_to_client', 'm': {
                        't': 'ohlc',
                        'd': {
                            'o': c['Open'],
                            'h': c['High'],
                            'l': c['Low'],
                            'c': c['Close'],
                            't': c['FromDate']
                        }
                    }})
            except:
                return 

    def add(self):
        self.counter += 1

    def reduce(self):
        self.counter -= 1

    def stop(self):
        self.must_stop = True


# Save chart
class Api_Chart_Save(TemplateView):
    def get(self, request):
        return JsonResponse({'status': 'err', 'msg': 'Wrong method!'})

    def post(self, request):
        if request.user.is_authenticated and not request.user.is_admin:
            asset_id = request.POST.get('asset_id')
            chart_tf = request.POST.get('chart_tf', '1D')
            if not asset_id:
                return JsonResponse({'status': 'err', 'msg': 'Asset ID not provided!'})
            else:
                charts = Chart.objects.filter(asset_id=asset_id, user_id=request.user.id)
                if charts:
                    try:
                        # Get data
                        data = json.loads(request.POST['data'])
                        # Assign new
                        for i in charts:
                            # Save indicators on all timeframes
                            i.settings['indicators'] = data['indicators']
                            # But save drawings only on the current timeframe
                            if i.tf == chart_tf:
                                i.settings['drawings'] = data['drawings']
                            i.save()
                        # Save
                        return JsonResponse({'status': 'ok'})
                    except:
                        return JsonResponse({'status': 'err', 'msg': 'Unknown error!'})
                else:
                    return JsonResponse({'status': 'err', 'msg': 'Chart with given ID not found!'})
        else:
            return JsonResponse({'status': 'err', 'msg': 'Unauthorized!'})

# Get rendered HTML for indicator
class Api_Chart_Request_Indicator_UI(TemplateView):
    def get(self, request):
        if request.user.is_authenticated and not request.user.is_admin:
            indicator = request.GET.get('indicator')
            if not indicator:
                return JsonResponse({'status': 'err', 'msg': 'Indicator name not provided!'})
            else:
                try:
                    return JsonResponse({'status': 'ok', 'data': render_to_string('indicators/{}.html'.format(indicator))})
                except:
                    return JsonResponse({'status': 'err', 'msg': 'Unknown error!'})
        else:
            return JsonResponse({'status': 'err', 'msg': 'Unauthorized!'})

# Perform action on users
class Api_Users_Action(TemplateView):
    def get(self, request):
        return JsonResponse({'status': 'err', 'msg': 'Wrong method!'})

    def post(self, request):
        if request.user.is_authenticated and request.user.is_admin:
            ids = request.POST.getlist('ids[]')
            action = request.POST.get('action')
            if not (ids or action):
                return JsonResponse({'status': 'err', 'msg': 'IDs of users or Action not provided!'})
            else:
                try:
                    for i in ids:
                        try:
                            user_ = CustomUser.objects.get(id=i)
                            if action == 'deactivate':
                                user_.is_active = False
                                user_.save()
                            elif action == 'activate':
                                user_.is_active = True
                                user_.save()
                            elif action == 'delete':
                                try:
                                    extra_data_ = SocialAccount.objects.get(user=user_)
                                    extra_data_.delete()
                                    Chart.objects.filter(user_id=user_.id).delete()
                                except:
                                    pass
                                user_.delete()
                            elif action == 'save':
                                try:
                                    data_ = json.loads(request.POST.get('data'))
                                    user_.balance = data_['balance']
                                    user_.save()
                                except:
                                    pass
                        except:
                            pass
                    return JsonResponse({'status': 'ok'})
                except Exception as e:
                    return JsonResponse({'status': 'err', 'msg': str(e)})
        else:
            return JsonResponse({'status': 'err', 'msg': 'Unauthorized!'})

# Perform action on assets
class Api_Assets_Action(TemplateView):
    def get(self, request):
        return JsonResponse({'status': 'err', 'msg': 'Wrong method!'})

    def post(self, request):
        if request.user.is_authenticated and request.user.is_admin:
            ids = request.POST.getlist('ids[]')
            action = request.POST.get('action')
            is_option = request.POST.get('is_option') == 'true'
            if not (ids or action or is_option):
                return JsonResponse({'status': 'err', 'msg': 'IDs of assets and/or Action and/or IsOption not provided!'})
            else:
                try:
                    for i in ids:
                        try:
                            print(is_option)
                            if is_option:
                                asset = Option.objects.get(id=i)
                            else:
                                asset = Asset.objects.get(id=i)
                            if action == 'list':
                                asset.listed = True
                                if not is_option:
                                    asset.bad_reason = ''
                            elif action == 'delist':
                                asset.listed = False
                            asset.save()
                        except Exception as e:
                            print(e)
                            pass
                    return JsonResponse({'status': 'ok'})
                except:
                    return JsonResponse({'status': 'err', 'msg': 'Unknown error!'})
        else:
            return JsonResponse({'status': 'err', 'msg': 'Unauthorized!'})

# Load list of assets
class Api_Assets_LoadList(TemplateView):
    def get(self, request):
        return JsonResponse({'status': 'err', 'msg': 'Wrong method!'})

    def post(self, request):
        if request.user.is_authenticated and request.user.is_admin:
            data = getAllAssets()

            # Delete all charts for all users
            Chart.objects.all().delete()
            # Delete old assets from DB
            Asset.objects.all().delete()
            # Delete all orders
            Order.objects.all().delete()
            # Delete all positions
            Position.objects.all().delete()
            # Delete all options
            Option.objects.all().delete()

            # Get list of available stocks
            avail_stocks = {}
            for i in data['s']:
                avail_stocks[i['SymbolFull']] = i['InstrumentDisplayName']

            # Add new assets and options
            for k, v in data.items():
                for i in v:  
                    # All except for options
                    if k != 'o':
                        new_asset = Asset()
                        new_asset.asset = i['SymbolFull']
                        new_asset.desc = i['InstrumentDisplayName']
                        new_asset.instrument_id = i['InstrumentID']
                        new_asset.instrument_type = k
                        new_asset.exchange_id = i['ExchangeID']
                        new_asset.save()
                    # Options
                    else:
                        desc_ = avail_stocks.get(i['Symbol'])
                        if desc_:
                            new_option = Option()
                            new_option.asset = i['Symbol']
                            new_option.desc = desc_
                            new_option.bid_price = i['BidPrice']
                            new_option.ask_price = i['AskPrice']
                            new_option.price = i['BaseLastPrice']
                            new_option.strike_price = i['StrikePrice']
                            new_option.option_type = i['Type']
                            new_option.moneyness = i['Moneyness']
                            new_option.exp_date = i['ExpDate']
                            new_option.last_price = i['LastPrice']
                            new_option.volume = i['Vol']
                            new_option.oi = i['OI']
                            new_option.iv = i['IV']
                            new_option.last_update = datetime.datetime.now()
                            new_option.listed = False
                            new_option.save()
                            print(new_option)

            getAssetMetadata()

            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'err', 'msg': 'Unauthorized!'})

# Called when we disconnect from client side websocket of Updates
class Api_Internal_WscRemove(TemplateView):
    def get(self, request):
        return JsonResponse({'status': 'err', 'msg': 'Wrong method!'})

    def post(self, request):
        if request.user.is_authenticated:
            try:
                instrument_id = request.POST.get('instrument_id')
                tf = request.POST.get('tf')
                if instrument_id and tf:
                    # For price / volume
                    a = price_update_threads.get(str(instrument_id) + '_' + tf)
                    if not a:
                        return JsonResponse({'status': 'err', 'msg': 'No thread found for given Instrument ID and Timeframe!'})
                    else:
                        if a.counter - 1 == 0:
                            a.stop()
                            del price_update_threads[str(instrument_id) + '_' + tf]
                        else:
                            a.reduce()

                    # For bid / ask prices
                    try:
                        iid_updates.remove(int(instrument_id))
                    except:
                        pass

                    return JsonResponse({'status': 'ok', 'data': 'disconnected'})
                else:
                    return JsonResponse({'status': 'err', 'msg': 'Instrument ID and/or Timeframe not provided!'})
            except Exception as e:
                return JsonResponse({'status': 'err', 'msg': str(e)})
        else:
            return JsonResponse({'status': 'err', 'msg': 'Unauthorized!'})

# Called when we connect to client side websocket of Updates
class Api_Internal_WscAdd(TemplateView):
    def get(self, request):
        return JsonResponse({'status': 'err', 'msg': 'Wrong method!'})

    def post(self, request):
        if request.user.is_authenticated:
            try:
                instrument_id = request.POST.get('instrument_id')
                tf = request.POST.get('tf')
                asset_name = request.POST.get('asset')

                if instrument_id and tf and asset_name:
                    # For price and volume updates
                    a = price_update_threads.get(str(instrument_id) + '_' + tf)
                    if not a:
                        price_update_threads[str(instrument_id) + '_' + tf] = UpdatesTarget(instrument_id, tf, asset_name)
                    else:
                        price_update_threads[str(instrument_id) + '_' + tf].add()

                    # For bid / ask updates
                    if not instrument_id in iid_updates:
                        iid_updates.append(int(instrument_id))

                    return JsonResponse({'status': 'ok', 'data': 'new'})
                else:
                    return JsonResponse({'status': 'err', 'msg': 'Instrument ID and/or Timeframe and/or Asset name not provided!'})
            except Exception as e:
                return JsonResponse({'status': 'err', 'msg': str(e)})
        else:
            return JsonResponse({'status': 'err', 'msg': 'Unauthorized!'})

# Called when a user goes to a chart and data on it is too old -> invalidates asset
class Api_Internal_InvalidateAsset(TemplateView):
    def get(self, request):
        return JsonResponse({'status': 'err', 'msg': 'Wrong method!'})

    def post(self, request):
        if request.user.is_authenticated:
            try:
                iid = request.POST.get('iid')
                lp = int(request.POST.get('lp'))
                reason = request.POST.get('reason')
                if datetime.datetime.now().timestamp() - lp >= 7 * 24 * 3600:
                    a = Asset.objects.get(instrument_id=iid)
                    a.bad_reason = reason
                    a.listed = False
                    a.is_market_open = False
                    a.save()
                    return JsonResponse({'status': 'ok'})
                else:
                    return JsonResponse({'status': 'err'})
            except Exception as e:
                return JsonResponse({'status': 'err', 'msg': str(e)})
        else:
            return JsonResponse({'status': 'err', 'msg': 'Unauthorized!'})