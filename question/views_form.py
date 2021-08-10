import logging

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from .funcs import show_question, register_question

logger = logging.getLogger(__name__)

ANONYMOUS_USER_NAME = "temp"


class Question(View):
    """https://stackoverflow.com/questions/17159567/how-to-create-a-list-of-fields-in-django-forms"""

    def get(self, request, *args, **kwargs):
        """Get questionary form."""
        question_text_obj = show_question.get_question_obj()
        answer_choice_obj = show_question.get_answer_list()
        answer_list = show_question.make_answer_list(answer_choice_obj)

        context = {
            "question_list": question_text_obj,
            "answer_list": answer_list
        }
        return render(request, 'question/question_form.html', context)

    def post(self, request, *args, **kwargs):
        """POST from form."""
        payload = request.POST
        session = request.session

        logger.info(payload)

        payload_parsed = register_question.parse_payload(payload)
        score = register_question.calc_scores(payload_parsed)

        # Viewに直接関連するUser/Session InfoはViewで処理する。
        request.session['answer'] = payload_parsed
        if request.user.is_authenticated:
            request.session['unsaved_answer'] = False
            user_name = request.user.username
            request.session['score'] = score
            request.session["primary_key"] = register_question.register_score(
                user_name, score)
        else:  # user is not authenticated, then we save session id instead of user id.
            user_name = ANONYMOUS_USER_NAME
            request.session['unsaved_answer'] = True
            # Because CustomUser obj in QuestionResult OBJ is forign key, so we have to retry by Session.
            request.session['score'] = score
            request.session["primary_key"] = register_question.register_score(
                ANONYMOUS_USER_NAME, score)

        question_result_url = reverse('question:result')

        logger.info(session["unsaved_answer"])
        logger.info(session["primary_key"])
        logger.info(session["score"])
        logger.info(session["answer"])

        return redirect(question_result_url)


question = Question.as_view()
