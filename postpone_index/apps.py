"""App config"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class Config(AppConfig):
    verbose_name = _('Postpone Index')
    name = 'postpone_index'
