# On importe les configuration
source chatbot_config.txt

# On se positionne dans le dossier de l'application
cd $SITEDIR

# On supprime le groupe de ressources de l'application
az group delete --name $RESOURCEGROUP --yes
