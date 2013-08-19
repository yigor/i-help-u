from django import forms
from magazine.models import Comment


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body', )

    def __init__(self, *args, **kwargs):
        author = kwargs.pop('author')
        article = kwargs.pop('article')
        parent = kwargs.pop('parent')
        super(CommentForm, self).__init__(*args, **kwargs)
        self.instance.article = article
        self.instance.author = author
        self.instance.parent = parent
