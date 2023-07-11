class DotDict(dict):
    """ dot accessible dict """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


developers = [519760564755365888]

compatibility_url = "https://raw.githubusercontent.com/m4fn3/AddonManagerDatabase/master/compatibility.json"
plugins_url = "https://raw.githubusercontent.com/m4fn3/AddonManagerDatabase/master/plugins.json"
themes_url = "https://raw.githubusercontent.com/m4fn3/AddonManagerDatabase/master/themes.json"

plugin_install_scheme = "discord://enmity?id=-1&command=install-plugin&params=%s"
theme_install_scheme = "discord://enmity?id=-1&command=install-theme&params=%s"

chiffon_guild = 1123260961931927672
plugin_update_channel = 1124388879378698281
theme_update_channel = 1124389265288212512

plugins_channel = 961782195767365732
themes_channel = 961782176062509117
message_link = "https://discord.com/channels/950850315601711176/%d/%d"

dropdown_timeout = 30

emojis = DotDict({
    "warn": '<:warn:1123285288546996345>',
    "xx": '<:xx:1123285292279939243>',
    "oo": '<:oo:1123285295568261200>',
    "plugin": '<:plugin:1128346794074587196>',
    "theme": '<:theme:1128346796981239878>'
})
