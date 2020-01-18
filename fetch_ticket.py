import json
import pytz
import math
import requests
import logging
import os
import dateutil.parser as dp
import click
import csv
import errno

from datetime import datetime
from typing import Dict, List

from urllib.parse import urljoin

SUMO_API_ROOT = "https://support.mozilla.org/api/2/"


logging.info("start logging")
logger = logging.getLogger("fetch_ticket")


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


# https://stackoverflow.com/a/23794010
def safe_open_w(path, mode="wt"):
    mkdir_p(os.path.dirname(path))
    return open(path, mode)


def archive_page(data, page, dir="./raw_data/"):
    with open(os.path.join(dir, f"tickets_{page}.json"), "w") as f:
        json.dump(data, f)


def transform_results(data):
    tickets = []
    for raw_ticket in data["results"]:
        tickets.append(
            {
                "ticket_id": raw_ticket["id"],
                "title": raw_ticket["title"],
                "content": raw_ticket["content"],
                "timestamp": convert_pst_to_utc(raw_ticket["created"]),
                "tags": {
                    # sumo tags
                    "0": [each["slug"] for each in raw_ticket["tags"]]
                },
            }
        )
    return tickets


# https://github.com/mozilla-it/sumo/blob/master/Kitsune/get_kitsune_data.py
def convert_pst_to_utc(dt_str):
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    pacific = pytz.timezone("US/Pacific")
    loc_dt = pacific.localize(datetime.strptime(dt_str, fmt))
    dt_utc = loc_dt.astimezone(pytz.utc)
    return dp.parse(dt_utc.strftime(fmt)).strftime("%s")


def get_question_data(api_url_base, params):
    api_url = "{0}?_method=GET".format(api_url_base)

    results = []
    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        raw = response.json()
        # archive_page(transform_results(raw), 1)
        archive_page(transform_results(raw), 13379)

        print(f"total count: {raw['count']}")
        total_pages = math.ceil(raw["count"] / 20.0)
        print(f"total pages: {total_pages}")

        # while raw['next'] is not None:
        for page in range(13380, total_pages):
            params["page"] = str(page)
            print(page)
            response = requests.get(api_url, params=params)

            if response.status_code == 200:
                raw = response.json()
                archive_page(transform_results(raw), page)
            else:
                print("[!] HTTP {0} calling [{1}]".format(response.status_code, raw["next"]))  # 401 unauthorized

        logger.info("returning results")
        return results

    else:
        print("[!] HTTP {0} calling [{1}]".format(response.status_code, api_url))  # 401 unauthorized
        return Nonesy


def fetch_sumo_tagged():
    query_string = {
        "format": "json",
        "product": "firefox",
        "locale": "en-US",
        "ordering": "-created",
        "created__lt": "2020-01-17 00:00:00",
        "page": 13379,
    }

    results = get_question_data("https://support.mozilla.org/api/2/question", query_string)


def get_pages(dir="raw_data") -> List[Dict]:
    if not os.path.isdir(dir):
        raise Exception('Directory "{}" does not exist.'.format(dir))

    (dirpath, _, filenames) = next(os.walk(dir))
    filenames = sorted([filename for filename in filenames if filename.endswith(".json")])

    tickets = []
    for filename in filenames:
        with open(os.path.join(dirpath, filename)) as input_f:
            tickets.extend(json.load(input_f))
    return tickets


def merge_tickets():
    """
    Merge tickets by pages and put crowdsource tags in as well.
    """
    # read all taggers info
    taggers = {}
    with open("csv/sheets/taggers.csv") as f:
        reader = csv.reader(f)
        next(reader, None)
        taggers = {
            row[1]: {"tagger_id": row[1], "is_expert": True if row[2] == "1" else False, "is_sumo": False}
            for row in reader
        }

    # read all crowdsource tickets and tags
    crowdsouce_tickets = {}
    with open("csv/sheets/tickets.csv") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if crowdsouce_tickets.get(row[3], None):
                crowdsouce_tickets[row[3]]["tags"][row[2]] = row[1].split(";") if row[1] else []
            else:
                crowdsouce_tickets[row[3]] = {
                    "ticket_id": row[3],
                    "tags": {row[2]: row[1].split(";") if row[1] else []},
                }

    # read all tickets from raw_data folder
    tickets = get_pages()
    output_tickets = []

    for each in tickets:
        ticket_id = each["ticket_id"]
        if crowdsouce_tickets.get(str(ticket_id), None):
            sumo_tags = each["tags"]
            crowdsource_tags = crowdsouce_tickets[str(ticket_id)]["tags"]
            output_tickets.append(
                {
                    "ticket_id": str(each["ticket_id"]),
                    "title": each["title"],
                    "content": each["content"],
                    "timestamp": each["timestamp"],
                    "tags": {**sumo_tags, **crowdsource_tags},
                }
            )
        else:
            output_tickets.append(each)

    with safe_open_w("data/tickets.json") as f:
        json.dump(
            {
                "created_timestamp": datetime.utcnow().strftime("%s"),
                "last_updated_timestamp": datetime.utcnow().strftime("%s"),
                "tickets": output_tickets,
                "taggers": list(taggers.values()),
            },
            f,
        )


@click.command()
@click.argument("command", required=True)
def main(command):
    """
    fetch_ticket.py [fetch|merge]
    """
    if command == "fetch":
        tickets = fetch_sumo_tagged()

    if command == "merge":
        merge_tickets()


if __name__ == "__main__":
    main()
