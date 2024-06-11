import os
import shutil
import tempfile
import unittest
from typing import Callable, Tuple, Dict

import django
from django.test import TestCase
import os

os.environ["DJANGO_SETTINGS_MODULE"] = "tests.apps.settings"
django.setup()


def file_creator(
    test_instance: unittest.TestCase,
) -> Callable[[str, str], Tuple[str, str]]:
    test_instance.test_dir = tempfile.mkdtemp()
    test_instance.file_content = {}
    test_instance.file_path = {}

    def create_file(relative_path: str, content: str):
        file_path = os.path.join(test_instance.test_dir, relative_path)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write(content)
        test_instance.file_content[relative_path] = content
        test_instance.file_path[relative_path] = file_path
        return file_path, relative_path

    test_instance.fc = create_file

    return create_file


class TemplateTestCase(TestCase):
    fc: Callable[[str, str], Tuple[str, str]]
    test_dir: str
    file_content: Dict[str, str]
    file_path: Dict[str, str]

    def setUp(self):
        super().setUp()
        self.fc = file_creator(self)

    def tearDown(self):
        if hasattr(self, "test_dir"):
            shutil.rmtree(self.test_dir)
