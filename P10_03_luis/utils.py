# -*- coding: utf-8 -*-
# +
import os, json, time, requests

from azureml.core import Workspace
from azureml.core.authentication import ServicePrincipalAuthentication

from azure.cognitiveservices.language.luis.authoring import LUISAuthoringClient
from azure.cognitiveservices.language.luis.authoring.models import ApplicationCreateObject, AzureAccountInfoObject, LuisApp
from azure.cognitiveservices.language.luis.runtime import LUISRuntimeClient
from msrest.authentication import CognitiveServicesCredentials

import pandas as pd

from dotenv import load_dotenv, set_key
# -

# On charge le fichier des variables d'environnement
load_dotenv("../P10_03_luis/.env", override=True)

# +
# On charge les variables d'environnement
LUIS_AUTH_KEY = os.getenv("LUIS_AUTH_KEY")
LUIS_AUTH_ENDPOINT = os.getenv("LUIS_AUTH_ENDPOINT")

LUIS_PRED_KEY = os.getenv("LUIS_PRED_KEY")
LUIS_PRED_ENDPOINT = os.getenv("LUIS_PRED_ENDPOINT")

LUIS_APP_ID = os.getenv("LUIS_APP_ID")


# -

def get_ws(azure_credentials: dict, azure_workspace: dict) -> Workspace:
    """Renvoie le workspace de Azure ML.
    
    Parameters
    ----------
        azure_credentials : dict
            Informations de connexion.
        azure_workspace : dict
            Informations sur le workspace.

    Returns
    ----------
        Azure Workspace
            Workspace de Azure ML.
    """
    
    # On crée un service d'authentification
    svc_pr = ServicePrincipalAuthentication(
        tenant_id=azure_credentials.get("tenantId"),
        service_principal_id=azure_credentials.get("clientId"),
        service_principal_password=azure_credentials.get("clientSecret")
    )

    # On se connecte au workspace
    ws = Workspace(
        subscription_id=azure_credentials.get("subscriptionId"),
        resource_group=azure_workspace.get("resourceGroup"),
        workspace_name=azure_workspace.get("workspaceName"),
        auth=svc_pr
    )

    return ws


def check_response_ok_or_raise_for_status(response):
    """Vérifie que la réponse est ok ou génère une erreur"""
    
    # On génère une exception en cas d'erreur
    if not response.ok:
        print(response.content)
        response.raise_for_status()


def create_new_version(app_version: str, app_params: dict, app_utterances: list=[]):
    """Crée un nouvelle version d'una application LUIS"""
    
    # On ajoute les utterances aux paramètres de l'application
    app_params_tmp = app_params.copy()
    app_params_tmp["utterances"] += app_utterances
    
    # On envoie la requête permettant de créer la nouvelle version
    response = requests.post(
        url=f"{LUIS_AUTH_ENDPOINT}luis/authoring/v3.0-preview/apps/{LUIS_APP_ID}/versions/import",
        params={
            "versionId": app_version,
        },
        headers={
            "Ocp-Apim-Subscription-Key": LUIS_AUTH_KEY,
        },
        json=app_params_tmp
    )
    
    # On vérifie la réponse
    check_response_ok_or_raise_for_status(response)


def train(app_version: str, check_status_period: int=10):
    """Entrainement du modèle de l'app LUIS"""
    
    # On crée le client avec les informations d'authentification
    client = LUISAuthoringClient(LUIS_AUTH_ENDPOINT, CognitiveServicesCredentials(LUIS_AUTH_KEY))

    # On entraine le modèle
    client.train.train_version(LUIS_APP_ID, app_version)
    
    # On attend la fin de l'entrainement
    waiting = True
    while waiting:
        # On demande le status de l'entrainement
        info = client.train.get_status(LUIS_APP_ID, app_version)

        # On vérifie si l'entrainement est en attente ou en cours d'exécution
        waiting = any(map(lambda x: x.details.status in ["Queued", "InProgress"], info))
        
        if waiting:
            time.sleep(check_status_period)


