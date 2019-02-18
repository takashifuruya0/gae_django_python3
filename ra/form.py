from django import forms


class FmanageForm(forms.Form):
    name = forms.CharField(required=True)
    age = forms.IntegerField(required=True)
    datetime = forms.DateTimeField(required=True)