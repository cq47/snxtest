import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser

# Order
class Order(models.Model):
    user_id = models.IntegerField(default=0)
    date = models.DateTimeField(null=True)
    status = models.CharField(max_length=1, default='p')
    iid = models.IntegerField(default=0)
    asset_name = models.CharField(max_length=64, default='')
    order_type = models.CharField(max_length=1, default='m')
    side = models.CharField(max_length=1, default='l')
    price = models.FloatField(default=0)
    size = models.FloatField(default=0)
    size_type = models.CharField(max_length=1, default='t')
    leverage = models.IntegerField(default=1)

# Position
class Position(models.Model):
    user_id = models.IntegerField(default=0)
    date = models.DateTimeField(null=True)
    status = models.CharField(max_length=1, default='o')
    iid = models.IntegerField(default=0)
    asset_name = models.CharField(max_length=64, default='')
    side = models.CharField(max_length=1, default='l')
    calc_price = models.FloatField(default=0)
    entry_price = models.FloatField(default=0)
    exit_price = models.FloatField(default=0)
    dollar_size = models.FloatField(default=0)
    size = models.FloatField(default=0)
    size_type = models.CharField(max_length=1, default='t')
    leverage = models.IntegerField(default=1)
    pnl = models.FloatField(default=0)

    @property
    def get_dollar_pnl(self):
        v = self.pnl * self.dollar_size / 100
        v2 = round(v, 3)
        v3 = v2 if v2 != 0 else round(v, 4)
        if v3 == 0:
            v3 = round(v, 6)
        return v3

# Chart
class Chart(models.Model):
    asset_id = models.IntegerField(default=0)
    user_id = models.IntegerField(default=0)
    tf = models.CharField(max_length=4, default='1D')
    settings = models.JSONField(default={})

# User
class CustomUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    balance = models.FloatField(default=1000000)
    pnl = models.FloatField(default=0.0)

    @property
    def pnl_perc(self):
        return round(self.pnl / (self.balance - self.pnl), 2)

# Asset
class Asset(models.Model):
    asset = models.CharField(max_length=32, default='')             # name of asset
    desc = models.TextField(default='')              # description
    instrument_id = models.IntegerField(null=True, default=0)
    instrument_type = models.CharField(null=True, max_length=1, default='')
    exchange_id = models.IntegerField(null=True, default=0)
    listed = models.BooleanField(default=False)                     # is asset tradable?
    precision = models.IntegerField(default=0)
    bid_price = models.FloatField(default=0)
    ask_price = models.FloatField(default=0)
    close_price = models.FloatField(default=0)
    official_close_price = models.FloatField(default=0)
    is_market_open = models.BooleanField(default=False)
    daily_volume = models.FloatField(null=True)
    last_update_daily_volume = models.DateTimeField(default=datetime.datetime.now() - datetime.timedelta(days=30))
    last_update_is_market_open = models.DateTimeField(default=datetime.datetime.now() - datetime.timedelta(days=30))
    last_update_current_price = models.DateTimeField(default=datetime.datetime.now() - datetime.timedelta(days=30))
    bad_reason = models.TextField(default='')  # for invalidation reason for example

    @property
    def ask_price_rounded(self):
        return round(self.ask_price, self.precision)

    @property
    def bid_price_rounded(self):
        return round(self.bid_price, self.precision)

    @property
    def is_bad_volume(self):
        return ((self.daily_volume == None) or ('e' in str(self.daily_volume).lower()))

    @property
    def price_color(self):
        val = (self.bid_price if self.is_market_open else self.official_close_price) - self.close_price
        return ('var(--green)' if val > 0 else ('var(--red)' if val < 0 else 'var(--text)'))

    @property
    def price_change(self):
        val = round((self.bid_price if self.is_market_open else self.official_close_price) - self.close_price, self.precision)
        return ('+' if val > 0 else '') + str(val)

    @property
    def price_change_float(self):
        return (self.bid_price if self.is_market_open else self.official_close_price) - self.close_price

    @property
    def perc_change(self):
        val = round(self.price_change_float / self.close_price * 100, 2) if self.close_price != 0 else 0
        return ('+' if val > 0 else '') + str(val)

# Options
class Option(models.Model):
    asset = models.CharField(max_length=32, default='') 
    desc = models.TextField(default='')
    listed = models.BooleanField(default=False)
    bid_price = models.FloatField(default=0)
    ask_price = models.FloatField(default=0)
    price = models.FloatField(default=0)
    strike_price = models.FloatField(default=0)
    option_type = models.CharField(max_length=1, default='')
    moneyness = models.FloatField(default=0)
    exp_date = models.DateTimeField(null=True, default=None)
    last_price = models.FloatField(default=0)
    volume = models.IntegerField(default=0)
    oi = models.IntegerField(default=0)
    iv = models.FloatField(default=0)
    last_update = models.DateTimeField(default=datetime.datetime.now() - datetime.timedelta(days=120))

    