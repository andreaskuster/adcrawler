import functools

from adcrawler.scraper import BaseScraper, Region, Sorting


class Tutti(BaseScraper):

    def __init__(self):
        super().__init__(name="tutti_ch")

    def scrape(self, region: str = "all", sorting: str = "price_ascending"):
        """

        :param region:
        :param sorting:
        :return:
        """
        # prepare parameters
        param_config = self.config["request"]["parameters"]
        parameters: dict = {"region": param_config["region"][region],
                            "with_all_regions": param_config["with_all_regions"][region] if region in param_config["with_all_regions"] else None,
                            "aggregated": param_config["aggregated"],
                            "limit": param_config["limit"],
                            "o": param_config["o"],
                            "sp": param_config["sp"][sorting],
                            "st": param_config["st"]["offer"]}
        parameters = {param: parameters[param] for param in parameters if parameters[param] is not None}
        # fetch data from server
        self.fetch_url(parameters)
        # extract regular data
        self.extract_data()
        # prepare irregular data
        # url format: tutti.ch/[language]/vi/[location_info][region_name]/[category_info][name]/[subject]/[id]
        # remove: ., &
        # replace: space -> -, ä -> ae, ö -> oe, ü -> ue
        for i, item in zip(range(len(self.parsed_response)), self.parsed_response):
            url = "/".join(["https://tutti.ch",
                            item["language"],
                            "vi",
                            self.clean_param(item["location_info"]["region_name"]),
                            self.clean_param(item["category_info"]["name"]),
                            self.clean_param(item["subject"]),
                            item["id"]])
            self.data[i]["url"] = url

    def clean_param(self, string: str):
        # make lower case
        lower = string.lower()
        # remove chars: ., &
        removed = lower.replace(".", "").replace("&", "")
        # replace space -> -, ..
        return removed.replace(" ", "-").replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")


if __name__ == "__main__":   # pragma: no cover

    tutti = Tutti()
    tutti.scrape(region=Region.SG.value, sorting=Sorting.PRICE_ASCENDING.value)

    for item in tutti.data:
        print(item)
