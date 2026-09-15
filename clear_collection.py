from app import app, db, Collection

with app.app_context():
    num_deleted = db.session.query(Collection).delete()
    db.session.commit()
    print(f"已經刪除 {num_deleted} 筆收藏紀錄")