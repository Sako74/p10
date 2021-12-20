# On importe les configuration
source "luis_config.txt"

# On crée le chemin vers le fichier qui va contenir les varaibles d'environnement
LUIS_ENV_FILE_PATH=".env"

################################################################################
# Création des ressources LUIS
################################################################################

# On crée le groupe de ressources
az group create -n $LUIS_RG -l $LUIS_LOC

# On crée la ressource d'authoring
az cognitiveservices account create -n $LUIS_AUTH_NAME -g $LUIS_RG --kind LUIS.Authoring --sku $LUIS_SKU -l $LUIS_LOC --yes

# On crée la ressource de prediction
az cognitiveservices account create -n $LUIS_PRED_NAME -g $LUIS_RG --kind LUIS --sku $LUIS_SKU -l $LUIS_LOC --yes

# On récupère les infos de connexion aux app LUIS
LUIS_AUTH_KEY=$(az cognitiveservices account keys list -n $LUIS_AUTH_NAME -g $LUIS_RG --query "key1" -o tsv | tr -d '[ \t\n\r\f\v]')
LUIS_AUTH_ENDPOINT=$(az cognitiveservices account show -n $LUIS_AUTH_NAME -g $LUIS_RG --query "properties.endpoint" -o tsv | tr -d '[ \t\n\r\f\v]')

LUIS_PRED_KEY=$(az cognitiveservices account keys list -n $LUIS_PRED_NAME -g $LUIS_RG --query "key1" -o tsv | tr -d '[ \t\n\r\f\v]')
LUIS_PRED_ENDPOINT=$(az cognitiveservices account show -n $LUIS_PRED_NAME -g $LUIS_RG --query "properties.endpoint" -o tsv | tr -d '[ \t\n\r\f\v]')

# On enregistrer les infos de connexion
echo LUIS_AUTH_KEY=$LUIS_AUTH_KEY > $LUIS_ENV_FILE_PATH
echo LUIS_AUTH_ENDPOINT=$LUIS_AUTH_ENDPOINT >> $LUIS_ENV_FILE_PATH

echo LUIS_PRED_KEY=$LUIS_PRED_KEY >> $LUIS_ENV_FILE_PATH
echo LUIS_PRED_ENDPOINT=$LUIS_PRED_ENDPOINT >> $LUIS_ENV_FILE_PATH

################################################################################
# Création de l'application LUIS
################################################################################

# On charge les paramètres du modèle LUIS
LUIS_PARAMS=`python -c "import json; f = open('params.json'); params = json.load(f); print(json.dumps(params['model'])); f.close();"`

# On crée une application LUIS
LUIS_APP_ID=`curl -v -X POST "https://westus.api.cognitive.microsoft.com/luis/authoring/v3.0-preview/apps/import" \
-H "Content-Type: application/json" \
-H "Ocp-Apim-Subscription-Key: $LUIS_AUTH_KEY" \
--data-ascii "$LUIS_PARAMS"`

# On enlève les guillements
LUIS_APP_ID=$(echo $LUIS_APP_ID | tr -d '"')

# On enregistre l'id de l'application
echo LUIS_APP_ID=$LUIS_APP_ID >> $LUIS_ENV_FILE_PATH

# On assigne la ressource de prédiction à l'application
TOKEN=`az account get-access-token --resource=https://management.core.windows.net/ --query accessToken --output tsv | tr -d '[ \t\n\r\f\v]'`
SUBSCRIPTION_ID=`az account show --query id --output tsv | tr -d '[ \t\n\r\f\v]'`
JSON_FMT='{"azureSubscriptionId": "%s", "resourceGroup": "%s", "accountName": "%s"}'

curl -v -X POST "https://westus.api.cognitive.microsoft.com/luis/authoring/v3.0-preview/apps/$LUIS_APP_ID/azureaccounts" \
-H "Authorization: Bearer $TOKEN" \
-H "Content-Type: application/json" \
-H "Ocp-Apim-Subscription-Key: $LUIS_AUTH_KEY" \
--data-ascii "$(printf "$JSON_FMT" "$SUBSCRIPTION_ID" "$LUIS_RG" "$LUIS_PRED_NAME")"

# On demande à l'utilisateur de créer un secret Github
echo "Créer un secret Github avec la clé LUIS_ENV et la valeur suivante :"
cat $LUIS_ENV_FILE_PATH
