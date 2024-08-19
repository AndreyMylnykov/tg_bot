import time
from colorama import Fore, Style, init
init(autoreset=True)
def custom_color(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'
grey_color = custom_color(80, 80, 80)
green_color = custom_color(47, 201, 0)

import os
def get_number(to, text):
    result = 0
    success = False
    while not success:
        a = input(text)
        try:
            result = int(a)
            if result >= 0 and result <= to:
                success = True
            else:
                print(Fore.RED + f"Please enter a value between 0 and {to}.")
        except:
            print(Fore.RED + f"Please enter a valid number between 0 and {to}..")
    return result

script_directory = os.path.dirname(os.path.abspath(__file__))

bot_folders = [
    name for name in os.listdir(script_directory)
    if os.path.isdir(os.path.join(script_directory, name)) and
    os.path.isfile(os.path.join(script_directory, name, 'name.txt'))
]


number = 0
print(Fore.GREEN + "Welcome to launchBot.py!", "\nThis program launches a Telegram bot based on the chat history. For this bot to work, you'll need 3 things:\n1. processed_chat.json\n2. precomputed_embeddings.npy\n3. Bot token\n\nTo get the first two, you'll need to first launch the createBot.py script. For the third, just google it.\n")
if len(bot_folders) == 0:
    input("There are no bot folders in the script's directory. Please visit createBot.py...")
    exit()
elif len(bot_folders) == 1:
    input("Press ENTER to launch: "+ Fore.CYAN + bot_folders[0])
else:
    print("Choose which bot to launch:")
    for number, name in enumerate(bot_folders):
        print(" ", str(number),"-",Fore.CYAN + name)
    number = get_number(len(bot_folders)-1, "\nEnter the corresponding number: ")

print(bot_folders[number])


print(Fore.CYAN + "Initializing modules...")
start_time = time.time()

import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import warnings
import random
import re
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")



model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print(Fore.GREEN + f"Initialized all modules in {round(time.time() - start_time,1)}s\n")


def load_chat_array(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

# New function to precompute and save embeddings
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

def load_embeddings(filename):
    return np.load(filename)



def find_similar(phrase, embeddings, k=5):
    # Encode the input phrase
    phrase_vector = model.encode([phrase]).astype('float32')

    # Create a FAISS index and add embeddings to it
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    # Search for the k nearest neighbors
    D, I = index.search(phrase_vector, k)

    # Randomly select one of the k nearest neighbors
    selected_index = np.random.choice(I[0])
    return selected_index
    

def extract_first_strings(two_dim_array):
    return [pair[0] for pair in two_dim_array if pair[0]]


def get_answer(text, embeddings, message_array):
    index = find_similar(text, embeddings)
    my_message, his_message = loaded_message_array[index]
    #print(grey_color + f"({my_message})")
    return his_message


loaded_message_array = load_chat_array(bot_folders[number]+"/"+'processed_chat.json')
inputs = extract_first_strings(loaded_message_array)

#embeddings = precompute_embeddings(inputs)
embeddings = load_embeddings(bot_folders[number]+"/"+'precomputed_embeddings.npy')


'''
               TELEGRAM PART
'''


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

def get_response(input_text):
    return get_answer(input_text, embeddings, loaded_message_array)

def start(update, context):
    global name
    update.message.reply_text("Hello, I'm "+name+". Ask me anything!")

def handle_message(update, context):
    global name
    user_input = update.message.text

    chat_type = update.message.chat.type  # Get the type of chat
    answering = False


    if update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
        answering = True
    elif chat_type == 'group' or chat_type == 'supergroup':
        chance = 0.2
        if random.random() < chance or name.lower() in user_input.lower():
            answering = True
            #user_input = re.sub(r'свят', '', user_input, flags=re.IGNORECASE)
            #print(user_input)

    elif chat_type == 'private':
        answering = True

    if answering:
        response = get_response(user_input)
        print(f"{update.message.from_user.full_name}: {user_input}")
        print(f"Bot Response: {response}\n")
        
        update.message.reply_text(response)
    else:
        print("ignoring")

name = ''
def main():
    global name
    filename = bot_folders[number]+ "/token.txt"
    TOKEN = ''

    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            TOKEN = file.read().strip()
        #print(f"Token read from file: {TOKEN}")
    else:
        TOKEN = input("Enter your Bot token from BotFather: ")
        
        with open(filename, 'w') as file:
            file.write(TOKEN)
        print(f"Token saved to {filename}")

    filename =bot_folders[number]+ "/name.txt"

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

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()