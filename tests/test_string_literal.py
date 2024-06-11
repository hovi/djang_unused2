import unittest

from django_unused2.dataclasses import StringWithLine
from django_unused2.file_finder import extract_string_literals


class TestStringLiteralExtraction(unittest.TestCase):
    def test_html_string_in_variable(self):
        source_code = """
homepage = "index.html"
stylesheet = "style.css"
        """
        expected_results = [StringWithLine(value="index.html", line=2)]
        actual_results = extract_string_literals(source_code)
        self.assertEqual(
            actual_results,
            expected_results,
            "Should extract '.html' strings assigned to variables.",
        )

    def test_html_string_in_list(self):
        source_code = """
files = ["index.html", "about.html", "contact.css"]
        """
        expected_results = [
            StringWithLine(value="index.html", line=2),
            StringWithLine(value="about.html", line=2),
        ]
        actual_results = extract_string_literals(source_code)
        self.assertEqual(
            actual_results,
            expected_results,
            "Should extract '.html' strings within lists.",
        )

    def test_html_string_as_function_argument(self):
        source_code = """
render("index.html")
load_stylesheet("style.css")
        """
        expected_results = [StringWithLine(value="index.html", line=2)]
        actual_results = extract_string_literals(source_code)
        self.assertEqual(
            actual_results,
            expected_results,
            "Should extract '.html' strings used as function arguments.",
        )

    def test_html_string_as_named_function_argument(self):
        source_code = """
render(template_name="index.html")
load_stylesheet(style="style.css")
        """
        expected_results = [StringWithLine(value="index.html", line=2)]
        actual_results = extract_string_literals(source_code)
        self.assertEqual(
            actual_results,
            expected_results,
            "Should extract '.html' strings used as named arguments in function calls.",
        )

    def test_robots(self):
        source_code = """
render(
    request,
    template_name="frontend/robots.txt",
    context={
        "MAINTENANCE_MODE": is_maintenance_mode(),
        "ALLOW_ROBOTS": settings.ALLOW_ROBOTS,
    },
    content_type="text/plain",
)
        """
        expected_results = [StringWithLine(value="frontend/robots.txt", line=4)]
        actual_results = extract_string_literals(source_code)
        self.assertEqual(
            actual_results,
            expected_results,
            "Should extract '.html' strings used as named arguments in function calls.",
        )
