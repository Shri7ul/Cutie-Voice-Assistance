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
import requests
import pyautogui
import threading
import time
import re
speech_lock = threading.Lock()
import pyperclip

NOTES_FILE = "notes.txt"


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
    with speech_lock:
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.3)  # small delay to avoid voice overlapping with microphone


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

def weather(query):
    CITY = "Dhaka"   # default city
    API_KEY = os.getenv("WEATHER_API_KEY")

    if "in" in query:
        CITY = query.split("in")[1].strip()

    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

    try:
        data = requests.get(url).json()
        if data["cod"] != 200:
                speak("I couldn't find that city.")
        else:
            temp = data["main"]["temp"]
            condition = data["weather"][0]["description"]
            speak(f"The temperature in {CITY} is {temp} degrees with {condition}.")
    except:
        speak("Sorry, I couldn't fetch the weather right now.")

def news():
    
    API = os.getenv("NEWS_API_KEY")
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={API}"

    try:
        data = requests.get(url).json()
        articles = data.get("articles", [])[:5]  # top 5 news

        speak("Here are the headlines.")

        for idx, article in enumerate(articles, 1):
            speak(f"Headline {idx}: {article['title']}")
    except:
        speak("Sorry, I couldn't fetch the news right now.")

def play_music():
    music_dir = r"D:\Inception bd\Project\Cutie-Voice-Assistance\Music"
        
    try:
        songs = os.listdir(music_dir)
            
        if not songs:
            speak("Your music folder is empty.")
        else:
            song = random.choice(songs)
            os.startfile(os.path.join(music_dir, song))
            speak("Playing a random song.")
    except:
        speak("I couldn't access your music folder.")


def take_screenshot():
    try:
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"Screenshot_{time_stamp}.png"
        save_path = os.path.join("Screenshots", file_name)

        # folder তৈরি করে নেবে যদি না থাকে
        os.makedirs("Screenshots", exist_ok=True)

        image = pyautogui.screenshot()
        image.save(save_path)

        speak("Screenshot taken and saved successfully.")
    except:
        speak("Sorry, I could not take the screenshot.")

def extract_google_query(text):
    remove_words = ["search", "on", "google", "for", "about"]
    
    q = text.lower()
    for w in remove_words:
        q = q.replace(w, " ")

    return " ".join(q.split()).strip()

def add_note(text):
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")
    speak("Note added.")

def read_notes():
    if not os.path.exists(NOTES_FILE) or os.path.getsize(NOTES_FILE) == 0:
        speak("You have no notes.")
        return
    with open(NOTES_FILE, "r", encoding="utf-8") as f:
        speak("Here are your notes.")
        for line in f:
            speak(line.strip())

def delete_notes():
    if os.path.exists(NOTES_FILE):
        open(NOTES_FILE, "w").close()
    speak("All notes deleted.")

# def auto_type_mode():
#     speak("What should I type?")
#     time.sleep(0.3)   # IMPORTANT extra buffer
#     text = takeCommand().lower()

#     if text == "" or text == "none":
#         speak("I didn’t catch that. Please try again.")
#         return

#     pyautogui.write(text, interval=0.03)
#     speak("Typing completed.")

def read_clipboard():
    try:
        text = pyperclip.paste()
        if text.strip() == "":
            speak("Your clipboard is empty.")
        else:
            speak("Your clipboard contains:")
            speak(text)
    except:
        speak("Sorry, I couldn't read your clipboard.")

# def extract_reminder_time(query):
#     query = query.lower()

#     pattern = r'(\d+)\s*(second|seconds|minute|minutes|hour|hours)'
#     matches = re.findall(pattern, query)

#     if not matches:
#         return None

#     total_seconds = 0
#     for amount, unit in matches:
#         amount = int(amount)
#         if "second" in unit:
#             total_seconds += amount
#         elif "minute" in unit:
#             total_seconds += amount * 60
#         elif "hour" in unit:
#             total_seconds += amount * 3600

#     return total_seconds
# def reminder_thread(wait_seconds, task):
#     speak(f"Okay boss, I will remind you in {wait_seconds//60} minutes.")
#     time.sleep(wait_seconds)
#     speak(f"Boss, reminder: {task}")

def get_today_schedule():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        service = build('calendar', 'v3', credentials=creds)

        today = datetime.datetime.now().date()
        start = datetime.datetime.combine(today, datetime.time.min).isoformat() + 'Z'
        end = datetime.datetime.combine(today, datetime.time.max).isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary', timeMin=start, timeMax=end,
            singleEvents=True, orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])

        if not events:
            speak("Boss, you have no schedule today.")
            return

        speak(f"Boss, you have {len(events)} events today.")

        for event in events:
            start_time = event['start'].get('dateTime', event['start'].get('date'))
            time_fmt = datetime.datetime.fromisoformat(start_time.replace("Z", "")).strftime("%I:%M %p")
            speak(f"At {time_fmt}: {event['summary']}")
            print(f"At {time_fmt}: {event['summary']}")

    except Exception as e:
        print(e)
        speak("Sorry boss, I couldn't fetch your schedule.")





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
    
    # PLAY MUSIC
    elif "play music" in query or "play song" in query:
        play_music()

    elif "weather" in query:
        weather(query)

    elif "news" in query or "headlines" in query:
        news()

    elif "screenshot" in query or "take a screenshot" in query:
        take_screenshot()

    elif "google" in query or "search on google" in query:
        topic = extract_google_query(query)

        if topic == "":
            speak("Please tell me what to search on Google.")
        else:
            speak(f"Searching Google for {topic}.")
            webbrowser.open(f"https://www.google.com/search?q={topic}")

            # AI summary (optional but powerful)
            summary = gemini_response(f"Explain shortly: {topic}")
            speak(summary)

    # ADD NOTE
    elif "make a note" in query or "write this down" in query:
        speak("What should I write?")
        note_text = takeCommand().lower()
        if note_text:
            add_note(note_text)

    # SHOW NOTES
    elif "show my notes" in query or "show my note" in query:
        read_notes()

    # DELETE NOTES
    elif "delete my notes" in query or "clear notes" in query:
        delete_notes()
    
    elif "clipboard" in query or "what's on my clipboard" in query or "read my clipboard" in query:
        read_clipboard()

    # elif "remind me" in query:
    #     wait_seconds = extract_reminder_time(query)

    #     if not wait_seconds:
    #         speak("Please tell me how long later I should remind you.")
    #         continue

    #     # extract the task after 'to'
    #     task = ""
    #     if "to" in query:
    #         task = query.split("to", 1)[1].strip()
    #     else:
    #         task = "your task"

    #     t = threading.Thread(target=reminder_thread, args=(wait_seconds, task))
    #     t.start()
    elif "today's schedule" in query or "todays schedule" in query or "today schedule" in query:
        get_today_schedule()



    else:
        response = gemini_response(query)
        speak(response)
        logging.info("User asked for others question")




    


