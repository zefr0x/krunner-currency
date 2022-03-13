#!/bin/bash

# Exit if something fails
set -e

/usr/bin/python3 -m pip install requests

mkdir -p ~/.local/share/kservices5/
mkdir -p ~/.local/share/dbus-1/services/

cat "plasma-runner-currency.desktop" > ~/.local/share/kservices5/plasma-runner-currency.desktop
sed "s|%{PROJECTDIR}/%{APPNAMELC}.py|${PWD}/main.py|" "com.github.zer0-x.krunner-currency.service" > ~/.local/share/dbus-1/services/com.github.zer0-x.krunner-currency.service

kquitapp5 krunner
