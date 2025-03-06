import re

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


def parse_feedback_response(response):
    """
    Função para formatar a resposta da API de feedback de forma adequada para o frontend.

    Args:
        response (dict): Resposta da API contendo o feedback.

    Returns:
        dict: Dados formatados para o frontend.
    """
    # Extrair dados relevantes da resposta
    execution_id = response.get("execution_id", "")
    conversation_id = response.get("conversation_id", "")
    progress = response.get("progress", {})
    steps = response.get("steps", [])
    
    # Processar a pontuação e feedback
    feedback = ""
    if steps:
        feedback_step = next((step for step in steps if step.get("step_name") == "feedback"), {})
        step_result = feedback_step.get("step_result", {})
        feedback = step_result.get("answer", "")

    # Extração do tempo de execução
    start_time = progress.get("start", "")
    end_time = progress.get("end", "")
    duration = progress.get("duration", 0)

    # Construção do formato de resposta para o frontend
    formatted_feedback = {
        "execution_id": execution_id,
        "conversation_id": conversation_id,
        "feedback": feedback,
        "start_time": start_time,
        "end_time": end_time,
        "duration": duration,
        "execution_percentage": progress.get("execution_percentage", 0),
        "status": progress.get("status", ""),
    }
    
    return formatted_feedback
