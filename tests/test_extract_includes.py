import unittest

from django_unused2.dataclasses import TemplateTokenReference, ReferenceType
from django_unused2.template_util import (
    extract_template_references,
)


class TestExtractTemplateReferences(unittest.TestCase):

    def test_extract_template_references(self):
        template_text = """
        {% extends "base.html" %}
        <html>
          {% include 'templates/header.html' %}
          <body>
            {% include "templates/body.html" %}
            {% include 'other_templates/footer.html' %}
          </body>
        </html>
        """.strip()

        expected_references = [
            TemplateTokenReference(
                file_path="base.html",
                line_number=1,
                reference_type=ReferenceType.extends,
            ),
            TemplateTokenReference(
                file_path="templates/header.html",
                line_number=3,
                reference_type=ReferenceType.include,
            ),
            TemplateTokenReference(
                file_path="templates/body.html",
                line_number=5,
                reference_type=ReferenceType.include,
            ),
            TemplateTokenReference(
                file_path="other_templates/footer.html",
                line_number=6,
                reference_type=ReferenceType.include,
            ),
        ]

        references = extract_template_references(template_text)
        self.assertEqual(references, expected_references)


if __name__ == "__main__":
    unittest.main()
