# On importe les configuration
source chatbot_config.txt

# On se positionne dans le dossier de l'application web
cd P10_02_chatbot/

# On crée les réssources et on déploie les fichiers présent dans le dossier de l'application web
az webapp up --resource-group $RESOURCEGROUP --name $SITENAME --location $LOCATION --plan $PLANNAME --runtime $RUNTIME --sku $PLANSKU
