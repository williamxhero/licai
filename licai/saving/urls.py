from django.urls import path, register_converter
from . import views

class TypeUrlParamConv:
    return_type = str

    def to_url(self, value):
        return str(value)
    
    def to_python(self, value):
        return self.return_type(value)

class NumberUPC(TypeUrlParamConv):
    regex = r'[0-9]+(\.[0-9]+)?'
    return_type = float

class DateUPC(TypeUrlParamConv):
    regex = r'[0-9]{4}[0-9]{2}[0-9]{2}'
    return_type = int

register_converter(NumberUPC, 'number')
register_converter(DateUPC, 'date')

app_name="saving"

urlpatterns = [
    path("", views.index, name="index"),
    path("test/<date:date>/<str:bucket>/<str:market>/<number:amount>",
         views.url_test, name="test_view"),
    path("buy/<date:date>/<str:bucket>/<str:market>/<number:amount>",
         views.url_buy, name="buy"),
    path("sell/<date:date>/<str:bucket>/<str:market>/<number:amount>",
         views.url_sell, name="sell"),
    path("change/<str:date>/<str:bucket>/<str:market>/<number:remains>",
         views.url_change, name="change"),
]