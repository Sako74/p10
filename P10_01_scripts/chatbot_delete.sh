# On importe les configuration
source "P10_01_scripts/chatbot_config.txt"

# On supprime le groupe de ressources du chatbot
az group delete --name $CHATBOT_RG --yes

# On récupère l'id de l'app
CHATBOT_BOT_OBJECT_ID=$(az ad app list --display-name p10-chatbot-bot --query "[0].objectId" -o tsv | tr -d '[ \t\n\r\f\v]')

# On supprime l'app
az rest --method DELETE --url https://graph.microsoft.com/v1.0/applications/$CHATBOT_BOT_OBJECT_ID
