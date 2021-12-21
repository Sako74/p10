import os
import logging
import json
from datetime import datetime

import azure.functions as func

from dotenv import load_dotenv
from github import Github


load_dotenv()

# On récupère les variables permettant de créer une issue sur Github
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")

def create_issue(issue_title: str, issue_body: str):
    # On crée le handler Github
    g = Github(GITHUB_TOKEN)

    # On configure le handler pour le repo du projet
    repo = g.get_repo(GITHUB_REPO)

    try:
        # On récupère le tag spécial pour les alertes
        issue_label_name = "azure alert"
        issue_label = repo.get_label(issue_label_name)
    except:
        # On crée un tag spécial pour les alertes
        issue_label = repo.create_label(
            issue_label_name,
            color="d73a4a",
            description="Azure alert"
        )
    
    # On crée une issue
    repo.create_issue(
        title=issue_title,
        body=json.dumps(issue_body, indent=2),
        labels=[issue_label]
    )


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # On spécifie que la réponse sera en JSON
    func.HttpResponse.mimetype = "application/json"
    func.HttpResponse.charset = "utf-8"

    try:
        # On récupère les données
        data = req.get_json()

        try:
            # On initialise les données de l'issue
            issue_title = data["data"]["essentials"]["description"]

            issue_body = {
                "start_dt": data["data"]["alertContext"]["condition"]["windowStartTime"],
                "end_dt": data["data"]["alertContext"]["condition"]["windowEndTime"]
            }
        except:
            # On log les données reçues en cas d'erreur
            logging.error(
                "Missing fields 'data.alertContext.condition.windowStartTime'"
                " and/or 'data.alertContext.condition.windowEndTime' in JSON data:"
            )
            logging.error(json.dumps(data))

            # On renvoie l'erreur
            return func.HttpResponse(json.dumps({"error": "Missing fields 'windowStartTime' and/or 'windowEndTime' in JSON data"}))
        
        # On crée l'issue github
        try:
            create_issue(issue_title, issue_body)
        except Exception as e:
            # On log l'erreur
            logging.error(e)

            # On renvoie l'erreur
            return func.HttpResponse(json.dumps({"error": str(e)}))

        # On renvoie les données de l'issue créée
        return func.HttpResponse(json.dumps({
            "title": issue_title,
            "body": issue_body
        }))
    except Exception as e:
        # On log l'erreur
        logging.error(e)

        # On renvoie l'erreur
        return func.HttpResponse(json.dumps({"error": str(e)}))