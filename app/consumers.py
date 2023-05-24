import json
import datetime
from django.db.models import Sum    
from .models import Asset, Order, Position
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.auth import get_user


# For account and trading updates
class AccountUpdatesConsumer(WebsocketConsumer):
    def connect(self):
        user_ = async_to_sync(get_user)(self.scope)
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        if user_.id == user_id and not user_.is_admin:
            self.room_name = user_id
            self.room_group_name = "account_" + str(self.room_name)
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )
            self.accept()
            self.send(json.dumps({"t": "i", "m": "Account websocket connected!"}))

    def disconnect(self, close_code):
        try:
            self.send(json.dumps({"t": "i", "m": "Disconnected!"}))
            async_to_sync(self.channel_layer.group_discard)(
                self.room_group_name,
                self.channel_name
            )
        except:
            pass
    
    def receive(self, text_data):
        json_data = json.loads(text_data)
        # Check if user is correct and is not an admin
        user_ = async_to_sync(get_user)(self.scope)
        user_id = self.scope["url_route"]["kwargs"]["user_id"]
        if user_.id == user_id and not user_.is_admin:
            # Get asset
            asset = Asset.objects.get(instrument_id=json_data['d']['iid'])
            # New order
            if json_data['t'] == 'o':
                # Check if market is open
                if asset.is_market_open or (not asset.is_market_open and json_data['d']['ot'] == 'l'):
                    order_size = json_data['d']['os']
                    ot = json_data['d']['ot']
                    side_ = json_data['d']['si']
                    opl = json_data['d']['opl']
                    # Check if order size was 0
                    if order_size > 0:
                        # Check if order price within allowed limits
                        if ((opl < asset.bid_price) if side_ == 'l' else (opl > asset.bid_price)) if ot == 'l' else True:
                            # Get neccessary data
                            opm = json_data['d']['opm']
                            order_size_type = json_data['d']['ost']
                            dollar_size = order_size if order_size_type == 't' else order_size * opm
                            # Check if user has enough balance
                            if (user_.balance >= dollar_size) if ot == 'm' else True:
                                # Create a new Order object
                                order_ = Order()
                                order_.user_id = user_.id
                                order_.date = datetime.datetime.now()
                                order_.status = 'p' if ot == 'l' else 'f'
                                order_.iid = json_data['d']['iid']
                                order_.asset_name = json_data['d']['a']
                                order_.side = side_
                                order_.leverage = json_data['d']['l']
                                # Order type
                                order_.order_type = ot
                                # Order price
                                price = opm if ot == 'm' else opl
                                order_.price = price
                                # Order size 
                                order_.size_type = order_size_type
                                order_.size = order_size
                                order_.save()

                                da_ = json_data['d']

                                # This will be sent via WS
                                data_ = {'t': 'o_', 's': 'ok'}

                                # Create new position if order type is Market
                                total_dollar_pnl = 0
                                np_ = False
                                if ot == 'm':
                                    # Open new position
                                    pos = Position()
                                    pos.user_id = user_.id
                                    pos.date = datetime.datetime.now()
                                    pos.status = 'o'
                                    pos.iid = asset.instrument_id
                                    pos.asset_name = asset.asset
                                    pos.side = order_.side
                                    pos.calc_price = round(json_data['d']['opc'], asset.precision)
                                    pos.entry_price = opm  # if we use <bid_price> -> we use current price (as if we had slippage); we can use <order_.price> to "have no slippage" and open position at the SAME EXACT price as was the order
                                    pos.exit_price = 0
                                    pos.dollar_size = dollar_size
                                    pos.size = order_.size
                                    pos.size_type = order_.size_type
                                    pos.leverage = order_.leverage
                                    # Calculate PnL
                                    pnl_ = (asset.bid_price / asset.ask_price - 1) * 100 * order_.leverage
                                    pos.pnl = pnl_
                                    pos.save()
                                    np_ = True
                                    # Add ID of opened position
                                    da_['pid'] = pos.id
                                    da_['osdollar'] = pos.dollar_size
                                    da_['pnl'] = pnl_
                                    da_['calcp'] = pos.calc_price
                                    da_['ep'] = pos.entry_price

                                    # Subtract from user's balance
                                    user_.balance -= dollar_size
                                    user_.save()

                                    # Get user's balance and total PnL accross account
                                    all_pos = Position.objects.filter(user_id=user_.id, status='o')
                                    for ipos in all_pos:
                                        total_dollar_pnl += ipos.dollar_size * ipos.pnl
                                    total_dollar_pnl /= 100
                                    total_dollar_pnl_s = str(total_dollar_pnl).replace(',', '.')
                                    try:
                                        if total_dollar_pnl_s[0] == '0' and total_dollar_pnl_s[1] == '.':
                                            total_dollar_pnl = round(total_dollar_pnl, 3)
                                        else:
                                            total_dollar_pnl = round(total_dollar_pnl, 2)
                                    except:
                                        total_dollar_pnl = round(total_dollar_pnl, 2)

                                    data_['user'] = {'b': round(user_.balance, 2), 'pnl': total_dollar_pnl}

                                # Send message back
                                da_['oid'] = order_.id
                                da_['ors'] = 'p' if ot == 'l' else 'f'

                                data_['d'] = da_
                                data_['np'] = np_

                                self.send(json.dumps(data_))
                            else:
                                self.send(json.dumps({'t': 'o_', 's': 'err', 'm': 'You have insufficient balance', 'np': False}))
                        else:
                            self.send(json.dumps({'t': 'o_', 's': 'err', 'm': 'Invalid order price', 'np': False}))
                    else:
                        self.send(json.dumps({'t': 'o_', 's': 'err', 'm': 'Order size must be greater than 0', 'np': False}))
                else:
                    self.send(json.dumps({'t': 'o_', 's': 'err', 'm': 'Market is closed', 'np': False}))
            # Cancel order
            elif json_data['t'] == 'co':
                # Get pending order with provided ID
                order_ = Order.objects.filter(user_id=user_.id, iid=asset.instrument_id, id=json_data['d']['id'], status='p')
                if len(order_) > 0:
                    order_[0].status = 'c'
                    order_[0].save()
                    self.send(json.dumps({'t': 'co_', 's': 'ok', 'd': json_data['d'], 'os': 'c'}))
                else:
                    self.send(json.dumps({'t': 'co_', 's': 'err', 'm': 'Unknown error'}))
            # Close position
            elif json_data['t'] == 'clp':
                # Get open position with provided ID
                pos_ = Position.objects.filter(user_id=user_.id, iid=asset.instrument_id, id=json_data['d']['id'], status='o')
                if len(pos_) > 0:
                    da_ = json_data['d']
                    da_['exp'] = asset.bid_price

                    pos_[0].status = 'c'
                    pos_[0].exit_price = asset.bid_price
                    # Change date of position to when it was closed (open positions show date when they were opened)
                    pos_[0].date = datetime.datetime.now()
                    # Recalculate PnL
                    if pos_[0].side == 'l':
                        if pos_[0].calc_price > 0:
                            pos_[0].pnl = (asset.bid_price / pos_[0].calc_price - 1) * 100 * pos_[0].leverage
                    else:
                        if asset.ask_price > 0:
                            pos_[0].pnl = (pos_[0].calc_price / asset.ask_price - 1) * 100 * pos_[0].leverage
                    pos_[0].save()

                    # Update user's balance
                    user_.balance += pos_[0].dollar_size + pos_[0].pnl / 100 * pos_[0].dollar_size
                    user_.save()

                    data_ = {'t': 'clp_', 's': 'ok', 'd': da_, 'ps': 'c'}

                    # Get user's balance and total PnL accross account
                    total_dollar_pnl = 0
                    all_pos = Position.objects.filter(user_id=user_.id, status='o')
                    for ipos in all_pos:
                        total_dollar_pnl += ipos.dollar_size * ipos.pnl
                    total_dollar_pnl /= 100
                    total_dollar_pnl_s = str(total_dollar_pnl).replace(',', '.')
                    try:
                        if total_dollar_pnl_s[0] == '0' and total_dollar_pnl_s[1] == '.':
                            total_dollar_pnl = round(total_dollar_pnl, 3)
                        else:
                            total_dollar_pnl = round(total_dollar_pnl, 2)
                    except:
                        total_dollar_pnl = round(total_dollar_pnl, 2)

                    data_['user'] = {'b': round(user_.balance, 2), 'pnl': total_dollar_pnl}

                    self.send(json.dumps(data_))
                else:
                    self.send(json.dumps({'t': 'clp_', 's': 'err', 'm': 'Unknown error'}))
    
    def send_to_client(self, event, type='send_to_client'):
        self.send(json.dumps(event['m']))

