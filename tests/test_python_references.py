from django_unused2.file_finder import (
    find_templates_in_directory,
    find_python_to_template_references,
    find_python_in_directory,
    find_all_references,
)
from django_unused2.dataclasses import TemplateReference, ReferenceType
from tests.template_test_util import TemplateTestCase


class TestSimplePython(TemplateTestCase):

    def test_simple_view_reference(self):
        self.fc("templates/template1.html", "")
        self.fc("view.py", "render('templates/template1.html')")

        templates = find_templates_in_directory(self.test_dir)
        python_files = find_python_in_directory(self.test_dir)

        references = find_python_to_template_references(
            python_files=python_files, templates=templates
        )
        self.assertEqual(
            references,
            [
                TemplateReference(
                    source_id=self.file_path["view.py"],
                    target_id=self.file_path["templates/template1.html"],
                    reference_type=ReferenceType.render,
                    broken=False,
                    line=1,
                )
            ],
        )

    def test_complex(self):
        self.fc("templates/template1.html", "{% include 'template2.html' %}")
        self.fc("view.py", "render('templates/template1.html')")

        templates = find_templates_in_directory(self.test_dir)
        python_files = find_python_in_directory(self.test_dir)

        references = find_all_references(python_files=python_files, templates=templates)
        self.assertEqual(
            references,
            [
                TemplateReference(
                    source_id=self.file_path["view.py"],
                    target_id=self.file_path["templates/template1.html"],
                    reference_type=ReferenceType.render,
                    broken=False,
                    line=1,
                ),
                TemplateReference(
                    source_id=self.file_path["templates/template1.html"],
                    target_id="template2.html",
                    reference_type=ReferenceType.include,
                    line=1,
                    broken=True,
                ),
            ],
        )
