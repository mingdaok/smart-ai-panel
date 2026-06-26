from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AI Panel Studio", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from backend.routes.rooms import router as rooms_router
from backend.routes.experts import router as experts_router

app.include_router(rooms_router)
app.include_router(experts_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
