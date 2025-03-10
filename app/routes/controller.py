from fastapi import FastAPI, APIRouter, Query, HTTPException
from mangum import Mangum
from pydantic import BaseModel, EmailStr

import httpx    

from app.services.api_service import (
    create_execution_softskill,
    create_execution_hardskill,
    create_execution_feedback,
    wait_for_execution_to_complete_softskill,
    wait_for_execution_to_complete_hardskill,
    wait_for_execution_to_complete_feedback,
)
from app.utils.utils import parse_questions, parse_feedback_response

app = FastAPI()
router = APIRouter()

API_JAVA_URL = "http://56.124.88.224:8080/"  # URL da API Java

# Definindo um modelo de dados para o usuário
class UserCreate(BaseModel):
    email: str
    password: str
    confirmPassword: str
# 🔹 Rota para criar um usuário
# 🔹 Rota para criar um usuário
@router.post("/users")
async def create_user(user_data: UserCreate):
    # Verifica se a senha e a confirmação são iguais
    if user_data.password != user_data.confirmPassword:
        raise HTTPException(status_code=400, detail="Senha e confirmação não coincidem.")
    
    # Log para conferir os dados antes de enviar para a API Java
    print("Dados enviados para a API Java:", user_data.dict())
    
    # Envia os dados para a API Java
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{API_JAVA_URL}/users", json=user_data.dict())
        
        # Verifica a resposta da API Java
        if response.status_code == 400:
            error_message = response.json().get("message", "Erro ao criar o usuário.")
            raise HTTPException(status_code=400, detail=error_message)
        
        return response.json()  # Retorna a resposta da API Java

# 🔹 Rota para atualizar um usuário
@router.put("/users/{user_id}")
async def update_user(user_id: int, user_data: dict):
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{API_JAVA_URL}/users/{user_id}", json=user_data)
        
        if response.status_code == 200:
            return response.json()  # Retorna os dados atualizados
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        else:
            error_message = response.json().get("message", "Erro ao atualizar o usuário.")
            raise HTTPException(status_code=response.status_code, detail=error_message)

# 🔹 Rota para deletar um usuário
@router.delete("/users/{user_id}")
async def delete_user(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{API_JAVA_URL}/users/{user_id}")
        
        if response.status_code == 204:
            return {"message": "Usuário deletado com sucesso"}
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        else:
            error_message = response.json().get("message", "Erro ao deletar o usuário.")
            raise HTTPException(status_code=response.status_code, detail=error_message)


# 🔹 Rota para obter perguntas de soft skills
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

# 🔹 Rota para obter perguntas de hard skills
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

# 🔹 Rota para obter feedback
@router.get("/feedback")
def get_feedback(score: int = Query(..., ge=0, le=8), title: str = Query(...)):
    input_data = {"input_data": f"{score}, {title}"}
    try:
        execution_id = create_execution_feedback(input_data)
        result = wait_for_execution_to_complete_feedback(execution_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=f"Erro ao processar a execução: {e.detail}")
    
    steps = result.get("steps", [])
    raw_text = next((step.get("step_result", {}).get("answer", "") for step in steps if step.get("step_name") == "feedback"), "")
    
    if not raw_text:
        raise HTTPException(status_code=500, detail="Não foi possível obter o feedback.")

    formatted_feedback = parse_feedback_response(raw_text)

    return {"feedback": formatted_feedback}

# ✅ Registrar o router no app
app.include_router(router)

# ✅ Suporte para AWS Lambda
handler = Mangum(app)
