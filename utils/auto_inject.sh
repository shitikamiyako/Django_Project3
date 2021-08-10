#! /bin/bash

# 運営からの情報 独立
python ./data_injector.py -r ./contents/Info.csv ../db.sqlite3 Info

# CustomUser 外部キー制約なし
python ./data_injector.py -r ./contents/accounts_customuser.csv ../db.sqlite3 accounts_customuser

# 投資信託・カテゴリ
# 親カテゴリ=>子カテゴリ=>投信
python ./data_injector.py -r ./contents/Category.csv ../db.sqlite3 Category
python ./data_injector.py -r ./contents/MutualFund.csv ../db.sqlite3 MutualFund

# 質問関連
# Question->QuestionAnswer(選択肢が質問文を外部キーとしている。)
python ./data_injector.py -r ./contents/Question.csv ../db.sqlite3 Question
python ./data_injector.py -r ./contents/QuestionAnswer.csv ../db.sqlite3 QuestionAnswer
