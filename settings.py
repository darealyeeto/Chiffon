from dataclasses import dataclass

compatibility_url = "https://raw.githubusercontent.com/m4fn3/AddonManagerDatabase/master/compatibility.json"
# compatibility_url = "https://cdn.discordapp.com/attachments/1009459069087649792/1124373630474784940/compatibility.json"
plugins_url = "https://raw.githubusercontent.com/m4fn3/AddonManagerDatabase/master/plugins.json"
# plugins_url = "https://cdn.discordapp.com/attachments/1009459069087649792/1124369428159676427/plugins.json"
themes_url = "https://raw.githubusercontent.com/m4fn3/AddonManagerDatabase/master/themes.json"
# themes_url = "https://raw.githubusercontent.com/m4fn3/AddonManagerDatabase/master/themes.json"

plugin_install_scheme = "discord://enmity?id=-1&command=install-plugin&params=%s"
theme_install_scheme = "discord://enmity?id=-1&command=install-theme&params=%s"

plugin_update_channel = 1124388879378698281
theme_update_channel = 1124389265288212512


@dataclass(frozen=True)
class Emojis:
    warn = '<:warn:1123285288546996345>'
    xx = '<:xx:1123285292279939243>'
    oo = '<:oo:1123285295568261200>'
