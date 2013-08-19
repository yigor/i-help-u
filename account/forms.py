# coding=utf-8
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.forms.widgets import CheckboxSelectMultiple, CheckboxInput
from django.utils.html import format_html, conditional_escape
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from account.models import User
from ihelpu.utils import CheckBox


class RegistrationForm(forms.Form):

    first_name = forms.CharField(label=u'имя')
    last_name = forms.CharField(label=u'фамилия')
    email = forms.EmailField(label=u'email')
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                label=u'пароль')
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                label=u'пароль ещё раз')

    def clean_email(self):
        """
        Validate that the username is alphanumeric and is not already
        in use.

        """
        existing = User.objects.filter(email__iexact=self.cleaned_data['email'])
        if existing.exists():
            raise forms.ValidationError(u"Пользователь с таким email уже зарегистрирован.")
        else:
            return self.cleaned_data['email']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.

        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(u"Пароли не совпадают.")
        return self.cleaned_data


class ImageInput(forms.ClearableFileInput):
    """
    A ImageField Widget that shows a thumbnail.
    """
    template_with_initial = '%(initial)s %(clear_template)s<br /><label>%(input_text)s:</label> %(input)s'

    def render(self, name, value, attrs=None):
        substitutions = {
            'initial_text': self.initial_text,
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
        }
        template = '%(input)s'
        substitutions['input'] = super(forms.ClearableFileInput, self).render(name, value, attrs)

        if value and hasattr(value, "url"):
            template = self.template_with_initial
            substitutions['initial'] = format_html('<img src="{0}" style="max-width: 300px;"></img>',
                                                   value.url)
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)


class UserProfileForm(forms.ModelForm):

    gender = forms.ChoiceField(widget=forms.RadioSelect(), choices=User.GENDER_CHOICES, label=u'пол', required=False)

    class Meta:
        model = User
        fields = ('city', 'phone_number', 'hide_contacts', 'web_site', 'gender', 'birth_date',
                  'i_can', 'i_want', 'about', 'interests')
        widgets = {'interests': CheckboxSelectMultiple,
                   'hide_contacts': CheckBox, 'birth_date': forms.DateInput(format='%d.%m.%Y')}

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['interests'].help_text = ''
    
    def clean_gender(self):
        gender = self.cleaned_data['gender']
        if not gender:
            return None
        return gender


class UserPhotoForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ('photo', )
        widgets = {'photo': ImageInput}


class LoginForm(AuthenticationForm):

    remember_me = forms.BooleanField(label=u'Запомни меня', widget=CheckBox, required=False, initial=True)

    def __init__(self, request=None, *args, **kwargs):
        super(LoginForm, self).__init__(request, *args, **kwargs)
        self.fields['username'].label = capfirst('Email')
