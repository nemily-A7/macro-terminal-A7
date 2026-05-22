from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.zones import router as zones_router
from backend.routes.calendar import router as calendar_router
from backend.routes.ws import router as ws_router
from backend.routes.markets import router as markets_router
from backend.routes.narrative import router as narrative_router
from backend.routes.insight import router as insight_router

app = FastAPI(title="Macro Terminal API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zones_router, prefix="/api")
app.include_router(calendar_router, prefix="/api")
app.include_router(markets_router, prefix="/api")
app.include_router(narrative_router, prefix="/api")
app.include_router(insight_router, prefix="/api")
app.include_router(ws_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
