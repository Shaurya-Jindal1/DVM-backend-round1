from django import forms


class PollForm(forms.Form):
    question_text = forms.CharField(label='Question', max_length=200)
    # first 2 choices are required, rest are optional
    choice1 = forms.CharField(label='Choice 1', max_length=200)
    choice2 = forms.CharField(label='Choice 2', max_length=200)
    choice3 = forms.CharField(label='Choice 3', max_length=200, required=False)
    choice4 = forms.CharField(label='Choice 4', max_length=200, required=False)
    choice5 = forms.CharField(label='Choice 5', max_length=200, required=False)
