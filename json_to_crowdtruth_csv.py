import json
import csv
import argparse
import pathlib


class Counter:
    """Keeps statistics about the tickets and annotations"""

    judgment_id = 0

    ticket_ids = set()
    total_tickets = 0
    unique_tickets = 0

    annotation_ids = set()
    total_annotations = 0
    unique_annotations = 0


def preprocess_text(text):
    """Clean and process the raw ticket text"""
    text = text.replace(",", "")  # remove commas
    text = text.replace('"', "")  # remove double quotes
    text = text.replace("\n", "")  # remove newlines
    text = text.replace("\r", "")  # remove other newlines
    text = text.lower()
    return text


def write_annotations(csv_writer, ticket, taggers, counter):
    """Writes annotations as rows in the CSV file"""

    ticket_id = ticket["ticket_id"]

    # CSV writer takes a list as a row
    ticket_list = [ticket_id, "1/1/2020 00:02:00"]

    # get tags for each tagger
    tag_dict = ticket["tags"]

    for tagger in tag_dict.keys():
        # ignore SUMO tags
        if tagger == "0":
            continue

        # keeping statistics on total and unique annotation counts
        annotation_id = f"{ticket_id};{tagger}"
        counter.total_annotations += 1
        if annotation_id in counter.annotation_ids:
            continue
        counter.annotation_ids.add(annotation_id)
        counter.unique_annotations += 1

        # non-SUMO tagger --> write to CSV
        annotation_list = list(ticket_list) + [counter.judgment_id]
        counter.judgment_id += 1
        tags = "["
        for tag in tag_dict[tagger]:
            tags += f'"{preprocess_text(tag)}",'
        tags = tags[: len(tags) - 1]
        tags += "]"

        annotation_list.append("1/1/2020 00:00:00")
        annotation_list.append(tagger)
        annotation_list.append(tags)

        if len(tags) > 0:
            csv_writer.writerow(annotation_list)


def ticket_to_csv(json_path, csv_path):
    """Converts a ticket JSON file into a CSV file"""

    num_tickets = 0
    num_unique_tickets = 0

    # load JSON file
    with open(json_path, "r") as json_file:
        json_dict = json.loads(json_file.read())

    taggers = []
    for tagger in json_dict["taggers"]:
        taggers.append(tagger["tagger_id"])
    print("Taggers:", taggers)

    # create CSV writer
    csv_file = open(csv_path, "w", newline="")
    csv_writer = csv.writer(csv_file, delimiter=",")

    # write the CSV header
    # ticket_id end_time judgement_id start_time tagger_id tags
    csv_columns = ["_unit_id", "_created_at", "_id", "_started_at", "_worker_id", "keywords"]
    csv_writer.writerow(csv_columns)

    counter = Counter()

    for ticket in json_dict["tickets"]:
        # check for duplicates, update statistics
        counter.total_tickets += 1
        if ticket["ticket_id"] in counter.ticket_ids:
            continue
        counter.ticket_ids.add(ticket["ticket_id"])
        counter.unique_tickets += 1

        write_annotations(csv_writer, ticket, taggers, counter)

    csv_file.close()

    print(f"Finished writing annotations to {csv_path}")
    print(f"{counter.unique_tickets} tickets ({counter.total_tickets - counter.unique_tickets} duplicates)")
    print(
        f"{counter.unique_annotations} annotations ({counter.total_annotations - counter.unique_annotations} duplicates)"
    )


# this runs when you directly run the file (not when imported)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a ticket JSON file to a CSV format that CrowdTruth can read")
    parser.add_argument("--json_file", help="the relative path to the input JSON file", required=True)
    parser.add_argument(
        "--csv_file", help="the relative path to the output CSV file (will be overwritten if exists)", required=True
    )

    args = parser.parse_args()

    path = pathlib.Path()
    json_path = path / args.json_file
    csv_path = path / args.csv_file

    print("json_path: ", json_path.absolute())
    print("csv_path:  ", csv_path.absolute())

    # exit if the JSON file doesn't exist
    if not json_path.exists():
        print("Error: that json file does not exist")
        exit(1)

    # if the CSV file already exists, ask the user whether they want to overwrite it
    if csv_path.exists():
        while True:
            choice = input("Warning: that CSV file already exists. Overwrite? (y/n): ").lower()
            if choice == "y":
                break
            elif choice == "n":
                print("Exiting")
                exit(0)

    # convert JSON to CSV
    ticket_to_csv(json_path, csv_path)
