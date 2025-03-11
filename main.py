from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import controller

app = FastAPI()

# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://newscreens.d1svubromz6zbm.amplifyapp.com/"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(controller.router)
