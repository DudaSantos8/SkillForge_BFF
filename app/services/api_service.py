import time
import requests
from fastapi import HTTPException
from app.services.auth import get_token, refresh_token
from app.config.config import CREATE_EXECUTION_URL, CALLBACK_URL_TEMPLATE, CREATE_EXECUTION_URL_CLEANCODE

# Função genérica para criar execução
def create_execution_helper(url, input_data):
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers, json=input_data)
    if response.status_code == 200:
        return response.text.strip()
    elif response.status_code == 403:
        token = refresh_token()
        headers["Authorization"] = f"Bearer {token}"
        response = requests.post(url, headers=headers, json=input_data)
        if response.status_code == 200:
            return response.text.strip()
    
    raise HTTPException(status_code=response.status_code, detail=f"Erro ao criar execução: {response.text}")

# Função genérica para obter callback
def get_callback_helper(url, execution_id):
    url = url.format(execution_id=execution_id.strip('"'))
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 403:
        token = refresh_token()
        headers["Authorization"] = f"Bearer {token}"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
    
    raise HTTPException(status_code=response.status_code, detail=f"Erro ao obter callback: {response.text}")

# Função genérica para esperar a execução completar
def wait_for_execution_to_complete_helper(url, execution_id, delay=15, max_retries=10):
    retries = 0
    while retries < max_retries:
        result = get_callback_helper(url, execution_id)
        if not result:
            raise HTTPException(status_code=500, detail="Erro ao obter o resultado da execução.")
        
        progress = result.get('progress', {})
        execution_percentage = progress.get('execution_percentage')
        
        if execution_percentage == 1.0:
            return result
        
        time.sleep(delay)
        retries += 1
    
    raise HTTPException(status_code=500, detail="Número máximo de tentativas atingido.")

#--------------------------- CLEAN CODE -----------------------------------
def create_execution_cleancode(input_data):
    return create_execution_helper(CREATE_EXECUTION_URL_CLEANCODE, input_data)

def get_callback_cleancode(execution_id):
    return get_callback_helper(CALLBACK_URL_TEMPLATE, execution_id)

def wait_for_execution_to_complete_cleancode(execution_id, delay=15, max_retries=10):
    return wait_for_execution_to_complete_helper(CALLBACK_URL_TEMPLATE, execution_id, delay, max_retries)

#--------------------------- EXECUÇÃO NORMAL ----------------------------

def create_execution(input_data):
    return create_execution_helper(CREATE_EXECUTION_URL, input_data)

def get_callback(execution_id):
    return get_callback_helper(CALLBACK_URL_TEMPLATE, execution_id)

def wait_for_execution_to_complete(execution_id, delay=15, max_retries=10):
    return wait_for_execution_to_complete_helper(CALLBACK_URL_TEMPLATE, execution_id, delay, max_retries)
