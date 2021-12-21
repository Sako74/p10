# -*- coding: utf-8 -*-
# +
import sys
import os
import json
from collections import defaultdict
from datetime import datetime
import tempfile
import subprocess

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from tqdm.notebook import tqdm

import ipywidgets as widgets
from IPython.display import display
import markdown

from dotenv import load_dotenv, set_key

sys.path.append("../")
from P10_02_luis.utils import *

# +
# On définit les variables globales
JSON_PATH = "data/json/"
PARQUET_PATH = "data/parquet/"

os.makedirs(JSON_PATH, exist_ok=True)
os.makedirs(PARQUET_PATH, exist_ok=True)

RANDOM_SEED = 42


# -

def copy_and_clean_notebooks():
    """Copie les notebooks et supprime les sorties."""
    
    # On récupère la liste des notebooks à convertir (avec les sorties)
    file_names = os.listdir()
    notebooks = [
        f.replace(".ipynb", "") for f in file_names
        if f.endswith(".ipynb") and not f.endswith("no_out.ipynb")
    ]
    
    for n in notebooks:
        # On crée un version nettoyée du notebook (sans les sorties)
        args = f"jupyter nbconvert --clear-output --to notebook --output {n}_no_out {n}.ipynb".split()
        subprocess.run(args)


def turn_to_luis_utterance(turn: dict, intent_name: str, label_to_entity: dict) -> dict:
    """Convertit un turn du jeu de données en une utterance labellisée pour LUIS."""
    
    text = turn["text"]

    entity_labels = []
    for i in turn["labels"]["acts_without_refs"]:
        for l in i["args"]:
            k = l["key"]
            v = l["val"]

            if k and v:
                if k in label_to_entity.keys():
                    start_char_index = text.lower().find(v.lower())
                    if start_char_index == -1:
                        continue
                    
                    end_char_index = start_char_index + len(v) - 1

                    entity_labels.append({
                        "startCharIndex": start_char_index,
                        "endCharIndex": end_char_index,
                        "entityName": label_to_entity[k],
                    })
    
    res = {
        "text": text,
        "intentName": intent_name,
        "entityLabels": entity_labels,
    }
    return res


def user_turns_to_luis_ds(
    frames: list,
    intent_name: str,
    label_to_entity: dict
) -> pd.DataFrame:
    """Convertit les turns utilisateur du jeu de données pour LUIS."""
    
    res = []
    # Pour chaque dialogue
    for frame in frames:
        # On crée un id pour identifier les tours de chaque dialogue
        user_turn_id = 0
        
        # Pour chaque tour du dialogue
        for turn in frame["turns"]:
            # On vérifie si il s'agit bien de l'utilisateur
            if turn["author"] == "user":
                # On ajoute l'id du tour
                row = {"user_turn_id": user_turn_id}
                user_turn_id += 1
                
                # On ajoute l'utterance au format LUIS
                row.update(turn_to_luis_utterance(turn, intent_name, label_to_entity))
                
                # On ajoute le résultat à la liste
                res.append(row)
    
    # On convertit les données en DataFrame
    df = pd.DataFrame(res)
    
    # On ajoute le nombre d'entitées labellisées dans le texte
    df["entity_total_nb"] = df["entityLabels"].apply(len)
    
    # Pour chaque entitée, on ajoute le nombre de fois qu'elle apparait
    for entity_name in label_to_entity.values():
        df[f"{entity_name}_nb"] = df["entityLabels"].apply(
            lambda x: len(list(
                filter(lambda x1: x1["entityName"] == entity_name, x)
            ))
        )
    
    # On ajoute le nombre de mot dans le texte
    df["text_word_nb"] = df["text"].apply(lambda x: len(x.split()))

    # Enfin, on labellise à None les phrases sans aucune entitée
    none_intent_mask = df["entity_total_nb"] == 0
    df.loc[none_intent_mask, "intentName"] = "None"
    
    return df


class AppInsightsAPIEnv:
    def __init__(self, env_file_path: str=""):
        # On charge le fichier des variables d'environnement
        if env_file_path:
            load_dotenv(env_file_path, override=True)

        # On charge les variables d'environnement
        self.APP_INSIGHTS_API_ID = os.getenv("APP_INSIGHTS_API_ID")
        self.APP_INSIGHTS_API_KEY = os.getenv("APP_INSIGHTS_API_KEY")


def get_tn_dialogs(env: AppInsightsAPIEnv, start_dt: str, end_dt: str) -> pd.DataFrame:
    """Récupère les dialogues des TN"""
    
    # On crée la requête en Kusto Query Language
    query = f"""customEvents
| where name == 'TN'
| where timestamp > datetime('{start_dt}') and timestamp < datetime('{end_dt}')
| extend mainDialogUuid = tostring(customDimensions['mainDialogUuid'])
| project mainDialogUuid
| join kind=rightsemi (
    customEvents
    | extend mainDialogUuid = tostring(customDimensions['mainDialogUuid'])
    | extend text = tostring(customDimensions['text'])
    | where text != ""
    | extend fromName = tostring(customDimensions['fromName'])
    | project mainDialogUuid, timestamp, fromName, session_Id, text
) on mainDialogUuid
| sort by mainDialogUuid asc, timestamp asc
"""
    
    # On envoie la requête
    response = requests.post(
        url=f"https://api.applicationinsights.io/v1/apps/{env.APP_INSIGHTS_API_ID}/query",
        headers={
            "X-Api-Key": env.APP_INSIGHTS_API_KEY,
        },
        json={"query": query}
    )
    
    # On vérifie la réponse
    check_response_ok_or_raise_for_status(response)
    
    # On récupère les données
    res = response.json()
    
    # On crée un dataframe à partir des données
    res = pd.DataFrame(res["tables"][0]["rows"])
    res.columns = ["main_dialog_uuid", "timestamp", "author", "session_id", "text"]
    res["timestamp"] = pd.to_datetime(res["timestamp"])
    
    # On renvoie le résultat
    return res


