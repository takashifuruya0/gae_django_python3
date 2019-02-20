from django import forms


class FmanageForm(forms.Form):
    name = forms.CharField(required=True)
    age = forms.IntegerField(required=True)
    datetime = forms.DateTimeField(required=True)


class TrainingForm(forms.Form):
    name = forms.CharField(required=True)
    weight = forms.IntegerField(required=True)
    no_set = forms.IntegerField(required=True)
    # feeling = forms.ChoiceField(required=True, choices=("◎", "○", "×"), initial=1)
    datetime = forms.DateTimeField(required=True)