import speech_recognition as sr
import pyttsx3
import datetime
import logging
import os
import webbrowser
import wikipedia
import random
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

#configure logging 

LOG_DIR="logs"
LOG_FILE_NAME ="application.log"

os.makedirs(LOG_DIR,exist_ok=True)
log_path = os.path.join(LOG_DIR , LOG_FILE_NAME)

logging.basicConfig(
    filename=log_path,
    format="[ %(asctime)s ] %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)


#Activate the speech engine 
engine = pyttsx3.init("sapi5")
engine.setProperty("rate",150)
voices =engine.getProperty("voices")
engine.setProperty("voice",voices[1].id)

# Function to make the assistant speak
def speak(text):
    """This function makes the assistant speak the given text.
    
    Args:
         text
    returns:
         voice
    """
    engine.say(text)
    engine.runAndWait()


# speak("Hi I am Sami friend of Mojo")

# speak("Hello, I am your assistant. How can I help you today?")

def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=0.3)

        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=7)
        except Exception as e:
            print("No input detected...")
            return ""

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
        return query

    except Exception as e:
        logging.info(e)
        print("Say that again please...")
        return ""


#AI intregated here
def gemini_response(user_text):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(user_text)
        return response.text
    except Exception as e:
        logging.error(e)
        return "Sorry, I couldn't process that."


def greeting():
    """This function greets the user based on the time of day.
    
    Args:
         None
    returns:
         None
    """
    hour = int(datetime.datetime.now().hour)
    if 0 <= hour < 12:
        speak("Good Morning!")
    elif 12 <= hour < 18:
        speak("Good Afternoon!")   
    else:
        speak("Good Evening!")  
    speak("I am Cutie .I am your personal voice assistant. Please tell me how may I help you")

greeting()

while True:
    query = takeCommand().lower()
    print(query)
    if "your name" in query:
        speak("I am Cutie.")
        logging.info("User asked for assistant's name.")
    elif "time" in query:
        strTime = datetime.datetime.now().strftime("%H:%M:%S")    
        speak(f"The time is {strTime}")
        logging.info("User asked for current time.")

    elif "exit" in query or "quit" in query or "goodbye" in query:
        speak("Sure! Turning myself off. Call me anytime you need me. Bye!")
        break
    elif "how are you" in query:
        speak("I am fine, thank you. How can I assist you today?")
        logging.info("User asked how the assistant is doing.")

    elif "who created you" in query or "who made you" in query:
        speak("I was created by InHuman.")
        logging.info("User asked about the assistant's creator.")

    elif "open google" in query:
        webbrowser.open("https://www.google.com")
        speak("Opening Google.")
        logging.info("User requested to open Google.")
    elif "open calculator" in query:
        subprocess.Popen('calc.exe')
        speak("Opening Calculator.")
        logging.info("User requested to open Calculator.")
    elif "open notepad" in query:
        subprocess.Popen('notepad.exe')
        speak("Opening Notepad.")
        logging.info("User requested to open Notepad.")
   
    elif "command prompt" in query:
        subprocess.Popen('cmd.exe')
        speak("Opening Command Prompt.")
        logging.info("User requested to open Command Prompt.")
    elif "open youtube" in query:
        search_keyword = ""

    # Find keyword after the word "search"
        if "search" in query:
            parts = query.lower().split("search", 1)
            search_keyword = parts[1].strip()

    # If keyword is empty, just open YouTube
        if search_keyword == "":
            webbrowser.open("https://www.youtube.com")
            speak("Opening YouTube.")
        else:
            webbrowser.open(f"https://www.youtube.com/results?search_query={search_keyword}")
            speak(f"Searching {search_keyword} on YouTube.")
    elif "my linkedin" in query:
        linkedin_url = "https://www.linkedin.com/in/shri7ul/"
        webbrowser.open(linkedin_url)
        speak("Opening your LinkedIn profile.")

    elif "my github" in query:
        github_url = "https://github.com/Shri7ul"
        webbrowser.open(github_url)
        speak("Opening your GitHub profile.")
    elif "wikipedia" in query:
        try:
            speak("Searching Wikipedia...")

            q = query.lower()

        # remove unnecessary words
            remove_words = ["wikipedia", "search", "on", "about", "in", "from"]
            for w in remove_words:
                q = q.replace(w, " ")

        # collapse multiple spaces
            topic = " ".join(q.split()).strip()

            if topic == "":
                speak("Please tell me what to search on Wikipedia.")
                continue

            results = wikipedia.summary(topic, sentences=2)
            speak("According to Wikipedia.")
            speak(results)
    
        except:
            speak("Sorry, I couldn't find that on Wikipedia.")
    else:
        response = gemini_response(query)
        speak(response)
        logging.info("User asked for others question")




    


