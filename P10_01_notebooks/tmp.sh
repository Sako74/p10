SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
CHATBOT_APP_DIR="conda_env.yml"

tail "$SCRIPT_DIR/$CHATBOT_APP_DIR"