from app import app, db, User, Prize, Collection

with app.app_context():
    print("========== 使用者 ==========")
    users = User.query.all()
    if not users:
        print("（目前沒有使用者）")
    for u in users:
        print(f"id={u.id}  username={u.username}")

    print("\n========== 獎品庫存 ==========")
    prizes = Prize.query.all()
    if not prizes:
        print("（目前沒有獎品資料）")
    for p in prizes:
        print(f"id={p.id}  name={p.name}  rarity={p.rarity}  stock={p.stock}")

    print("\n========== 收藏紀錄 ==========")
    collections = Collection.query.all()
    if not collections:
        print("（目前沒有收藏紀錄）")
    for c in collections:
        print(f"id={c.id}  user_id={c.user_id}  prize_name={c.prize_name}  rarity={c.prize_rarity}")