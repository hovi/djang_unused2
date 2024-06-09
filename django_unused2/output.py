import os
from typing import List

from colorama import init, Fore

from django_unused2.dataclasses import (
    ReferenceType, TemplateReference, Template,
)

init(autoreset=True)

reference_type_colors = {
    ReferenceType.include: Fore.CYAN,
    ReferenceType.extends: Fore.LIGHTBLUE_EX,
    ReferenceType.unknown: Fore.RED,
    ReferenceType.render: Fore.MAGENTA
}


def print_unreferenced_templates(templates: List[Template], base_dir: str):
    if not templates:
        print(Fore.GREEN + "No unreferenced templates found.")
        return

    # Group templates by AppConfig name
    grouped_templates = {}
    for template in templates:
        app_config_name = template.app_config.name if template.app_config else "No AppConfig"
        if app_config_name not in grouped_templates:
            grouped_templates[app_config_name] = []
        grouped_templates[app_config_name].append(template)

    # Print the grouped templates
    print(Fore.YELLOW + "\nTemplates Never Referenced by Python files:")
    for app_config_name, templates in grouped_templates.items():
        print(Fore.CYAN + f"\nAppConfig: {app_config_name}")
        for template in templates:
            relative_path = os.path.relpath(template.id, base_dir)
            print(
                Fore.MAGENTA + f"{template.relative_path}"
            )


def print_broken_references(references: List[TemplateReference], base_dir: str):
    if not references:
        print(Fore.GREEN + "No broken references found.")
        return

    print(Fore.RED + "\nBroken References Found:")
    for ref in references:
        source_path = os.path.relpath(ref.source_id, base_dir)
        target_path = os.path.relpath(ref.target_id, base_dir)
        ref_type_color = reference_type_colors.get(ref.reference_type, Fore.WHITE)
        print(
            Fore.BLUE + f"{source_path} " +
            ref_type_color + f"{ref.reference_type.value} " +
            Fore.BLUE + f"{target_path} " +
            Fore.YELLOW + "at line " +
            Fore.GREEN + f"{ref.line}"
        )
