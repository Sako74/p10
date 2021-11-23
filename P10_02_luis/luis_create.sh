# On importe les configuration
source "P10_02_luis/luis_config.txt"

# On crée le chemin vers le fichier qui va contenir les varaibles d'environnement
LUIS_ENV_FILE_PATH = "P10_02_luis/$LUIS_ENV_FILE_NAME"

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

# On crée l'application LUIS
LUIS_APP_ID=$(python -m "P10_02_luis.app.create")

# On enregistrer l'id de l'application
echo LUIS_APP_ID=$LUIS_APP_ID > $LUIS_ENV_FILE_PATH
