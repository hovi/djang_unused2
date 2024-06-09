from tests.template_test_util import TemplateTestCase
from django_unused2.file_finder import (
    find_template_to_template_references,
    find_templates_in_directory,
)
from django_unused2.dataclasses import TemplateReference, ReferenceType


class TestSimpleTemplate(TemplateTestCase):

    def test_broken_template(self):
        self.fc(
            "templates/template1.html", "{% include 'non-existent-template.html' %}"
        )

        references = find_template_to_template_references(
            find_templates_in_directory(self.test_dir)
        )
        self.assertEqual(
            references,
            [
                TemplateReference(
                    source_id=self.file_path["templates/template1.html"],
                    target_id="non-existent-template.html",
                    reference_type=ReferenceType.include,
                    broken=True,
                    line=1,
                )
            ],
        )

    def test_reference_itself(self):
        self.fc(
            "templates/template1.html", "\n{% extends 'templates/template1.html' %}"
        )

        references = find_template_to_template_references(
            find_templates_in_directory(self.test_dir)
        )
        self.assertEqual(
            references,
            [
                TemplateReference(
                    source_id=self.file_path["templates/template1.html"],
                    target_id=self.file_path["templates/template1.html"],
                    reference_type=ReferenceType.extends,
                    broken=False,
                    line=2,
                )
            ],
        )

    def test_unknown(self):
        self.fc(
            "templates/template1.html",
            "{% non_existent_reference_type 'templates/template1.html' %}",
        )

        references = find_template_to_template_references(
            find_templates_in_directory(self.test_dir)
        )
        self.assertEqual(references, [])

    def test_normalize_path(self):
        self.fc(
            "templates/template1.html",
            "\n{% extends 'templates/../templates/template1.html' %}",
        )

        references = find_template_to_template_references(
            find_templates_in_directory(self.test_dir)
        )
        self.assertEqual(
            references,
            [
                TemplateReference(
                    source_id=self.file_path["templates/template1.html"],
                    target_id=self.file_path["templates/template1.html"],
                    reference_type=ReferenceType.extends,
                    broken=False,
                    line=2,
                )
            ],
        )

    def test_normalize_path_v2(self):
        self.fc("template1.html", "\n{% extends 'templates/../template1.html' %}")

        references = find_template_to_template_references(
            find_templates_in_directory(self.test_dir)
        )
        self.assertEqual(
            references,
            [
                TemplateReference(
                    source_id=self.file_path["template1.html"],
                    target_id=self.file_path["template1.html"],
                    reference_type=ReferenceType.extends,
                    broken=False,
                    line=2,
                )
            ],
        )
