from typing import List, Optional, Dict, Set

from colorama import Fore

from django_unused2.dataclasses import (
    TemplateFilterOptions,
    Template,
    TemplateReference,
    Python,
    AnalysisResult, )
from django_unused2.file_finder import (
    find_global_templates,
    find_app_templates,
    find_py_files,
    find_all_references,
)


def filter_templates(
        templates: List[Template], filter_options: Optional[TemplateFilterOptions]
) -> List[Template]:
    initial_app_template_count = len([t for t in templates if t.app_config])

    if filter_options and filter_options.excluded_apps:
        excluded_apps_set = set(filter_options.excluded_apps)
        templates = [
            t
            for t in templates
            if not (t.app_config and t.app_config.name in excluded_apps_set)
        ]
        filtered_app_template_count = initial_app_template_count - len(
            [t for t in templates if t.app_config]
        )
        print(
            f"{Fore.YELLOW}{filtered_app_template_count} templates excluded by app filter.\n"
        )

    initial_template_count = len(templates)

    if filter_options and filter_options.excluded_template_dirs:
        excluded_dirs_set = set(filter_options.excluded_template_dirs)
        templates = [
            t
            for t in templates
            if not any(t.relative_path.startswith(d) for d in excluded_dirs_set)
        ]
        filtered_dir_template_count = initial_template_count - len(templates)
        print(
            f"{Fore.YELLOW}{filtered_dir_template_count} templates excluded by directory filter.\n"
        )

    print(f"{Fore.GREEN}{len(templates)} app templates found after filtering.\n")
    return templates


def analyze_references(
        references: List[TemplateReference],
        templates: List[Template],
        python_files: List[Python],
) -> AnalysisResult:
    broken_references = find_broken_references(references, python_files, templates)
    never_referenced_templates = find_unreferenced_templates(references, templates, python_files)

    return AnalysisResult(never_referenced_templates, broken_references)


def find_unreferenced_templates(
    references: List[TemplateReference],
    templates: List[Template],
    python_files: List[Python]
) -> List[Template]:
    template_dict: Dict[str, Template] = {template.id: template for template in templates}
    python_file_dict: Dict[str, Python] = {py_file.id: py_file for py_file in python_files}

    visited_templates: Set[str] = set()

    for ref in references:
        if ref.source_id in python_file_dict and ref.target_id in template_dict:
            visited_templates.add(ref.target_id)

    for ref in references:
        if ref.source_id in visited_templates and ref.target_id in template_dict:
            visited_templates.add(ref.target_id)

    for ref in references:
        if ref.source_id in visited_templates and ref.target_id in template_dict:
            visited_templates.add(ref.target_id)

    never_visited = [t for t in templates if t.id not in visited_templates]

    return never_visited

def find_broken_references(
        references: List[TemplateReference],
        python_files: List[Python],
        templates: List[Template]
) -> List[TemplateReference]:
    return [r for r in references if r.broken]


def run_analysis(config: TemplateFilterOptions) -> AnalysisResult:
    templates = filter_templates(find_app_templates() + find_global_templates(), config)
    python_files = find_py_files()
    references = find_all_references(templates, python_files)
    return analyze_references(references, templates, python_files)
