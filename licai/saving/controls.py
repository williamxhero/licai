
import re
from typing import Any

from django.db.models import Q, Max

from saving.models import *

def _date_to_str(date:Any):
    date = str(date)
    date = re.sub(r'[-/\\.:]', '', date)
    return date[:8]

def _check_date_gte(date1:str, date2:Any):
    date1 = _date_to_str(date1)
    date2 = _date_to_str(date2)
    return int(date1) >= int(date2)

def _get_latest_history(bucket:str, market:str):
    query = None
    if bucket != "":
        query = Q(bucket=bucket)
    if market != "":
        qmkt = Q(market=market)
        query = qmkt if query is None else query & qmkt

    shi_ds = History.objects.filter(query).order_by('-id')
    if len(shi_ds) == 0:
        return None
    return shi_ds[0]

def _change_share(date:str, bucket:str, market:str, amount:float):
    his = _get_latest_history(bucket, market)

    if not his:
        History(date=date,
                market=market,
                bucket=bucket,
                buy_sell=amount,
                remains=amount,
                net_value=1,
                total_shares=amount).save()
        return
    
    if not _check_date_gte(date, his.date):
        raise ValueError(f"Can only change share in the future. {date}{bucket}{market}")
    
    shares_to_chg = amount / his.net_value
    new_ttl_shares = his.total_shares + shares_to_chg
    new_remains = his.remains + amount

    if _date_to_str(his.date) == date:
        his.buy_sell += amount
        his.total_shares = new_ttl_shares
        his.remains = new_remains
        his.save()
    else:
        History(date=date,
                market=market,
                bucket=bucket,
                buy_sell=amount,
                remains=new_remains,
                net_value=his.net_value,
                total_shares=new_ttl_shares).save()
        
def _change_remains(date:str, bucket:str, market:str, remains:float, old_remains:float):
    if old_remains < 0:
        raise ValueError(f"Old remains must be positive.{date}{bucket}{market}")
    
    his = _get_latest_history(bucket, market)

    if not his:
        raise ValueError(f"Remains not bought yet. {date}{bucket}{market}")

    if not _check_date_gte(date, his.date):
        raise ValueError(f"Can only change remains in the future.{date}{bucket}{market}")

    remains_before = his.remains
    if old_remains == 0: old_remains = remains_before
    new_remains = remains_before - old_remains + remains

    total_shares = his.total_shares
    new_net_value = new_remains / total_shares
    hist_date = _date_to_str(his.date)

    if hist_date == date and his.buy_sell == 0: 
        # pure changed, change it again.
        his.remains = new_remains
        his.net_value = new_net_value
        his.save()
    else:
        # other day, new entry to change.
        History(date=date,
                buy_sell=0,
                bucket=his.bucket,
                market=his.market,
                remains=new_remains, 
                net_value=new_net_value,
                total_shares=total_shares).save()

    return remains_before

def buy_share(date:str, bucket:str, market:str, amount:float):
    for b, m in [(bucket, market), (bucket, '*'), ('*', market), ('*', '*')]:
        _change_share(date, b, m, amount)

def sell_share(date:str, bucket:str, market:str, amount:float):
    for b, m in [(bucket, market), (bucket, '*'), ('*', market), ('*', '*')]:
        _change_share(date, b, m, -amount)

def change_remains(date:str, bucket:str, market:str, remains:float):
    old_remains = _change_remains(date, bucket, market, remains, 0)
    for b, m in [(bucket, '*'), ('*', market), ('*', '*')]:
        _change_remains(date, b, m, remains, old_remains)

def load_all()->list[History]:
    his_ds = History.objects.values('date', 'bucket', 'market').annotate(max_id=Max('id'))
    if len(his_ds) == 0:
        return []
    his_ds = History.objects.filter(id__in=his_ds.values('max_id'))
    his_lst = []
    for his in his_ds:
        # change his to dictionary:
        his_dic = {}
        his_dic['date'] = his.date.strftime("%Y/%m/%d")
        his_dic['bm'] = f'{his.bucket}{his.market}'
        his_dic['fund'] = his.remains
        his_dic['nv'] = round(his.net_value, 4)
        his_lst.append(his_dic)
    return his_lst

