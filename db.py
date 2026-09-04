import aiosqlite

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        print(f"db_path:{self.db_path} conn: {self.conn}")
        self.conn.row_factory = aiosqlite.Row

    async def add_user_city(self, user_id: int, city: str):
        await self.conn.execute(
            "INSERT OR REPLACE INTO params (user_id, city) VALUES (?,?)",
            (user_id, city)
        )
        await self.conn.commit()
    
    async def get_user_city(self, user_id: int):
        async with self.conn.execute(
            "SELECT city FROM params WHERE user_id = ?", (user_id,)
        ) as cursor:
        
            row = await cursor.fetchone()
            if row:
                return row["city"]

            return None

        return city
    
    async def close(self):
        if self.conn:
            await self.conn.close()

db = Database("weather_db.db")