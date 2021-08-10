from django.db import models
from accounts.models import CustomUser
from datetime import datetime


class Question(models.Model):
    """質問文モデル

    question: str
    """
    class Meta:
        db_table = 'Question'
        verbose_name_plural = 'アンケート質問文'

    question = models.CharField('質問文', max_length=255, default='')

    def __str__(self):
        return f"{self.id} - {self.question}"


class QuestionAnswer(models.Model):
    """質問文と紐付く選択肢モデル.

    Question_obj: 質問文モデルのFK
    choice: 選択肢 as str
    risk: risk score as int
    term: term score as int
    """
    class Meta:
        db_table = 'QuestionAnswer'
        verbose_name_plural = 'アンケート選択肢'

    question_obj = models.ForeignKey(
        Question, verbose_name='アンケート質問文', on_delete=models.CASCADE, default=0)
    choice = models.CharField('選択肢', max_length=255, default='')
    risk = models.IntegerField('リスク値', default=0)
    term = models.IntegerField('期間', default=0)

    def __str__(self):
        return f"{self.choice}"


class QuestionResult(models.Model):
    """質問回答結果モデル

    customuser_obj: FK of CustomUser
    risk_score: risk score by int
    term_score: term score by int
    datetime: datetime data registered"""
    class Meta:
        db_table = 'QuestionResult'
        verbose_name_plural = 'アンケート回答結果'
    customuser_obj = models.ForeignKey(CustomUser, verbose_name='ユーザー情報',
                                       on_delete=models.CASCADE)
    risk_score = models.IntegerField('リスク値計', default=0)
    term_score = models.IntegerField('期間計', default=0)
    datetime = models.DateTimeField('日付情報', default=datetime.now())
