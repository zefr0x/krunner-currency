"""Parse queries, send them to the API then parse the result."""
from typing import Optional, Generator
from functools import lru_cache
from itertools import groupby
from json import load as load_json, loads as loads_json
from pathlib import Path


BASE_API_URL = "https://duckduckgo.com/js/spice/currency"


class Converter:
    """Class to parse queries and convert currencies."""

    def __init__(self):
        """Create a requests session and load currencies data."""
        self.requests = __import__("requests.sessions").Session()
        # self.requests.proxies = {
        #     "http": "socks5h://127.0.0.1:9050",
        #     "https": "socks5h://127.0.0.1:9050",
        # }
        self.currencies_data = load_json(open("./data/iso-4217.json", "r"))
        self.alpha2_to_alpha3 = load_json(
            open("./data/iso-3166-1-alpha-2-to-iso-4217.json", "r")
        )

        self.flags_base_dir = Path.joinpath(Path(__name__).resolve().parent, "flags")

    @staticmethod
    def split_alpha_and_numbers(string: str) -> Generator:
        """Get a string and return list form numbers and alphas."""
        for k, g in groupby(string, str.isalpha):
            yield "".join(g)

    def get_currency_flag_path(self, currency_code: str) -> Optional[str]:
        """Take a currency code and return the path of its flag."""
        path = Path.joinpath(self.flags_base_dir, currency_code + ".png")
        if path.exists():
            return str(path)
        return None

    def query_parser(self, user_query: str) -> Optional[dict]:
        """Parse user input to a format that can be sent to the API."""
        query = user_query.upper().split()
        query0_parts = list(self.split_alpha_and_numbers(query[0]))
        if query[2] == "TO" and len(query) == 4:
            # 45 SRA to USD
            amount = query[0]
            from_currency = query[1]
            to_currency = query[3]
        elif query[1] == "TO" and len(query0_parts) == 2:
            # 45SRA to USD
            amount = query0_parts[0]
            from_currency = query0_parts[1]
            to_currency = query[2]
        elif len(query) == 3:
            # 45 SRA USD
            amount = query[0]
            from_currency = query[1]
            to_currency = query[2]
        elif len(query) == 2:
            if query[0][-1].replace(".", "", 1).isnumeric():
                # 45 SRA
                amount = query[0]
                from_currency = query[1]
                to_currency = "SAR"
            else:
                if (
                    len(query0_parts) == 2
                    and query0_parts[0].replace(".", "", 1).isnumeric()
                ):
                    # 45SAR USD
                    amount = query0_parts[0]
                    from_currency = query0_parts[1]
                    to_currency = query[1]
        else:
            return None

        # Check if the currency is valide and convert it to 3 alpha code if it was 2.
        if len(from_currency) == 3 and from_currency.isalpha():
            if from_currency not in self.currencies_data:
                return None
        elif len(from_currency) == 2 and from_currency.isalpha():
            try:
                from_currency = self.alpha2_to_alpha3[from_currency]
            except KeyError:
                return None
        else:
            return None
        if len(to_currency) == 3 and to_currency.isalpha():
            if to_currency not in self.currencies_data:
                return None
        elif len(to_currency) == 2 and to_currency.isalpha():
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

    @lru_cache(13)
    def get_data_from_api(self, from_currency: str, to_currency: str):
        """
        Fetch data from API.

        For privacy purposes it will request the rate only, rather than sending the amount.
        """
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
                int(converted_data["decimalDigits"]),
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
            "description": description,
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
