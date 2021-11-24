# On importe les configuration
source "P10_01_scripts/luis_config.txt"

# On crée le chemin vers le fichier qui va contenir les varaibles d'environnement
LUIS_ENV_FILE_PATH="P10_03_luis/.env"

# On crée l'application LUIS
LUIS_APP_ID=$(python -m "P10_03_luis.create")

# On enregistrer l'id de l'application
echo LUIS_APP_ID=$LUIS_APP_ID >> $LUIS_ENV_FILE_PATH
