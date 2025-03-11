import re
import json

def extract_question_data(lines):
    """
    Função auxiliar que extrai dados da pergunta, opções e resposta correta de um bloco de texto.
    """
    question_match = re.match(r"\d+\.\s\*\*(.+?)\*\*", lines[0])
    if not question_match:
        return None

    question_text = question_match.group(1).strip()
    options = []
    correct_answer_index = None

    for line in lines[1:]:
        option_match = re.match(r"([a-d])\)\s(.+)", line.strip())
        if option_match:
            options.append(option_match.group(2).strip())

        correct_option_match = re.search(r"\*\*Resposta correta:\*\*\s([a-d])\)", line)
        if correct_option_match:
            correct_answer_index = ["a", "b", "c", "d"].index(correct_option_match.group(1))

    if question_text and options and correct_answer_index is not None:
        return {
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer_index
        }
    return None


def parse_feedback_response(raw_text: str):
    try:
        response_data = json.loads(raw_text)
    except json.JSONDecodeError as e:
        return {"error": f"Invalid JSON format: {e}"}


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

        question_data = extract_question_data(lines)
        if question_data:
            questions.append(question_data)

    return questions


def parse_questions_hardskills(raw_text):
    """
    Extrai perguntas, opções e respostas corretas do texto formatado da API no formato específico.
    """
    data = json.loads(raw_text)
    answer_text = data['steps'][0]['step_result']['answer']

    questions = []
    question_blocks = answer_text.split("\n\n")

    for block in question_blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue

        question_data = extract_question_data(lines)
        if question_data:
            questions.append(question_data)

    return questions
