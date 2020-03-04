import json
import csv
import argparse
import pathlib
import random
import datetime
from textpipe import pipeline


def preprocess_text(text):
    """
    Clean and process the raw ticket text
    
    text -- string to be preprocessed
    """
    # text = text.replace(",", "")  # remove commas
    # text = text.replace('"', "")  # remove double quotes
    text = text.replace("\n", "")  # remove newlines
    text = text.replace("\r", "")  # remove other newlines

    pipe = pipeline.Pipeline(["CleanText"])

    return pipe(text)["CleanText"]


def write_ticket(csv_writer, ticket):
    """
    Writes a ticket as a row in the CSV file

    csv_writer -- csv.writer object
    ticket -- ticket dictionary
    """
    ticket_title = preprocess_text(ticket["title"])
    ticket_content = preprocess_text(ticket["content"])

    # CSV writer takes a list as a row
    # ticket_list = [ticket["ticket_id"], ticket_title, ticket_content]
    ticket_list = [ticket_title, ticket_content]

    csv_writer.writerow(ticket_list)


def ticket_to_csv(json_path, csv_path):
    """
    Converts a ticket JSON file into a CSV file, with ticket title and content as columns
    
    json_path -- path to the input JSON file
    csv_path -- path to the output CSV file
    """
    num_tickets = 2000  # how many tickets / rows we want in the output
    current_num_tickets = 0

    day_delta = 18 * 30  # consider tickets from now to day_delta days ago
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=day_delta)
    print(f"Cutoff time for random tickets: {cutoff_date.strftime('%b %d %Y %H:%M:%S')}")

    # load JSON file
    with open(json_path, "r") as json_file:
        json_dict = json.loads(json_file.read())

    # create set of human tagger IDs
    human_taggers = set()
    for tagger in json_dict["taggers"]:
        if tagger["tagger_id"] != "0":
            human_taggers.add(tagger["tagger_id"])
    print("Human Taggers:", human_taggers)

    tickets = json_dict["tickets"]
    ticket_ids = set()  # IDs of tickets we want in the output CSV

    # get the IDs of all tickets with >= 2 human annotations
    for ticket in tickets:
        ticket_taggers = ticket["tags"].keys()

        # set containing IDs of humans who tagged it
        human_ticket_taggers = human_taggers & set(ticket_taggers)

        if len(human_ticket_taggers) >= 2:  # >= 2 humans have tagged this ticket
            if ticket["ticket_id"] not in ticket_ids:
                ticket_ids.add(ticket["ticket_id"])
                current_num_tickets += 1

    print(f"{current_num_tickets} tickets with >= 2 human annotations included")

    # fill the rest with random tickets
    # note that this will loop forever if not enough tickets satisfying the conditions exist
    while current_num_tickets < num_tickets:
        ticket = random.choice(tickets)
        ticket_time = datetime.datetime.utcfromtimestamp(int(ticket["timestamp"]))

        if ticket["ticket_id"] not in ticket_ids and ticket_time > cutoff_date:
            ticket_ids.add(ticket["ticket_id"])
            current_num_tickets += 1

    # create CSV writer
    csv_file = open(csv_path, "w")
    csv_writer = csv.writer(csv_file, delimiter=",")

    # write the CSV header
    # csv_columns = ["ticket_id", "sumo-ticket-title", "sumo-ticket-text"]
    csv_columns = ["sumo-ticket-title", "sumo-ticket-text"]
    csv_writer.writerow(csv_columns)

    # write the tickets to the output CSV
    written_tickets = set()
    for ticket in tickets:
        if ticket["ticket_id"] in ticket_ids and ticket["ticket_id"] not in written_tickets:
            # write the ticket as a row in the CSV
            write_ticket(csv_writer, ticket)
            written_tickets.add(ticket["ticket_id"])

    csv_file.close()

    print(f"Wrote {len(written_tickets)} unique tickets to {csv_path}")


# this runs when you directly run the file (not when imported)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a ticket JSON file to CSV format, with ticket title and content as columns"
    )
    parser.add_argument("--json_file", help="the relative path to the input JSON file", required=True)
    parser.add_argument("--csv_file", help="the relative path to the output CSV file", required=True)

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
