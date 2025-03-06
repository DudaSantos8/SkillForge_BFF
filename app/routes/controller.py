from fastapi import FastAPI, APIRouter, Query, HTTPException
from mangum import Mangum
from app.services.api_service import (
    create_execution_softskill,
    create_execution_hardskill,
    create_execution_feedback,
    wait_for_execution_to_complete_softskill,
    wait_for_execution_to_complete_hardskill,
    wait_for_execution_to_complete_feedback,
    get_callback
)
from app.utils.utils import parse_questions, parse_feedback_response

app = FastAPI()
router = APIRouter()

@router.get("/softskills/questions")
def get_softskills_questions(title: str = Query(...)):
    input_data = {"input_data": title}
    try:
        execution_id = create_execution_softskill(input_data)
        result = wait_for_execution_to_complete_softskill(execution_id)
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
        execution_id = create_execution_hardskill(input_data)
        result = wait_for_execution_to_complete_hardskill(execution_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"Erro ao processar a execução: {e.detail}")
    
    steps = result.get("steps", [])
    raw_text = next((step.get("step_result", {}).get("answer", "") for step in steps if step.get("step_name") == "questionario"), "")
    
    if not raw_text:
        raise HTTPException(status_code=500, detail="Não foi possível obter perguntas.")

    formatted_questions = parse_questions(raw_text)
    return {"questions": formatted_questions}


@router.get("/feedback")
def get_newskills_feedback(score: int = Query(..., ge=0, le=8), title: str = Query(...)):
    # O input_data agora é composto pela pontuação (score) e pelo título
    input_data = {"input_data": f"pontuação {score}, {title}"}
    try:
        execution_id = create_execution_feedback(input_data)  # Usando a nova função de criação
        result = wait_for_execution_to_complete_feedback(execution_id)  # Aguardar a execução
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"Erro ao processar a execução: {e.detail}")
    
    # Obter a resposta da execução
    steps = result.get("steps", [])
    raw_text = next((step.get("step_result", {}).get("answer", "") for step in steps if step.get("step_name") == "feedback"), "")
    
    if not raw_text:
        raise HTTPException(status_code=500, detail="Não foi possível obter o feedback.")

    # Processar o feedback com a função de utilitário
    formatted_feedback = parse_feedback_response(raw_text)

    # Retornar o feedback formatado
    return {"feedback": formatted_feedback}

handler = Mangum(app)
