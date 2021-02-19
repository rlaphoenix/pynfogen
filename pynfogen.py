import os
import re
import yaml

from helpers import scrape
from nfo import NFO


conditional_regex = re.compile(r"<\?(\w+)\?([\D\d]*?)\?>")

# Create NFO object
nfo = NFO()

# Set Configuration values from config.yml
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
    nfo.setConfig(yaml.load(f, Loader=yaml.FullLoader))

# Parse NFO template
with open(f"templates/{nfo.title_type}.nfo", "rt", encoding="utf-8") as f:
    template = f.read()
for i, m in enumerate(re.finditer(conditional_regex, template)):
    template = re.sub(
        "<\\?" + m.group(1) + "\\?([\\D\\d]*?)\\?>",
        m.group(2) if nfo.getVariable(m.group(1)) else "",
        template
    )
template_buffer = []
for line in template.splitlines():
    line = line.rstrip()
    for VarName in nfo.getVariables():
        VarNameS = f"%{VarName}%"
        if VarNameS not in line:
            continue
        pre = line[:line.index(VarNameS)]
        VarValue = nfo.getVariable(VarName)
        if isinstance(VarValue, int):
            VarValue = str(VarValue)
        elif isinstance(VarValue, list):
            if isinstance(VarValue[0], list):
                VarValue = f"\n{pre}".join([
                    f"\n{pre}".join([
                        y for y in x
                    ]) for x in VarValue
                ])
            else:
                VarValue = f"\n{pre}".join(VarValue)
        line = line.replace(VarNameS, VarValue or "")
    template_buffer.append(line)
template = "\n".join(template_buffer)

# Apply Art template
with open(f"art/{nfo.art}.nfo", "rt", encoding="utf-8") as f:
    template = f.read().replace("%nfo%", template)

# Strip unnecessary whitespace to reduce character count
template = "\n".join([line.rstrip() for line in template.splitlines()])

# Save template to file with release name, next to input file
with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.nfo"), "wt", encoding="utf-8") as f:
    f.write(template)

# generate bb code description
with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.desc.txt"), "wt", encoding="utf-8") as f:
    description = ""
    if nfo.preview_url:
        supported_domains = ["imgbox.com", "beyondhd.co"]
        for domain in supported_domains:
            if domain in nfo.preview_url.lower():
                page = scrape(nfo.preview_url)
                description += "[align=center]\n"
                if domain == "imgbox.com":
                    regex = 'src="(https://thumbs2.imgbox.com.+/)(\\w+)_b.([^"]+)'
                    bb_code = "[URL=https://imgbox.com/{1}][IMG]{0}{1}_t.{2}[/IMG][/URL]"
                elif domain == "beyondhd.co":
                    regex = '/image/([^"]+)"\\D+src="(https://beyondhd.co/images.+/(\\w+).md.[^"]+)'
                    bb_code = "[URL=https://beyondhd.co/image/{0}][IMG]{1}[/img][/URL]"
                for i, m in enumerate(re.finditer(regex, page)):
                    description += bb_code.format(*m.groups())
                    if (i % 2) != 0:
                        description += "\n"
                if not description.endswith("\n"):
                    description += "\n"
                description += "[/align]\n"
    description += f"[code]\n{template}\n[/code]"
    f.write(description)

print(f"Generated NFO for {nfo.release_name}")
