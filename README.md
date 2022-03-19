# KRunner Currency
[![Get the runner from kde store](https://raw.githubusercontent.com/ZER0-X/badges/main/kde/store/get-the-app-runner.svg)](https://www.pling.com/p/)

A KRunner plugin for converting currencies using DuckDuckGo spice API.

# Installation
## Dependencies
- python-requests
> If you dan't have `requests` installed the `install.sh` script will use `pip` to install it.
## Install from git source code
Go to the directory that you want to keep the code in it, for example `/home/<username>/.local/share/krunner-sources/`.
```bash
$ git clone https://github.com/zer0-x/krunner-currency.git
$ cd krunner-currency
$ ./install.sh
```
🔴 Don't delete the source code after the installation.
### Uninstall
Go to the source code directory and run the uninstall script:
```bash
$ ./uninstall.sh
```

## Install from the kde store
1. Open system settings
2. Go to `search` > `KRunner`
3. Click on `Get New Plugins...`
4. Search for the Plugin
5. Click `Install`
### Uninstall
Please run the uninstall script manually, because the GUI will remove the script before running it.

# Usage
## terms
You are able to use any type of the following terms:
- `13 SAR USD`
- `13.64 sar usd`
- `13 SAR $`
- `13 SR $`
- `13 US euro` - Not available yet.
- `13 dollars riyal` - Not available yet.
> Not all the currencies are supporter when using a symbol or a name. Take a lock on the `data/` directory.
## qeury
1. Type the keyword `~` in KRunner.
2. type `<Space>` and then writer your conversion term.
3. Click `<Enter>` to flip the conversion.
4. Also you are able to use the actions to copy the result, copy the conversion or copy the URL for the conversion in xe.com

# Todo list
- [ ] Find better keyword
- [ ] Support convert by name by creating names dict
- [ ] Support convert by localized names
- [ ] Localize the displayed currencies names
