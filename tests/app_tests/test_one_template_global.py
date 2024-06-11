from django.conf import settings
from django.test import override_settings

from django_unused2.dataclasses import TemplateFilterOptions
from django_unused2.filter import run_analysis
from tests.template_test_util import TemplateTestCase


@override_settings(
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [settings.BASE_DIR + "/apps/one_template/templates"],
            "APP_DIRS": True,
        },
    ]
)
class TestEmptyDjangoApps(TemplateTestCase):
    def test_no_bad_results(self):
        result = run_analysis(TemplateFilterOptions())
        self.assertEqual(["template1.html"], result.unused_filenames)
        self.assertEqual([], result.broken_references)
