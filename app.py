from flask import Flask, session, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import random

app = Flask(__name__)
app.secret_key = "dev-secret-key"

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

# 這一盒的初始庫存，補貨時會用這份資料重新補滿
INITIAL_STOCK = {"A": 1, "B": 3, "C": 5, "D": 10, "E": 20}

PRIZE_IMAGES = {
    "A": ["prizes/a_figure.png"],
    "B": ["prizes/b_bowl.png"],
    "C": ["prizes/c_pouch_1.png", "prizes/c_pouch_2.png"],
    "D": ["prizes/d_keychain_1.png", "prizes/d_keychain_2.png", "prizes/d_keychain_3.png"],
    "E": ["prizes/e_sticker_1.png", "prizes/e_sticker_2.png"],
    "LAST": ["prizes/last_cushion.png"],
}

def restock_prizes():
    """把所有獎品的庫存補回初始數量，代表「開新的一盒」"""
    for pid, count in INITIAL_STOCK.items():
        prize = Prize.query.filter_by(id=pid).first()
        if prize:
            prize.stock = count
    db.session.commit()

def perform_single_draw(user_id):
    """執行一次抽獎，回傳這次抽到的結果（dict）。庫存歸零時會自動補貨。"""
    available_prizes = Prize.query.filter(Prize.stock > 0).all()

    if not available_prizes:
        return None

    ids = [p.id for p in available_prizes]
    weights = [p.stock for p in available_prizes]

    picked_id = random.choices(ids, weights=weights, k=1)[0]
    picked_prize = Prize.query.filter_by(id=picked_id).first()

    picked_prize.stock -= 1
    db.session.commit()

    total_remaining = db.session.query(db.func.sum(Prize.stock)).scalar()
    is_last_one = (total_remaining == 0)

    new_collection_item = Collection(
        user_id=user_id,
        prize_name=picked_prize.name,
        prize_rarity=picked_prize.rarity,
    )
    db.session.add(new_collection_item)
    db.session.commit()

    image_choices = PRIZE_IMAGES.get(picked_id, [])
    image_path = random.choice(image_choices) if image_choices else None

    result = {
        "name": picked_prize.name,
        "rarity": picked_prize.rarity,
        "is_last_one": is_last_one,
        "image": image_path,
    }

    # 這一盒抽完了，自動開新盒（補貨），讓十連抽可以無縫繼續
    if is_last_one:
        restock_prizes()
        last_one_images = PRIZE_IMAGES.get("LAST", [])
        result["last_one_image"] = random.choice(last_one_images) if last_one_images else None

    return result

def perform_ten_draw(user_id):
    """執行十連抽，回傳10筆結果組成的清單"""
    results = []
    for _ in range(10):
        result = perform_single_draw(user_id)
        if result is None:
            break
        results.append(result)
    return results

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template("register.html", error="このユーザー名はすでに使用されています。別の名前をお試しください。")

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
            return render_template("login.html", error="ユーザー名またはパスワードが正しくありません。")

        session["user_id"] = user.id
        return redirect(url_for("home"))

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/draw")
@login_required
def draw_select():
    return render_template("draw_select.html")

@app.route("/draw/single")
@login_required
def draw_single():
    result = perform_single_draw(session["user_id"])

    if result is None:
        return redirect(url_for("home"))

    session["last_draw"] = [result]
    return redirect(url_for("result"))

@app.route("/draw/ten")
@login_required
def draw_ten():
    results = perform_ten_draw(session["user_id"])

    if not results:
        return redirect(url_for("home"))

    session["last_draw"] = results
    return redirect(url_for("result"))

@app.route("/result")
@login_required
def result():
    results = session.get("last_draw")

    if not results:
        return redirect(url_for("home"))

    return render_template("result.html", results=results)

@app.route("/collection")
@login_required
def collection():
    items = Collection.query.filter_by(user_id=session["user_id"]).all()

    summary = {}
    for item in items:
        key = (item.prize_name, item.prize_rarity)
        summary[key] = summary.get(key, 0) + 1

    collection_list = []
    for (name, rarity), count in summary.items():
        images = PRIZE_IMAGES.get(rarity[0] if rarity != "ラストワン賞" else "LAST", [])
        collection_list.append({
            "name": name,
            "rarity": rarity,
            "count": count,
            "image": images[0] if images else None,
        })

    return render_template("collection.html", items=collection_list, total=len(items))

@app.route("/stock")
def stock():
    prizes = Prize.query.all()
    prize_list = []
    for p in prizes:
        images = PRIZE_IMAGES.get(p.id, [])
        prize_list.append({
            "name": p.name,
            "rarity": p.rarity,
            "stock": p.stock,
            "image": images[0] if images else None,
        })
    return render_template("stock.html", prizes=prize_list)

@app.route("/reset")
@login_required
def reset():
    session.pop("last_draw", None)
    return render_template("reset.html")

if __name__ == "__main__":
    app.run(debug=True)