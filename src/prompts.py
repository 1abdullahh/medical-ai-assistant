from langchain_classic.schema import SystemMessage
from langchain_classic.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

message =[
    SystemMessage(content='''You are a Medical assistant, not a doctor. So suggest to consult a doctor. EMERGENCY-level output must tell the user to seek emergency help immediately. It must never present a confirmed diagnosis. The app is clearly labelled an educational AI system, not a doctor. You must respond with ONLY a valid JSON object matching the required schema.Do not include any explanation, preamble, or extra text before or after the JSON. Do not wrap the JSON in ```json code fences or any other markdown formatting.Your entire response must be parseable directly by json.loads().''')
   ]

JSON_SCHEMA_INSTRUCTION = '''{
  "summary": "",
  "possible_conditions": [ { "name": "", "reason": "" } ],
  "urgency_level": "",
  "recommended_next_steps": [],
  "questions_for_doctor": [],
  "warning_signs": []
}
urgency_level must be exactly one of: LOW, MEDIUM, HIGH, EMERGENCY.
possible_conditions must be a list of objects, each with a "name" and "reason" field, for educational purposes only.
summary must be a short 1-2 sentence recap of the patient's reported symptoms.'''

SYSTEM_PROMPT = '''You are a Medical assistant, not a doctor. So suggest to consult a doctor. EMERGENCY-level output must tell the user to seek emergency help immediately. It must never present a confirmed diagnosis. The app is clearly labelled an educational AI system, not a doctor. You must respond with ONLY a valid JSON object matching the required schema.Do not include any explanation, preamble, or extra text before or after the JSON. Do not wrap the JSON in ```json code fences or any other markdown formatting.Your entire response must be parseable directly by json.loads().'''



template = '''Analyze the following patient information: {age}, {gender}, {symptoms}, {duration}, {severity}, {existing_conditions}, {medications}, {notes} in {language}'''
symptom_prompt_template = PromptTemplate.from_template(template=template)
prompt = symptom_prompt_template.format(age="25", gender="Male", symptoms="fever", duration="2 day", severity="5", existing_conditions="none", medications="none", notes="none", language="English")


from langchain_classic.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, AIMessagePromptTemplate
from langchain_core.messages import SystemMessage
chat_template = ChatPromptTemplate.from_messages([
    SystemMessage(content=SYSTEM_PROMPT + JSON_SCHEMA_INSTRUCTION),
    HumanMessagePromptTemplate.from_template(template)
])

message = chat_template.format_prompt(age="25", gender="Male", symptoms="fever", duration="1 day", severity="5", existing_conditions="none", medications="none", notes="none", language="English")
