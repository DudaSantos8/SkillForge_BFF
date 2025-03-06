import re
import json

def parse_feedback_response(raw_text):
    try:
        response = json.loads(raw_text)
    except json.JSONDecodeError:
        print("Erro ao decodificar JSON:", raw_text)
        return {}

    return response.get("execution_id", "")


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
