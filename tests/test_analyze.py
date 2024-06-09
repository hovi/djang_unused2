from django_unused2.file_finder import (
    find_templates_in_directory,
    find_python_to_template_references,
    find_python_in_directory,
    find_all_references,
    find_template_to_template_references,
)
from django_unused2.dataclasses import TemplateReference, ReferenceType, Template
from django_unused2.filter import analyze_references
from tests.template_test_util import TemplateTestCase


class TestAnalyze(TemplateTestCase):

    def test_simple_view_reference(self):
        self.fc("templates/template1.html", "")
        self.fc("view.py", "render('templates/template1.html')")

        templates = find_templates_in_directory(self.test_dir)
        python_files = find_python_in_directory(self.test_dir)

        references = find_all_references(python_files=python_files, templates=templates)
        analysis = analyze_references(
            references=references, templates=templates, python_files=python_files
        )
        self.assertEqual(analysis.broken_references, [])
        self.assertEqual(analysis.never_referenced_templates, [])

    def test_broken_reference(self):
        self.fc(
            "templates/template1.html", "{% extends 'templates/../template1.html' %}"
        )

        templates = find_templates_in_directory(self.test_dir)
        python_files = find_python_in_directory(self.test_dir)

        references = find_template_to_template_references(templates=templates)
        analysis = analyze_references(
            references=references, templates=templates, python_files=python_files
        )
        self.assertEqual(
            analysis.broken_references,
            [
                TemplateReference(
                    source_id=self.file_path["templates/template1.html"],
                    target_id="template1.html",
                    reference_type=ReferenceType.extends,
                    broken=True,
                    line=1,
                )
            ],
        )
        self.assertEqual(
            analysis.never_referenced_templates,
            [
                Template(
                    id=self.file_path["templates/template1.html"],
                    relative_path="templates/template1.html",
                    base_dir=self.test_dir,
                    app_config=None,
                ),
            ],
        )
