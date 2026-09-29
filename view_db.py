from app import app, db, User, Prize, Collection

with app.app_context():
    print("========== ユーザー ==========")
    users = User.query.all()
    if not users:
        print("（現在ユーザーはいません）")
    for u in users:
        print(f"id={u.id}  username={u.username}")

    print("\n========== 景品在庫 ==========")
    prizes = Prize.query.all()
    if not prizes:
        print("（現在景品データはありません）")
    for p in prizes:
        print(f"id={p.id}  name={p.name}  rarity={p.rarity}  stock={p.stock}")

    print("\n========== コレクション履歴 ==========")
    collections = Collection.query.all()
    if not collections:
        print("（現在コレクション履歴はありません）")
    for c in collections:
        print(f"id={c.id}  user_id={c.user_id}  prize_name={c.prize_name}  rarity={c.prize_rarity}")