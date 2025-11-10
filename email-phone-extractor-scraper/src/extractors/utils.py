thondef load_urls(file_path):
    """
    Load URLs from a text file.
    
    :param file_path: Path to the file containing URLs.
    :return: A list of URLs.
    """
    with open(file_path, "r") as file:
        urls = file.readlines()
    return [url.strip() for url in urls]