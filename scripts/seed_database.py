import asyncio
import sys
import os
from sqlalchemy.future import select

# Appending root directory to path to import core/services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import engine, Base, AsyncSessionLocal
from core.models import Sector, Stock, MFCategory, MutualFund
from services.stock_scraper import get_all_sectors, get_sector_stocks
from services.mf_scraper import get_sector_mfs
from core.logger import get_logger

logger = get_logger("seed_database")

async def init_db():
    async with engine.begin() as conn:
        logger.info("Dropping existing tables to start fresh...")
        await conn.run_sync(Base.metadata.drop_all)
        logger.info("Creating normalized tables in Database...")
        await conn.run_sync(Base.metadata.create_all)
        
async def seed_stocks_and_sectors():
    logger.info("--- Beginning Stock Seeding ---")
    sectors = await get_all_sectors()
    
    async with AsyncSessionLocal() as session:
        for sector_name in sectors:
            logger.info(f"Processing Sector: {sector_name}")
            
            # 1. Upsert Sector
            stmt = select(Sector).where(Sector.name == sector_name)
            result = await session.execute(stmt)
            sector_obj = result.scalars().first()
            
            if not sector_obj:
                sector_obj = Sector(name=sector_name)
                session.add(sector_obj)
                await session.flush() # flush to get the sector_obj.id generated
                
            # 2. Get Stocks for Sector
            stocks = await get_sector_stocks(sector_name)
            
            # 3. Batch Insert Stocks
            for stock_data in stocks:
                symbol = stock_data.get('searchId')
                if not symbol: continue
                
                # Check if stock exists
                stmt_stock = select(Stock).where(Stock.symbol == symbol)
                res_stock = await session.execute(stmt_stock)
                existing_stock = res_stock.scalars().first()
                
                if not existing_stock:
                    new_stock = Stock(
                        symbol=symbol,
                        company_name=stock_data.get('companyName', symbol),
                        sector_id=sector_obj.id,
                        close_price=stock_data.get('closePrice'),
                        market_cap=stock_data.get('marketCap')
                    )
                    session.add(new_stock)
                else:
                    existing_stock.close_price = stock_data.get('closePrice')
                    existing_stock.market_cap = stock_data.get('marketCap')
                    
            await session.commit()
            logger.info(f"Committed {len(stocks)} stocks for {sector_name}")

async def seed_mutual_funds():
    logger.info("--- Beginning Mutual Fund Seeding ---")
    categories = ["Equity", "Debt", "Hybrid", "Index Funds"]
    
    async with AsyncSessionLocal() as session:
        for cat_name in categories:
            logger.info(f"Processing Category: {cat_name}")
            
            # 1. Upsert Category
            stmt = select(MFCategory).where(MFCategory.name == cat_name)
            result = await session.execute(stmt)
            cat_obj = result.scalars().first()
            
            if not cat_obj:
                cat_obj = MFCategory(name=cat_name)
                session.add(cat_obj)
                await session.flush()
                
            # 2. Get MFs
            mfs = await get_sector_mfs(cat_name)
                
            # 3. Batch Insert
            for mf_data in mfs:
                search_id = mf_data.get('search_id')
                if not search_id: continue
                
                stmt_mf = select(MutualFund).where(MutualFund.search_id == search_id)
                res_mf = await session.execute(stmt_mf)
                existing = res_mf.scalars().first()
                
                if not existing:
                    new_mf = MutualFund(
                        search_id=search_id,
                        scheme_name=mf_data.get('schemeName', search_id),
                        category_id=cat_obj.id,
                        return_3y=mf_data.get('return3y'),
                        return_5y=mf_data.get('return5y')
                    )
                    session.add(new_mf)
                else:
                    existing.return_3y = mf_data.get('return3y')
                    existing.return_5y = mf_data.get('return5y')
                    
            await session.commit()
            logger.info(f"Committed {len(mfs)} Mutual funds for {cat_name}")

async def main():
    await init_db()
    await seed_stocks_and_sectors()
    await seed_mutual_funds()
    logger.info("DATABASE SEEDING COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(main())