# For candle and volume updates on chart
class UpdatesConsumer(WebsocketConsumer):
    def connect(self):
        iid = str(self.scope["url_route"]["kwargs"]["instrument_id"])
        tf = self.scope["url_route"]["kwargs"]["tf"]
        self.room_name = iid + "_" + tf
        self.room_group_name = "updates_" + self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(json.dumps({"t": "i", "m": "Asset and timeframe updates connected!"}))

    def disconnect(self, close_code):
        self.send(json.dumps({"t": "i", "m": "Disconnected!"}))
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def send_to_client(self, event, type='send_to_client'):
        self.send(json.dumps(event['m']))

class IIDUpdatesConsumer(WebsocketConsumer):
    def connect(self):
        iid = str(self.scope["url_route"]["kwargs"]["instrument_id"])
        self.room_name = iid
        self.room_group_name = "updates_" + self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(json.dumps({"t": "i", "m": "Asset updates connected!"}))

    def disconnect(self, close_code):
        self.send(json.dumps({"t": "i", "m": "Disconnected!"}))
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def send_to_client(self, event, type='send_to_client'):
        self.send(json.dumps(event['m']))

class ListUpdatesConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = 'updates_list'
        self.room_group_name = self.room_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(json.dumps({"t": "i", "m": "List updates connected!"}))

    def disconnect(self, close_code):
        self.send(json.dumps({"t": "i", "m": "Disconnected!"}))
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
    
    def send_to_client(self, event, type='send_to_client'):
        self.send(json.dumps(event['m']))