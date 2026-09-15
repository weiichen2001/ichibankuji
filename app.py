from flask import Flask, session, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import random

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # 之後會解釋這是什麼

# 資料庫設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ichibankuji.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

class Prize(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rarity = db.Column(db.String(10), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class Collection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    prize_name = db.Column(db.String(100), nullable=False)
    prize_rarity = db.Column(db.String(10), nullable=False)

def is_logged_in():
    return "user_id" in session

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

LAST_ONE_PRIZE = {"id": "LAST", "name": "ラストワン賞・特製立牌", "rarity": "LAST"}

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # 檢查使用者名稱有沒有被用過
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "這個使用者名稱已經被註冊過了，換一個試試"

        # 建立新使用者，密碼加密後存起來
        new_user = User(
            username=username,
            password_hash=generate_password_hash(password, method="pbkdf2:sha256")
        )
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()

        if user is None or not check_password_hash(user.password_hash, password):
            return "使用者名稱或密碼錯誤"

        # 登入成功，把使用者id存進session，代表「這個瀏覽器現在是登入狀態」
        session["user_id"] = user.id
        return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/draw")
@login_required
def draw():
    # 從資料庫抓出所有還有庫存的獎品
    available_prizes = Prize.query.filter(Prize.stock > 0).all()

    if not available_prizes:
        return "全部獎品都已經被抽完了！"

    ids = [p.id for p in available_prizes]
    weights = [p.stock for p in available_prizes]

    picked_id = random.choices(ids, weights=weights, k=1)[0]
    picked_prize = Prize.query.filter_by(id=picked_id).first()

    # 扣庫存，直接改資料庫裡的資料
    picked_prize.stock -= 1
    db.session.commit()

    # 檢查是不是最後一抽（扣完之後，全部獎品庫存加起來是不是0）
    total_remaining = db.session.query(db.func.sum(Prize.stock)).scalar()
    is_last_one = (total_remaining == 0)

    session["last_draw"] = {
        "name": picked_prize.name,
        "rarity": picked_prize.rarity,
        "is_last_one": is_last_one,
    }

    new_collection_item = Collection(
        user_id=session["user_id"],
        prize_name=picked_prize.name,
        prize_rarity=picked_prize.rarity,
    )
    db.session.add(new_collection_item)
    db.session.commit()

    return redirect(url_for("result"))

@app.route("/result")
@login_required
def result():
    draw_data = session.get("last_draw")

    if not draw_data:
        return redirect(url_for("home"))

    return render_template("result.html", prize=draw_data)

@app.route("/collection")
@login_required
def collection():
    items = Collection.query.filter_by(user_id=session["user_id"]).all()
    return render_template("collection.html", items=items)

@app.route("/stock")
@login_required
def stock():
    prizes = Prize.query.all()
    return render_template("stock.html", prizes=prizes)

@app.route("/reset")
def reset():
    session.clear()
    return "已經重置，庫存跟抽獎紀錄都清空了。"

if __name__ == "__main__":
    app.run(debug=True)