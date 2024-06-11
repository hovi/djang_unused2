from django.test import override_settings

from django_unused2.dataclasses import TemplateFilterOptions
from django_unused2.filter import run_analysis
from tests.template_test_util import TemplateTestCase


@override_settings(
    INSTALLED_APPS=(
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django.contrib.sitemaps",
    ),
)
class TestEmptyDjangoApps(TemplateTestCase):
    def test_no_bad_results(self):
        result = run_analysis(TemplateFilterOptions())
        self.assertTrue(result)
