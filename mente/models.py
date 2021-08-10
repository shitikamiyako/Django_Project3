from django.db import models
from datetime import datetime


class Info(models.Model):
    class Meta:
        db_table = 'Info'
        verbose_name_plural = '運営からの連絡'

    FLAG = ((0, '表示'), (1, '非表示'))

    title = models.CharField('タイトル', max_length=255, default='')
    contents = models.TextField('本文', default='')
    datetime = models.DateTimeField('登録日時', default=datetime.now)
    show_flag = models.IntegerField('表示フラグ', choices=FLAG, default=0)

    def __str__(self):
        return self.title
