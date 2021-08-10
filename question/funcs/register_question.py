import logging
from typing import List

from accounts.models import CustomUser
from ..models import Question, QuestionAnswer, QuestionResult
from question.funcs.show_question import make_answer_list
from django.utils.datastructures import MultiValueDictKeyError

logger = logging.getLogger(__name__)


def parse_payload(payload: dict):
    """Parse payload and return answer_list."""
    question_list: list = Question.objects.all()

    result = []

    for q in question_list:
        question_num = str(q.id)
        try:
            obj = payload[question_num]
            result.append(obj)
        except (KeyError, MultiValueDictKeyError):
            result.append(None)

    return result


def make_correspond_choices():
    """Create corresponding list with choices."""
    choice_data = QuestionAnswer.objects.all()
    corresponding_choices = make_answer_list(choice_data)

    return corresponding_choices


def calc_scores(payload_parsed: List[str]) -> dict:
    """get payload and create score dict."""
    choice_base = make_correspond_choices()

    risk: int = 0
    term: int = 0

    # choice_base<Choice corresponding scores>/ parsed_payload<answer user entered>
    for choice_score, user_answer in zip(choice_base, payload_parsed):
        if user_answer is None:
            continue
        q_id = int(user_answer) - 1
        risk += choice_score[q_id].risk
        term += choice_score[q_id].term

    calc_result: dict = {'risk': risk, 'term': term}

    return calc_result


def register_score(user_info: str, score: dict):
    """Register quesitonary results to DB.

    Userinfo will be user_id"""
    user_obj = CustomUser.objects.get(username=user_info)
    logging.info(user_obj)
    data_to_update = QuestionResult(  # datetime should be used as default one.
        customuser_obj=user_obj,
        risk_score=score["risk"],
        term_score=score["term"],
    )

    data_to_update.save()

    return data_to_update.id
