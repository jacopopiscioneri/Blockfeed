from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    content = forms.CharField(label="", widget=forms.Textarea(
        attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Say something...'}))
    #error_css_class = 'error'
    #required_css_class = 'required'

    class Meta:
        model = Post
        fields = ['content']

    def clean(self):

        super(PostForm, self).clean()
        content = self.cleaned_data.get('content')

        if content and "hack" in content.lower():
            self._errors['content'] = self.error_class(
                ["Using the 'hack' word is not allowed. "])

        return self.cleaned_data
