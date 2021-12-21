# On importe les configurations
source "alert_config.txt"
source "../P10_03_chatbot/chatbot_config.txt"
source "../P10_04_function/function_config.txt"

# On récupère les infos de la fonction azure
FUNCTION_ID=$(az functionapp show -n $FUNCTION_NAME -g $FUNCTION_RG --query id --output tsv)
FUNCTION_URL=$(az functionapp function show -n $FUNCTION_NAME -g $FUNCTION_RG --function-name $FUNCTION_APP_NAME --query invokeUrlTemplate -o tsv)

# On crée un groupe d'actions qui va trigger la fonction azure
az monitor action-group create \
-n $ALERT_ACTION_GROUP_NAME \
-g $CHATBOT_RG \
--action azurefunction az-function $FUNCTION_ID $FUNCTION_APP_NAME $FUNCTION_URL usecommonalertschema

# On récupère les infos du groupe d'actions
CHATBOT_ACTIONS_ID=$(az monitor action-group show -n $ALERT_ACTION_GROUP_NAME -g $CHATBOT_RG --query id -o tsv)

# On récupère les infos du service application insight du chatbot
CHATBOT_APP_INSIGHTS_ID=$(az monitor app-insights component show -g $CHATBOT_RG --app $CHATBOT_APP_INSIGHTS_NAME --query id --output tsv)

# On crée l'alert qui va monitorer le nombre d'insatisfactions
az monitor scheduled-query create \
-n $ALERT_NAME \
-g $CHATBOT_RG \
--scopes $CHATBOT_APP_INSIGHTS_ID \
--condition "count 'Placeholder_1' > $ALERT_COUNT_MAX" \
--condition-query Placeholder_1="$ALERT_QUERY" \
--description "$ALERT_DESC" \
--action $CHATBOT_ACTIONS_ID \
--evaluation-frequency $ALERT_EVAL_FREQ \
--window-size $ALERT_WIN_SIZE \
--severity 2 \
--auto-mitigate false 
