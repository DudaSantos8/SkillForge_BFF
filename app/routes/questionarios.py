from fastapi import FastAPI, APIRouter, Query, HTTPException
from mangum import Mangum
from app.services.api_service import (
    create_execution,
    wait_for_execution_to_complete,
    create_execution_cleancode,
    wait_for_execution_to_complete_cleancode
)
from app.utils.utils import parse_questions

app = FastAPI()
router = APIRouter()

@router.get("/softskills/questions")
def get_softskills_questions(title: str = Query(...)):
    input_data = {"input_data": title}
    try:
        execution_id = create_execution(input_data)
        result = wait_for_execution_to_complete(execution_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"Erro ao processar a execução: {e.detail}")
    
    steps = result.get("steps", [])
    raw_text = next((step.get("step_result", {}).get("answer", "") for step in steps if step.get("step_name") == "questionario"), "")
    
    if not raw_text:
        raise HTTPException(status_code=500, detail="Não foi possível obter perguntas.")

    formatted_questions = parse_questions(raw_text)
    return {"questions": formatted_questions}

@router.get("/hardskills/questions")
def get_hardskills_questions(title: str = Query(...)):
    input_data = {"input_data": title}
    try:
        execution_id = create_execution_cleancode(input_data)
        result = wait_for_execution_to_complete_cleancode(execution_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"Erro ao processar a execução: {e.detail}")
    
    steps = result.get("steps", [])
    raw_text = next((step.get("step_result", {}).get("answer", "") for step in steps if step.get("step_name") == "questionario"), "")
    
    if not raw_text:
        raise HTTPException(status_code=500, detail="Não foi possível obter perguntas.")

    formatted_questions = parse_questions(raw_text)
    return {"questions": formatted_questions}

app.include_router(router)

# Handler para AWS Lambda
handler = Mangum(app)
