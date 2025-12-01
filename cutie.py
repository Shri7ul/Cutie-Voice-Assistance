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
import fnmatch
speech_lock = threading.Lock()
import pyperclip
import ctypes
from monitorcontrol import get_monitors
from gtts import gTTS
from playsound import playsound





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
        time.sleep(0.3)
def speak_bangla(text):
    filename = f"bn_{random.randint(1,9999)}.mp3"
    tts = gTTS(text=text, lang='bn')
    tts.save(filename)
    playsound(filename)
    os.remove(filename)


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
        prompt = (
            "Your name is Cutie. You act like JARVIS. "
            "Answer the user's question in 1-3 short sentences. "
            "Do NOT start with greetings. "
            "Do NOT say your name. "
            "Answer directly.\n\n"
            f"User: {user_text}\nAnswer:"
        )
        response = model.generate_content(prompt)
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

def summarize_clipboard_to_notes():
    try:
        text = pyperclip.paste()
        if text.strip() == "":
            speak("Your clipboard is empty.")
            return

        # Clean summary prompt
        prompt = (
            "Summarize the following text in 2-4 short, clean sentences. "
            "Do NOT use bullet points, stars, numbering, or bold text. "
            "Just write simple exam-focused sentences:\n\n" + text
        )

        summary = gemini_response(prompt)

        # Remove unwanted formatting that the model might add
        clean = summary.replace("*", "").replace("-", "").replace("•", "")
        clean = clean.replace("\n", " ")
        clean = " ".join(clean.split())   # remove extra spaces

        speak(clean)

        # Save to notes.txt
        with open(NOTES_FILE, "a", encoding="utf-8") as f:
            f.write("\n[Clipboard Summary]\n")
            f.write(clean + "\n")

        speak("Summary added to your notes.")

    except Exception as e:
        print(e)
        speak("Sorry boss, I couldn't summarize your clipboard.")



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

def extract_video_id(url):
    url = url.strip()

    # Case 1: Standard watch?v=
    if "watch?v=" in url:
        return url.split("watch?v=")[1].split("&")[0]

    # Case 2: youtu.be short link
    if "youtu.be/" in url:
        return url.split("youtu.be/")[1].split("?")[0]

    # Case 3: shorts
    if "/shorts/" in url:
        return url.split("/shorts/")[1].split("?")[0]

    # Case 4: mobile link m.youtube.com
        # same as watch?v=
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]

    return None


from youtube_transcript_api import YouTubeTranscriptApi

def get_youtube_transcript(url):
    try:
        video_id = extract_video_id(url)

        if not video_id:
            return None

        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([t["text"] for t in transcript])
        return full_text

    except:
        return None

def summarize_text(text):
    prompt = f"Summarize the following content in simple bullet points:\n{text}"
    summary = gemini_response(prompt)
    return summary

timer_running = False
timer_thread = None

def start_timer(minutes):
    global timer_running
    timer_running = True

    speak(f"Boss, starting a {minutes} minute study timer.")
    seconds = minutes * 60

    while seconds > 0 and timer_running:
        time.sleep(1)
        seconds -= 1

    if timer_running:  # only alert if not stopped manually
        speak("Boss, your study timer is over. Take a short break.")
    timer_running = False


def stop_timer():
    global timer_running
    if timer_running:
        timer_running = False
        speak("Study timer stopped.")
    else:
        speak("Boss, no timer is running right now.")

def search_files(keyword, root_paths=None):
    matches = []

    # If no specific root folder given → scan common locations
    if root_paths is None:
        root_paths = [
            "D:\\",
            os.path.expanduser("~\\Documents"),
            os.path.expanduser("~\\Desktop"),
            os.path.expanduser("~\\Downloads")
        ]

    speak(f"Searching for files related to {keyword}...")

    for root in root_paths:
        for path, dirs, files in os.walk(root):
            for file in files:
                file_lower = file.lower()
                key_lower = keyword.lower()

                # Loose matching logic
                if (key_lower in file_lower) or fnmatch.fnmatch(file_lower, f"*{key_lower}*.pdf") or fnmatch.fnmatch(file_lower, f"*{key_lower}*.docx") or fnmatch.fnmatch(file_lower, f"*{key_lower}*"):
                    matches.append(os.path.join(path, file))

    return matches

