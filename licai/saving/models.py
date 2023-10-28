from django.db import models

class History(models.Model):
    date = models.DateField()
    market = models.CharField(max_length=4, verbose_name="C存Z债J基G股Q期", blank=True)
    bucket = models.CharField(max_length=4, verbose_name="Y养L理X消", blank=True)
    buy_sell = models.FloatField()
    remains = models.FloatField()
    net_value = models.FloatField()
    total_shares = models.FloatField()

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['remains']),
            models.Index(fields=['market']),
            models.Index(fields=['bucket']),
        ]

    def __str__(self) -> str:
        if self.buy_sell == 0:
            chg_str = ' '
        else:
            if self.buy_sell < 0:
                chg_str = f" {self.buy_sell:.2f}  → "
            else:
                chg_str = f" +{self.buy_sell:.2f}  → "

        return f"[{self.date}]({self.net_value:.2f}|{self.bucket}{self.market}){chg_str}{self.remains:.2f} "