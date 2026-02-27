# Groww Data API Architecture

The application is structured as a modernized Fast-API application combining static data scraping with dynamic SDK quote retrieval. 

## High Level System Architecture

```mermaid
graph TD
    Client((Client App / Swagger UI)) -->|HTTP Requests| FastAPI[FastAPI App api.py]
    
    FastAPI -->|/api/stocks| StocksRouter[Stocks Router]
    FastAPI -->|/api/mutual-funds| MFRouter[Mutual Funds Router]
    
    subgraph "API Routing Layer (Controllers)"
        StocksRouter
        MFRouter
    end

    subgraph "Core Components"
        Schemas(Pydantic Schemas schemas.py)
        Logger(Centralized Logger logger.py)
    end
    
    StocksRouter --> Schemas
    MFRouter --> Schemas
    FastAPI --> Logger
    
    subgraph "Service Layer"
        StockScraper[Stock Data Fetcher]
        MFScraper[Mutual Fund Fetcher]
        GrowwAuth[Groww SDK Auth Dependency]
    end
    
    StocksRouter -->|Request Quotes| GrowwAuth
    StocksRouter -->|Async Sector Query| StockScraper
    MFRouter -->|Async Category Query| MFScraper
    
    subgraph "External Providers"
        SDK((Groww Official SDK))
        GrowwWeb((Groww Web Backend / SSR State))
    end
    
    StockScraper -->|httpx async GET / __NEXT_DATA__| GrowwWeb
    MFScraper -->|httpx async GET /v1/api/search| GrowwWeb
    GrowwAuth -->|gRPC / WebSockets| SDK
```

## Data Flow for Rich Quotes

Because official APIs only provide shallow data (like `live_quote`), the system unifies data from two sources on individual ID queries:

```mermaid
sequenceDiagram
    participant Client
    participant API as Stocks Router
    participant SDK as Groww SDK dependency
    participant Web as Groww.in React Scraper
    
    Client->>API: GET /api/stocks/RELIANCE
    
    par Live Tracking (Sync)
        API->>SDK: get_quote('RELIANCE')
        SDK-->>API: returns {day_change, ohlc, depth}
    and Deep State Scrape (Async httpx)
        API->>Web: GET https://groww.in/stocks/reliance-industries-ltd
        Web-->>API: returns HTML
        API->>API: BeautifulSoup extract id=__NEXT_DATA__
        API->>API: Parse JSON for 'fundamentals', 'financials'
    end
    
    API->>Client: Return Unified Response (Pydantic StockDetailResponse)
```
