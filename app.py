import time
import streamlit as st

from src.config import GENDER_OPTIONS, DURATION_OPTIONS, LANGUAGE_OPTIONS, SYMPTOM_OPTIONS, OPENAI_API_KEY
from src.prompts import chat_template
from src.chains import build_llm
from src.utils import safe_parse_json, get_urgency_color
from src.cache_manager import enable_in_memory_cache, enable_sqlite_cache, disable_cache

st.set_page_config(page_title="MediGuide AI", page_icon="🩺", layout="wide")

# ============================== SIDEBAR ==============================
with st.sidebar:
    st.title("🩺 MediGuide AI")
    st.caption("Educational AI-powered symptom guidance")

    st.warning(
        "**Not a medical device.** This is an educational prototype only. "
        "It is not a licensed doctor and must never replace professional "
        "medical advice, diagnosis, or emergency care."
    )

    st.subheader("Model configuration")
    st.text("Model: gpt-5-nano")

    st.subheader("OpenAI API key")
    user_api_key = st.text_input(
        "Enter your OpenAI API key",
        type="password",
        placeholder="sk-...",
        help="Your key is only used for this session and is never saved or sent anywhere else.",
    )

    # Prefer the key typed here; fall back to the one in .env if present.
    effective_api_key = user_api_key.strip() or OPENAI_API_KEY

    if not effective_api_key:
        st.error("Please enter your API key above to use MediGuide AI.")
    else:
        st.success("API key detected. You're ready to go.")

    st.subheader("Caching")
    cache_choice = st.radio("Cache type", ["No cache", "In-memory", "SQLite"], index=0)
    if cache_choice == "In-memory":
        enable_in_memory_cache()
    elif cache_choice == "SQLite":
        enable_sqlite_cache()
    else:
        disable_cache()

    st.subheader("Answer language")
    language = st.selectbox("Language", LANGUAGE_OPTIONS)

    st.divider()
    st.caption("If this is an emergency, contact local emergency services immediately.")


# ============================== MAIN AREA ==============================
st.title("AI-Powered Medical Symptom Assessment")
st.info(
    "Fill in your details below. MediGuide AI will summarize your symptoms, "
    "suggest an urgency level, and outline next steps to discuss with a professional. "
    "**This tool never provides a confirmed diagnosis.**"
)

if not effective_api_key:
    st.warning("⚠️ Enter your API key in the sidebar first to use MediGuide AI.")
    st.stop()

with st.form("assessment_form"):
    col1, col2 = st.columns(2)
    with col1:
        age = st.text_input("Age", placeholder="e.g. 25")
    with col2:
        gender = st.selectbox("Gender", GENDER_OPTIONS)

    symptoms_selected = st.multiselect("Symptoms", SYMPTOM_OPTIONS)
    symptoms_free_text = st.text_area("Describe your symptoms in your own words (optional)")

    col3, col4 = st.columns(2)
    with col3:
        duration = st.selectbox("Duration of symptoms", DURATION_OPTIONS)
    with col4:
        severity = st.slider("Severity (1 = mild, 10 = severe)", 1, 10, 4)

    existing_conditions = st.text_area(
        "Existing medical conditions", placeholder="e.g. asthma, diabetes — or 'none'"
    )
    medications = st.text_area(
        "Current medications", placeholder="e.g. paracetamol — or 'none'"
    )
    notes = st.text_area("Additional notes")

    submitted = st.form_submit_button("Get guidance")


# ============================== HANDLE SUBMISSION ==============================
if submitted:
    combined_symptoms = symptoms_selected + ([symptoms_free_text] if symptoms_free_text.strip() else [])
    all_symptoms = ", ".join(combined_symptoms)

    if not all_symptoms.strip():
        st.warning("Please select or describe at least one symptom before submitting.")
        st.stop()

    inputs = {
        "age": age or "unknown",
        "gender": gender,
        "symptoms": all_symptoms,
        "duration": duration,
        "severity": str(severity),
        "existing_conditions": existing_conditions or "none",
        "medications": medications or "none",
        "notes": notes or "none",
        "language": language,
    }

    # Build the LLM fresh with whichever key is active for this session
    # (typed key takes priority over the .env key).
    llm = build_llm(effective_api_key)

    st.divider()
    st.subheader("Results")

    tab1, tab2 = st.tabs(["Narrative", "Structured Guidance"])

    # ---------------- Tab 1: streamed narrative ----------------
    with tab1:
        st.caption("Live AI narrative")
        start_time = time.time()

        def stream_generator():
            messages = chat_template.format_messages(**inputs)
            try:
                for chunk in llm.stream(messages):
                    if chunk.content:
                        yield chunk.content
            except Exception as e:
                yield f"\n\n⚠️ Could not reach OpenAI. Please check that your API key is valid. ({e})"

        full_response = st.write_stream(stream_generator)
        elapsed = time.time() - start_time
        st.caption(f"Generated in {elapsed:.1f}s")

    # ---------------- Tab 2: structured JSON dashboard ----------------
    with tab2:
        data, error = safe_parse_json(full_response)

        if error:
            st.error("The AI response could not be parsed as valid JSON. Showing raw output for debugging.")
            with st.expander("Raw model output"):
                st.code(full_response)
        else:
            urgency = data.get("urgency_level", "UNKNOWN").upper()

            colA, colB = st.columns([1, 3])
            with colA:
                st.metric("Urgency level", urgency)
            with colB:
                if urgency == "EMERGENCY":
                    st.error("🚨 EMERGENCY — seek immediate emergency medical help.")
                elif urgency == "HIGH":
                    st.error("⚠️ HIGH urgency — see a healthcare professional promptly.")
                elif urgency == "MEDIUM":
                    st.warning("🟠 MEDIUM urgency — consider seeing a doctor if symptoms persist.")
                else:
                    st.success("🟢 LOW urgency — monitor symptoms and rest.")

            st.markdown("#### Patient summary")
            st.write(data.get("summary", "—"))

            st.markdown("#### Possible conditions (for education only)")
            for cond in data.get("possible_conditions", []):
                with st.expander(cond.get("name", "Condition")):
                    st.write(cond.get("reason", ""))

            col5, col6 = st.columns(2)
            with col5:
                st.markdown("#### Recommended next steps")
                for step in data.get("recommended_next_steps", []):
                    st.write(f"- {step}")

                st.markdown("#### Questions for your doctor")
                for q in data.get("questions_for_doctor", []):
                    st.write(f"- {q}")

            with col6:
                st.markdown("#### ⚠️ Warning signs")
                st.warning("Seek immediate care if any of these appear:")
                for w in data.get("warning_signs", []):
                    st.write(f"- {w}")

            st.divider()
            st.warning(
                "Reminder: this guidance is educational only and is not a diagnosis. "
                "Always consult a licensed healthcare professional."
            )