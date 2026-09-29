from app import app, db, Collection, Prize, INITIAL_STOCK

with app.app_context():
    # 収集履歴を全て削除
    num_deleted = db.session.query(Collection).delete()

    # 景品の在庫を初期数量にリセット
    for pid, count in INITIAL_STOCK.items():
        prize = Prize.query.filter_by(id=pid).first()
        if prize:
            prize.stock = count

    db.session.commit()
    print(f"収集履歴を{num_deleted}件削除し、在庫を初期数量にリセットしました：{INITIAL_STOCK}")