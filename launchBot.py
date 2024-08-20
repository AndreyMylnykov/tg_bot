import time
from colorama import Fore, init
init(autoreset=True)

# Function to generate a custom color
def custom_color(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'

# Define colors
grey_color = custom_color(80, 80, 80)
green_color = custom_color(47, 201, 0)

import os

# Function to get a valid number input from the user
def get_number(to, text):
    while True:
        a = input(text)
        try:
            result = int(a)
            if 0 <= result <= to:
                return result
            else:
                print(Fore.RED + f"Please enter a value between 0 and {to}.")
        except ValueError:
            print(Fore.RED + f"Please enter a valid number between 0 and {to}.")

# Get the current script's directory
script_directory = os.path.dirname(os.path.abspath(__file__))

# Get a list of bot folders that contain a name.txt file
bot_folders = [
    name for name in os.listdir(script_directory)
    if os.path.isdir(os.path.join(script_directory, name)) and
    os.path.isfile(os.path.join(script_directory, name, 'name.txt'))
]

print(Fore.GREEN + "Welcome to launchBot.py!")
print("\nThis program launches a Telegram bot based on the chat history. For this bot to work, you'll need 3 things:")
print("1. processed_chat.json")
print("2. precomputed_embeddings.npy")
print("3. Bot token\n")
print("To get the first two, you'll need to first launch the createBot.py script. For the third, just google it.\n")

# Handle cases based on the number of bot folders available
if len(bot_folders) == 0:
    input("There are no bot folders in the script's directory. Please visit createBot.py...")
    exit()
elif len(bot_folders) == 1:
    input("Press ENTER to launch: " + Fore.CYAN + bot_folders[0])
else:
    print("Choose which bot to launch:")
    for number, name in enumerate(bot_folders):
        print(" ", str(number), "-", Fore.CYAN + name)
    number = get_number(len(bot_folders) - 1, "\nEnter the corresponding number: ")

print(Fore.CYAN + "Initializing modules...")
start_time = time.time()

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import warnings
import random
import re

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")

# Load the SentenceTransformer model
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print(Fore.GREEN + f"Initialized all modules in {round(time.time() - start_time, 1)}s\n")

# Function to load chat array from a JSON file
def load_chat_array(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# Function to precompute and save embeddings
def precompute_embeddings(array_of_phrases, batch_size=1000, filename='precomputed_embeddings.npy'):
    print("Precomputing embeddings...")
    phrase_vectors = []
    for i in range(0, len(array_of_phrases), batch_size):
        batch_phrases = array_of_phrases[i:i + batch_size]
        batch_vectors = model.encode(batch_phrases)
        phrase_vectors.append(batch_vectors)
    phrase_vectors = np.vstack(phrase_vectors).astype('float32')
    np.save(filename, phrase_vectors)  # Save embeddings for later use
    return phrase_vectors

# Function to load precomputed embeddings from a file
def load_embeddings(filename):
    return np.load(filename)

# Function to find similar phrases using FAISS
def find_similar(phrase, embeddings, k=5):
    phrase_vector = model.encode([phrase]).astype('float32')
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    D, I = index.search(phrase_vector, k)
    selected_index = np.random.choice(I[0])
    return selected_index

# Function to extract the first element from each pair in a 2D array
def extract_first_strings(two_dim_array):
    return [pair[0] for pair in two_dim_array if pair[0]]

# Function to get an answer based on the input text
def get_answer(text, embeddings, message_array):
    index = find_similar(text, embeddings)
    my_message, his_message = loaded_message_array[index]
    return his_message

# Load the chat array and embeddings
loaded_message_array = load_chat_array(bot_folders[number] + "/" + 'processed_chat.json')
inputs = extract_first_strings(loaded_message_array)
embeddings = load_embeddings(bot_folders[number] + "/" + 'precomputed_embeddings.npy')

'''
               TELEGRAM PART
'''

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Function to get a response from the bot
def get_response(input_text):
    return get_answer(input_text, embeddings, loaded_message_array)

# Handler for the /start command
def start(update, context):
    global name
    update.message.reply_text("Hello, I'm " + name + ". Ask me anything!")

# Handler for incoming messages
def handle_message(update, context):
    global name
    try:
        user_input = update.message.text
        chat_type = update.message.chat.type  # Get the type of chat
        message_time = update.message.date.timestamp()  # Get the message timestamp
        answering = False

        # Only respond to messages sent after the bot was started
        if message_time > bot_start_time:
            if update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
                answering = True
            elif chat_type in ['group', 'supergroup']:
                chance = 0.2
                if random.random() < chance or name.lower() in user_input.lower():
                    answering = True
            elif chat_type == 'private':
                answering = True

            if answering:
                response = get_response(user_input)
                print(f"{update.message.from_user.full_name}: {user_input}")
                print(f"Bot Response: {response}\n")
                update.message.reply_text(response)
            else:
                print("Ignoring message.")
        else:
            print("Ignoring old message.")
    except Exception as ex:
        print(Fore.RED + f"FATAL ERROR: {str(ex)}")
        input("\n\nPress ENTER to exit...")


name = ''
bot_start_time = time.time()

# Main function to start the bot
def main():
    global name
    try:
        filename = bot_folders[number] + "/token.txt"
        TOKEN = ''

        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                TOKEN = file.read().strip()
        else:
            TOKEN = input("Enter your Bot token from BotFather: ")
            with open(filename, 'w') as file:
                file.write(TOKEN)
            print(f"Token saved to {filename}")

        filename = bot_folders[number] + "/name.txt"

        if os.path.isfile(filename):
            with open(filename, 'r') as file:
                name = file.read().strip()
        else:
            name = input("Enter your Bot's name: ")
            with open(filename, 'w') as file:
                file.write(name)
            print(f"Name saved to {filename}")

        updater = Updater(TOKEN, use_context=True)
        dp = updater.dispatcher

        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

        print("The bot is running.")
        updater.start_polling()
        updater.idle()
    except Exception as ex:
        print(Fore.RED + f"FATAL ERROR: {str(ex)}")
        input("\n\nPress ENTER to exit...")

if __name__ == '__main__':
    main()
