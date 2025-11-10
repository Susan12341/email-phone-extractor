thonimport os
from extractors.contact_parser import parse_contact_info
from outputs.exporters import export_data
from extractors.utils import load_urls

def run_scraper(input_file, output_format="json"):
    """
    Main function to run the Email & Phone Extractor scraper.
    
    :param input_file: The file containing a list of URLs to scrape.
    :param output_format: Desired output format (json, csv, xml, etc.)
    """
    urls = load_urls(input_file)
    results = []
    
    for url in urls:
        contact_info = parse_contact_info(url)
        results.append(contact_info)
    
    export_data(results, output_format)

if __name__ == "__main__":
    input_file = "data/inputs.sample.txt"
    output_format = "json"
    run_scraper(input_file, output_format)