from django.shortcuts import redirect, render
from django.http import HttpResponse
from saving.controls import *

# Create your views here.
def index(request:Any):
    hist_lst = load_all()
    context = {"all_hist": hist_lst}
    return render(request, "saving/index.html", context)

def url_buy(request:Any, date:int, bucket:str, market:str, amount:float):
    buy_share(str(date), bucket, market, amount)
    return redirect("saving:index")

def url_sell(request:Any, date:int, bucket:str, market:str, amount:float):
    sell_share(str(date), bucket, market, amount)
    return redirect("saving:index")

def url_change(request:Any, date:int, bucket:str, market:str, remains:float):
    change_remains(str(date), bucket, market, remains)
    return redirect("saving:index")

def url_test(request:Any, date:int, bucket:str, market:str, amount:float):
    return HttpResponse(f"Date: {date}, {bucket}, {market}, {amount}")

    #change/20230926/L/G/113920