# CANOSP2020

## Motivation

Firefox desktop users file anywhere from 30 support tickets per day during quiet times up to 50 or more support tickets per day just after new releases at support.mozilla.org (SUMO). In the event of a Firefox incident, we can receive almost 300 tickets in one day (e.g., the add-on incident in 2019 [1]). While this is too much for staff and volunteers to tag manually, annotations provide immense value when triaging and responding to support questions.

## Scope

In our project we are going to focus on questions related to only Firefox desktop forum questions. 

## Outline

The aim of this project is to develop and evaluate a prototype system for enriching support request submissions by automated annotation and language analysis. Our goal is to achieve accurate annotations consistent with human reviewers. 

The project will consist of three main work products:

- Language modelling of support tickets
    - Development of a meaningful lexicon of tags that are helpful in classifying SUMO tickets.
    - Application of basic natural language processing (NLP) methods to the corpus of SUMO support requests.
    
- Refined triaging based on NLP analysis of support tickets
    - Design and development of metrics for evaluating system performance via liaison with SUMO experts.
    - Assess the utility of sentiment analysis for detecting critical/urgent support issues.
    - Assess internal consistency of tags based on automated system and inter-tagger agreement for human annotations via a controlled study.
    
- Improve analytical capabilities in analyzing support issue corpora
    - Reporting of issue-based ticket volumes and other signals that may help identify growing browser issues.
    - Develop meaningful aggregation and reporting strategies that leverage existing and newly developed annotation data.
    - Detect trending issues via analysis of historical issue topics.
    
We will investigate improvements to the quality and throughput of the support systems at Mozilla when supplementing a portion of manual annotation work with an automated system. We will work on prototyping the application of existing and novel tools from the domain of Natural Language Processing into existing workflows for triaging, response, and analysis of online support requests.


## Setup

```sh
$ virtualenv venv --python=python3
$ source venv/bin/activate
$ pip install -r requirements.txt
$ pip freeze > requirements.txt
```

## Code Style

```sh
# or use IDE intergration
$ black . --exclude=venv
```
