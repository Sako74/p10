# On importe les configurations
source "alert_config.txt"
source "../P10_03_chatbot/chatbot_config.txt"

# On supprime le groupe d'actionse
az monitor action-group delete \
-n $ALERT_ACTION_GROUP_NAME \
-g $CHATBOT_RG

# On supprime l'alerte
az monitor scheduled-query delete \
-n $ALERT_NAME \
-g $CHATBOT_RG \
--yes
