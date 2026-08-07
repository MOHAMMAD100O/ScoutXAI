import sqlite3
from datetime import datetime


class WalletMemory:

    def __init__(self):
        self.db="app/database/scoutxai.db"
        self.init_db()


    def init_db(self):

        con=sqlite3.connect(self.db)

        cur=con.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS whale_wallets(
            wallet TEXT,
            volume REAL,
            buys INTEGER,
            sells INTEGER,
            created TEXT
        )
        """)

        con.commit()
        con.close()


    def save(self,data):

        con=sqlite3.connect(self.db)

        cur=con.cursor()

        cur.execute(
        """
        INSERT INTO whale_wallets
        VALUES(?,?,?,?,?)
        """,
        (
            data.get("wallet"),
            data.get("volume",0),
            data.get("buys",0),
            data.get("sells",0),
            datetime.utcnow().isoformat()
        ))

        con.commit()
        con.close()


wallet_memory=WalletMemory()
