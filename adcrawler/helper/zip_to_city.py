import os


zip2city = None


def zip_to_city(zip_code: str):
    """
    Returns the human readable city name from any Swiss zip code.
    :param zip_code: zip code
    :return: city name of given zip code
    """
    # check if data has been loaded from file
    if zip2city is None:
        load_zip_map()
    # return value
    return zip2city[zip_code]


def load_zip_map():
    """
    Loads the zip code to city mapping from the external file.
    """
    # use global var
    global zip2city
    # init dict
    zip2city = dict()
    # open csv file
    with open(os.path.join(os.path.dirname(__file__), "zip_codes.csv")) as f:
        # first column: titles
        title = f.readline().split(",")
        # loop over all entries
        for line in f.readlines():
            # split values
            zip, city, canton = line.split(",")
            # use first occurrence
            if zip not in zip2city:
                zip2city[zip] = city

# data source: Swiss Post (post.ch)
# version: Post_Adressdaten20200421


if __name__ == "__main__":  # pragma: no cover
    # do a lookup
    zip_code = "9200"
    city = zip_to_city(zip_code)
    # report result
    print("City with zip code {} is: {}".format(zip_code, city))
