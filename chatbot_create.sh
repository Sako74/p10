# On importe les configuration
source chatbot_config.txt

# On se positionne dans le dossier de l'application web
cd $SITEDIR

################################################################################
# Création et déploiement de l'application web
################################################################################

# On crée les réssources et on déploie les fichiers présent dans le dossier de l'application web
az webapp up --resource-group $RESOURCEGROUP --name $SITENAME --location $LOCATION --plan $PLANNAME --runtime $RUNTIME --sku $PLANSKU

# On ajoute le script permettant de démarrer l'application web
az webapp config set --resource-group $RESOURCEGROUP --name $SITENAME --startup-file $STARTUPFILE

################################################################################
# Création du service Application Insights
################################################################################

# On ajoute l'extension app insights
az extension add -n application-insights

# On crée une ressource app insights
az monitor app-insights component create -g $RESOURCEGROUP --location $LOCATION --app $APPINSIGHTSNAME --kind web --application-type web

# On lie app insights à l'application web
az monitor app-insights component connect-webapp -g $RESOURCEGROUP -a $APPINSIGHTSNAME --web-app $SITENAME

################################################################################
# Création du service Bot
################################################################################

# On génère un mot de passe aléatoire
APP_PASSWORD=$(uuidgen)

# On génère une azure application et on récupère son id
APP_ID=$(az ad app create --display-name $APPNAME --password $APP_PASSWORD --available-to-other-tenants --query "appId" -o tsv | tr -d '[ \t\n\r\f\v]')

# On crée un Bot
az bot create --resource-group $RESOURCEGROUP --appid $APP_ID --name $BOTNAME --kind "registration"  --location $LOCATION --password $APP_PASSWORD --sku $BOTSKU --endpoint "https://$SITENAME.azurewebsites.net/api/messages"

#################################################################################
## Ajout de settings dans l'application web
#################################################################################

# On ajoute l'id de l'application
az webapp config appsettings set --resource-group $RESOURCEGROUP --name $SITENAME --settings APP_ID=$APP_ID

# On ajoute le mot de passe de l'application
az webapp config appsettings set --resource-group $RESOURCEGROUP --name $SITENAME --settings APP_PASSWORD=$APP_PASSWORD

# On redémarre l'application web
az webapp restart --resource-group $RESOURCEGROUP --name $SITENAME
