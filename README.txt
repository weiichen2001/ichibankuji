一番くじシミュレーター（Flask Webアプリ）
実行手順

このプロジェクトはPython/Flaskで作成しています。以下の手順で動作確認ができます。

【事前準備】
Python 3系がインストールされていること（Python 3.9以降推奨）

【手順】

1. このフォルダをVSCode等で開く

2. 仮想環境を作成する
   python3 -m venv venv

3. 仮想環境を有効化する
   Mac/Linux: source venv/bin/activate
   Windows  : venv\Scripts\activate
   ※ ターミナルの先頭に (venv) と表示されればOK

4. 必要なパッケージをインストールする
   pip install -r requirements.txt

5. データベースを作成する（このプロジェクトにはデータベースファイルを含めていません。
   以下のコマンドで新規作成してください）

   python3
   （Pythonの対話モードに入ったら、以下を貼り付けて実行）
   from app import app, db
   with app.app_context():
       db.create_all()
   exit()

6. 初期の景品データを投入する
   python3 seed_prizes.py

7. アプリを起動する
   python3 app.py

8. ブラウザで以下のURLを開く
   http://127.0.0.1:5000

【補足】
・データベースファイル（.db）や仮想環境（venv）フォルダは容量が大きく、
　環境依存のため提出フォルダには含めていません。上記の手順で再作成できます。
・新規登録画面からアカウントを作成すれば、すぐにくじ引きを試せます。
