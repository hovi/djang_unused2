from django.test import override_settings

from django_unused2.dataclasses import TemplateFilterOptions
from django_unused2.filter import run_analysis
from tests.template_test_util import TemplateTestCase


@override_settings(
    INSTALLED_APPS=["tests.apps.relative_include_parent"],
)
class TestEmptyDjangoApps(TemplateTestCase):
    def test_no_bad_results(self):
        result = run_analysis(TemplateFilterOptions())
        self.assertEqual([], result.unused_filenames)
        self.assertEqual([], result.broken_references)
