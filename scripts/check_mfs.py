import asyncio
import os
import sys

# Append root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

load_dotenv()

async def check():
    engine = create_async_engine(os.environ.get('DATABASE_URL'))
    async with engine.connect() as conn:
        res1 = await conn.execute(text('SELECT COUNT(*) FROM mf_categories'))
        res2 = await conn.execute(text('SELECT COUNT(*) FROM mutual_funds'))
        print(f"Categories Count: {res1.scalar()}")
        print(f"Funds Count: {res2.scalar()}")

if __name__ == "__main__":
    asyncio.run(check())
