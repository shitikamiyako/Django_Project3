from typing import Dict, Optional, List
from ..models import Question, QuestionAnswer


def get_question_obj():
    """Get Question All object."""
    question_text = Question.objects.all()

    return question_text


def get_answer_list():
    answer_query_set = QuestionAnswer.objects.all()

    return answer_query_set


def make_answer_list(answer_obj):
    """Make Answer list for Each Question.

    Make Choices for each question. defining by question_obj_id."""
    # result is dict and the key is question id and values is list which contains choices
    result: Dict[int, Optional(List[QuestionAnswer])] = {}

    for ans_single in answer_obj:
        key_num: int = ans_single.question_obj_id
        if result.get(key_num, None) is None:
            result[key_num] = []
            result[key_num].append(ans_single)
        else:
            result[key_num].append(ans_single)

    question_id_list = sorted(result.keys())

    result_listed = [result[q_id] for q_id in question_id_list]

    return result_listed
