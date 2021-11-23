# On importe les configuration
source "P10_03_chatbot/config.txt"

# On se positionne dans le dossier de l'application web
pushd "P10_03_chatbot/app/"

# On crée les réssources et on déploie les fichiers présent dans le dossier de l'application web
az webapp up -g $CHATBOT_RG -n $CHATBOT_APP_SITE_NAME -l $CHATBOT_APP_LOC --plan $CHATBOT_APP_PLAN_NAME --runtime $CHATBOT_APP_RUNTIME --sku $CHATBOT_APP_SKU

popd