study_folders = {
    "computer architecture": r"D:\Versity\253\Computer Architecture\Before Midterm",
    "electronics": r"D:\Versity\253\Electronics",
    "lap report": r"D:\Versity\253\Lab Report",
    "state": r"D:\Versity\252\STATE\MID",
    "toc": r"D:\Versity\252\TOC\MID",
    "dsa lab": r"D:\Versity\252\DSA LAB",
}
def set_brightness(level):
    try:
        level = int(level)

        # limit the brightness 0–100
        if level < 0: level = 0
        if level > 100: level = 100

        monitors = get_monitors()

        if not monitors:
            speak("Boss, I could not detect any external monitor.")
            return

        for m in monitors:
            with m:
                m.set_luminance(level)

        speak(f"Brightness set to {level} percent.")

    except Exception as e:
        print(e)
        speak("Sorry boss, I could not adjust your brightness.")

motivation_quotes = [
    "Boss, মন খারাপ থাকতেই পারে। একটু একটু করে এগোলে সব ঠিক হয়ে যায়।",
    "একটা ছোট কাজ শুরু করে দাও, মনটা নিজের থেকেই ঠিক হয়ে যাবে।",
    "তুমি আগেও কঠিন সময় সামলেছো, এবারও পারবে।",
    "সবাই দুর্বল হয়, কিন্তু হাল না ছাড়াই আসল শক্তি।",
    "একটু বিশ্রাম নাও, পানি খাও, তারপর ধীরে ধীরে আবার শুরু করি।",
]

def start_break_timer(minutes):
    def _run():
        speak(f"Boss, starting a {minutes} minute break. Just relax and breathe.")
        seconds = minutes * 60
        while seconds > 0:
            time.sleep(1)
            seconds -= 1
        speak_bangla("Break sesh boss, jodi paro ekhon abar ektu pora start kore dao.")
    t = threading.Thread(target=_run)
    t.start()

def handle_mood_support(query):
    q = query.lower()

    # basic breathing tip
    breathing_tip =(
    "চলো একটা ছোট শ্বাস-প্রশ্বাসের ব্যায়াম করি। "
    "চার সেকেন্ড শ্বাস নাও, চার সেকেন্ড ধরে রাখো, তারপর ধীরে ধীরে ছেড়ে দাও। "
    "দুই তিনবার করলে মাথা হালকা লাগবে।"
)


    # choose a random quote
    quote = random.choice(motivation_quotes)

    if "stressed" in q or "stress" in q or "pressure" in q:
        speak_bangla("ঠিক আছে Boss, মনে হচ্ছে তুমি একটু চাপের মধ্যে আছো।")
        speak_bangla(breathing_tip)
        speak_bangla(quote)
        start_break_timer(3)   

    elif "sad" in q or "down" in q or "feeling low" in q:
        speak_bangla("Boss, মন খারাপ হওয়া খুবই স্বাভাবিক।")
        speak_bangla(quote)

    elif "motivate me" in q or "give me motivation" in q or "motivation dao" in q:
        speak_bangla("থাক Boss, একটু অনুপ্রেরণা দিচ্ছি।")
        speak_bangla(quote)

    else:
        speak_bangla("Boss, মনে হচ্ছে তুমি ঠিক ভালো নেই। একটু বিশ্রাম নাও, পানি খাও, তারপর ধীরে ধীরে পড়া শুরু করি।")

bangla_jokes = [
    "বস, জানেন কম্পিউটার সবসময় ঠান্ডা থাকে কেন? কারণ তার অনেক ফ্যান আছে।",
    "বস, পরীক্ষার আগে স্টুডেন্ট কম্পিউটারকে কী বলে? প্লিজ হ্যাং হয়ে যেও!",
    "বস, রোবট কেন দুঃখিত ছিল? তার সার্কিটে একটু 'কারেন্ট' সমস্যা ছিল।"
]

