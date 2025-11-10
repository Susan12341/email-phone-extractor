thonimport json
import csv

def export_data(data, output_format):
    """
    Export scraped data to the specified format.
    
    :param data: The data to export.
    :param output_format: The format to export the data to (json, csv, xml, etc.).
    """
    if output_format == "json":
        export_json(data)
    elif output_format == "csv":
        export_csv(data)
    elif output_format == "xml":
        export_xml(data)
    else:
        raise ValueError(f"Unsupported format: {output_format}")

def export_json(data):
    """Export data to a JSON file."""
    with open("output.json", "w") as f:
        json.dump(data, f, indent=4)

def export_csv(data):
    """Export data to a CSV file."""
    with open("output.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

def export_xml(data):
    """Export data to an XML file."""
    # Example implementation for exporting to XML (simplified)
    with open("output.xml", "w") as f:
        f.write("<contacts>\n")
        for entry in data:
            f.write("  <contact>\n")
            for key, value in entry.items():
                f.write(f"    <{key}>{value}</{key}>\n")
            f.write("  </contact>\n")
        f.write("</contacts>\n")