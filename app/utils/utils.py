import re
import json

def parse_feedback_response(raw_text: str):
    """
    Processa a resposta bruta do feedback e retorna um dicionário estruturado.
    Agora lida com o formato JSON e extraí as informações necessárias.
    """
    # Converte a string JSON para um dicionário Python
    try:
        response_data = json.loads(raw_text)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}
    
    # Extrai a resposta do feedback da estrutura JSON
    feedback_text = ""
    for step in response_data.get("steps", []):
        if step.get("step_name") == "feedback":
            feedback_text = step["step_result"].get("answer", "")
            break
    
    # Extrai a pontuação e o título usando regex
    score_match = re.search(r"(\d+)\s*em\s*uma\s*escala.*?\"(.*?)\".*", feedback_text)
    score = int(score_match.group(1)) if score_match else None
    title = score_match.group(2) if score_match else ""
    
    # Remove a parte inicial do texto (Pontuação e título)
    processed_text = feedback_text.replace(f"Com base na pontuação de {score} em uma escala", "") if score else feedback_text
    
    # Separa as seções por parágrafos
    paragraphs = [p.strip() for p in processed_text.split(".") if p.strip()]
    
    return {
        "score": score,
        "title": title,
        "feedback_summary": paragraphs[0] if paragraphs else "",
        "detailed_feedback": paragraphs[1:] if len(paragraphs) > 1 else []
    }


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
