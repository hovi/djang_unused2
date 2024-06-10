import unittest

from django_unused2.dataclasses import TemplateReference, ReferenceType, Template
from django_unused2.file_finder import (
    find_templates_in_directory,
    find_python_in_directory,
    find_all_references,
)
from django_unused2.filter import analyze_references
from tests.template_test_util import TemplateTestCase


class TestAnalyze(TemplateTestCase):

    def test_simple_view_reference(self):
        self.fc("templates/template1.html", "")
        self.fc("view.py", "render('templates/template1.html')")

        templates = find_templates_in_directory(self.test_dir, local_app=True)
        python_files = find_python_in_directory(self.test_dir, local_app=True)

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

        templates = find_templates_in_directory(self.test_dir, local_app=True)
        python_files = find_python_in_directory(self.test_dir, local_app=True)

        references = find_all_references(templates=templates, python_files=python_files)
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
                    local_app=True,
                ),
            ],
        )

    def test_nested_template_references(self):
        self.fc("templates/base.html", "")
        self.fc("templates/child.html", "{% extends 'templates/base.html' %}")
        self.fc("view.py", "render('templates/child.html')")

        templates = find_templates_in_directory(self.test_dir, local_app=True)
        python_files = find_python_in_directory(self.test_dir, local_app=True)
        references = find_all_references(python_files=python_files, templates=templates)
        analysis = analyze_references(
            references=references, templates=templates, python_files=python_files
        )

        self.assertEqual(analysis.broken_references, [])
        self.assertEqual(analysis.never_referenced_templates, [])

    def test_multiple_python_files(self):
        self.fc("templates/shared.html", "")
        self.fc("view1.py", "render('templates/shared.html')")
        self.fc("view2.py", "render('templates/shared.html')")

        templates = find_templates_in_directory(self.test_dir, local_app=True)
        python_files = find_python_in_directory(self.test_dir, local_app=True)
        references = find_all_references(python_files=python_files, templates=templates)
        analysis = analyze_references(
            references=references, templates=templates, python_files=python_files
        )

        self.assertEqual(analysis.broken_references, [])
        self.assertEqual(analysis.never_referenced_templates, [])

    def test_unreferenced_templates(self):
        self.fc("templates/unused.html", "")

        templates = find_templates_in_directory(self.test_dir, local_app=True)
        python_files = find_python_in_directory(self.test_dir, local_app=True)
        references = find_all_references(python_files=python_files, templates=templates)
        analysis = analyze_references(
            references=references, templates=templates, python_files=python_files
        )

        self.assertEqual(analysis.broken_references, [])
        self.assertTrue(
            any(
                t.id.endswith("unused.html")
                for t in analysis.never_referenced_templates
            )
        )

    @unittest.skip("Broken link check from python needs implementing")
    def test_incorrect_template_path(self):
        self.fc("view.py", "render('templates/nonexistent.html')")

        templates = find_templates_in_directory(self.test_dir, local_app=True)
        python_files = find_python_in_directory(self.test_dir, local_app=True)
        references = find_all_references(python_files=python_files, templates=templates)
        analysis = analyze_references(
            references=references, templates=templates, python_files=python_files
        )

        self.assertEqual(1, len(analysis.broken_references))
        self.assertEqual([], analysis.never_referenced_templates)

    def test_chained_template_references(self):
        # Base template which is extended by others
        self.fc("templates/base.html", "")
        # Intermediate template that extends base and is included by others
        self.fc("templates/intermediate.html", "{% extends 'templates/base.html' %}")
        # Final template that includes intermediate and is rendered by a view
        self.fc("templates/final.html", "{% include 'templates/intermediate.html' %}")
        self.fc("view.py", "render('templates/final.html')")

        templates = find_templates_in_directory(self.test_dir, local_app=True)
        python_files = find_python_in_directory(self.test_dir, local_app=True)
        references = find_all_references(python_files=python_files, templates=templates)
        analysis = analyze_references(
            references=references, templates=templates, python_files=python_files
        )

        self.assertEqual(analysis.broken_references, [])
        self.assertEqual(analysis.never_referenced_templates, [])

    def test_mixed_broken_and_successful_references(self):
        self.fc("templates/valid.html", "")
        self.fc("templates/broken.html", "{% extends 'templates/nonexistent.html' %}")
        self.fc("view.py", "render('templates/valid.html')")
        self.fc("another_view.py", "render('templates/broken.html')")

        templates = find_templates_in_directory(self.test_dir, local_app=True)
        python_files = find_python_in_directory(self.test_dir, local_app=True)
        references = find_all_references(python_files=python_files, templates=templates)
        analysis = analyze_references(
            references=references, templates=templates, python_files=python_files
        )

        self.assertTrue(any(ref.broken for ref in analysis.broken_references))
        self.assertEqual(len(analysis.never_referenced_templates), 0)

    def test_cascading_broken_references(self):
        self.fc("templates/base.html", "{% extends 'templates/nonexistent.html' %}")
        self.fc("templates/child.html", "{% extends 'templates/base.html' %}")
        self.fc("view.py", "render('templates/child.html')")

        templates = find_templates_in_directory(self.test_dir, local_app=True)
        python_files = find_python_in_directory(self.test_dir, local_app=True)
        references = find_all_references(python_files=python_files, templates=templates)
        analysis = analyze_references(
            references=references, templates=templates, python_files=python_files
        )

        self.assertTrue(any(ref.broken for ref in analysis.broken_references))
        self.assertEqual(len(analysis.never_referenced_templates), 0)

    def test_all_used_various_combinations(self):
        self.fc("templates/base.html", "")
        self.fc(
            "templates/intermediate.html",
            "{% extends 'templates/base.html' %} {% include 'templates/component.html' %}",
        )
        self.fc("templates/component.html", "")
        self.fc("templates/final.html", "{% extends 'templates/intermediate.html' %}")
        self.fc("view.py", "render('templates/final.html')")

        templates = find_templates_in_directory(self.test_dir, local_app=True)
        python_files = find_python_in_directory(self.test_dir, local_app=True)
        references = find_all_references(python_files=python_files, templates=templates)
        analysis = analyze_references(
            references=references, templates=templates, python_files=python_files
        )

        self.assertEqual(analysis.broken_references, [])
        self.assertEqual(analysis.never_referenced_templates, [])
