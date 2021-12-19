#!/bin/bash

# On installe la clé GPG du référentiel de packages Microsoft pour valider l’intégrité du package
curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
sudo mv microsoft.gpg /etc/apt/trusted.gpg.d/microsoft.gpg

# On configure la liste de sources APT avant d’effectuer une mise à jour d’APT
sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/microsoft-ubuntu-$(lsb_release -cs)-prod $(lsb_release -cs) main" > /etc/apt/sources.list.d/dotnetdev.list'

# On installe le package Functions Core Tools
sudo apt-get update
sudo apt-get install azure-functions-core-tools-3

# On importe les configuration
source function_config.txt

# Create a resource group.
az group create \
  --name $FUNCTION_RG \
  --location $FUNCTION_LOC

# On crée un espace de stockage dans le groupe de ressource de l'azure function
az storage account create \
  --name $FUNCTION_STORAGE \
  --location $FUNCTION_LOC \
  --resource-group $FUNCTION_RG \
  --sku Standard_LRS

# On crée l'application web qui va faire tourner l'azure function
az functionapp create \
  --name $FUNCTION_NAME \
  --storage-account $FUNCTION_STORAGE \
  --consumption-plan-location $FUNCTION_LOC \
  --resource-group $FUNCTION_RG \
  --runtime python \
  --runtime-version 3.8 \
  --functions-version 3 \
  --os-type linux

echo "Créer un secret Github avec la clé AZURE_FUNCTION_PUBLISH_PROFILE et la valeur suivante :"

# On affiche le profile de publication de l'application
az functionapp deployment list-publishing-profiles \
  --name $FUNCTION_NAME \
  --resource-group $FUNCTION_RG \
  --xml