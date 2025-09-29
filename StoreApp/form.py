from django import forms

from StoreApp.models import ReviewRating


class ReviewRatingForm(forms.ModelForm):

    class Meta:
        model = ReviewRating
        fields = ['subject','review','rating']