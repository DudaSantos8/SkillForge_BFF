import os

# Caminho do arquivo de token
TOKEN_FILE = "./scripts/token.txt"  # Atualizado para o novo caminho

# URLs da API externa
CREATE_EXECUTION_URL = "https://genai-code-buddy-api.stackspot.com/v1/quick-commands/create-execution/diversidade-e-inclusao"
CALLBACK_URL_TEMPLATE = "https://genai-code-buddy-api.stackspot.com/v1/quick-commands/callback/{execution_id}"

CREATE_EXECUTION_URL_CLEANCODE = "https://genai-code-buddy-api.stackspot.com/v1/quick-commands/create-execution/cleancode"
