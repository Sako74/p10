# On importe les configuration
source chatbot_config.txt

# On supprime le groupe de ressources du chatbot
az group delete --name $CHATBOT_RG --yes