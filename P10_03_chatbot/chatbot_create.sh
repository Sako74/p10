# On importe les configurations du chatbot
source "chatbot_config.txt"

# On importe les variables d'environnement de LUIS
source "../P10_02_luis/.env"

# On crée le chemin vers le fichier qui va contenir les varaibles d'environnement
CHATBOT_ENV_FILE_PATH="webapp/.env"

# On crée le chemin vers le fichier qui va contenir les varaibles d'environnement
NOTEBOOK_ENV_FILE_PATH="../P10_01_notebooks/.env"

################################################################################
# Création et déploiement de l'application web
################################################################################

# On se positionne dans le dossier de l'application web
pushd "webapp/"

# On crée les réssources et on déploie les fichiers présent dans le dossier de l'application web
az webapp up -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME -l $CHATBOT_APP_LOC --plan $CHATBOT_APP_PLAN_NAME --runtime $CHATBOT_APP_RUNTIME --sku $CHATBOT_APP_SKU

popd

# On ajoute le script permettant de démarrer l'application web
az webapp config set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --startup-file $CHATBOT_APP_STARTUP_FILE

################################################################################
# Création du service Application Insights
################################################################################

# On ajoute l'extension app insights
az extension add -n application-insights

# On crée une ressource app insights
az monitor app-insights component create -g $CHATBOT_RG -l $CHATBOT_APP_LOC --app $CHATBOT_APP_INSIGHTS_NAME --kind web --application-type web

# On lie app insights à l'application web
az monitor app-insights component connect-webapp -g $CHATBOT_RG -a $CHATBOT_APP_INSIGHTS_NAME --web-app $CHATBOT_APP_SITE_NAME

# On récupère la clé d'instrumentation
CHATBOT_APP_INSIGHTS_KEY=$(az monitor app-insights component show -g $CHATBOT_RG --app $CHATBOT_APP_INSIGHTS_NAME --query  "instrumentationKey" --output tsv)

# On récupère l'id de l'app de l'api de app insights
CHATBOT_APP_INSIGHTS_APP_ID=$(az monitor app-insights component show -g $CHATBOT_RG --app $CHATBOT_APP_INSIGHTS_NAME --query  "appId" --output tsv)

# On crée une nouvelle clé d'api
CHATBOT_APP_INSIGHTS_API_KEY=$(az monitor app-insights api-key create \
-g $CHATBOT_RG \
--app $CHATBOT_APP_INSIGHTS_NAME \
--api-key $CHATBOT_APP_INSIGHTS_API_KEY_NAME \
--read-properties ReadTelemetry \
--query  "apiKey" --output tsv)

# On enregistrer les infos de connexion
echo APP_INSIGHTS_API_ID=$CHATBOT_APP_INSIGHTS_APP_ID > $NOTEBOOK_ENV_FILE_PATH
echo APP_INSIGHTS_API_KEY=$CHATBOT_APP_INSIGHTS_API_KEY >> $NOTEBOOK_ENV_FILE_PATH

################################################################################
# Création du service Bot
################################################################################

# On génère un mot de passe aléatoire
CHATBOT_BOT_PASSWORD=`python -c "import uuid; print(uuid.uuid1(), end=None)"`

# On génère une azure application et on récupère son id
CHATBOT_BOT_ID=$(az ad app create --display-name $CHATBOT_BOT_NAME --password $CHATBOT_BOT_PASSWORD --available-to-other-tenants --query "appId" -o tsv | tr -d '[ \t\n\r\f\v]')

# On crée un Bot
az bot create -g $CHATBOT_RG --appid $CHATBOT_BOT_ID -n $CHATBOT_BOT_NAME --kind "registration"  -l $CHATBOT_BOT_LOC --password $CHATBOT_BOT_PASSWORD --sku $CHATBOT_BOT_SKU --endpoint "https://$CHATBOT_APP_SITE_NAME.azurewebsites.net/api/messages"

################################################################################
# Ajout de settings dans l'application web
################################################################################

# On ajoute les information de connexion au bot
az webapp config appsettings set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --settings CHATBOT_BOT_ID=$CHATBOT_BOT_ID
az webapp config appsettings set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --settings CHATBOT_BOT_PASSWORD=$CHATBOT_BOT_PASSWORD

# On ajoute les information de connexion à l'app LUIS
az webapp config appsettings set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --settings LUIS_APP_ID=$LUIS_APP_ID
az webapp config appsettings set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --settings LUIS_PRED_KEY=$LUIS_PRED_KEY
az webapp config appsettings set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --settings LUIS_PRED_ENDPOINT=$LUIS_PRED_ENDPOINT

# On redémarre l'application web
az webapp restart -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME

# On enregistre les variables d'environnement
az webapp config appsettings list -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --query "[].[name, value]" -o tsv | tr '\t' '=' > $CHATBOT_ENV_FILE_PATH

echo "Créer un secret Github avec la clé WEBAPP_ENV et la valeur suivante :"
cat $CHATBOT_ENV_FILE_PATH
