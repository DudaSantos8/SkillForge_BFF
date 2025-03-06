from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import questionarios

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (pode ser ajustado conforme necessário)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui as rotas da aplicação
app.include_router(questionarios.router)
