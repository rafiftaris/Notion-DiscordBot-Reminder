import os
import json
from datetime import date

import requests

TaskPropertyKey = "Task"
DueDatePropertyKey = "Due Date"
PriorityPropertyKey = "Priority"
LabelsPropertyKey = "Labels"
AssigneePropertyKey = "Assigned To"

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


def list_tasks_from_notion(args):
    url = "https://api.notion.com/v1/databases/" + \
        os.environ['DATABASE_TOKEN'] + "/query"

    today = date.today()
    daysAhead = today + args
    payload = json.dumps({
      "filter": {
        "property": "Due Date",
        "date": {
          "on_or_after": str(today),
          "on_or_before": str(daysAhead)
        }
      }
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
        return(search_results)
    for result in query_results:
        # Create Search Object for each result
        search_object = Task(
            title=result["properties"][TaskPropertyKey]["title"][0]["plain_text"],
            due_date=result["properties"][DueDatePropertyKey]["date"]["start"],
            priority=result["properties"][PriorityPropertyKey]["select"]["name"],
            labels=", ".join([label["name"] for label in result["properties"][LabelsPropertyKey]["multi_select"]]),
            assignee=", ".join([label["name"] for label in result["properties"][AssigneePropertyKey]["multi_select"]])
        )
        search_results.append(search_object)
    return(search_results)