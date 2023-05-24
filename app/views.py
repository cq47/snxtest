import requests
import datetime
import functools
from .etoro import *
from .tv_ws import getPriceData
from pprint import pprint
from django.db.models import Q
from paper.asgi import channel_layer
from asgiref.sync import async_to_sync
from .models import *
from django.db.models import Case, Count, When
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.forms.models import model_to_dict
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.core.exceptions import ObjectDoesNotExist
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponseNotFound


# DELETE LATER, ONLY FOR TEST
class Obj:
    def __init__(self):
        self.symbol = None
        self.desc = None
        self.price = None
        self.perc = None
        self.volume = None

class Obj1:
    def __init__(self):
        self.dt = None
        self.status = None
        self.symbol = None
        self.type = None
        self.side = None
        self.price = None
        self.amount = None

class Obj2:
    def __init__(self):
        self.dt = None
        self.status = None
        self.symbol = None
        self.side = None
        self.entry_price = None
        self.exit_price = None
        self.amount = None
        self.pl = None  # must be calculated (profit)
        self.plp = None  # must be calculated (profit %)
#

# Updates last visit
def update_last_visit(view_method):
    @functools.wraps(view_method)
    def wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            request.user.last_login = datetime.datetime.now()
            request.user.save()
        return view_method(self, request, *args, **kwargs)
    return wrapper

# Adds extra_data from all-auth to context
def fetch_extra_data(view_method):
    @functools.wraps(view_method)
    def wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            self.context['all_auth_extra_data'] = SocialAccount.objects.get(user=request.user).extra_data
        return view_method(self, request, *args, **kwargs)
    return wrapper

