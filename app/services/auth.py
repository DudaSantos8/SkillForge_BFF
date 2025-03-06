import subprocess
from app.config.config import TOKEN_FILE

def get_token():
    """Lê o token salvo no arquivo. Se não existir, executa o script Bash para gerar um novo."""
    try:
        with open(TOKEN_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return refresh_token()

def refresh_token():
    """Executa o script Bash para obter um novo token e lê o resultado."""
    print("🔄 Token expirado! Renovando...")
    subprocess.run(['/bin/bash', './scripts/get_token.sh'], check=True)
    return get_token()
