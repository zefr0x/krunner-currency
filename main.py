#!/usr/bin/python3
"""Plasma runner for converting currencies."""
from gettext import gettext, bindtextdomain, textdomain

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from converter import Converter

bindtextdomain("messages", "locales")
textdomain("messages")
_ = gettext

key_word = _("~")
key_word_length = len(key_word) + 1

icon_path = "view-financial-account-cash"

DBusGMainLoop(set_as_default=True)
OBJPATH = "/krunnerCurrency"
IFACE = "org.kde.krunner1"
SERVICE = "com.github.zer0-x.krunner-currency"


class Runner(dbus.service.Object):
    """Comunicate with KRunner, deal with queries, provide and run actions."""

    def __init__(self) -> None:
        """Create dbus service."""
        dbus.service.Object.__init__(
            self,
            dbus.service.BusName(SERVICE, dbus.SessionBus()),
            OBJPATH,
        )

        return None

    @dbus.service.method(IFACE, in_signature="s", out_signature="a(sssida{sv})")
    def Match(self, query: str) -> list:
        """Get the matches and return a list of tupels."""
        return [
            (
                "Test data",
                _("Test message"),
                icon_path,
                100,
                1.0,
                {},
            )
        ]

    @dbus.service.method(IFACE, out_signature="a(sss)")
    def Actions(self) -> list:
        """Return a list of actions."""
        return [("0", _("Tex me"), "action-unavailable-symbolic")]

    @dbus.service.method(IFACE, in_signature="ss")
    def Run(self, data: str, action_id: str) -> None:
        """Handle actions calls."""
        return None

    @dbus.service.method(IFACE)
    def Teardown(self) -> None:
        """Sava memory by closing database connection when not needed."""
        return None


runner = Runner()
loop = GLib.MainLoop()
loop.run()
