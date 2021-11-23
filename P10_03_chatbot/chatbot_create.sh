# On importe les configurations du chatbot
source "P10_03_chatbot/chatbot_config.txt"

################################################################################
# Création et déploiement de l'application web
################################################################################

# On se positionne dans le dossier de l'application web
pushd "P10_03_chatbot/$CHATBOT_APP_DIR"

# On crée les réssources et on déploie les fichiers présent dans le dossier de l'application web
az webapp up -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME -l $CHATBOT_APP_LOC --plan $CHATBOT_APP_PLAN_NAME --runtime $CHATBOT_APP_RUNTIME --sku $CHATBOT_APP_SKU

# On ajoute le script permettant de démarrer l'application web
az webapp config set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --startup-file $CHATBOT_APP_STARTUP_FILE

popd

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
CHATBOT_APP_INSIGHTS_KEY=$(az monitor app-insights component show -g $CHATBOT_RG --app $CHATBOT_APP_INSIGHTS_NAME --query  "instrumentationKey" --output tsv | tr -d '[ \t\n\r\f\v]')

################################################################################
# Création du service Bot
################################################################################

# On génère un mot de passe aléatoire
CHATBOT_BOT_PASSWORD=$(uuidgen)

# On génère une azure application et on récupère son id
CHATBOT_BOT_ID=$(az ad app create --display-name $CHATBOT_BOT_NAME --password $CHATBOT_BOT_PASSWORD --available-to-other-tenants --query "appId" -o tsv | tr -d '[ \t\n\r\f\v]')

# On crée un Bot
az bot create -g $CHATBOT_RG --appid $CHATBOT_BOT_ID -n $CHATBOT_BOT_NAME --kind "registration"  -l $CHATBOT_BOT_LOC --password $CHATBOT_BOT_PASSWORD --sku $CHATBOT_BOT_SKU --endpoint "https://$CHATBOT_APP_SITE_NAME.azurewebsites.net/api/messages"

#################################################################################
## Ajout de settings dans l'application web
#################################################################################

# On crée le chemin vers le fichier des variables d'environnement
CHATBOT_APP_ENV_FILE_PATH="P10_03_chatbot/$CHATBOT_APP_DIR/.env"

# On copie les variables d'environnement de l'app LUIS
cp "../P10_02_luis/.env" $CHATBOT_APP_ENV_FILE_PATH

# On ajoute les information de connexion au bot
echo CHATBOT_BOT_ID=$CHATBOT_BOT_ID > $CHATBOT_APP_ENV_FILE_PATH
echo CHATBOT_BOT_PASSWORD=$CHATBOT_BOT_PASSWORD > $CHATBOT_APP_ENV_FILE_PATH

# On ajoute la clé d'instrumentation de app insights
echo CHATBOT_APP_INSIGHTS_KEY=$CHATBOT_APP_INSIGHTS_KEY > $CHATBOT_APP_ENV_FILE_PATH

# On déploie le fichier
az webapp deploy -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --clean false --src-path $CHATBOT_APP_ENV_FILE_PATH --type static

# On redémarre l'application web
az webapp restart -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME

##################################################################################
### Ajout de settings dans l'application web
##################################################################################
#
## On ajoute les information de connexion au bot
#az webapp config appsettings set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --settings CHATBOT_BOT_ID=$CHATBOT_BOT_ID
#az webapp config appsettings set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --settings CHATBOT_BOT_PASSWORD=$CHATBOT_BOT_PASSWORD
#
## On ajoute les information de connexion à l'app LUIS
#az webapp config appsettings set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --settings LUIS_APP_ID=$LUIS_APP_ID
#az webapp config appsettings set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --settings LUIS_PRED_KEY=$LUIS_PRED_KEY
#az webapp config appsettings set -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME --settings LUIS_PRED_ENDPOINT=$LUIS_PRED_ENDPOINT
#
## On redémarre l'application web
#az webapp restart -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME
