from typing import Dict
import logging

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from .funcs import get_question_result

logger = logging.getLogger(__name__)


class QuestionResult(View):

    def get(self, request, *args, **kwargs):
        """Get METHOD, will get user's data."""
        # Check auth status
        if request.user.is_authenticated:
            username = request.user.username
        else:
            username = None

        score = None

        # Check session status
        score_from_session = request.session.get('score')

        if score_from_session:  # if we have session data, user has latest data for session.
            score = score_from_session
        else:
            if username:  # logged in so we have to fetch from db.  prefer session because already stored in browser.
                score = get_question_result.fetch_stored_data(username)
            else:  # Not logged in and do not have any session data.
                return redirect(reverse("question:form"))

        risk_class, term_class = get_question_result.get_classification_from_score(
            score)
        img_pos = get_question_result.get_class_img_from_classification(
            risk_class, term_class)

        context: Dict[str, str] = {
            'risk_class': risk_class[1],
            'term_class': term_class[1],
            'img_pos': img_pos,  # just concat str like HH.png
        }
        return render(request, "question/question_result.html", context=context)


question_result = QuestionResult.as_view()
