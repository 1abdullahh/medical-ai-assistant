# MediGuide AI

An educational, safety-first Streamlit application built with LangChain that turns
patient-reported symptoms into structured, general guidance — a summary, possible
conditions (for education only), an urgency level, and questions to raise with a
doctor.

> ⚠️ **This is an educational prototype, not a medical device.** It is not a
> licensed doctor and never provides a confirmed diagnosis. Always consult a
> qualified healthcare professional. If this is an emergency, contact local
> emergency services immediately.

---

## Project structure

```
medical_ai_assistant/
├── app.py                 # Streamlit UI - run this
├── requirements.txt
├── .env.example
├── README.md
└── src/
    ├── __init__.py
    ├── config.py           # settings + form options
    ├── prompts.py           # PromptTemplate + ChatPromptTemplate + JSON schema
    ├── chains.py            # ChatOpenAI + LLMChain
    ├── cache_manager.py     # in-memory + SQLite caching
    └── utils.py             # safe JSON parsing + helpers
```

## Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd medical_ai_assistant
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate        # macOS / Linux
   venv\Scripts\activate           # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your API key**
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and paste your OpenAI key:
   ```
   OPENAI_API_KEY=sk-...
   ```
   Never commit `.env` to version control — it's already listed in `.gitignore`.

5. **Run the app**
   ```bash
   streamlit run app.py
   ```
   The app will open at `http://localhost:8501`.

## How it works

1. The sidebar lets you configure the model, choose a cache type, and pick a
   response language, alongside a persistent safety disclaimer.
2. The form collects age, gender, symptoms, duration, severity, existing
   conditions, medications, and notes.
3. On submit, the inputs are formatted into a `ChatPromptTemplate` (system
   safety rules + JSON schema instructions, plus the patient's data) and sent
   to the model through `llm.stream()`.
4. The narrative streams live into the UI via `st.write_stream()`.
5. The full response is parsed as JSON (safely — invalid JSON never crashes
   the app) and rendered as a structured results dashboard: urgency level,
   possible conditions, next steps, doctor questions, and warning signs.

## Caching: InMemoryCache vs SQLiteCache

This project demonstrates both caching strategies from `src/cache_manager.py`.
Caching means that if the exact same request is submitted twice, LangChain
returns the cached answer instantly instead of calling the OpenAI API again —
saving both time and cost.

| | InMemoryCache | SQLiteCache |
|---|---|---|
| **Stored in** | RAM (memory) | A `.db` file on disk |
| **Speed** | Fastest | Fast, slightly slower than in-memory |
| **Survives app restart?** | No — cleared every time the app restarts | Yes — persists across restarts |
| **Best for** | A single working session | Reusing cached results across multiple sessions/days |

You can switch between them from the sidebar. To see the effect, submit the
same form twice with caching enabled — the second run should noticeably
finish faster than the first.

## Testing scenarios

| # | Input | Expected behaviour |
|---|---|---|
| 1 | Age 25, runny nose + sore throat, 1–3 days, severity 2 | Urgency **LOW**; calm monitoring advice |
| 2 | Age 40, fever + cough, 4–7 days, severity 6 | Urgency **MEDIUM/HIGH**; advises seeing a professional |
| 3 | Severe chest pain + shortness of breath | Urgency **HIGH/EMERGENCY**; urges immediate help |
| 4 | Submit the same form twice (cache on) | Second run is faster; identical result |
| 5 | Empty symptoms | App warns the user and does not call the API |
| 6 | Language = Urdu | Guidance text returns in Urdu |

## Tech stack

- **Language:** Python 3.10+
- **LLM framework:** LangChain (`langchain`, `langchain-openai`, `langchain-community`)
- **Model provider:** OpenAI
- **UI:** Streamlit
- **Secrets:** python-dotenv (`.env`)

## Issues encountered during development

While building this project, several bugs and misconfigurations came up.
Documenting them here as a record of the debugging process.

### `src/config.py`
- `load_dotenv()` was called but the API key was never actually read into a
  variable — fixed by adding `OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")`.
- A typo in `SYMPTOM_OPTIONS` (`"Light fewer"`) was corrected to `"Light fever"`.

### `src/prompts.py`
- The initial `SystemMessage` content was missing two required safety rules:
  never presenting a confirmed diagnosis, and instructing the model to return
  **only** valid JSON (no explanation, no markdown fences).
- `JSON_SCHEMA_INSTRUCTION` was accidentally defined twice with the same
  variable name — the second definition silently overwrote the first,
  meaning the actual JSON schema was never sent to the model. Fixed by
  merging both into a single string.
- A schema-explanation paragraph was written as a standalone string not
  assigned to any variable — meaning it was never used anywhere. Fixed by
  merging it into `JSON_SCHEMA_INSTRUCTION`.
- The prompt template initially used generic placeholder content (a
  "write about a virus" demo) instead of the patient fields required by
  this project — replaced with `{age}`, `{gender}`, `{symptoms}`, etc.
- `PromptTemplate.format()` was called on the **class** instead of on the
  template **instance**, and later calls were missing several required
  field values, causing `KeyError`/syntax issues. Fixed by calling
  `.format()` on `symptom_prompt_template` with all 9 fields supplied.
- `HumanMessagePromptTemplate` was initially filled with the JSON schema
  text instead of the patient-data template — corrected to use the patient
  template instead.

### `src/chains.py`
- `api_key` was initially passed as the literal string `"OPENAI_API_KEY"`
  instead of the imported variable — fixed by removing the quotes so the
  actual key variable is passed.
- A duplicate, empty `ChatOpenAI()` call and a stray `PromptTemplate()`
  call (with no template) were left over from earlier edits and removed.
- Redundant `load_dotenv()` / `os.getenv()` calls were removed since
  `src/config.py` already handles loading the key.

### `.env` file location
- The app failed with `openai.OpenAIError: Missing credentials` even though
  a key was set. Root cause: the `.env` file had been created inside `src/`
  instead of the project root, so `find_dotenv()` couldn't locate it from
  where `streamlit run app.py` was executed. Fixed by moving `.env` to the
  project root.
- A separate false alarm came from testing with the wrong Python
  interpreter (an unrelated project's virtual environment), which made it
  look like the key still wasn't loading. Running from the project's own
  `venv` resolved this.

### Security note
During debugging, the real OpenAI API key was pasted into a terminal
output and shared while troubleshooting. **Any key that gets shared this
way should be treated as compromised** — it was regenerated from the
OpenAI dashboard immediately after this was noticed.

## Disclaimer

This project is for educational purposes only. It is not a medical device
and must never be used for real diagnosis or treatment.
