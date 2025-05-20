import gettext

gettext.bindtextdomain("telex", "/usr/share/locale")
gettext.textdomain("telex")
_ = gettext.gettext
