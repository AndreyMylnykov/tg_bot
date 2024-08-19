import json
from colorama import Fore, Style, init
import os
import glob
import numpy as np
import time
import warnings

init(autoreset=True)
def custom_color(r, g, b):
    return f'\033[38;2;{r};{g};{b}m'
grey_color = custom_color(80, 80, 80)
json_filename = ""
npm_filename = ""

def extract_first_strings(two_dim_array):
    return [pair[0] for pair in two_dim_array if pair[0]]

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

def precompute_embeddings(array_of_phrases, batch_size=1000, filename='precomputed_embeddings.npy'):
    global npm_filename
    npm_filename = filename
    print("Loading model...", grey_color + "(it may take some time, plesae wait)")
    start_time = time.time()

    from sentence_transformers import SentenceTransformer
    warnings.filterwarnings("ignore", message=".*clean_up_tokenization_spaces*.")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    print(Fore.GREEN + f"Model loaded successfully in {round(time.time() - start_time,1)}s\n")

    print("Precomputing embeddings...", grey_color + "(this can also take a few minutes)")
    phrase_vectors = []
    for i in range(0, len(array_of_phrases), batch_size):
        batch_phrases = array_of_phrases[i:i + batch_size]
        batch_vectors = model.encode(batch_phrases)
        phrase_vectors.append(batch_vectors)
    phrase_vectors = np.vstack(phrase_vectors).astype('float32')
    np.save(filename, phrase_vectors)  # Save embeddings for later use
    print(green_color + "Successfully saved embeddings to", Fore.GREEN + filename)
    return phrase_vectors

def convert_text_to_string(text):
    if isinstance(text, list):
        return "".join(part["text"] if isinstance(part, dict) and "text" in part else str(part) for part in text)
    return text

def process_chat(data):
    print("\nFound", green_color + str(len(data["messages"])), "messages.\n")
    message_dict = {}
    message_array = []
    people = []
    
    
    for message in data["messages"]:
        if message["type"] == "message" and "text" in message:
            if not message["from"] in people:
                people.append(message["from"])
            message_id = message.get("id")
            if message_id:
                message_dict[message_id] = {
                    "from": message["from"],
                    "text": convert_text_to_string(message["text"]),
                    "reply_to_message_id": message.get("reply_to_message_id")
                }
    print("Choose who you want to make a bot out of:")
    for number, name in enumerate(people):
        print(" ", str(number),"- ",Fore.CYAN + name)

    number = get_number(1, "\nEnter the corresponding number: ")

    for message_id, message in message_dict.items():
        if message["reply_to_message_id"]:
            reply_message = message_dict.get(message["reply_to_message_id"])
            if reply_message:
                # Check if the reply message is not from you and neither message is empty
                if reply_message["from"] != people[number] and reply_message["text"].strip() and message["text"].strip() and message["from"] == people[number]:
                    # Add the original message and its reply to the array
                    message_array.append([reply_message["text"], message["text"]])

    print(green_color + f"Successfully extracted {len(message_array)} messages from replies!")
    return message_array

def saveChatArray(array, filename = 'processed_chat.json'):
    global json_filename
    json_filename = filename
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(array, f, ensure_ascii=False, indent=4)
    print(green_color + "Successfully saved chat array to", Fore.GREEN + filename)

def loadChatArray(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

try:
    green_color = custom_color(47, 201, 0)

    print(Fore.GREEN + "Welcome to createBot.py!","\nThe goal of this script is to create a",Fore.CYAN + ".npy", "file and a",Fore.CYAN+".json","files that are required for the bot to work.\nFor this, the script requires a",Fore.CYAN + ".json","file which you can get from Telegram's",Fore.BLUE + '"Export chat history"', "option.\n")

    script_dir = os.path.dirname(os.path.abspath(__file__))

    json_files = glob.glob(os.path.join(script_dir, '*.json'))

    num_files = len(json_files)
    val = 0
    if num_files == 0:
        print(Fore.RED + "No JSON files found in the directory.\n", "Please make sure to put a",Fore.CYAN + ".json","file in the same directory as this script.")
        input("Press ENTER to exit...")
        quit()
    else:
        print("Found", green_color + str(num_files), ".json files in the directory.")
        if num_files == 1:

            for json_file in json_files:
                print(green_color + f"JSON file: {os.path.basename(json_file)}")
                input("\nPress ENTER if correct...")
        else:
            for number, json_file in enumerate(json_files):
                print(" ", str(number),"- ",Fore.CYAN + str(os.path.basename(json_file)))

            #HERE!
            val = get_number(num_files-1, "\nEnter the corresponding number for a" + Fore.CYAN + ".json"+Fore.WHITE +" file that you exported from Telegram:")
            print("Processing chat...")

    filename = json_files[val]


    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    message_array = process_chat(data)
    saveChatArray(message_array)

    precompute_embeddings(extract_first_strings(message_array))
    print("\n\nDone! Now you have two files:", Fore.CYAN + json_filename, "and", Fore.CYAN + npm_filename, ". The bot is ready to use now. You can launch the bot with launchBot.py")
    input("\nPress ENTER...")

except Exception as ex:
    print(Fore.RED + f"FATAL ERROR: {str(ex)}")
    input("\n\nPress ENTER to exit...")