from fastapi import APIRouter

router = APIRouter()

@router.get("/leaderboard")
async def get_leaderboard():
    return {"message": "Get leaderboard - TODO"}

@router.get("/homework")
async def get_available_homework():
    return {"message": "Get available homework - TODO"}

@router.post("/homework/{homework_id}/submit")
async def submit_homework(homework_id: int):
    return {"message": f"Submit homework {homework_id} - TODO"}

@router.get("/submissions")
async def get_submissions():
    return {"message": "Get submissions - TODO"}