english_jokes = [
    "Why did the computer go to the doctor? Because it had a virus.",
    "Why don’t programmers like nature? Too many bugs.",
    "My WiFi isn't working… I guess it's having a connection problem."
]

def tell_joke(query):
    q = query.lower()

    # If the user says 'bangla'
    if "bangla" in q or "bengali" in q:
        joke = random.choice(bangla_jokes)
        speak_bangla(joke)
        return
    
    # If the user says 'english'
    if "english" in q:
        joke = random.choice(english_jokes)
        speak(joke)
        return
    
    # Auto detect minimal
    if any(word in q for word in ["joke", "jokes"]):
        # default English
        joke = random.choice(english_jokes)
        speak(joke)
def introduce_cutie():
    text = (
        "আসসালামু আলাইকুম বস, আমি কিউটি! "
        "আমি আপনার স্টাডি অ্যাসিস্ট্যান্ট এবং পার্সোনাল এআই হেল্পার। "
        "আমি আপনার জন্য অনেক কাজ করতে পারি। যেমন— "
        "গুগল সার্চ করা, উইকিপিডিয়ায় তথ্য বের করা, আপনার নোট লিখে রাখা, "
        "ক্লিপবোর্ড পড়া এবং সারমারি করে নোটসে যোগ করা, "
        "গুগল ক্যালেন্ডার থেকে আজকের শিডিউল জানানো, "
        "স্টাডি টাইমার চালানো, ইউটিউব ভিডিওর সারমারি দেয়া, "
        "পিসির ভলিউম কন্ট্রোল, ব্রাইটনেস কন্ট্রোল, স্ক্রিনশট নেওয়া, "
        "ফোল্ডার ওপেন করা, মিউজিক প্লে করা, এবং আরও অনেক কিছু। "
        "বস, আপনি যা বলবেন আমি সেটাই করে দেবো।"
    )

    speak_bangla(text)














greeting()

