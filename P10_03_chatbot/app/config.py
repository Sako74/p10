#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 3978
    APP_ID = os.environ.get("APP_ID", "")
    APP_PASSWORD = os.environ.get("APP_PASSWORD", "")
    LUIS_APP_ID = os.environ.get("LUIS_APP_ID", "312feabb-a787-4ed9-9435-5aec64f921cd")
    LUIS_API_KEY = os.environ.get("LUIS_API_KEY", "ecd2957d50b34a6f801e23081b921cf2")
    LUIS_API_HOST_NAME = os.environ.get("LUIS_API_HOST_NAME", "westus.api.cognitive.microsoft.com/")
    APPINSIGHTS_INSTRUMENTATIONKEY = os.environ.get("APPINSIGHTS_INSTRUMENTATIONKEY", "35e22e42-ab70-4baa-a500-e56275d76a0f")
