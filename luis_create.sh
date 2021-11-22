# On importe les configuration
source chatbot_config.txt

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
LUIS_AUTH_KEY=$(az cognitiveservices account keys list -n $LUIS_AUTH_NAME -g LUIS_RG --query "key1" -o tsv | tr -d '[ \t\n\r\f\v]')
LUIS_AUTH_ENDPOINT=$(az cognitiveservices account show -n $LUIS_AUTH_NAME -g $LUIS_RG --query "properties.endpoint" -o tsv | tr -d '[ \t\n\r\f\v]')

LUIS_PRED_KEY=$(az cognitiveservices account keys list -n $LUIS_PRED_NAME -g LUIS_RG --query "key1" -o tsv | tr -d '[ \t\n\r\f\v]')
LUIS_PRED_ENDPOINT=$(az cognitiveservices account show -n $LUIS_PRED_NAME -g $LUIS_RG --query "properties.endpoint" -o tsv | tr -d '[ \t\n\r\f\v]')

# On crée le fichier qui va contenir les infos de connexion aux app LUIS 
touch $LUIS_ENV_FILE_NAME

# On enregistrer les infos de connexion dans un fichier
echo LUIS_AUTH_KEY=$LUIS_AUTH_KEY >> $LUIS_ENV_FILE_NAME
echo LUIS_AUTH_ENDPOINT=$LUIS_AUTH_ENDPOINT >> $LUIS_ENV_FILE_NAME

echo LUIS_PRED_KEY=$LUIS_PRED_KEY >> $LUIS_ENV_FILE_NAME
echo LUIS_PRED_ENDPOINT=$LUIS_PRED_ENDPOINT >> $LUIS_ENV_FILE_NAME

################################################################################
# Création de l'application LUIS
################################################################################