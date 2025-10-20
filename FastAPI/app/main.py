from fastapi import FastAPI
import uvicorn
from routers import items

app = FastAPI(
    title="My FastAPI APP",
    description="My first APP!",
    version="1.0.0"
)

app.include_router(items.router)

@app.get("/")
async def root():
    return {
        "message":"FastAPI 서버가 정상적으로 실행 중입니다."
    }

@app.get("/health")
async def health_check():
    return {"status":"healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8012,
        reload=True
    )