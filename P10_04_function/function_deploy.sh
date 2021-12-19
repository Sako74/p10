#!/bin/bash

source function_config.txt

# On initialise les fichiers de configuration
func init . --python

# On déploie l'azure function
func azure functionapp publish $FUNCTION_NAME