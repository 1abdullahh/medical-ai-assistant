from langchain_openai import ChatOpenAI
from langchain_classic.chains import LLMChain
from src.config import OPENAI_API_KEY
from src.prompts import symptom_prompt_template, chat_template


def build_llm(api_key, model="gpt-5-nano", temperature=0):
    """
    Builds a ChatOpenAI instance using the given API key.
    Used by app.py so each request can use the key the user typed in
    the sidebar, instead of only relying on the .env file.
    """
    return ChatOpenAI(model=model, api_key=api_key, temperature=temperature)


# Default instances built from the .env key - ONLY if a key is actually
# present. If .env has no key, these stay None instead of crashing the
# app at import time. app.py always builds its own llm via build_llm()
# using whichever key (typed or .env) is active, so this is just a
# fallback kept for backward compatibility with the rest of the assignment.
if OPENAI_API_KEY:
    llm = ChatOpenAI(model="gpt-5-nano", api_key=OPENAI_API_KEY, temperature=0)
    medical_chain = LLMChain(llm=llm, prompt=chat_template)
else:
    llm = None
    medical_chain = None