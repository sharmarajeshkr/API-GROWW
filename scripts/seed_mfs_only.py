import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.database import engine, Base, AsyncSessionLocal
from core.models import MFCategory, MutualFund
from services.mf_scraper import get_sector_mfs
from core.logger import get_logger
from sqlalchemy.future import select

logger = get_logger("seed_mfs_only")

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
            try:
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
            except Exception as e:
                await session.rollback()
                logger.error(f"Failed to commit {cat_name}: {e}")

if __name__ == "__main__":
    asyncio.run(seed_mutual_funds())
