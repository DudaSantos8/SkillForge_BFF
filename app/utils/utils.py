import re
import json

import re

def parse_feedback_response(api_response):

    feedback = {
        "areas_para_melhorar": [],
        "recomendacoes": [],
        "motivacao": ""
    }

    if not api_response.get("steps"):
        return feedback

    # Extrai o texto da resposta dentro de "steps[0]['step_result']['answer']"
    raw_text = api_response["steps"][0]["step_result"]["answer"]

    # Divide o texto em linhas
    lines = raw_text.split("\n")

    # Variáveis auxiliares
    current_section = None

    for line in lines:
        line = line.strip()

        # Detecta se é uma área para melhorar (numeradas)
        match_melhoria = re.match(r"\d+\.\s\*\*(.+?)\*\*", line)
        if match_melhoria:
            feedback["areas_para_melhorar"].append(match_melhoria.group(1).strip())
            current_section = "areas_para_melhorar"
            continue

        # Detecta se é uma recomendação (começa com número ou marcador "- **")
        match_recommendation = re.match(r"-\s\*\*(.+?)\*\*", line)
        if match_recommendation:
            feedback["recomendacoes"].append(match_recommendation.group(1).strip())
            current_section = "recomendacoes"
            continue

        # Detecta a motivação (após "Lembre-se de que a empatia...")
        if "Lembre-se de que a empatia" in line or "Você já está no caminho certo" in line:
            feedback["motivacao"] += line + " "
            current_section = "motivacao"
            continue

        # Se continuar na mesma seção, concatena o texto
        if current_section and line:
            feedback[current_section][-1] += " " + line

    return feedback

def parse_questions(raw_text):
    """
    Extrai perguntas, opções e respostas corretas do texto formatado da API.
    """
    questions = []
    question_blocks = raw_text.split("\n\n")

    for block in question_blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue

        # Identifica a pergunta e as opções
        question_match = re.match(r"\d+\.\s\*\*(.+?)\*\*", lines[0])
        if not question_match:
            continue

        question_text = question_match.group(1).strip()
        options = []
        correct_answer_index = None

        for line in lines[1:]:
            option_match = re.match(r"([a-d])\)\s(.+)", line.strip())
            if option_match:
                options.append(option_match.group(2).strip())

            if "**Resposta correta:**" in line:
                correct_option = re.search(r"\*\*Resposta correta:\*\*\s([a-d])\)", line)
                if correct_option:
                    correct_answer_index = ["a", "b", "c", "d"].index(correct_option.group(1))

        if question_text and options and correct_answer_index is not None:
            questions.append({
                "question": question_text,
                "options": options,
                "correct_answer": correct_answer_index
            })

    return questions
