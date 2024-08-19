# Telegram Chatbot

This project provides a way to create and launch a Telegram chatbot using historical chat data. It involves two main scripts:

- createBot.py - Prepares data and embeddings needed for the bot.
- launchBot.py - Launches the bot using the prepared data.

## Overview

## createBot.py

This script prepares the necessary files for the chatbot by processing chat history and generating embeddings.

### Features:

- Loads chat data from a JSON file exported from Telegram.
- Processes the chat data to extract message pairs.
- Precomputes sentence embeddings and saves them to a .npy file.
- Saves processed chat data to a .json file.
- Prompts for a bot name and token.

### Usage:

Prepare your environment:

- Ensure you have Python 3.x installed.
- Install required packages: colorama, numpy, sentence-transformers.
- Run the script:

```bash
python createBot.py
```

Follow the prompts to:

- Choose a name for the bot.
- Select the JSON file containing chat history.
- Provide a token from BotFather on Telegram.
Files created:

- processed_chat.json - Contains processed chat data.
- precomputed_embeddings.npy - Contains precomputed sentence embeddings.
- token.txt - Contains the bot token.

## launchBot.py

This script launches the chatbot using the precomputed data and the bot token.

### Features:

- Loads the processed chat data and embeddings.
- Uses the SentenceTransformer model to find similar phrases.
- Integrates with Telegram using python-telegram-bot library.
- Responds to messages based on the precomputed embeddings.

# Usage:
### Prepare your environment:

- Ensure you have Python 3.x installed.
- Install required packages: colorama, numpy, sentence-transformers, faiss, python-telegram-bot.
- Run the script:

```bash
python launchBot.py
```


It will be ready to respond to messages in groups or private chats.


# Dependencies

- Python 3.x
- colorama
- numpy
- sentence-transformers
- faiss
- python-telegram-bot
## Install the required packages using:

```bash
pip install colorama numpy sentence-transformers faiss python-telegram-bot
```

# Notes

- Ensure the JSON file exported from Telegram is in the same directory as createBot.py before running it.
- Make sure to keep your bot token secure. Do not expose it publicly.

# Troubleshooting

- No JSON files found: Make sure you have exported a chat history from Telegram and placed the JSON file in the same directory as createBot.py.
- Module not found errors: Ensure all required packages are installed correctly.
- Bot not responding: Check that the bot token is correct and that the bot is properly added to the chat or group.

# License

This project is licensed under the MIT License. See the LICENSE file for details.
