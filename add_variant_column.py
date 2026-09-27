from app import app, db
from sqlalchemy import text

with app.app_context():
    db.session.execute(text("ALTER TABLE collection ADD COLUMN variant_index INTEGER"))
    db.session.commit()
    print("variant_index 欄位已新增")