from app import app, db, Prize

with app.app_context():
    prizes_data = [
        {"id": "A", "name": "S級・限定手辦", "rarity": "SS", "stock": 1},
        {"id": "B", "name": "亮面吊飾", "rarity": "S", "stock": 3},
        {"id": "C", "name": "壓克力立牌", "rarity": "A", "stock": 5},
        {"id": "D", "name": "貼紙組", "rarity": "B", "stock": 10},
        {"id": "E", "name": "明信片", "rarity": "C", "stock": 20},
    ]

    for p in prizes_data:
        new_prize = Prize(id=p["id"], name=p["name"], rarity=p["rarity"], stock=p["stock"])
        db.session.add(new_prize)

    db.session.commit()
    print("獎品資料寫入完成！")