from app import app, db, Prize

with app.app_context():
    prizes_data = [
        {"id": "A", "name": "フィギュア", "rarity": "A賞", "stock": 1},
        {"id": "B", "name": "フードボウル", "rarity": "B賞", "stock": 3},
        {"id": "C", "name": "ポーチ", "rarity": "C賞", "stock": 5},
        {"id": "D", "name": "ぬいぐるみキーホルダー", "rarity": "D賞", "stock": 10},
        {"id": "E", "name": "ステッカー", "rarity": "E賞", "stock": 20},
    ]

    for p in prizes_data:
        new_prize = Prize(id=p["id"], name=p["name"], rarity=p["rarity"], stock=p["stock"])
        db.session.add(new_prize)

    db.session.commit()
    print("景品データの登録が完了しました！")