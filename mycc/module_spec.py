"""Module specification data structures.

This module defines structured data types for module operations,
replacing string-based parsing with type-safe data structures.
Eliminates the scattered string parsing logic found in cli.py.
"""

from typing import List, Optional
from dataclasses import dataclass


@dataclass
class ModuleSpec:
    """Structured specification for a module and its sub-modules.

    This replaces the string parsing pattern "module_name:sub1,sub2"
    with a structured, type-safe representation.
    """

    name: str
    sub_modules: Optional[List[str]] = None

    @classmethod
    def parse(cls, spec_string: str) -> "ModuleSpec":
        """Parse a module specification string into structured data.

        Args:
            spec_string: Module spec in format "module_name" or "module_name:sub1,sub2"

        Returns:
            ModuleSpec instance with parsed data

        Examples:
            >>> ModuleSpec.parse("deps")
            ModuleSpec(name="deps", sub_modules=None)

            >>> ModuleSpec.parse("claude_user_setting:commands,configs")
            ModuleSpec(name="claude_user_setting", sub_modules=["commands", "configs"])
        """
        if ":" in spec_string:
            module_name, sub_modules_str = spec_string.split(":", 1)
            sub_modules = [sm.strip() for sm in sub_modules_str.split(",") if sm.strip()]
            return cls(name=module_name.strip(), sub_modules=sub_modules)
        else:
            return cls(name=spec_string.strip(), sub_modules=None)

    @classmethod
    def parse_multiple(cls, spec_strings: List[str]) -> List["ModuleSpec"]:
        """Parse multiple module specification strings.

        Args:
            spec_strings: List of module spec strings

        Returns:
            List of ModuleSpec instances
        """
        return [cls.parse(spec) for spec in spec_strings]

    def __str__(self) -> str:
        """String representation for debugging."""
        if self.sub_modules:
            return f"{self.name}:{','.join(self.sub_modules)}"
        else:
            return self.name

    @property
    def has_sub_modules(self) -> bool:
        """Check if this spec includes sub-modules."""
        return self.sub_modules is not None and len(self.sub_modules) > 0
