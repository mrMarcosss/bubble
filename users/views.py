# coding=utf-8
from django.contrib import messages
from django.contrib.auth import BACKEND_SESSION_KEY, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import TemplateView
from users.forms import ProfileSettingsForm, UserChangePasswordForm, UserChangeEmailForm, WallPostForm
from users.models import User


class UserProfileView(TemplateView):
    template_name = 'users/profile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated() and request.user.pk == int(kwargs['user_id']):
            self.user = request.user
        else:
            self.user = get_object_or_404(User, pk=kwargs['user_id'])
        self.wall_post_form = WallPostForm(request.POST or None)
        return super(UserProfileView, self).dispatch(request, *args, **kwargs)

    def get_wall_posts(self):
        paginator = Paginator(self.user.wall_posts.select_related('author'), 10)
        page = self.request.GET.get('page')
        try:
            posts_on_wall = paginator.page(page)
        except PageNotAnInteger:
            posts_on_wall = paginator.page(1)
        except EmptyPage:
            posts_on_wall = paginator.page(paginator.num_pages)
        return posts_on_wall

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        context['profile_user'] = self.user
        context['posts_on_wall'] = self.get_wall_posts()
        context['wall_post_form'] = self.wall_post_form
        return context

    def post(self, request, *args, **kwargs):
        if self.wall_post_form.is_valid():
            post = self.wall_post_form.save(commit=False)
            post.user = self.user
            post.author = request.user
            post.save()
            messages.success(request, _(u'Повідомлення успішно опубліковано'))
            return redirect(request.path)
        return self.get(request, *args, **kwargs)


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
