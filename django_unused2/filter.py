from typing import List, Optional, Dict, Set

from colorama import Fore

from django_unused2.dataclasses import (
    TemplateFilterOptions,
    Template,
    TemplateReference,
    Python,
    AnalysisResult,
)
from django_unused2.file_finder import (
    find_global_templates,
    find_app_templates,
    find_py_files,
    find_all_references,
)


def filter_templates(
    templates: List[Template], filter_options: Optional[TemplateFilterOptions]
) -> List[Template]:
    if filter_options and filter_options.excluded_apps:
        excluded_apps_set = set(filter_options.excluded_apps)
        templates = [
            t
            for t in templates
            if not (t.app_config and t.app_config.name in excluded_apps_set)
        ]

    if filter_options and filter_options.excluded_template_dirs:
        excluded_dirs_set = set(filter_options.excluded_template_dirs)
        templates = [
            t
            for t in templates
            if not any(t.relative_path.startswith(d) for d in excluded_dirs_set)
        ]

    if filter_options and filter_options.excluded_templates:
        et = set(filter_options.excluded_templates)
        templates = [
            template
            for template in templates
            if template.relative_path not in et and template.absolute_path not in et
        ]

    return templates


def filter_py_files(
    files: List[Python], filter_options: Optional[TemplateFilterOptions]
):
    result = files
    if filter_options and filter_options.excluded_apps:
        excluded_apps_set = set(filter_options.excluded_apps)
        result = [
            t
            for t in result
            if not (t.app_config and t.app_config.name in excluded_apps_set)
        ]

    return result


def analyze_references(
    references: List[TemplateReference],
    templates: List[Template],
    python_files: List[Python],
) -> AnalysisResult:
    broken_references = find_broken_references(references, python_files, templates)
    never_referenced_templates = find_unreferenced_templates(
        references, templates, python_files
    )

    return AnalysisResult(
        never_referenced_templates=never_referenced_templates,
        broken_references=broken_references,
        references=references,
        python_files=python_files,
        templates=templates,
    )


def find_unreferenced_templates(
    references: List[TemplateReference],
    templates: List[Template],
    python_files: List[Python],
) -> List[Template]:
    template_dict: Dict[str, Template] = {
        template.id: template for template in templates
    }
    python_file_dict: Dict[str, Python] = {
        py_file.id: py_file for py_file in python_files
    }

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

    for ref in references:
        if ref.source_id in visited_templates and ref.target_id in template_dict:
            visited_templates.add(ref.target_id)

    never_visited = [
        t for t in templates if t.id not in visited_templates and t.local_app
    ]

    return never_visited


def find_broken_references(
    references: List[TemplateReference],
    python_files: List[Python],
    templates: List[Template],
) -> List[TemplateReference]:
    local_ids = set([t.id for t in templates if t.local_app])
    return [r for r in references if r.broken and r.source_id in local_ids]


def run_analysis(config: TemplateFilterOptions) -> AnalysisResult:
    templates = filter_templates(find_app_templates() + find_global_templates(), config)
    python_files = filter_py_files(find_py_files(), config)
    references = find_all_references(templates, python_files)
    return analyze_references(references, templates, python_files)