def get_params(app_version: str) -> dict:
    """Renvoie les paramètres de l'app LUIS"""
    
    # On envoie la requête permettant d'exporter le modèle au format json
    response = requests.get(
        url=f"{LUIS_AUTH_ENDPOINT}luis/authoring/v3.0-preview/apps/{LUIS_APP_ID}/versions/{app_version}/export",
        params={
            "format": "json"
        },
        headers={
            "Ocp-Apim-Subscription-Key": LUIS_AUTH_KEY,
        }
    )
    
    # On vérifie la réponse
    check_response_ok_or_raise_for_status(response)
    
    # On renvoie les paramètres
    return response.json()


def get_utterances(app_version: str) -> list:
    """Renvoie les utterances de l'app LUIS"""
    
    # On envoie la paramètres du modèle
    params = get_params(app_version)
    
    # On retourne les utterances
    return params["utterances"]


def deploy(app_version: str, is_staging: bool=True):
    """Déploiement de l'application LUIS"""
    
    # On crée le client avec les informations d'authentification
    client = LUISAuthoringClient(LUIS_AUTH_ENDPOINT, CognitiveServicesCredentials(LUIS_AUTH_KEY))

    # On plublie l'app
    client.apps.publish(LUIS_APP_ID, app_version, is_staging=is_staging);


def get_prediction(is_staging: bool, utterance) -> dict:
    """Renvoie une prédiction faite par l'application LUIS"""
    
    # On définie le slot à tester
    slots = "Staging" if is_staging else "Production"
    
    # On crée le client avec les informations d'authentification
    client_runtime = LUISRuntimeClient(LUIS_PRED_ENDPOINT, CognitiveServicesCredentials(LUIS_PRED_KEY))

    # On effectue la prédiction
    pred = client_runtime.prediction.get_slot_prediction(
        LUIS_APP_ID,
        slots,
        {"query" : [utterance]}
    )
    
    return pred.as_dict()


def evaluate(is_staging: bool, utterances: list, check_status_period: int=10) -> pd.DataFrame:
    """Evaluation de l'application LUIS sur un jeu de test"""
    
    # On définie le slot à tester
    slots = "staging" if is_staging else "production"
    
    # On envoie la requête permettant de lancer l'évaluation
    response = requests.post(
        url=f"{LUIS_PRED_ENDPOINT}luis/v3.0-preview/apps/{LUIS_APP_ID}/slots/{slots}/evaluations",
        headers={
            "Ocp-Apim-Subscription-Key": LUIS_AUTH_KEY,
        },
        json=utterances
    )
    
    # On vérifie la réponse
    check_response_ok_or_raise_for_status(response)
    
    # On récupère l'id de l'opération
    operation_id = response.json()["operationId"]
    
    waiting = True
    while waiting:
        # On check le status
        response = requests.get(
            url=f"{LUIS_PRED_ENDPOINT}luis/v3.0-preview/apps/{LUIS_APP_ID}/slots/{slots}/evaluations/{operation_id}/status",
            headers={
                "Ocp-Apim-Subscription-Key": LUIS_AUTH_KEY,
            }
        )
        
        # On vérifie s'il y a une erreur
        if response.json()["status"] == "failed":
            raise ValueError(response.content)
        
        waiting = response.json()["status"] in ["notstarted", "running"]
        
        if waiting:
            time.sleep(check_status_period)
        
    # On récupère les résultats de l'évaluation
    response = requests.get(
        url=f"{LUIS_PRED_ENDPOINT}luis/v3.0-preview/apps/{LUIS_APP_ID}/slots/{slots}/evaluations/{operation_id}/result",
        headers={
            "Ocp-Apim-Subscription-Key": LUIS_AUTH_KEY,
        }
    )
    
    # On vérifie la réponse
    check_response_ok_or_raise_for_status(response)
    
    # On récupère les résultats
    res = response.json()
    
    # On met en forme les résultats dans un DataFrame
    res = pd.DataFrame(res["intentModelsStats"] + res["entityModelsStats"])
    res.iloc[:, -3:] = res.iloc[:, -3:].astype(float)
    res.columns = [
        "model_name",
        "model_type",
        f"precision",
        f"recall",
        f"f_score",
    ]
    
    return res


def delete(app_version: str):
    """Déploiement de l'application LUIS"""
    
    # On crée le client avec les informations d'authentification
    client = LUISAuthoringClient(LUIS_AUTH_ENDPOINT, CognitiveServicesCredentials(LUIS_AUTH_KEY))

    # On plublie l'app
    client.versions.delete(LUIS_APP_ID, app_version)
