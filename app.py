from flask import Flask, session, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import random

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # 之後會解釋這是什麼

# 新增：資料庫設定
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ichibankuji.db"
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

PRIZES = [
    {"id": "A", "name": "S級・限定手辦", "rarity": "SS"},
    {"id": "B", "name": "亮面吊飾", "rarity": "S"},
    {"id": "C", "name": "壓克力立牌", "rarity": "A"},
    {"id": "D", "name": "貼紙組", "rarity": "B"},
    {"id": "E", "name": "明信片", "rarity": "C"},
]
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

@app.route("/draw")
def draw():
    if "stock" not in session:
        session["stock"] = {"A": 1, "B": 3, "C": 5, "D": 10, "E": 20}

    stock = session["stock"]
    available_ids = [pid for pid, count in stock.items() if count > 0]

    if not available_ids:
        return "全部獎品都已經被抽完了！"

    weights = [stock[pid] for pid in available_ids]
    picked_id = random.choices(available_ids, weights=weights, k=1)[0]
    stock[picked_id] -= 1
    session["stock"] = stock

    picked_prize = next(p for p in PRIZES if p["id"] == picked_id)

    total_remaining = sum(stock.values())
    is_last_one = (total_remaining == 0)

    session["last_draw"] = {
        "name": picked_prize["name"],
        "rarity": picked_prize["rarity"],
        "is_last_one": is_last_one,
    }

    # 新增：把這次抽到的獎項，加進收藏紀錄清單裡
    if "collection" not in session:
        session["collection"] = []

    session["collection"].append({
        "name": picked_prize["name"],
        "rarity": picked_prize["rarity"],
    })
    session.modified = True  # 之後會解釋這行是做什麼的

    return redirect(url_for("result"))

@app.route("/result")
def result():
    draw_data = session.get("last_draw")

    if not draw_data:
        return redirect(url_for("home"))

    return render_template("result.html", prize=draw_data)

@app.route("/collection")
def collection():
    items = session.get("collection", [])
    return render_template("collection.html", items=items)

@app.route("/reset")
def reset():
    session.clear()
    return "已經重置，庫存跟抽獎紀錄都清空了。"

if __name__ == "__main__":
    app.run(debug=True)