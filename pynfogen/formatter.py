import re
import textwrap
from string import Formatter
from typing import Any, List, Union


class CustomFormats(Formatter):
    def chain(self, value: Any, format_spec: str) -> Any:
        """Support chaining format specs separated by `:`."""
        for spec in format_spec.split(":"):
            value = self.format_field(value, spec)
        return value

    @staticmethod
    def boolean(value: Any, spec: str) -> int:
        """Return evaluated boolean value of input as a bool-int."""
        true = spec in ("true", "!false")
        false = spec in ("false", "!true")
        if not true and not false:
            raise ValueError("spec must be true, !false, false, or !true")
        b = bool(value)
        if false:
            b = not b
        return int(b)

    @staticmethod
    def length(value: Any) -> int:
        """Return object length."""
        return len(value)

    @staticmethod
    def bbimg(value: Union[List[Union[dict, str]], Union[dict, str]]) -> Union[List[str], str]:
        """Convert a list of values into a list of BBCode [LIST][IMG] strings."""
        if not value:
            return ""
        if not isinstance(value, list):
            value = [value]
        value = [({"url": x, "src": x} if not isinstance(x, dict) else x) for x in value]
        value = [f"[URL={x['url']}][IMG]{x['src']}[/IMG][/URL]" for x in value]
        if len(value) == 1:
            return value[0]
        return value

    @staticmethod
    def layout(value: Union[List[str], str], width: int, height: int, spacing: int) -> str:
        """Lay out data in a grid with specific lengths, heights, and spacing."""
        if not value:
            return ""
        if not isinstance(value, list):
            value = [value]
        if len(value) != width * height:
            # TODO: How about just ignore and try fill as much as it can?
            raise ValueError("Layout invalid, not enough images...")
        value = [(value[i:i + width]) for i in range(0, len(value), width)]
        value = [(" " * spacing).join(x) for x in value]
        value = ("\n" * (spacing + 1)).join(value)
        return value

    def wrap(self, value: Union[List[str], str], indent: int, width: int) -> str:
        """Text-wrap data at a specific width and indent amount."""
        if isinstance(value, list):
            return self.list_to_indented_strings(value, indent)
        return "\n".join(textwrap.wrap(value or "", width, subsequent_indent=" " * indent))

    @staticmethod
    def center(value: str, center_width: int, wrap_width: int) -> str:
        """Center data at a specific width, while also text-wrapping at a specific width."""
        return "\n".join([x.center(center_width) for x in textwrap.wrap(value or "", wrap_width)])

    def format_field(self, value: Any, format_spec: str) -> str:
        """Apply both standard formatters along with custom formatters to value."""
        if ":" in format_spec:
            return self.chain(value, format_spec)
        if format_spec in ("true", "!false", "false", "!true"):
            return str(self.boolean(value, format_spec))
        if format_spec == "len":
            return str(self.length(value))
        if format_spec == "bbimg":
            return self.bbimg(value)
        if re.match(r"^layout,\d+x\d+x\d+$", format_spec):
            return self.layout(value, *map(int, format_spec[7:].split("x")))
        if re.match(r"^>>\d+x\d+$", format_spec):
            return self.wrap(value, *map(int, format_spec[2:].split("x")))
        if re.match(r"^\^>\d+x\d+$", format_spec):
            return self.center(value, *map(int, format_spec[2:].split("x")))
        return super().format_field(value, format_spec)

    def list_to_indented_strings(self, value: list, indent: int = 0):
        """Recursively convert a list to an indented \n separated string."""
        if isinstance(value[0], list):
            return self.list_to_indented_strings(value[0], indent)
        return f"\n{' ' * indent}".join(value)
