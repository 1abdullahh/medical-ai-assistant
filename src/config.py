from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)
import os


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("KEY LOADED:", OPENAI_API_KEY)
GENDER_OPTIONS = ["Male", "Female", "Transgender" ,"Rather not say"]
DURATION_OPTIONS = ["1 day", "2 day", "3 day", "4 day", "5 day", "6 day", "7 day", "1 week", "2 week", "1 month"]
LANGUAGE_OPTIONS = ["English", "Urdu", "Hindi", "Persian"]
SYMPTOM_OPTIONS = ["Light fever", "Cough", "Body pain","Chest pain", "Fatigue","Nausea", "Shortness of breath"]