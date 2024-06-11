import enum
import os
from dataclasses import dataclass, field
from typing import Optional, Iterable, List, ClassVar, Dict

from django.apps import AppConfig


@dataclass
class StringWithLine:
    value: str
    line: int


@dataclass
class TemplateFilterOptions:
    excluded_apps: Optional[Iterable[str]] = None
    excluded_template_dirs: Optional[Iterable[str]] = None
    excluded_templates: Optional[Iterable[str]] = None


class ReferenceType(enum.Enum):
    include = "include"
    extends = "extends"
    unknown = "unknown"
    render = "render"


@dataclass
class TemplateTokenReference:
    file_path: str
    line_number: int
    reference_type: ReferenceType


@dataclass
class TemplateReference:
    source_id: str
    target_id: str
    reference_type: ReferenceType
    """
    Starting with 1
    """
    line: int
    broken: bool = field(default=False)


@dataclass
class BasePath:
    id: str
    base_dir: str
    relative_path: str
    app_config: Optional["AppConfig"]
    local_app: bool

    @property
    def absolute_path(self):
        return os.path.join(self.base_dir, self.relative_path)

    @property
    def relative_dir_path(self):
        return os.path.dirname(self.relative_path)


@dataclass
class Python(BasePath):
    extensions: ClassVar[List[str]] = [".py"]


@dataclass
class Template(BasePath):
    extensions: ClassVar[List[str]] = [".html", ".txt"]


@dataclass
class AnalysisResult:
    never_referenced_templates: List[Template] = field(default_factory=list)
    broken_references: List[TemplateReference] = field(default_factory=list)
    references: List[TemplateReference] = field(default_factory=list)
    templates: List[Template] = field(default_factory=list)
    python_files: List[Python] = field(default_factory=list)

    @property
    def unused_local_filenames(self) -> List[str]:
        return [f.relative_path for f in self.never_referenced_templates if f.local_app]

    @property
    def unused_filenames(self) -> List[str]:
        return [f.relative_path for f in self.never_referenced_templates]

    @property
    def templates_by_id(self) -> Dict[str, Template]:
        return {template.id: template for template in self.templates}

    def __bool__(self) -> bool:
        """Return True if the analysis found no issues, False otherwise."""
        return not self.never_referenced_templates and not self.broken_references
