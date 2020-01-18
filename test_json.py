import pytest
import jsonschema
import json

SCHEMA = {
    "type" : "object",
    "properties" : 
    {
        "created_timestamp" : {"type" : "number"},
        "last_updated_timestamp" : {"type" : "number"},
        "tickets" : {"type" : "array",
                     "items" : [
                     {"type" : "object",
                      "properties" : {
                           "ticket_id" : {"type" : "string"},
                           "title" : {"type" : "string"},
                           "content" : {"type" : "string"},
                           "timestamp" : {"type" : "number"},
                           "tags" : {"type" : "object"}
                                     }
                     }
                                ]
                     },
        "taggers" : {"type" : "array",
                     "items" : [
                      {"type" : "object",
                       "properties" : {
                            "tager_id" :{"type" : "string"},
                            "is_expert" : {"type" : "boolean"},
                            "is_sumo" : {"type" : "boolean"}
                       }}
                            ]
                    }
    },
}


def json_producer():
    return(
        {
            "created_timestamp": 1579302881,
            "last_updated_timestamp": 1579302881,
            "tickets": [
                {
                    "ticket_id": "1",
                    "title": "Example Ticket Title 1",
                    "content": "Example Ticket Body 1",
                    "timestamp": 1579302881,
                    "tags": {
                        "1": [
                            "tag1",
                            "tag2",
                            "tag3"
                        ],
                        "2": [
                            "tag3",
                            "tag4",
                            "tag5"
                        ]
                    }
                },
                {
                    "ticket_id": "2",
                    "title": "Example Ticket Title 2",
                    "content": "Example Ticket Body 2",
                    "timestamp": 1579302881,
                    "tags": {
                        "1": [
                            "tag1",
                            "tag2",
                            "tag3"
                        ],
                        "2": [
                            "tag3",
                            "tag4",
                            "tag5"
                        ]
                    }
                }
            ],
            "taggers": [
                {
                    "tagger_id": "1",
                    "is_expert": True,
                    "is_sumo": False
                },
                {
                    "tagger_id": "2",
                    "is_expert": False,
                    "is_sumo": False
                }
            ]
        }
    )

def test_json_schema():

    json_dict = json_producer()
    assert jsonschema.validate(instance = json_dict, schema = SCHEMA) is None
