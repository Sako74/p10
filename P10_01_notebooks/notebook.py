# -*- coding: utf-8 -*-
# +
import os
import json
from collections import defaultdict
from datetime import datetime
import tempfile

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from tqdm.notebook import tqdm

from IPython.display import display

from dotenv import set_key

# +
# On définit les variables globales
JSON_PATH = "data/json/"

os.makedirs(JSON_PATH, exist_ok=True)

RANDOM_SEED = 42


# -

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
