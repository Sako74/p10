# On importe les configuration
source "P10_02_luis/config.txt"

# On crée le chemin vers le fichier qui va contenir les varaibles d'environnement
LUIS_ENV_FILE_PATH="P10_02_luis/app/.env"

# Définition des variables
SUBSCRIPTION_ID=`az account show --query id --output tsv`
LUIS_AUTH_ID="/subscriptions/$SUBSCRIPTION_ID/providers/Microsoft.CognitiveServices/locations/$LUIS_LOC/resourceGroups/$LUIS_RG/deletedAccounts/$LUIS_AUTH_NAME"
LUIS_PRED_ID="/subscriptions/$SUBSCRIPTION_ID/providers/Microsoft.CognitiveServices/locations/$LUIS_LOC/resourceGroups/$LUIS_RG/deletedAccounts/$LUIS_PRED_NAME"

# Suppression du groupe
az group delete --name $LUIS_RG --yes

# Suppression "hard" des services LUIS (https://stackoverflow.com/a/67938295)
az resource delete --ids $LUIS_AUTH_ID
az resource delete --ids $LUIS_PRED_ID

# Suppression des infos de connexion
rm $LUIS_ENV_FILE_PATH
