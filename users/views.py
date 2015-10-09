# coding=utf-8
from django.contrib import messages
from django.contrib.auth import BACKEND_SESSION_KEY, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from users.forms import ProfileSettingsForm, UserChangePasswordForm, UserChangeEmailForm


class UserProfileView(TemplateView):
    template_name = 'users/profile.html'


class UserSettings(TemplateView):
    template_name = 'users/settings.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        action = request.POST.get('action')
        self.profile_settings_form = ProfileSettingsForm(
            (request.POST if action == 'profile' else None),
            (request.FILES if action == 'profile' else None),
            prefix='profile', instance=request.user
        )
        self.user_change_password = UserChangePasswordForm(request.user, (request.POST if action == 'password' else None),
                                                           prefix='password')
        self.user_change_email = UserChangeEmailForm(request.user, (request.POST if action == 'email' else None),
                                                     prefix='email')
        return super(UserSettings, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserSettings, self).get_context_data(**kwargs)
        context['profile_settings_form'] = self.profile_settings_form
        context['user_change_password'] = self.user_change_password
        context['user_change_email'] = self.user_change_email
        return context

    def post(self, request, *args, **kwargs):
        if self.profile_settings_form.is_valid():
            self.profile_settings_form.save()
            messages.success(request, _(u'Дані успішно змінені та збережені'))
            return redirect(request.path)
        elif self.user_change_password.is_valid():
            self.user_change_password.save()
            request.user.backend = request.session[BACKEND_SESSION_KEY]
            login(request, request.user)
            messages.success(request, _(u'Пароль успішно змінений'))
            return redirect(request.path)
        elif self.user_change_email.is_valid():
            self.user_change_email.save()
            messages.success(request, _(u'Email успішно змінений та збережений'))
            return redirect(request.path)
        return self.get(request, *args, **kwargs)
