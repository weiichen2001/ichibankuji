from app import app, db, Collection, Prize, INITIAL_STOCK

with app.app_context():
    # 清空所有收藏紀錄
    num_deleted = db.session.query(Collection).delete()

    # 把所有獎品庫存還原成初始數量
    for pid, count in INITIAL_STOCK.items():
        prize = Prize.query.filter_by(id=pid).first()
        if prize:
            prize.stock = count

    db.session.commit()
    print(f"已清除 {num_deleted} 筆收藏紀錄，庫存已還原成初始數量：{INITIAL_STOCK}")