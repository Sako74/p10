# -*- coding: utf-8 -*-
import os
import json
import tempfile
import argparse

from azureml.core import Workspace, Dataset

from utils import *


if __name__ == "__main__":
    # On récupère les arguments
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--app_version", type=str)
    parser.add_argument("--is_staging", type=int, default=1)
    parser.add_argument("--is_tmp", type=int, default=1)
    
    args = parser.parse_args()
    
    print("Chargement des variables d'environement.")
    
    get_env(".env")
    
    print("Chargement du workspace.")
    
    try:
        ws = Workspace.from_config()
    except:
        # On charge les variables d'environnemnt
        azure_credentials = json.loads(os.getenv("AZURE_CREDENTIALS"))
        azure_workspace = json.loads(os.getenv("AZURE_WORKSPACE"))

        # On charge l’espace de travail Azure Machine Learning existant
        ws = get_ws(azure_credentials, azure_workspace)
    
    print("Chargement des paramètres du modèle.")
    
    with open("params.json") as f:
        params = json.load(f)
        
    print("Chargement des jeux de données.")
    
    with tempfile.TemporaryDirectory() as tmp_dir_name:
        dataset = Dataset.get_by_name(ws, **params["dataset"])
        dataset.download(target_path=tmp_dir_name, overwrite=False)
        
        # On charge le jeu d'entrainement
        file_path = os.path.join(tmp_dir_name, "utterances_train.json")
        with open(file_path) as f:
            utterances_train = json.load(f)

        # On charge le jeu de test
        file_path = os.path.join(tmp_dir_name, "utterances_test.json")
        with open(file_path) as f:
            utterances_test = json.load(f)
    
    # On crée le nom de version du modèle
    app_version = args.app_version if args.app_version else str(params["model"]["versionId"])
    
    print(f"Création de la version {app_version}.")
    
    create_new_version(app_version, params["model"], utterances_train)
    
    print("Entrainement du modèle.")
    
    train(app_version)
    
    slots = "staging" if args.is_staging else "production"
    print(f"Déploiement du modèle en {slots}.")
    
    deploy(app_version, args.is_staging)
    
    print("Evaluation du modèle.")
    
    res = evaluate(args.is_staging, utterances_test)
    
    # On affiche les résultats
    print(res.to_markdown())
    
    # On supprime le modèle si besoin
    if args.is_tmp:
        print("Suppression du modèle.")
        delete(app_version)
