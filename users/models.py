# coding=utf-8
import hashlib
import os
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.core.signing import Signer, TimestampSigner
from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext, ugettext_lazy as _


class UserManager(BaseUserManager):
    def _create_user(self, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()

        email = self.normalize_email(email)
        user = self.model(email=email, is_staff=is_staff, is_active=True, is_superuser=is_superuser,
                          date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **extra_fields):
        return self._create_user(email, password, False, False, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self._create_user(email, password, True, True, **extra_fields)


def get_image_file_name(instance, filename):
    id_str = str(instance.pk)
    return 'avatars/{sub_dir}/{id}_{rand}{ext}'.format(
        sub_dir=id_str.zfill(2)[-2:],
        id=id_str,
        rand=get_random_string(8, 'abcdefghijklmnopqrstuvwxyz0123456789'),
        ext=os.path.splitext(filename)[1],
    )


class User(AbstractBaseUser, PermissionsMixin):
    GENDER_NONE = 0
    GENDER_MALE = 1
    GENDER_FEMALE = 2
    GENDER_CHOICES = (
        (GENDER_NONE, _('---')),
        (GENDER_MALE, _(u'чоловік')),
        (GENDER_FEMALE, _(u'жінка')),
    )
    email = models.EmailField(_('email'), unique=True)
    first_name = models.CharField(_('first name'), max_length=40)
    last_name = models.CharField(_('last name'), max_length=40, blank=True)
    avatar = models.ImageField(_(u'аватарка'), upload_to=get_image_file_name, blank=True)
    is_staff = models.BooleanField(_('staff status'), default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))
    is_active = models.BooleanField(_('active'), default=True,
                                    help_text=_('Designates whether this user should be treated as '
                                                'active. Unselect this instead of deleting accounts.'))
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    confirmed_registration = models.BooleanField(_('confirmed registration'), default=True)
    gender = models.SmallIntegerField(_(u'стать'), choices=GENDER_CHOICES, default=GENDER_NONE)
    birth_date = models.DateField(_(u'день народження'), null=True, blank=True)
    city = models.CharField(_(u'місто'), max_length=50, blank=True)
    job = models.CharField(_(u'робота'), max_length=200, blank=True)
    about_me = models.TextField(_(u'про мене'), max_length=10000, blank=True)
    interests = models.TextField(_(u'інтереси'), max_length=10000, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name']

    def get_full_name(self):
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_registration_email(self):
        url = 'http://{}{}'.format(
            Site.objects.get_current().domain,
            reverse('registration_confirm', kwargs={'token': Signer(salt='registration-confirm').sign(self.pk)})
        )
        self.email_user(
            ugettext(u'Підтвердіть реєстрацію | bubble'),
            ugettext(u'Для підтвердження реєстрації перейдіть по лінку: {}'.format(url))
        )

    def get_last_login_hash(self):
        return hashlib.md5(self.last_login.strftime('%Y-%m-%d-%H-%M-%S-%f')).hexdigest()[:8]

    def send_password_recovery_email(self):
        data = '{}:{}'.format(self.pk, self.get_last_login_hash())
        token = TimestampSigner(salt='password-recovery-confirm').sign(data)
        url = 'http://{}{}'.format(
            Site.objects.get_current().domain,
            reverse('password_recovery_confirm', kwargs={'token': token})
        )
        self.email_user(
            ugettext(u'Підтвердіть відновлення пароля | bubble'),
            ugettext(u'Для підтвердження перейдіть по лінку: {}'.format(url))
        )


class UserWallPost(models.Model):
    user = models.ForeignKey(User, verbose_name=_(u'вланик стіни'), related_name='wall_posts')
    author = models.ForeignKey(User, verbose_name=_(u'автор'), related_name='+')
    content = models.TextField(verbose_name=_(u'контент'), max_length=4000)
    created = models.DateTimeField(verbose_name=_(u'дата створення'), auto_now_add=True, db_index=True)

    class Meta:
        ordering = ('-created',)