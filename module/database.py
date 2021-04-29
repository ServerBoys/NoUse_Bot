import aiosqlite
class Database:
    def __init__(self, db_path):
        self.db_path = db_path
        self.db = aiosqlite.connect(db_path)
        self.cursor = None
    async def open(self):
        self.cursor = await self.db.cursor()