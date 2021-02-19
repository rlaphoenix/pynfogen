import re
import textwrap
from string import Formatter


class CustomFormats(Formatter):
    def format_field(self, value, format_spec: str):
        if ":" in format_spec:
            # add chaing support, e.g. {var:bbimg:layout,2x2x0}
            for spec in format_spec.split(":"):
                value = self.format_field(value, spec)
            return value
        if format_spec in ("true", "!false"):
            # e.g. {var:true} will return 1 if var is a truthy value, {var:!false} is an identical alternative
            return "1" if value else "0"
        if format_spec in ("false", "!true"):
            # e.g. {var:false} will return 1 if var is not a truthy value, {var:!true} is an identical alternative
            return "0" if value else "1"
        if format_spec == "bbimg":
            if not isinstance(value, list):
                value = [value]
            value = [({"url": x, "src": x} if not isinstance(x, dict) else x) for x in value]
            value = [f"[URL={x['url']}][IMG]{x['src']}[/IMG][/URL]" for x in value]
            if len(value) == 1:
                return value[0]
            return value
        if re.match(r"^layout,\d+x\d+x\d+$", format_spec):
            # e.g. {var:layout,3x2x1} will return the var list 3 items horizontally separated by 1 space, twice vertically by 1 (+1) lines.
            w, h, space = [int(x) for x in format_spec[7:].split("x")]  # w x h x spacer
            if not isinstance(value, list):
                value = [value]
            if len(value) != w * h:
                raise ValueError("Layout invalid, not enough images...")
            value = [(value[i:i + w]) for i in range(0, len(value), w)]
            value = [(" " * space).join(x) for x in value]
            value = ("\n" * (space + 1)).join(value)
            return value
        if re.match(r"^>>\d+x\d+$", format_spec):
            # e.g. {var:>>2x68} will textwrap each line (at 68 chars), and each line will be indented by 2 spaces
            indent, chars = [int(x) for x in format_spec[2:].split("x")]
            if isinstance(value, list):
                value = self.list_to_indented_strings(value, indent)
                return value
            return "\n".join(textwrap.wrap(value, chars, subsequent_indent=" " * indent))
        if re.match(r"^\^>\d+x\d+$", format_spec):
            # e.g. {var:^>70x68} will center each line (at 70 chars) and textwrap each line (at 68 chars)
            center, wrap = [int(x) for x in format_spec[2:].split("x")]
            return "\n".join([x.center(center) for x in textwrap.wrap(value, wrap)])
        return super().format_field(value, format_spec)

    def list_to_indented_strings(self, value: list, indent: int = 0):
        """Recursively convert a list to an indented \n separated string."""
        if isinstance(value[0], list):
            return self.list_to_indented_strings(value[0], indent)
        return f"\n{' ' * indent}".join(value)
