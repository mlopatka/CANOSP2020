import csv
import sys
import json
import argparse
import pathlib
import re

from textpipe import pipeline


def preprocess_text(text):
    """
    Clean and process the raw ticket text
    
    text -- string to be preprocessed
    """
    # text = text.replace(",", "")  # remove commas
    # text = text.replace('"', "")  # remove double quotes
    pipe = pipeline.Pipeline(["CleanText"])

    text = text.replace("\n", "")  # remove newlines
    text = text.replace("\r", "")  # remove other newlines
    text = re.sub('<[^<]+?>', '', text)
    text = pipe(text)["CleanText"]
    text = re.sub('<[^<]+?>', '', text)

    return text


def write_ticket(csv_writer, ticket, taggers):
    """
    Writes a ticket as a row in the CSV file

    csv_writer -- csv.writer object
    ticket -- ticket dictionary
    taggers -- dictionary of taggers
    """
    ticket_id = ticket["ticket_id"]

    ticket_title = preprocess_text(ticket["title"])
    ticket_content = preprocess_text(ticket["content"])

    # CSV writer takes a list as a row
    ticket_list = [ticket_id, ticket_title, ticket_content]

    human_tagged = False

    # get tags for each tagger
    tag_dict = ticket["tags"]
    ticket_taggers = tag_dict.keys()
    for tagger in taggers:
        if tagger in ticket_taggers:
            if tagger != "0":
                human_tagged = True
            tags = preprocess_text("|".join(tag_dict[tagger]))  # using | as a delimeter for now
        else:
            tags = ""
        ticket_list.append(tags)
        # print(ticket_id, tagger, tags)

    # if human_tagged:
    csv_writer.writerow(ticket_list)
    # print(ticket_list)


def mturk_to_csv(mturk_path, tickets_json_path, csv_path):
    """
    Converts an MTurk CSV file into an annotation CSV file

    mturk_path -- path to the mechanical turk output CSV
    tickets_json_path -- path to the tickets JSON file
    csv_path -- path to the desired output CSV file (will be overwritten)
    """
    # Load ticket JSON
    with open(tickets_json_path, "r") as json_file:
        json_dict = json.loads(json_file.read())

    print(json_dict["tickets"][0])

    ticket_content_dict = {}
    # hash ticket title + content to the ticket itself, so we can match the MTurk tags with the other tags
    pipe = pipeline.Pipeline(["CleanText"])
    for ticket in json_dict["tickets"]:
        ticket_text = preprocess_text(preprocess_text(ticket["title"]) + preprocess_text(ticket["content"]))

        if ticket_text not in ticket_content_dict.keys():
            ticket_content_dict[ticket_text] = [ticket]
        else:
            ticket_content_dict[ticket_text] += [ticket]

    for ticket_text, tickets in ticket_content_dict.items():
        # take any duplicate tickets (same title and content) and consolidate the tags
        if len(tickets) >= 2:
            all_tags = {}
            for ticket in tickets:
                for tagger in ticket["tags"].keys():
                    if tagger not in all_tags.keys():
                        all_tags[tagger] = [ticket["tags"][tagger]]
                    else:
                        all_tags[tagger] += [ticket["tags"][tagger]]
            consolidated_tags = {}
            for tagger, tagger_tags in all_tags.items():
                longer_annotation = tagger_tags[0]
                for annotation in tagger_tags:
                    if len(annotation) > len(longer_annotation):
                        longer_annotation = annotation
                consolidated_tags[tagger] = longer_annotation
            tickets[0]["tags"] = consolidated_tags
        ticket_content_dict[ticket_text] = tickets[0]

    print(len(ticket_content_dict.values()))
    print(list(ticket_content_dict.values())[0])

    mturk_count = 0

    # Add the MTurk annotations to ticket objects loaded from the tickets_json
    csv.field_size_limit(sys.maxsize)   # increase max field size
    with open(mturk_path, "r", newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row["AssignmentStatus"] not in ("Approved", "Submitted"):
                continue

            ticket_text = preprocess_text(preprocess_text(row["Input.sumo-ticket-title"]) + preprocess_text(row["Input.sumo-ticket-text"]))

            tags = row["Answer.tags"].lower().replace("#", "").replace("\r", "").replace("\n", "").replace(",", " ").replace(";", " ").replace("|", " ").split(" ")

            tags = [tag for tag in tags if len(tag) >= 2]

            if len(tags) < 2:
                print("Skipped ticket (too few tags):", tags)
                continue

            try:
                ticket_content_dict[ticket_text]["tags"][row["WorkerId"]] = tags
                mturk_count += 1
            except:
                for ticket_text_ in ticket_content_dict.keys():
                    if ticket_text_[:30] == ticket_text[:30]:
                        ticket_content_dict[ticket_text_]["tags"][row["WorkerId"]] = tags
                        mturk_count += 1

            # print(ticket_content_dict[ticket_text])

    print(len(json_dict["tickets"]), type(json_dict["tickets"]), type(json_dict["tickets"][0]), json_dict["tickets"][0])

    json_dict["tickets"] = list(ticket_content_dict.values())

    print(len(json_dict["tickets"]), type(json_dict["tickets"]), type(json_dict["tickets"][0]), json_dict["tickets"][0])

    with open('data/mturk_tickets.json', 'w') as f:
        json.dump(json_dict, f)

    print("MTurk Count:", mturk_count)

    tickets = ticket_content_dict.values()
    
    taggers = {}
    for ticket in tickets:
        for tagger in ticket["tags"].keys():
            if tagger not in taggers.keys():
                taggers[tagger] = 1
            else:
                taggers[tagger] += 1

    print("Taggers:", sorted([(key, item) for key, item in taggers.items()], key=lambda x : x[1], reverse=True))
    taggers = sorted(list(taggers.keys()))

    num_tickets = 0
    num_unique_tickets = 0
    ticket_ids = set()

    # create CSV writer
    csv_file = open(csv_path, "w", newline="")
    csv_writer = csv.writer(csv_file, delimiter=",")

    # write the CSV header
    csv_columns = ["id", "title", "content"] + taggers
    csv_writer.writerow(csv_columns)
    # print(csv_columns)

    for ticket in tickets:
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
    parser = argparse.ArgumentParser(description="Take Mechanical Turk output and generate a master annotation CSV")
    parser.add_argument("--mturk_file", help="the relative path to the input MTurk CSV file", required=True)
    parser.add_argument("--tickets_json", help="the relative path to the ticket JSON file", required=True)
    parser.add_argument(
        "--output_file", help="the relative path to the output CSV file (will be overwritten if exists)", required=True
    )

    args = parser.parse_args()

    path = pathlib.Path()
    mturk_path = path / args.mturk_file
    tickets_path = path / args.tickets_json
    csv_path = path / args.output_file

    print("Input Path (Mechanical Turk):", mturk_path.absolute())
    print("Input Path (Tickets JSON):", tickets_path.absolute())
    print("Output Path (Annotations):  ", csv_path.absolute())

    # exit if the MTurk file doesn't exist
    if not mturk_path.exists():
        print("Error: mechanical turk file does not exist")
        exit(1)

    # exit if the JSON file doesn't exist
    if not tickets_path.exists():
        print("Error: tickets JSON file does not exist")
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
    mturk_to_csv(mturk_path, tickets_path, csv_path)