while True:
    query = takeCommand().lower()
    print(query)

    # IGNORE empty or very short noise-like input
    if query.strip() == "":
        continue

    trash_words = ["greetings", "hello", "hi", "hey", "thank you", "thanks"]
    if query.strip() in trash_words:
        continue

    if "your name" in query:
        speak("I am Cutie.")
        logging.info("User asked for assistant's name.")

    elif "introduce yourself" in query or "introduce" in query:
        introduce_cutie()

    elif "time now" in query:
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
    
    elif "clipboard read" in query or "what's on my clipboard" in query or "read my clipboard" in query:
        read_clipboard()

    elif "summarize my clipboard" in query or "clipboard summary" in query or "add clipboard summary to notes" in query:
        summarize_clipboard_to_notes()


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

    elif "youtube summary" in query or "summarize youtube" in query or "summarize video" in query:
        speak("Okay boss, reading link from your clipboard.")
        link = pyperclip.paste()

        if "youtube.com" not in link and "youtu.be" not in link:
            speak("Clipboard does not contain a valid YouTube link.")
            continue

        speak("Fetching video transcript...")
        transcript = get_youtube_transcript(link)

        if transcript:
            speak("Generating summary...")
            summary = summarize_text(transcript)
            speak("Here is the summary.")
            speak(summary)
        else:
            speak("Sorry boss, this video has no transcript.")

    elif "start study timer" in query:
        if timer_running:
            speak("Boss, a timer is already running.")
            continue

        t = threading.Thread(target=start_timer, args=(25,))
        t.start()

    elif "start" in query and "minute timer" in query:
        try:
            minutes = int(re.findall(r'\d+', query)[0])
            if timer_running:
                speak("A timer is already running.")
                continue

            t = threading.Thread(target=start_timer, args=(minutes,))
            t.start()
        except:
            speak("Boss, I could not understand the time.")

    elif "stop timer" in query or "cancel timer" in query:
        stop_timer()

    # DICTIONARY MODE
    elif ("define" in query) or ("meaning of" in query) or ("what is" in query) or ("explain" in query):
        try:
            # remove keywords
            keywords = ["define", "meaning of", "what is", "explain"]
            term = query
            for k in keywords:
                term = term.replace(k, "")
            term = term.strip()

            if term == "":
                speak("Boss, please tell me what word you want the meaning of.")
                continue

            prompt = f"Explain the definition and short meaning of '{term}' in one or two simple lines."
            meaning = gemini_response(prompt)
            speak(meaning)

        except:
            speak("Sorry boss, I couldn't explain that.")

    elif "find" in query or "search file" in query:
        speak("Okay boss, what file should I search?")
        keyword = takeCommand().lower()

        if keyword == "":
            speak("I did not catch the file name.")
            continue

        results = search_files(keyword)

        if not results:
            speak("Sorry boss, I didn't find any file with that name.")
        else:
            speak(f"I found {len(results)} files. Opening the first one.")
            os.startfile(results[0])
            print("Matches:")
            for f in results:
                print(f)

    elif "open" in query and "folder" in query:
        found = False

        for key in study_folders:
            if key in query:
                path = study_folders[key]
                if os.path.exists(path):
                    os.startfile(path)
                    speak(f"Opening your {key} folder.")
                else:
                    speak("Boss, that folder path does not exist.")
                found = True
                break

        if not found:
            speak("Boss, I could not match any study folder.")

    # SYSTEM CONTROL COMMANDS
    elif "increase volume" in query:
        for _ in range(5):
            pyautogui.press("volumeup")
        speak("Volume increased.")

    elif "decrease volume" in query:
        for _ in range(5):
            pyautogui.press("volumedown")
        speak("Volume decreased.")

    elif "mute" in query:
        pyautogui.press("volumemute")
        speak("Muted.")

    elif "unmute" in query:
        pyautogui.press("volumemute")
        speak("Unmuted.")

    elif "shutdown" in query:
        speak("Shutting down your computer, boss.")
        os.system("shutdown /s /t 3")

    elif "restart" in query:
        speak("Restarting your computer.")
        os.system("shutdown /r /t 3")

    elif "sleep" in query:
        speak("Putting your PC to sleep.")
        ctypes.windll.PowrProf.SetSuspendState(0, 1, 0)

    elif "lock my pc" in query or "lock computer" in query:
        speak("Locking your computer.")
        ctypes.windll.user32.LockWorkStation()

    elif "open task manager" in query:
        speak("Opening Task Manager.")
        os.system("start taskmgr")

    elif "open settings" in query:
        speak("Opening Windows settings.")
        os.system("start ms-settings:")

    elif "open control panel" in query:
        speak("Opening Control Panel.")
        os.system("control")

    elif "open file explorer" in query:
        speak("Opening File Explorer.")
        os.system("explorer")

    elif "brightness" in query or "light" in query:
        nums = re.findall(r'\d+', query)

        # If user says "increase brightness"
        if "increase" in query:
            try:
                monitors = get_monitors()
                with monitors[0]:
                    current = monitors[0].get_luminance()
                    new_value = min(current + 10, 100)
                    monitors[0].set_luminance(new_value)
                speak("Brightness increased.")
            except:
                speak("I couldn't increase brightness.")

        # If user says "decrease brightness"
        elif "decrease" in query:
            try:
                monitors = get_monitors()
                with monitors[0]:
                    current = monitors[0].get_luminance()
                    new_value = max(current - 10, 0)
                    monitors[0].set_luminance(new_value)
                speak("Brightness decreased.")
            except:
                speak("I couldn't decrease brightness.")

        # If user says "set brightness to 50%"
        elif nums:
            set_brightness(nums[0])

        else:
            speak("Boss, please tell me the brightness level.")

        # MOOD / STRESS ASSISTANT
    elif "i am stressed" in query or "feeling stressed" in query or "stress lagche" in query \
         or "i am sad" in query or "feeling low" in query or "motivate me" in query \
         or "give me motivation" in query or "motivation dao" in query:
        handle_mood_support(query)

    elif "joke" in query or "tell me a joke" in query or "make me laugh" in query:
        tell_joke(query)








    else:
        response = gemini_response(query)
        speak(response)
        logging.info("User asked for others question")




    


