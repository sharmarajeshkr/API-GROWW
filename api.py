from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from stocks.router import router as stocks_router
from mutual_funds.router import router as mf_router
from logger import get_logger

logger = get_logger("groww_api")
logger.info("Initializing Groww Data API Application")

app = FastAPI(title="Groww Data API", description="Modular API to fetch Stock and Mutual Fund details from Groww")

# Include specialized routers
app.include_router(stocks_router)
app.include_router(mf_router)

@app.get("/")
def home():
    logger.info("Redirecting home to Swagger UI docs")
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
