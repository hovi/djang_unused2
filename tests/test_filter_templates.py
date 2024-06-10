import unittest
from unittest.mock import MagicMock

from django_unused2.dataclasses import Template
from django_unused2.filter import (
    TemplateFilterOptions,
    filter_templates,
)


class TestFilterTemplates(unittest.TestCase):

    def setUp(self):
        self.app_config1 = MagicMock()
        self.app_config1.name = "app1"
        self.template1 = Template(
            app_config=self.app_config1,
            relative_path="dir1/template1.html",
            base_dir="",
            id="dir1/template1.html",
            local_app=True,
        )

        self.app_config2 = MagicMock()
        self.app_config2.name = "app2"
        self.template2 = Template(
            app_config=self.app_config2,
            relative_path="dir2/template2.html",
            base_dir="",
            id="dir2/template2.html",
            local_app=True,
        )

        self.template3 = Template(
            app_config=None,
            relative_path="dir3/template3.html",
            base_dir="",
            id="dir3/template3.html",
            local_app=True,
        )
        self.templates = [self.template1, self.template2, self.template3]

    def test_filter_templates_excluded_apps(self):
        filter_options = TemplateFilterOptions(excluded_apps=["app1"])

        filtered_templates = filter_templates(self.templates, filter_options)
        self.assertEqual(len(filtered_templates), 2)
        self.assertIn(self.template2, filtered_templates)
        self.assertIn(self.template3, filtered_templates)
        self.assertNotIn(self.template1, filtered_templates)

    def test_filter_templates_excluded_dirs(self):
        filter_options = TemplateFilterOptions(excluded_template_dirs=["dir2"])

        filtered_templates = filter_templates(self.templates, filter_options)
        self.assertEqual(len(filtered_templates), 2)
        self.assertIn(self.template1, filtered_templates)
        self.assertIn(self.template3, filtered_templates)
        self.assertNotIn(self.template2, filtered_templates)

    def test_filter_templates_excluded_apps_and_dirs(self):
        filter_options = TemplateFilterOptions(
            excluded_apps=["app1"], excluded_template_dirs=["dir2"]
        )

        filtered_templates = filter_templates(self.templates, filter_options)
        self.assertEqual(len(filtered_templates), 1)
        self.assertIn(self.template3, filtered_templates)
        self.assertNotIn(self.template1, filtered_templates)
        self.assertNotIn(self.template2, filtered_templates)


if __name__ == "__main__":
    unittest.main()
