#!/usr/bin/python3
"""Plasma runner for converting currencies."""
from gettext import gettext, bindtextdomain, textdomain

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

# The next imports are on-time imports (imported when they are needed) to reduce memory usage:
# from converter import Converter

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

    def get_converter(self) -> None:
        """Check if there wasn't Converter object then create new one."""
        if not hasattr(self, "converter"):
            self.converter = __import__("converter").Converter()
        return None

    @dbus.service.method(IFACE, in_signature="s", out_signature="a(sssida{sv})")
    def Match(self, query: str) -> list:
        """Get the matches and return a list of tupels."""
        returns: list[tuple] = []

        if query.startswith(key_word + " "):
            self.get_converter()
            results = self.converter(query[key_word_length:])

            if results:
                relevance = 1.0
                if results["message"]:
                    returns.append(
                        (
                            "",
                            results["message"],
                            icon_path,
                            100,
                            relevance,
                            {"actions": ""},
                        )
                    )

                relevance -= 0.1
                returns.append(
                    (
                        f'{results["amount"]} {results["from"]} '
                        + f'= {results["result"]} {results["to-data"]["code"]}',
                        f'{results["result"]} {results["to-data"]["symbol"]}',
                        results["to_flag"] or icon_path,
                        100,
                        relevance,
                        {"subtext": results["to-data"]["name"]},
                    )
                )

                for conversion in results["top_convertions"]:
                    relevance -= 1
                    returns.append(
                        (
                            f'{results["amount"]} {results["from"]} '
                            + f'= {conversion["converted-amount"]} {conversion["data"]["code"]}',
                            f'{conversion["converted-amount"]} {conversion["data"]["symbol"]}',
                            conversion["flag"] or icon_path,
                            100,
                            relevance,
                            {"subtext": conversion["data"]["name"]},
                        )
                    )
            elif results == {}:
                returns.append(
                    (
                        "",
                        _("Error: Unable to fetch or parse data from API."),
                        icon_path,
                        100,
                        1.0,
                        {"actions": ""},
                    )
                )
            elif results is None:
                returns.append(
                    (
                        "",
                        _("Error: Unable to parse the input"),
                        icon_path,
                        100,
                        1.0,
                        {"actions": ""},
                    )
                )

        return returns

    @dbus.service.method(IFACE, out_signature="a(sss)")
    def Actions(self) -> list:
        """Return a list of actions."""
        return [
            ("copy_result", _("Copy result"), "edit-copy"),
            ("copy_convertion", _("Copy convertion"), "exchange-positions"),
            ("copy_link", _("Copy a link to the convertion in xe.com"), "link"),
        ]

    @dbus.service.method(IFACE, in_signature="ss")
    def Run(self, data: str, action_name: str) -> None:
        """Handle actions calls."""
        data_parts = data.split()

        if action_name == "" and data:
            # When clicking on the results.
            # Create krunner dbus iface.
            krunner_iface = dbus.Interface(
                dbus.SessionBus().get_object("org.kde.krunner", "/App"),
                "org.kde.krunner.App",
            )

            krunner_iface.querySingleRunner(
                "currency-runner",
                f"{key_word} {data_parts[0]} {data_parts[4]} {data_parts[1]}",
            )
        else:
            # When clicking on the actions buttons.
            # Create klipper dbus iface.
            klipper_iface = dbus.Interface(
                dbus.SessionBus().get_object("org.kde.klipper", "/klipper"),
                "org.kde.klipper.klipper",
            )

            if action_name == "copy_result":
                klipper_iface.setClipboardContents(data_parts[3])
            elif action_name == "copy_convertion":
                klipper_iface.setClipboardContents(data)
            elif action_name == "copy_link":
                klipper_iface.setClipboardContents(
                    "https://www.xe.com/currencyconverter/convert/"
                    + f"?Amount={data_parts[0]}&From={data_parts[1]}&To={data_parts[4]}"
                )

        return None

    @dbus.service.method(IFACE)
    def Teardown(self) -> None:
        """Sava memory by deleting objects when not needed and cleaning cache."""
        # TODO keep cache for longer time.
        self.converter.get_data_from_api.cache_clear()
        del self.converter
        return None


runner = Runner()
loop = GLib.MainLoop()
loop.run()
