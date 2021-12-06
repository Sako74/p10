import os
import logging
import json
from datetime import datetime

import azure.functions as func

from dotenv import load_dotenv
from github import Github


load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

g = Github(GITHUB_TOKEN) if GITHUB_TOKEN else None

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
            logging.info(json.dumps(req_body, indent=2))
            
            repo = g.get_repo(GITHUB_REPO)

            try:
                label_name = "insatisfaction alert"
                label = repo.get_label(label_name)
            except:
                logging.info('Create Insatisfaction alert label.')

                label = repo.create_label(
                    label_name,
                    color="d73a4a",
                    description="High insatisfaction rate"
                )
            
            repo.create_issue(
                title="This is a new issue",
                body=json.dumps(req_body, indent=2),
                labels=[label]
            )
        except ValueError:
            pass
        else:
            name = req_body.get('name')
    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
