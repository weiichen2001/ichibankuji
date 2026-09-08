from app import app, db, Prize

with app.app_context():
    real_stock = {"A": 1, "B": 3, "C": 5, "D": 10, "E": 20}
    for pid, count in real_stock.items():
        prize = Prize.query.filter_by(id=pid).first()
        prize.stock = count
    db.session.commit()
    print("庫存已經還原成正式數值")