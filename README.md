# KRunner Currency
[![Get the runner from kde store](https://raw.githubusercontent.com/ZER0-X/badges/main/kde/store/get-the-app-runner.svg)](https://www.pling.com/p/1740976/)

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

# Privacy
The amount will not be sent to the API, but it will query the value of 1 currency unit to get the rate, then it will do the conversion locally.
## Using tor or any proxy
If i found a good reference for the Config method in KRunner i would've done this in a UI, but i didn't so you need to edit the source code for that feature.

Go to the source directory and open 'converter.py', then comment and uncomment the following lines:
- To use an union link if use want to use tor:
```python
- BASE_API_URL = "https://duckduckgo.com/js/spice/currency"
+ # BASE_API_URL = "https://duckduckgo.com/js/spice/currency"
- # BASE_API_URL = (
- #     "https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/"
- #     + "js/spice/currency"
- # )
+ BASE_API_URL = (
+     "https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/"
+     + "js/spice/currency"
+ )
```
- To specify a proxy to be used by the requests session:
```python
- PROXIES: dict = {}
+ # PROXIES: dict = {}
- # PROXIES = {
- #     "http": "socks5h://127.0.0.1:9050",
- #     "https": "socks5h://127.0.0.1:9050",
- # }
+ PROXIES = {
+     "http": "socks5h://127.0.0.1:9050",
+     "https": "socks5h://127.0.0.1:9050",
+ }
```

# Usage as a python module
```python
import converter
convert = converter.Converter()

# Parsing the input then returning the result
term = "48.120 eur sa"
result = convert(term)
# Or giving direct data without the need te be parsed
# amount: float, from_currency: str, to_currency: str
result = convert.get_results(48.120, "EUR", "SAR")
```

# Todo list
- [ ] Find better keyword
- [ ] Support convert by name by creating names dict
- [ ] Support convert by localized names
- [ ] Localize the displayed currencies names