# Adds extra_data from all-auth to context (for specific user_id)
def fetch_extra_data_from_user_id(view_method):
    @functools.wraps(view_method)
    def wrapper(self, request, user_id, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_admin:
            try:
                user_ = CustomUser.objects.get(id=user_id)
                self.context['all_auth_extra_data_user_'] = SocialAccount.objects.get(user=user_).extra_data
            except ObjectDoesNotExist:
                pass
        return view_method(self, request, user_id, *args, **kwargs)
    return wrapper

# Login required for GET
def get_login_required(view_method):
    @functools.wraps(view_method)
    def wrapper(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_method(self, request, *args, **kwargs)
        else:
            return redirect('index')
    return wrapper

# User must be "is_admin"
def admin_required(view_method):
    @functools.wraps(view_method)
    def wrapper(self, request, *args, **kwargs):
        if request.user.is_admin:
            return view_method(self, request, *args, **kwargs)
        else:
            return redirect('index')
    return wrapper

# User must NOT be "is_admin"
def not_admin_required(view_method):
    @functools.wraps(view_method)
    def wrapper(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return view_method(self, request, *args, **kwargs)
        else:
            return redirect('users')
    return wrapper

# Redirect to index
class View_RedirectToIndex(TemplateView):
    def get(self, request):
        return redirect('index')

# If account is not active
class View_InactiveAccount(TemplateView):
    template_name = 'account_inactive.html'
    context = {}    

    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, self.template_name, context=self.context)
        else:
            return redirect('index')

# Main page
class View_Index(TemplateView):
    template_name = 'index.html'
    context = {}    

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('assets')
        else:
            return render(request, self.template_name, context=self.context)

# We're redirected here when logging in with Google
class View_Login(TemplateView):
    @get_login_required
    def get(self, request):
        return redirect('assets')

# Logout
class View_Logout(TemplateView):
    def get(self, request):
        if request.user.is_authenticated:
            logout(request)
        return redirect('index')

# For admin: list of users
class View_Admin_Users(TemplateView):
    template_name = 'users.html'
    context = {}

    @get_login_required
    @admin_required
    @fetch_extra_data
    def get(self, request):
        c1 = ~Q(id=request.user.id)
        c2 = Q(is_superuser=False)
        self.context['users'] = CustomUser.objects.filter(c1 & c2)
        return render(request, self.template_name, context=self.context)

# For admin: account view of certain user
class View_Admin_UserAccount(TemplateView):
    template_name = 'account.html'
    context = {}

    @get_login_required
    @admin_required
    @fetch_extra_data
    @fetch_extra_data_from_user_id
    def get(self, request, user_id):
        try:
            user_ = CustomUser.objects.get(id=user_id)
            if user_.is_admin or (user_id == request.user.id) or user_.is_superuser:
                user_ = '0'
        except ObjectDoesNotExist:
            user_ = '1'
        self.context['user_'] = user_

        if type(user_) == CustomUser:
            try:
                orders = Order.objects.filter(user_id=user_.id).annotate(
                    relevancy=Count(Case(When(status='p', then=1)))
                ).order_by('-relevancy', '-date')
                orders_pending = orders.filter(status='p')
                orders_filled = orders.filter(status='f')
                orders_cancelled = orders.filter(status='c')
                orders_rejected = orders.filter(status='r')

                positions = Position.objects.filter(user_id=user_.id).annotate(
                    relevancy=Count(Case(When(status='o', then=1)))
                ).order_by('-relevancy', '-date')
                positions_open = positions.filter(status='o')
                positions_closed = positions.filter(status='c')

                self.context['posord_all'] = [
                    {'type': 'orders', 'data': [    
                        {'type': 'all', 'data': orders},
                        {'type': 'pending', 'data': orders_pending},
                        {'type': 'filled', 'data': orders_filled},
                        {'type': 'cancelled', 'data': orders_cancelled},
                        {'type': 'rejected', 'data': orders_rejected}
                    ]},
                    {'type': 'positions', 'data': [    
                        {'type': 'all', 'data': positions},
                        {'type': 'open', 'data': positions_open},
                        {'type': 'closed', 'data': positions_closed}
                    ]}
                ]

                total_pnl = 0
                pos_ds = 0
                for i in positions:
                    total_pnl += i.pnl * i.dollar_size
                    if i.status == 'o':
                        pos_ds += i.dollar_size
                total_pnl /= 100

                self.context['total_pnl'] = total_pnl
                self.context['total_pnl_perc'] = round(total_pnl / (user_.balance + abs(total_pnl) + pos_ds) * 100, 3)
            except:
                pass

        return render(request, self.template_name, context=self.context)

# Chart with asset
class View_Chart(TemplateView):
    template_name = 'chart.html'
    context = {}

    @get_login_required
    @not_admin_required
    @fetch_extra_data
    @update_last_visit
    def get(self, request, asset):
        try:
            asset_id = int(asset.split('_')[0])
            asset_ = Asset.objects.get(id=asset_id)
            self.context['asset'] = asset_  
            # Check if asset is tradable
            if asset_.listed:
                timeframe = request.GET.get('tf', None)
                tfs_ = ['1m', '5m', '15m', '30m', '1h', '4h', '1D']
                if not timeframe in tfs_:
                    prev_ = ('&prev=' + request.GET.get('prev')) if request.GET.get('prev') else ''
                    return redirect('/chart/' + asset + '?tf=1D' + prev_)
                else:
                    try:
                        chart = Chart.objects.filter(user_id=request.user.id, asset_id=asset_id, tf=timeframe)
                        if len(chart) > 0:
                            self.context['chart'] = chart[0]
                        else:
                            for i in tfs_:
                                chart = Chart()
                                chart.asset_id = asset_id
                                chart.user_id = request.user.id
                                chart.tf = i
                                chart.save()
                                if i == timeframe:
                                    self.context['chart'] = chart
                    except:
                        pass
                    # Timeframe as in eToro
                    self.context['tf_name_etoro'] = {
                        '1m': 'OneMinute',
                        '5m': 'FiveMinutes',
                        '15m': 'FifteenMinutes',
                        '30m': 'ThirtyMinutes',
                        '1h': 'OneHour',
                        '4h': 'FourHours',
                        '1D': 'OneDay'
                    }[timeframe]
                    # Timeframe as in TV
                    self.context['tf_name_tv'] = {
                        '1m': '1',
                        '5m': '5',
                        '15m': '15',
                        '30m': '30',
                        '1h': '60',
                        '4h': '240',
                        '1D': '1D'
                    }[timeframe]
                    #
                    self.context['ma_ribbon'] = render_to_string('indicators/ma_ribbon.html')
                    self.context['vol'] = render_to_string('indicators/vol.html')
                    self.context['macd'] = render_to_string('indicators/macd.html')
                    self.context['rsi'] = render_to_string('indicators/rsi.html')
                    self.context['vrvp'] = render_to_string('indicators/vrvp.html')
                    # For volume from Tradingview
                    self.context['tv_price_data'] = getPriceData(asset_.asset, timeframe)
                    # Default order size (10%)
                    self.context['default_order_size'] = int('1' + '0' * (len(str(int(request.user.balance * 0.1))) - 1))
                    # Orders
                    self.context['orders'] = Order.objects.filter(user_id=request.user.id, iid=asset_.instrument_id).annotate(
                        relevancy=Count(Case(When(status='p', then=1)))
                    ).order_by('-relevancy', '-date')
                    # Positions
                    self.context['positions'] = Position.objects.filter(user_id=request.user.id, iid=asset_.instrument_id).annotate(
                        relevancy=Count(Case(When(status='o', then=1)))
                    ).order_by('-relevancy', '-date')
                    # Total PnL
                    all_pos = Position.objects.filter(user_id=request.user.id, status='o')
                    user_total_pnl = 0
                    for ipos in all_pos:
                        user_total_pnl += ipos.dollar_size * ipos.pnl
                    user_total_pnl /= 100
                    #
                    pnl_char = '+' if user_total_pnl > 0 else ''
                    pnl_cond = str(user_total_pnl).replace(',', '.')
                    try:
                        pnl_cond = pnl_cond[0] == '0' and pnl_cond[1] == '.'
                    except:
                        pnl_cond = False
                    self.context['user_total_pnl'] = user_total_pnl
                    self.context['user_total_pnl_f'] = pnl_char + (str(round(user_total_pnl, 3)) if pnl_cond else str(round(user_total_pnl, 2)))
                    return render(request, self.template_name, context=self.context)
            else:
                return redirect('/assets')
        except Exception as e:
            print(e)
            return redirect('/assets')

# Account page with balances and PnL
class View_Account(TemplateView):
    template_name = 'account.html'
    context = {}

    @get_login_required
    @not_admin_required
    @fetch_extra_data
    @update_last_visit
    def get(self, request):
        orders = Order.objects.filter(user_id=request.user.id).annotate(
            relevancy=Count(Case(When(status='p', then=1)))
        ).order_by('-relevancy', '-date')
        orders_pending = orders.filter(status='p')
        orders_filled = orders.filter(status='f')
        orders_cancelled = orders.filter(status='c')
        orders_rejected = orders.filter(status='r')

        positions = Position.objects.filter(user_id=request.user.id).annotate(
            relevancy=Count(Case(When(status='o', then=1)))
        ).order_by('-relevancy', '-date')
        positions_open = positions.filter(status='o')
        positions_closed = positions.filter(status='c')

        self.context['posord_all'] = [
            {'type': 'orders', 'data': [    
                {'type': 'all', 'data': orders},
                {'type': 'pending', 'data': orders_pending},
                {'type': 'filled', 'data': orders_filled},
                {'type': 'cancelled', 'data': orders_cancelled},
                {'type': 'rejected', 'data': orders_rejected}
            ]},
            {'type': 'positions', 'data': [    
                {'type': 'all', 'data': positions},
                {'type': 'open', 'data': positions_open},
                {'type': 'closed', 'data': positions_closed}
            ]}
        ]
        self.context['user_'] = request.user

        total_pnl = 0
        pos_ds = 0
        for i in positions:
            total_pnl += i.pnl * i.dollar_size
            if i.status == 'o':
                pos_ds += i.dollar_size
        total_pnl /= 100

        self.context['total_pnl'] = total_pnl
        self.context['total_pnl_perc'] = round(total_pnl / (request.user.balance + abs(total_pnl) + pos_ds) * 100, 3)

        return render(request, self.template_name, context=self.context)


# List of assets
class View_AssetsList(TemplateView):
    template_name = 'assets_list.html'
    context = {}

    @get_login_required
    @fetch_extra_data
    @update_last_visit
    def get(self, request):
        if not request.GET.get('asset_type') in ['stocks', 'etfs', 'options', 'commodities']:
            return redirect('/assets?asset_type=stocks')
        else:
            asset_type = request.GET.get('asset_type')
            self.context['asset_type_is_option'] = False
            if request.user.is_admin:
                if asset_type != 'options':
                    assets = Asset.objects.filter(instrument_type=asset_type[0]).order_by('-listed', 'asset')
                    self.context['all_assets'] = {'type': asset_type, 'data': [{'type': 'all', 'data': assets}]}
                else:
                    assets = Option.objects.all().order_by('-listed', 'asset', '-strike_price')
                    self.context['all_assets'] = {'type': asset_type, 'data': [{'type': 'all', 'data': assets}]}
                    self.context['asset_type_is_option'] = True
            else:
                if asset_type != 'options':
                    assets = Asset.objects.filter(instrument_type=asset_type[0], listed=True).order_by('asset')
                    ga, lo = [], []
                    for i in assets:
                        pc = i.price_change_float
                        if pc > 0:
                            ga.append(i)
                        elif pc < 0:
                            lo.append(i)
                    self.context['all_assets'] = {'type': asset_type, 'data': [
                            {'type': 'all', 'data': assets},
                            {'type': 'gainers', 'data': ga},
                            {'type': 'losers', 'data': lo}
                        ]
                    }
                else:
                    assets = Option.objects.filter(listed=True).order_by('-listed', 'asset', '-strike_price')
                    self.context['all_assets'] = {'type': asset_type, 'data': [
                            {'type': 'all', 'data': assets},
                            {'type': 'gainers', 'data': assets.filter(option_type='Call')},
                            {'type': 'losers', 'data': assets.filter(option_type='Put')}
                        ]
                    }
                    self.context['asset_type_is_option'] = True

            self.context['assets_number'] = len(assets)
            aids, ans = [], []
            for i in assets:
                if asset_type != 'options':
                    aids.append(str(i.instrument_id))
                ans.append(i.asset)
            self.context['aids_list'] = aids
            self.context['aids'] = ','.join(aids)
            self.context['asset_names'] = ans

            return render(request, self.template_name, context=self.context)


# List of assets
class View_ClearOrdpos(TemplateView):
    @get_login_required
    def get(self, request):
        Order.objects.filter(user_id=request.user.id).delete()
        Position.objects.filter(user_id=request.user.id).delete()
        Option.objects.all().delete()
        return JsonResponse({})