import os
import re
import yaml

from helpers import scrape
from nfo import NFO


# Create NFO object
nfo = NFO()

# Set Configuration values from config.yml
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")) as f:
    nfo.setConfig(yaml.load(f, Loader=yaml.FullLoader))

# Parse NFO template
NFO = []
with open(f"templates/{nfo.title_type}.nfo", mode="rt", encoding="utf-8") as f:
    fs = f.read()
    conditional_regex = re.compile('<\\?(\\w+)\\?([\\D\\d]*?)\\?>')
    for i, m in enumerate(re.finditer(conditional_regex, fs)):
        fs = re.sub(
            '<\\?' + m.group(1) + '\\?([\\D\\d]*?)\\?>',
            m.group(2) if nfo.getVariable(m.group(1)) else "",
            fs
        )
    for line in fs.splitlines():
        line = line.rstrip("\n\r")
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
        NFO.append(line)
NFO = "\n".join(NFO)

# Apply Art template
with open(f"art/{nfo.art}.nfo", mode="rt", encoding="utf-8") as f:
    NFO = f.read().replace("%nfo%", NFO)

# Save NFO to file with release name, next to input file
with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.nfo"), "wt", encoding="utf-8") as f:
    f.write(NFO)

# generate bb code description
with open(os.path.join(os.path.dirname(nfo.file), f"{nfo.release_name}.desc.txt"), "wt", encoding="utf-8") as f:
    DESC = ""
    if nfo.preview_url:
        supported_domains = ["imgbox.com", "beyondhd.co"]
        for domain in supported_domains:
            if domain in nfo.preview_url.lower():
                page = scrape(nfo.preview_url)
                DESC += "[align=center]\n"
                if domain == "imgbox.com":
                    regex = 'src="(https://thumbs2.imgbox.com.+/)(\\w+)_b.([^"]+)'
                    template = "[URL=https://imgbox.com/{1}][IMG]{0}{1}_t.{2}[/IMG][/URL]"
                if domain == "beyondhd.co":
                    regex = '/image/([^"]+)"\\D+src="(https://beyondhd.co/images.+/(\\w+).md.[^"]+)'
                    template = "[URL=https://beyondhd.co/image/{0}][IMG]{1}[/img][/URL]"
                for i, m in enumerate(re.finditer(regex, page)):
                    DESC += template.format(*m.groups())
                    if (i % 2) != 0:
                        DESC += "\n"
                if not DESC.endswith("\n"):
                    DESC += "\n"
                DESC += "[/align]\n"
    DESC += f"[code]\n{NFO}\n[/code]"
    f.write(DESC)

print(f"Generated NFO for {nfo.release_name}")
