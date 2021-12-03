#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os

from dotenv import load_dotenv


class DefaultConfig:
    """Configuration for the bot."""

    def __init__(self):
        load_dotenv()

        self.PORT = 3978
        self.CHATBOT_BOT_ID = os.environ.get("CHATBOT_BOT_ID", "")
        self.CHATBOT_BOT_PASSWORD = os.environ.get("CHATBOT_BOT_PASSWORD", "")
        self.LUIS_APP_ID = os.environ.get("LUIS_APP_ID", "")
        self.LUIS_PRED_KEY = os.environ.get("LUIS_PRED_KEY", "")
        self.LUIS_PRED_ENDPOINT = os.environ.get("LUIS_PRED_ENDPOINT", "")
        self.APPINSIGHTS_INSTRUMENTATIONKEY = os.environ.get("APPINSIGHTS_INSTRUMENTATIONKEY", "")
