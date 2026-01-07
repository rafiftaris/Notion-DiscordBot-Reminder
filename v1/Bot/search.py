import datetime
import os
import json
from datetime import date

import requests

# TODO move to const.py
TaskPropertyKey = "Task"
DueDatePropertyKey = "Due Date"
PriorityPropertyKey = "Priority"
LabelsPropertyKey = "Labels"
AssigneePropertyKey = "Assigned To"

EventsLabel = "Events"
POLabel = "Preorders & Orders"

class Task:
    # Class for Search Results
    title = ""
    due_date = ""
    priority=""
    labels=""
    assignee=""

    def __init__(self, title, due_date, priority, labels, assignee):
        self.title = title
        self.due_date = due_date
        self.priority = priority
        self.labels = labels
        self.assignee=assignee

def filter_due_date_ahead(days_ahead):
    today = date.today()
    if isinstance(days_ahead, int):
        days_ahead = datetime.timedelta(days=days_ahead)
    date_ahead = today + days_ahead
    return {
        "property": "Due Date",
        "date": {
          "on_or_after": str(today),
          "on_or_before": str(date_ahead)
        }
    }

def filter_multiselect(prop_key, prop_val):
    return {
        "property": prop_key,
        "multi_select": {
          "contains": prop_val
        }
    }

def filter_select(prop_key, prop_val):
    return {
        "property": prop_key,
        "select": {
          "equals": prop_val
        }
    }

def filter_op(opkey, a, b):
    return {
        opkey:[a,b]
    }

def list_tasks_from_notion(query):
    url = "https://api.notion.com/v1/databases/" + \
        os.environ['DATABASE_TOKEN'] + "/query"

    payload = json.dumps({
      "filter": query
    })
    headers = {
        'Authorization': "Bearer " + os.environ["AUTH_KEY"],
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=payload)

    query_results = response.json()["results"]
    no_of_results = len(query_results)

    search_results = []
    if no_of_results == 0:
        # No results found
        return search_results
    for result in query_results:
        # Create Search Object for each result
        search_object = Task(
            title=try_get_response_value(result,["properties",TaskPropertyKey,"title",0,"plain_text"]),
            due_date=try_get_response_value(result, ["properties",DueDatePropertyKey,"date","start"]),
            priority=try_get_response_value(result, ["properties",PriorityPropertyKey,"select","name"]),
            labels=try_get_response_value_with_join(result,["properties",LabelsPropertyKey,"multi_select"],"name",", "),
            assignee=try_get_response_value_with_join(result,["properties",AssigneePropertyKey,"multi_select"],"name",", ")
        )
        search_results.append(search_object)
    return search_results

def try_get_response_value(result, key_list):
    desired_value = result
    for key in key_list:
        try:
            desired_value = desired_value[key]
        except TypeError:
            return ""

    if isinstance(desired_value, str):
        return desired_value
    return ""

def try_get_response_value_with_join(result, key_list, last_key, sep):
    desired_value = result
    for key in key_list:
        try:
            desired_value = desired_value[key]
        except TypeError:
            return ""
    return sep.join([result_dict[last_key] for result_dict in desired_value])