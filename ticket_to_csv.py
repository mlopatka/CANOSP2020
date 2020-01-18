import json
import csv
import argparse
import pathlib


def preprocess_text(text):
    """Clean and process the raw ticket text"""
    text = text.replace(",", "")  # remove commas
    text = text.replace("\"", "")  # remove double quotes
    return text


def write_ticket(csv_writer, ticket, taggers):
    """Writes a ticket as a row in the CSV file"""
    ticket_id = ticket["ticket_id"]

    ticket_title = preprocess_text(ticket["title"])
    ticket_content = preprocess_text(ticket["content"])

    # CSV writer takes a list as a row
    ticket_list = [ticket_id, ticket_title, ticket_content]

    # get tags for each tagger
    tag_dict = ticket["tags"]
    ticket_taggers = tag_dict.keys()
    for tagger in taggers:
        if tagger in ticket_taggers:
            tags = "|".join(tag_dict[tagger])   # using | as a delimeter for now
        else:
            tags = ""
        ticket_list.append(tags)
        # print(ticket_id, tagger, tags)

    csv_writer.writerow(ticket_list)
    # print(ticket_list)


def ticket_to_csv(json_path, csv_path):
    """Converts a ticket JSON file into a CSV file"""
    num_tickets = 0
    num_unique_tickets = 0
    ticket_ids = set()

    # load JSON file
    with open(json_path, "r") as json_file:
        json_dict = json.loads(json_file.read())

    taggers = []
    for tagger in json_dict["taggers"]:
        taggers.append(tagger["tagger_id"])
    # print("Taggers:", taggers)

    # create CSV writer
    csv_file = open(csv_path, "w", newline="")
    csv_writer = csv.writer(csv_file, delimiter=",")

    # write the CSV header
    csv_columns = ["id", "title", "content"] + taggers
    csv_writer.writerow(csv_columns)

    for ticket in json_dict["tickets"]:
        # check for duplicates, update statistics
        num_tickets += 1
        if ticket["ticket_id"] in ticket_ids:
            continue
        ticket_ids.add(ticket["ticket_id"])
        num_unique_tickets += 1

        # write the ticket as a row in the CSV
        write_ticket(csv_writer, ticket, taggers)

    csv_file.close()

    print(f"Wrote {num_unique_tickets} tickets to {csv_path} ({num_tickets - num_unique_tickets} duplicates)")


# this runs when you directly run the file (not when imported)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a ticket JSON file to CSV format")
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
