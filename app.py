from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from sentence_transformers import SentenceTransformer
from werkzeug.utils import secure_filename
from flask import send_from_directory
from langdetect import detect
from pymongo import MongoClient
import numpy as np
import json, os, datetime, openai, pyttsx3, threading, time



app = Flask(__name__, static_folder='./app',
            static_url_path='/', template_folder='./app')
CORS(app)
# Replace this with a random string.
app.secret_key = 'MTCHATBOTisrunnedbyYASIJI'

AUDIO_FOLDER = './audio_files'
client = MongoClient(os.getenv('MONGODB_URI'))
model = SentenceTransformer(os.getenv('MODEL_PATH'))
openai.api_key = os.getenv('OPENAI_API_KEY')

# Replace this with your MongoDB Atlas connection string.
db = client['chatbot']
chat_collection = db['chats']

app.config['prompt_response_pairs'] = None
app.config['prompt_embeddings'] = None

# Detect the language:
def detect_language(text):
    try:
        return detect(text)
    except:
        return 'en'  # default to French if detection fails

# Your text_to_speech function
def text_to_speech(text, filename):
    engine = pyttsx3.init()

    # Set properties for the speech engine
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1)   # Volume (0.0 to 1.0)

    # Set the desired voice
    lang = detect_language(text)
    if lang.startswith('en'):
        engine.setProperty('voice', 'english')  # Use default English voice
    elif lang.startswith('fr'):
        engine.setProperty('voice', 'french')   # Use default French voice
    elif lang.startswith('ar'):
        engine.setProperty('voice', 'arabic')   # Use default Arabic voice
    # Add more language cases if necessary

    engine.save_to_file(text, f'{AUDIO_FOLDER}/{filename}')
    engine.runAndWait()

def read_jsonl_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.read().splitlines()
    data = [json.loads(line) for line in lines]
    return data


def load_prompts_and_responses(filepath):
    app.config['prompt_response_pairs'], app.config['prompt_embeddings']
    data = read_jsonl_file(filepath)
    app.config['prompt_response_pairs'] = [
        (entry['prompt'], entry['completion']) for entry in data]
    app.config['prompt_embeddings'] = model.encode(
        [pair[0] for pair in app.config['prompt_response_pairs']])


def cosine_similarity(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)


def get_response_for_input(user_input, chat_id):
    chat_data = chat_collection.find_one({'chat_id': chat_id})

    if chat_data is None:
        # This is a new chat, let's create a chat document in the database
        chat_data = {
            'chat_id': chat_id,
            'messages': [
                {
                    'role': 'user',
                    'content': user_input,
                    'time': datetime.datetime.now()
                }
            ]
        }
        chat_collection.insert_one(chat_data)
    else:
        # This is an existing chat, let's append the new user message to the messages list
        chat_collection.update_one(
            {'chat_id': chat_id},
            {'$push': {'messages': {'role': 'user',
                                    'content': user_input, 'time': datetime.datetime.now()}}}
        )
        # Let's fetch the updated chat data
        chat_data = chat_collection.find_one({'chat_id': chat_id})

    messages_for_gpt3 = [{'role': msg['role'], 'content': msg['content']}
                         for msg in chat_data['messages']]

    threshold = 0.68
    input_embedding = model.encode([user_input])
    best_match = {'similarity': 0, 'response': None}
    for pair, prompt_embedding in zip(app.config['prompt_response_pairs'], app.config['prompt_embeddings']):
        similarity = cosine_similarity(input_embedding[0], prompt_embedding)
        if similarity > threshold and similarity > best_match['similarity']:
            best_match = {'similarity': similarity, 'response': pair[1]}

    if best_match['response'] is None:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=[
                {'role': 'system', 'content': "You are a helpful assistant."},
                *messages_for_gpt3
            ]
        )
        response = response['choices'][0]['message']['content']
    else:
        response = best_match['response']

    # Add bot's response to the messages list
    chat_collection.update_one(
        {'chat_id': chat_id},
        {'$push': {'messages': {'role': 'assistant',
                                'content': response, 'time': datetime.datetime.now()}}}
    )

    # Generate the filename for the output mp3 file
    filename = f"{chat_id}_response.mp3"
    filepath = os.path.join(AUDIO_FOLDER, filename)

    # Start a new thread to generate the audio file
    thread = threading.Thread(target=text_to_speech, args=(response, filename))
    thread.start()
    thread.join()  # Wait for the thread to finish

    return response, filename


load_prompts_and_responses('ALX_DATA.jsonl')


@app.route('/')
def home():
    return render_template('index.html')


ALLOWED_EXTENSIONS = {'mp3', 'mp4', 'mpeg', 'mpga', 'm4a', 'wav', 'webm'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def cleanup_old_files(directory, max_age=300):
    """Delete all files in a directory older than max_age (default is 24 hours)."""
    now = time.time()

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        # Check if the file is a file (not a directory) and if it's older than max_age
        if os.path.isfile(filepath) and os.path.getmtime(filepath) < now - max_age:
            os.remove(filepath)

# Call the cleanup function every hour in a background thread


def cleanup_thread():
    while True:
        cleanup_old_files('./audio_files')
        time.sleep(60)


cleanup_thread = threading.Thread(target=cleanup_thread, daemon=True)
cleanup_thread.start()


def process_message(message):
    chat_id = session['chat_id']
    chat_data = chat_collection.find_one({'chat_id': chat_id})
    if chat_data is None:
        chat_data = {
            'chat_id': chat_id,
            'messages': [{'role': 'system', 'content': "You are a helpful assistant."}, {'role': 'user', 'content': message}]
        }
    else:
        chat_data['messages'].append({'role': 'user', 'content': message})

    response, filename = get_response_for_input(message, chat_id)
    chat_data['messages'].append({'role': 'assistant', 'content': response})

    chat_collection.replace_one({'chat_id': chat_id}, chat_data, upsert=True)

    return response, filename


@app.route('/message', methods=['POST'])
def message():
    message = request.json['message']

    if 'chat_id' not in session:
        session['chat_id'] = os.urandom(24).hex()
    response, filename = process_message(message)

    # Print input and output with IP address and date in the console
    ip_address = request.remote_addr
    current_time = datetime.datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")
    print(f"{ip_address} - - {current_time} User Input: {message}")
    print(f"{ip_address} - - {current_time} Chatbot Response: {response}")

    # Updated this line
    return jsonify({'message': response, 'audio': f'http://localhost:3010/audio_files/{filename}'})


@app.route('/transcribe_audio', methods=['POST'])
def transcribe_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(
            "Audio/", filename)
        file.save(filepath)

        with open(filepath, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)

        audio_message = transcript["text"]

        if 'chat_id' not in session:
            session['chat_id'] = os.urandom(24).hex()
            response, filename = process_message(audio_message)

    # Print input with IP address and date in the console
    ip_address = request.remote_addr
    current_time = datetime.datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")
    print(f"{ip_address} - - {current_time} User Input (Audio): {audio_message}")

    # Updated this line
    return jsonify({'transcript': audio_message, 'audio': f'http://localhost:3010/audio_files/{filename}'})


@app.route('/audio_files/<filename>')
def serve_audio_file(filename):
    return send_from_directory(AUDIO_FOLDER, filename)


if __name__ == '__main__':
    app.run(host="localhost", port=3010)
