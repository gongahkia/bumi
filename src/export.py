# ----- OUTPUT FORMATS -----

import json
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom


def export_to_csv(data, output_file, data_key=None):
    """
    exports scraped data to CSV format

    Args:
        data: dict or list of dicts to export
        output_file: path to output CSV file
        data_key: if data is nested dict, key to extract list from

    Returns:
        path to created CSV file
    """
    # extract list from nested structure if needed
    if data_key and isinstance(data, dict):
        items = data.get(data_key, [])
    elif isinstance(data, list):
        items = data
    else:
        items = [data]

    if not items:
        print("No data to export")
        return None

    # flatten nested dicts for CSV
    def flatten_dict(d, parent_key="", sep="_"):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key, sep).items())
            elif isinstance(v, list):
                items.append((new_key, str(v)))
            else:
                items.append((new_key, v))
        return dict(items)

    flattened = [
        flatten_dict(item) if isinstance(item, dict) else {"value": item}
        for item in items
    ]

    # get all unique keys
    all_keys = set()
    for item in flattened:
        all_keys.update(item.keys())
    fieldnames = sorted(all_keys)

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened)

    print(f"Exported {len(flattened)} items to {output_file}")
    return output_file


def export_to_xml(data, output_file, root_element="data"):
    """
    exports scraped data to XML format

    Args:
        data: dict to export
        output_file: path to output XML file
        root_element: name of root XML element

    Returns:
        path to created XML file
    """

    def dict_to_xml(d, parent):
        for key, value in d.items():
            # sanitize key for XML element name
            safe_key = str(key).replace(" ", "_").replace("-", "_")
            if not safe_key[0].isalpha():
                safe_key = "item_" + safe_key

            if isinstance(value, dict):
                child = ET.SubElement(parent, safe_key)
                dict_to_xml(value, child)
            elif isinstance(value, list):
                list_el = ET.SubElement(parent, safe_key)
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        item_el = ET.SubElement(list_el, "item")
                        dict_to_xml(item, item_el)
                    else:
                        item_el = ET.SubElement(list_el, "item")
                        item_el.text = str(item) if item is not None else ""
            else:
                child = ET.SubElement(parent, safe_key)
                child.text = str(value) if value is not None else ""

    root = ET.Element(root_element)
    if isinstance(data, dict):
        dict_to_xml(data, root)
    elif isinstance(data, list):
        for item in data:
            item_el = ET.SubElement(root, "item")
            if isinstance(item, dict):
                dict_to_xml(item, item_el)
            else:
                item_el.text = str(item)

    # pretty print
    xml_str = ET.tostring(root, encoding="unicode")
    pretty_xml = minidom.parseString(xml_str).toprettyxml(indent="  ")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    print(f"Exported to {output_file}")
    return output_file


def export_to_json(data, output_file, indent=2):
    """
    exports scraped data to JSON format

    Args:
        data: data to export
        output_file: path to output JSON file
        indent: indentation level for pretty printing

    Returns:
        path to created JSON file
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
    print(f"Exported to {output_file}")
    return output_file


def export_data(data, output_file, format="json"):
    """
    exports data to specified format

    Args:
        data: data to export
        output_file: output file path (extension added if missing)
        format: 'json', 'csv', or 'xml'

    Returns:
        path to created file
    """
    format = format.lower()
    if format == "json":
        if not output_file.endswith(".json"):
            output_file += ".json"
        return export_to_json(data, output_file)
    elif format == "csv":
        if not output_file.endswith(".csv"):
            output_file += ".csv"
        return export_to_csv(data, output_file)
    elif format == "xml":
        if not output_file.endswith(".xml"):
            output_file += ".xml"
        return export_to_xml(data, output_file)
    else:
        raise ValueError(f"Unsupported format: {format}. Use 'json', 'csv', or 'xml'")


def pretty_print_json(json_object):
    """pretty prints a JSON object to stdout"""
    print(json.dumps(json_object, indent=2, ensure_ascii=False))
