"""Parse queries, send them to the API then parse the result."""
from typing import Optional
from json import load as load_json, loads as loads_json
from pathlib import Path
from functools import lru_cache

# The next imports are on-time imports (imported when they are needed) to reduce memory usage:
# from requests.sessions import Session

BASE_API_URL = "https://duckduckgo.com/js/spice/currency"
# If you wanted to use tor, uncomment the next lines and comment the previous one.
# BASE_API_URL = (
#     "https://duckduckgogg42xjoc72x3sjasowoarfbgcmvfimaftt6twagswzczad.onion/"
#     + "js/spice/currency"
# )

PROXIES: dict = {}
# PROXIES = {
#     "http": "socks5h://127.0.0.1:9050",
#     "https": "socks5h://127.0.0.1:9050",
# }


class Converter:
    """Class to parse queries and convert currencies."""

    def __init__(self):
        """Create a requests session and load currencies data."""
        self.base_dir = Path(__file__).resolve().parent

    def get_currency_flag_path(self, currency_code: str) -> Optional[str]:
        """Take a currency code and return the path of its flag."""
        path = Path.joinpath(self.base_dir, "flags", currency_code + ".png")
        if path.exists():
            return str(path)
        return None

    def load_data(self, name: str):
        """Load data from file to memory."""
        if name == "currencies_data" and not hasattr(self, "currencies_data"):
            self.currencies_data = load_json(
                open(Path.joinpath(self.base_dir, "data/iso-4217.json"), "r")
            )
        elif name == "alpha2_to_alpha3" and not hasattr(self, "alpha2_to_alpha3"):
            self.alpha2_to_alpha3 = load_json(
                open(
                    Path.joinpath(
                        self.base_dir, "data/iso-3166-1-alpha-2-to-iso-4217.json"
                    ),
                    "r",
                )
            )
        elif name == "name_to_alpha3" and not hasattr(self, "name_to_alpha3"):
            self.name_to_alpha3 = load_json(
                open(
                    Path.joinpath(
                        self.base_dir, "data/name_and_namePlural_to_iso-4217.json"
                    ),
                    "r",
                )
            )
        elif name == "sympol_to_alpha3" and not hasattr(self, "sympol_to_alpha3"):
            self.sympol_to_alpha3 = load_json(
                open(
                    Path.joinpath(self.base_dir, "data/sympol_to_iso-4217.json"),
                    "r",
                )
            )

    def query_parser(self, user_query: str) -> Optional[dict]:
        """Parse user input to a format that can be sent to the API."""
        query = user_query.upper().split()
        if len(query) == 3:
            # 45 SRA USD || 45 $ SAR || 45 dollars euro || 45 riyal $
            amount = query[0]
            from_currency = query[1]
            to_currency = query[2]
        else:
            return None

        # Check if the currency is valide and convert it to 3 alpha code.
        self.load_data("sympol_to_alpha3")
        # TODO check for name
        if from_currency in self.sympol_to_alpha3:
            from_currency = self.sympol_to_alpha3[from_currency]
        elif len(from_currency) == 3 and from_currency.isalpha():
            self.load_data("currencies_data")
            if from_currency not in self.currencies_data:
                return None
        elif len(from_currency) == 2 and from_currency.isalpha():
            self.load_data("alpha2_to_alpha3")
            try:
                from_currency = self.alpha2_to_alpha3[from_currency]
            except KeyError:
                return None
        else:
            return None

        # Check if the currency is valide and convert it to 3 alpha code.
        # self.load_data("sympol_to_alpha3")
        # TODO check for name
        if to_currency in self.sympol_to_alpha3:
            to_currency = self.sympol_to_alpha3[to_currency]
        elif len(to_currency) == 3 and to_currency.isalpha():
            self.load_data("currencies_data")
            if to_currency not in self.currencies_data:
                return None
        elif len(to_currency) == 2 and to_currency.isalpha():
            self.load_data("alpha2_to_alpha3")
            try:
                to_currency = self.alpha2_to_alpha3[to_currency]
            except KeyError:
                return None
        else:
            return None

        try:
            return {
                "from": from_currency,
                "to": to_currency,
                "amount": float(amount),
            }
        except ValueError:
            # If the amount can't be converted to float.
            return None

    @lru_cache(3)
    def get_data_from_api(self, from_currency: str, to_currency: str):
        """
        Fetch data from API.

        For privacy purposes it will request the rate only, rather than sending the amount.
        """
        if not hasattr(self, "requests"):
            self.requests = __import__("requests.sessions").Session()
            self.requests.proxies = PROXIES

        response = self.requests.get(f"{BASE_API_URL}/1/{from_currency}/{to_currency}")
        return loads_json(response.text[19:-4])

    def get_results(
        self, amount: float, from_currency: str, to_currency: str
    ) -> Optional[dict]:
        """Send a request to the API to get the rates then calculate the result."""
        conversion_data = self.get_data_from_api(from_currency, to_currency)

        description = conversion_data["headers"]["description"]
        utc_timestamp = conversion_data["conversion"]["rate-utc-timestamp"]
        converted_data = self.currencies_data[to_currency]
        converted_flag = self.get_currency_flag_path(to_currency)
        try:
            converted_amount = round(
                float(conversion_data["conversion"]["converted-amount"]) * amount,
                converted_data["decimalDigits"],
            )
        except ValueError:
            # If the rate can't be converted to float.
            return None

        top_conversions = []
        for x in conversion_data["topConversions"]:
            data = self.currencies_data[x["to-currency-symbol"]]
            converted_amount_ = round(
                float(x["converted-amount"]) * amount, data["decimalDigits"]
            )
            top_conversions.append(
                {
                    "symbol": x["to-currency-symbol"],
                    "data": data,
                    "flag": self.get_currency_flag_path(x["to-currency-symbol"]),
                    "name": x["to-currency-name"],
                    "converted-amount": converted_amount_,
                }
            )

        return {
            "message": description,
            "amount": amount,
            "from": from_currency,
            "time": utc_timestamp,
            "result": converted_amount,
            "to-data": converted_data,
            "to_flag": converted_flag,
            "top_convertions": top_conversions,
        }

    def __call__(self, query) -> Optional[dict]:
        """Take a query and return a list of results."""
        parsed_input = self.query_parser(query)

        if parsed_input:
            results = self.get_results(
                parsed_input["amount"], parsed_input["from"], parsed_input["to"]
            )
            return results
        else:
            return None
