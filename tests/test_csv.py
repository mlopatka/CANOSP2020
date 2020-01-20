import pytest
import csv

DATA = []


def CSV_producer():

    data_list = [
        ["ticket_url", "tags", "tagger_id", "ticket_id", "is_expert", "is_sumo"],
        [
            "https://support.mozilla.org/questions/1276631",
            "prefereces;ui;ux;rendering;linux;kde;search-bar;version;interface;button",
            "1",
            "1276631",
            "0",
            "0",
        ],
        [
            "https://support.mozilla.org/questions/1276635",
            "phishing;scam;webcompat;freeze;froze;crash",
            "1",
            "1276635",
            "0",
            "0",
        ],
    ]
    with open("tests/ticket_csv_schema.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(data_list)


def test_columns_length():

    CSV_producer()

    with open("tests/ticket_csv_schema.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            assert len(row) == 6
            DATA.append(row)


def test_columns_title():

    assert DATA[0] == ["ticket_url", "tags", "tagger_id", "ticket_id", "is_expert", "is_sumo"]


def test_empty_columns():

    for row in DATA[1:]:
        for column in row:
            assert len(column) > 0


def test_number_columns():

    for row in DATA[1:]:
        numbers = row[2:]
        for number in numbers:
            assert number.isdigit()


def test_boolean_value():

    for row in DATA[1:]:
        export_value = row[-2]
        sumo_value = row[-1]
        assert export_value == "0" or export_value == "1"
        assert sumo_value == "0" or sumo_value == "1"


def test_ticket_id():

    for row in DATA[1:]:
        ticket_id = row[-3]
        ticket_url = row[0]
        assert ticket_id == ticket_url[-7:]
