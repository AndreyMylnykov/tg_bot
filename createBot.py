import json
from colorama import Fore, Style, init
import os
import glob
import numpy as np
import time
import warnings

# Initialize colorama for colored terminal output
init(autoreset=True)

# Define custom color function for terminal output
def custom_color(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'

# Define custom colors
grey_color = custom_color(80, 80, 80)
green_color = custom_color(47, 201, 0)

# Initialize global filenames
json_filename = ""
npm_filename = ""

# Extract the first string from each sub-array
def extract_first_strings(two_dim_array):
    return [pair[0] for pair in two_dim_array if pair[0]]

# Get a valid number input from the user
def get_number(to, text):
    result = 0
    success = False
    while not success:
        a = input(text)
        try:
            result = int(a)
            if 0 <= result <= to:
                success = True
            else:
                print(Fore.RED + f"Please enter a value between 0 and {to}.")
        except ValueError:
            print(Fore.RED + f"Please enter a valid number between 0 and {to}.")
    return result

# Precompute embeddings and save them to a file
def precompute_embeddings(array_of_phrases, batch_size=1000, filename='precomputed_embeddings.npy'):
    global npm_filename
    npm_filename = filename
    print("Loading model...", grey_color + "(it may take some time, please wait)")
    start_time = time.time()

    # Import the necessary modules only when needed
    from sentence_transformers import SentenceTransformer
    warnings.filterwarnings("ignore", message=".*clean_up_tokenization_spaces*.")

    # Load the model
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    print(Fore.GREEN + f"Model loaded successfully in {round(time.time() - start_time, 1)}s\n")

    print("Precomputing embeddings...", grey_color + "(this can also take a few minutes)")
    phrase_vectors = []

    # Compute embeddings in batches
    for i in range(0, len(array_of_phrases), batch_size):
        batch_phrases = array_of_phrases[i:i + batch_size]
        batch_vectors = model.encode(batch_phrases)
        phrase_vectors.append(batch_vectors)

    # Stack and save embeddings
    phrase_vectors = np.vstack(phrase_vectors).astype('float32')
    np.save(filename, phrase_vectors)
    print(green_color + "Successfully saved embeddings to", Fore.GREEN + filename)
    return phrase_vectors

# Convert message text to a string
def convert_text_to_string(text):
    if isinstance(text, list):
        return "".join(part["text"] if isinstance(part, dict) and "text" in part else str(part) for part in text)
    return text

# Process chat data to extract messages
def process_chat(data):
    print("\nFound", green_color + str(len(data["messages"])), "messages.\n")
    message_dict = {}
    message_array = []
    people = []

    # Iterate through messages and build a dictionary
    for message in data["messages"]:
        if message["type"] == "message" and "text" in message:
            if message["from"] not in people:
                people.append(message["from"])
            message_id = message.get("id")
            if message_id:
                message_dict[message_id] = {
                    "from": message["from"],
                    "text": convert_text_to_string(message["text"]),
                    "reply_to_message_id": message.get("reply_to_message_id")
                }

    # Prompt user to choose a bot persona
    print("Choose who you want to make a bot out of:")
    for number, name in enumerate(people):
        print(" ", str(number), "- ", Fore.CYAN + name)

    number = get_number(len(people) - 1, "\nEnter the corresponding number: ")

    # Create an array of message pairs
    for message_id, message in message_dict.items():
        if message["reply_to_message_id"]:
            reply_message = message_dict.get(message["reply_to_message_id"])
            if reply_message:
                if reply_message["from"] != people[number] and reply_message["text"].strip() and message["text"].strip() and message["from"] == people[number]:
                    message_array.append([reply_message["text"], message["text"]])

    print(green_color + f"Successfully extracted {len(message_array)} messages from replies!")
    return message_array

# Save the processed chat array to a file
def save_chat_array(array, filename='processed_chat.json'):
    global json_filename
    json_filename = filename
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(array, f, ensure_ascii=False, indent=4)
    print(green_color + "Successfully saved chat array to", Fore.GREEN + filename)

# Load a chat array from a file
def load_chat_array(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

try:
    print(Fore.GREEN + "Welcome to createBot.py!", "\nThe goal of this script is to create a", Fore.CYAN + ".npy", "file and a", Fore.CYAN + ".json", "file required for the bot to work.\nFor this, the script requires a", Fore.CYAN + ".json", "file which you can get from Telegram's", Fore.BLUE + '"Export chat history"', "option.\n")

    # Prompt the user to name the bot
    success = False
    while not success:
        name = input("\nChoose a name for the bot: ")
        if name:
            os.makedirs(name, exist_ok=True)
            success = True

    # Save the bot name
    with open(os.path.join(name, "name.txt"), 'w') as file:
        file.write(name)
    name = os.path.join(name, "")

    # Search for JSON files in the current directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_files = glob.glob(os.path.join(script_dir, '*.json'))
    
    val = 0
    if not json_files:
        print(Fore.RED + "No JSON files found in the directory.\nPlease make sure to put a", Fore.CYAN + ".json", "file in the same directory as this script.")
        input("Press ENTER to exit...")
        quit()
    else:
        print("Found", green_color + str(len(json_files)), ".json files in the directory.")

        # If only one JSON file is found, confirm with the user
        if len(json_files) == 1:
            print(green_color + f"JSON file: {os.path.basename(json_files[0])}")
            input("\nPress ENTER if correct...")
        else:
            # List all found JSON files and let the user choose
            for number, json_file in enumerate(json_files):
                print(" ", str(number), "- ", Fore.CYAN + os.path.basename(json_file))

            val = get_number(len(json_files) - 1, "\nEnter the corresponding number for a" + Fore.CYAN + ".json" + Fore.WHITE + " file that you exported from Telegram:")
            print("Processing chat...")

    # Load the selected JSON file
    filename = json_files[val]
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Process the chat data
    message_array = process_chat(data)

    # Save processed chat and precompute embeddings
    save_chat_array(message_array, filename=name + 'processed_chat.json')
    precompute_embeddings(extract_first_strings(message_array), filename=name + 'precomputed_embeddings.npy')

    # Prompt the user for the bot's token and save it
    token = input("\n\nEnter the bot's token from BotFather" + grey_color + " (you can change it later in a file token.txt)" + Fore.WHITE + ": ")
    with open(name + "token.txt", 'w') as file:
        file.write(token)

    print("\n\nDone! Now you have two files:", Fore.CYAN + json_filename, "and", Fore.CYAN + npm_filename, ". The bot is ready to use now. You can launch the bot with launchBot.py")
    input("\nPress ENTER...")

except Exception as ex:
    print(Fore.RED + f"FATAL ERROR: {str(ex)}")
    input("\n\nPress ENTER to exit...")
