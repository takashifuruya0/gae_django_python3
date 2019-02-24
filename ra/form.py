from django import forms


class FmanageForm(forms.Form):
    name = forms.CharField(required=True)
    age = forms.IntegerField(required=True)
    datetime = forms.DateTimeField(required=True)


class TrainingForm(forms.Form):
    name = forms.CharField(required=True)
    weight = forms.IntegerField(required=True)
    set = forms.IntegerField(required=True)
    # feeling = forms.ChoiceField(required=True, choices=("◎", "○", "×"), initial=1)
    datetime = forms.DateTimeField(required=True)


class PhotoForm(forms.Form):
    sitename = forms.CharField(required=True)
    prefecture = forms.CharField(required=True)
    country = forms.CharField(required=True)
    comment = forms.CharField(required=True)
    datetime = forms.DateTimeField(required=True)
    path = forms.CharField(required=True)
    path_resized = forms.CharField(required=True)
