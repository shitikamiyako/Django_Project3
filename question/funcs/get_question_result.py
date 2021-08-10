from typing import Dict, List, Tuple

from django.db.models import QuerySet

from ..models import QuestionResult
from accounts.models import CustomUser

RISK_THRESHOLD: List[int] = [100, 200]  # L-M: 100, M-H: 200
TERM_THRESHOLD: List[int] = [100, 200]  # S-M: 100, M-H: 200
RISK_CLASS_MAPPING: Dict[int, str] = {0: "低め", 1: "そこそこ", 2: "高い"}
RISK_CLASS_SHORT_MAPPING: Dict[int, str] = {0: "L", 1: "M", 2: "H"}
TERM_CLASS_MAPPING: Dict[int, str] = {0: "短め", 1: "そこそこ", 2: "長め"}
TERM_CLASS_SHORT_MAPPING: Dict[int, str] = {0: "S", 1: "M", 2: "L"}


def fetch_stored_data(username: str):
    """Fetch QuestionResult Stored by Question Form."""
    user_obj = CustomUser.objects.get(username=username)
    result_query_set: QuerySet = QuestionResult.objects.filter(
        customuser_obj=user_obj)
    # Django orderby descending: https://qiita.com/Hyperion13fleet/items/1a0369f4f5d523be5870
    latest_result = result_query_set.order_by("datetime").reverse().first()

    return {"risk": latest_result.risk_score, "term": latest_result.term_score}


def get_classification_from_score(score: Dict[str, int]) -> Tuple[Tuple[str, str], Tuple[str, str]]:
    """Get classification from score dict.

    return mapping from score dict."""
    risk_score: int = score["risk"]
    term_score: int = score["term"]

    risk_flag: List[bool] = [risk_score > t for t in RISK_THRESHOLD]
    term_flag: List[bool] = [term_score > t for t in TERM_THRESHOLD]

    risk_index: int = sum(risk_flag)
    risk_result: Tuple[str, str] = (
        RISK_CLASS_SHORT_MAPPING[risk_index],
        RISK_CLASS_MAPPING[risk_index]
    )

    term_index: int = sum(term_flag)
    term_result: Tuple[str, str] = (
        TERM_CLASS_SHORT_MAPPING[term_index],
        TERM_CLASS_MAPPING[term_index]
    )

    return risk_result, term_result


def get_class_img_from_classification(risk_class: Tuple[str, str], term_class: Tuple[str, str]) -> str:
    """Get classification image name from classification"""
    return risk_class[0] + term_class[0]
