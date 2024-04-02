## AI Chatbot with Speech Recognition and Synthesis
![alxchatbot](app/logo.png)

This project implements an AI chatbot with speech recognition and synthesis capabilities. The chatbot can interact with users via text and audio inputs, providing responses generated by AI models. It utilizes technologies such as Flask, SentenceTransformer, OpenAI's GPT-3, and pyttsx3 for text-to-speech conversion.

## Features

Text Interaction: Users can communicate with the chatbot via text inputs.

Audio Interaction: Users can also interact with the chatbot using audio inputs.
*
Speech Recognition: Audio inputs are transcribed into text using OpenAI's Speech API.

Speech Synthesis: Text responses from the chatbot are converted into speech using pyttsx3.

Persistent Chat History: Chat history is stored in a MongoDB database for future reference.

AI-based Responses: The chatbot utilizes GPT-3 from OpenAI for generating responses.

## Setup

Clone the Repository:

```bash
git clone https://github.com/MohammmedBENHADINE/alxchatbot.git
cd alxchatbot
```
Install Dependencies:


```bash
pip install -r requirements.txt
```
### Environment Variables:

Set up environment variables for MongoDB URI, OpenAI API key, and model paths.
### Run the Server:

```bash
env MODEL_PATH=Model/all-mpnet-base-v2 OPENAI_API_KEY=sk-[your openia key] MONGODB_URI=mongodb+srv://[user:password]@cluster0.zxe1qwo.mongodb.net/ python app.py
```
### Access the Chatbot:

Open a web browser and navigate to https://localhost:3010.

## Usage
Visit the web interface to interact with the chatbot.

Type messages in the text input field or click the microphone button to speak.

Chat history is displayed in real-time, including both user and chatbot messages.

Audio responses are played automatically after receiving them.

## Contributors

Mohammed Benhadine

## Known issues

pyttsx3 : doesn't work on Linux for some reason, need to shift to another engine