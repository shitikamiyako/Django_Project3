from django import forms


class SearchForm(forms.Form):
    category_list = forms.ChoiceField(
        label='カテゴリ',
        widget=forms.widgets.Select
    )
    query = forms.CharField(
        initial='',
        label='クエリ',
        required=False,
    )
