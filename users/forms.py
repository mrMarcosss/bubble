# coding=utf-8
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.core import validators
from django.utils.translation import ugettext
from bubble.forms import BootstrapFormMixin
from users.models import User, UserWallPost


class ProfileSettingsForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = User
        fields = ('avatar', 'first_name', 'last_name', 'gender', 'birth_date', 'city', 'job', 'about_me', 'interests')

    def __init__(self, *args, **kwargs):
        super(ProfileSettingsForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        self.fields['birth_date'].widget.attrs['placeholder'] = ugettext(u'Введіть дату у форматі РРРР-ММ-ДД')
        self.fields['about_me'].widget.attrs['rows'] = 3
        self.fields['interests'].widget.attrs['rows'] = 3


class UserChangePasswordForm(PasswordChangeForm, BootstrapFormMixin):
    def __init__(self, *args, **kwargs):
        super(UserChangePasswordForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)
        for field_name in ('old_password', 'new_password1', 'new_password2'):
            self.fields[field_name] = self.fields.pop(field_name)
            if field_name != 'old_password':
                self.fields[field_name].validators.extend([validators.MinLengthValidator(4),
                                                           validators.MaxLengthValidator(40)])


class UserChangeEmailForm(forms.Form, BootstrapFormMixin):
    new_email = forms.EmailField(max_length=75, label=ugettext(u'новий email'))
    password = forms.CharField(label=(ugettext(u'поточний пароль')), min_length=6, max_length=40,
                               widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(UserChangeEmailForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)

    def clean_new_email(self):
        new_email = self.cleaned_data['new_email'].strip()
        if User.objects.filter(email=new_email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError(ugettext(u'Користувач з тиким email вже зареєстрований'))
        return new_email

    def clean_password(self):
        password = self.cleaned_data['password']
        if not self.user.check_password(password):
            raise forms.ValidationError(ugettext(u'Невірно введений пароль'))
        return password

    def save(self, commit=True):
        self.user.email = self.cleaned_data['new_email']
        if commit:
            self.user.save()
        return self.user


class WallPostForm(forms.ModelForm, BootstrapFormMixin):
    class Meta:
        model = UserWallPost
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'placeholder': ugettext(u'напишіть на стіні...'), 'rows': 4})
        }

    def __init__(self, *args, **kwargs):
        super(WallPostForm, self).__init__(*args, **kwargs)
        BootstrapFormMixin.__init__(self)

    def clean_content(self):
        return self.cleaned_data['content'].strip()