class InsatisfactionsAnalyser:
    def __init__(self, data, res=None):
        self.data = data.groupby("main_dialog_uuid")
        
        if res is None:
            self.res = data.groupby("main_dialog_uuid", as_index=False).agg({
                "timestamp": ["min", "max"],
                "session_id": "first",
                "text": "count",
            })
            self.res.columns = ["main_dialog_uuid", "timestamp_min", "timestamp_max", "session_id", "text_nb"]
            self.res["error_type"] = ""
            self.res["comment"] = ""
        else:
            self.res = res
        
        self.uuids = self.res["main_dialog_uuid"].to_list()
        
        self.idx = 0
        self.idx_min = 0
        self.idx_max = len(self.uuids) - 1
        
        self.dialog_vbox = widgets.VBox(layout=widgets.Layout(
            width="60%",
            height="300px",
            display="block",
            overflow_y='auto',
            border="1px solid black"
        ))
        
        self.prev_button = widgets.Button(
            description="Previous",
            icon="arrow-left"
        )

        self.next_button = widgets.Button(
            description="Next",
            icon="arrow-right"
        )
        
        self.error_type_sel = widgets.RadioButtons(
            options=["unknown", "luis", "chatbot"],
            value=None,
            description="Error type:"
        )
        
        self.comment_text = widgets.Textarea(
            placeholder="Add a comment",
            description="Comment:"
        )
        
        self.options_vbox = widgets.VBox([
            self.error_type_sel,
            self.comment_text,
            self.prev_button,
            self.next_button
        ])
        
        self.analyser = widgets.HBox([self.dialog_vbox, self.options_vbox])
        
        self.prev_button.on_click(self.on_prev_button_clicked)
        self.next_button.on_click(self.on_next_button_clicked)
        self.error_type_sel.observe(self.on_error_type_sel_change, names="value")
        self.comment_text.observe(self.on_comment_text_change, names="value")
        
        self.update_all()
        
    def on_prev_button_clicked(self, b):
        if self.idx > self.idx_min:
            self.idx -= 1

        self.update_all()
        
    def on_next_button_clicked(self, b):
        if self.idx < self.idx_max:
            self.idx += 1

        self.update_all()
        
    def on_error_type_sel_change(self, value):
        self.res.loc[self.idx, "error_type"] = value["new"]
        self.update_error_type_sel()
        
    def on_comment_text_change(self, value):
        self.res.loc[self.idx, "comment"] = value["new"]
        self.update_comment_text()
        
    def update_all(self):
        self.update_dialog_vbox()
        self.update_buttons()
        self.update_error_type_sel()
        self.update_comment_text()
        
    def update_buttons(self):
        if self.idx <= self.idx_min:
            self.prev_button.disabled = True
        else:
            self.prev_button.disabled = False

        if self.idx >= self.idx_max:
            self.next_button.disabled = True
        else:
            self.next_button.disabled = False
        
    def update_dialog_vbox(self):
        data = self.data.get_group(self.uuids[self.idx])
        texts = []
        for i, row in data.iterrows():
            if row["author"] == "p10-chatbot-bot":
                layout = widgets.Layout(justify_content="flex-end")
            else:
                layout = widgets.Layout(justify_content="flex-start")

            text = row["text"].replace("\n", "\n\r")
            texts.append(widgets.HBox([widgets.HTML(
                markdown.markdown(text),
                layout=widgets.Layout(
                    max_width="70%",
                    border="1px solid black",
                    padding="5px",
                    margin="10px 5px 10px 5px"
                ))], layout=layout))

        self.dialog_vbox.children = texts
        
    def update_error_type_sel(self):
        value = self.res.loc[self.idx, "error_type"]
        self.error_type_sel.value = value if value != "" else None
        
    def update_comment_text(self):
        value = self.res.loc[self.idx, "comment"]
        self.comment_text.value = value
        
    def display(self):
        display(self.analyser)
        
    def save(self, dir_path, name):
        # On enregistre les données. "coerce_timestamps" permet de conserver
        # le type datetime dans les métadonnées du fichier parquet.
        file_path = os.path.join(dir_path, f"{name}_data.parquet")
        self.data.obj.to_parquet(
            file_path,
            index=False,
            coerce_timestamps="ms",
            allow_truncated_timestamps=True
        )
        
        file_path = os.path.join(dir_path, f"{name}_res.parquet")
        self.res.to_parquet(
            file_path,
            index=False,
            coerce_timestamps="ms",
            allow_truncated_timestamps=True
        )
        
    def load(self, dir_path, name):
        # On enregistre les données. "coerce_timestamps" permet de conserver
        # le type datetime dans les métadonnées du fichier parquet.
        file_path = os.path.join(dir_path, f"{name}_data.parquet")
        data = pd.read_parquet(file_path)
        
        file_path = os.path.join(dir_path, f"{name}_res.parquet")
        res = pd.read_parquet(file_path)
        
        self.__init__(data, res)


