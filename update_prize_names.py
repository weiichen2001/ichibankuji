from app import app, db, Prize

with app.app_context():
    updates = {
        "A": {"name": "フィギュア", "rarity": "A賞"},
        "B": {"name": "お椀", "rarity": "B賞"},
        "C": {"name": "ポーチ", "rarity": "C賞"},
        "D": {"name": "ぬいぐるみキーチェン", "rarity": "D賞"},
        "E": {"name": "ステッカー", "rarity": "E賞"},
    }
    for pid, info in updates.items():
        prize = Prize.query.filter_by(id=pid).first()
        if prize:
            prize.name = info["name"]
            prize.rarity = info["rarity"]
    db.session.commit()
    print("品名・賞別を更新しました")
