from django import template
from allauth.socialaccount.models import SocialAccount

register = template.Library()

# Add + if percentage is >= 0, and - if < 0
@register.filter(name='price_perc_filter')
def price_perc_filter(val):
    return ('' if val < 0 else '+') + str(round(val, 2))

# Add , to big numbers
@register.filter(name='balance_filter')
def balance_filter(val):
    return '{:,}'.format(round(val, 2))

# 0 - market, 1 - limit
@register.filter(name='order_type_filter')
def order_type_filter(val):
    return {'m': 'Market', 'l': 'Limit'}[val]

# 
@register.filter(name='order_side_filter')
def order_side_filter(val):
    return {'l': 'Long', 's': 'Short'}[val]

# 
@register.filter(name='order_status_filter')
def order_status_filter(val):
    return {'p': 'Pending', 'f': 'Filled', 'c': 'Cancelled', 'r': 'Rejected'}[val]

#
@register.filter(name='order_status_color_filter')
def order_status_color_filter(val):
    return {'p': 'text', 'f': 'blue', 'c': 'text', 'r': 'red'}[val]

# 0 - Open, 1 - Closed
@register.filter(name='position_status_filter')
def position_status_filter(val):
    return ['Open', 'Closed'][int(val)]

# Datetime filter for date
@register.filter(name='dtformat_date')
def dtformat_date(dt):
    return dt.strftime("%d %b %Y")

# Datetime filter for time
@register.filter(name='dtformat_time')
def dtformat_time(dt):
    return dt.strftime("%I:%M:%S %p")

# Format volume as K, M, B etc
@register.filter(name='volume_filter')
def volume_filter(val):
    if val and not ('e' in str(val)):
        if val >= 1000000000000:  # Trillion
            return str(round(val / 1000000000000, 2)) + 'T'
        elif val >= 1000000000:  # Billion
            return str(round(val / 1000000000, 2)) + 'B'
        elif val >= 1000000:  # Million
            return str(round(val / 1000000, 2)) + 'M'
        elif val >= 1000:  # Thousand
            return str(round(val / 1000, 2)) + 'K'
        else:
            return str(round(val, 2))
    else:
        return '-'

# 0 -> nothing, > 0 -> green, < 0 -> red
@register.filter(name='price_perc_class')
def price_perc_class(val):
    if val > 0:
        return 'green'
    elif val < 0:
        return 'red'
    else:
        return ''

# 0 -> nothing, > 0 -> green, < 0 -> red
@register.filter(name='price_char')
def price_char(val):
    return '+' if val >= 0 else ''

# Round price automatically
@register.filter(name='round_filter')
def round_filter(val, n):
    return round(val, n)

# For displaying info fetched after logging in with Google
@register.filter(name='google_auth')
def google_auth(user):
    return SocialAccount.objects.get(user=user).extra_data

# Replace True for true and False for false
@register.filter(name='boolean_safety')
def boolean_safety(s):
    return str(s).replace('True', 'true').replace('False', 'false')

# Round
@register.filter(name='math_round')
def math_round(val, n):
    return round(val, n)

# Order size font size filter
@register.filter(name='order_size_fs_filter')
def order_size_fs_filter(val):
    return 12 if len(str(val)) < 5 else 10