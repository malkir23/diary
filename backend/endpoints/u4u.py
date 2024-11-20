from fastapi import APIRouter


router = APIRouter()

@router.get("/api/data")
async def get_data():
    return {"message": "Hello from FastAPI", "data": [1, 2, 3, 4]}
