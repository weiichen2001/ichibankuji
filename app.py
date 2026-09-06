from flask import Flask, session, render_template, redirect, url_for
import random

app = Flask(__name__)
app.secret_key = "dev-secret-key"  # 之後會解釋這是什麼

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