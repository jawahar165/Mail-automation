from openai import OpenAI
import json
import os, sys
import email


GOOGLE_API_KEY = os.environ.get("GOOGLE_API_URL", "<APIKEY>")
GOOGLE_API_URL = os.environ.get("GOOGLE_API_URL", "<GEMINI URL>")

client = OpenAI(api_key=GOOGLE_API_KEY, 
                base_url=GOOGLE_API_URL)


def log_exception(module, log_file):
    exe_type, exe_ob, tb = sys.exc_info()
    line_no = tb.tb_lineno
    error_message = f"\nIN {module} LINE NO: {line_no} -->> {exe_ob}"
    with open(log_file, 'a', encoding='utf-8') as fp:
        fp.writelines(error_message)


def classify_email_response(email_data, log_file):
    try:
        """
        Uses OpenAI to classify an email and draft a response.
        """
        prompt = f"""
        You are an intelligent email assistant. Your task is to analyze an incoming email, 
        classify its intent, decide if a reply is needed, and draft a professional response.

        Email Details:
        From: {email_data['original_from']}
        Subject: {email_data['original_subject']}
        Body: {email_data['original_text']}

        Instructions:
        1. Classify the email intent: 'Inquiry', 'Meeting Request', 'Work-Related', 'Urgent Issue', 'Personal', 'Spam/Junk', 'General Info'.
        2. Determine if a reply is needed: 'Yes' or 'No'.
        3. If a reply is needed, draft a concise, professional, and helpful response. If not needed, set the reply_draft to 'N/A'.
        4. Provide the output strictly in a JSON format with keys: 'classification', 'reply_needed', 'reply_draft'.
        """

        response = client.chat.completions.create(
            model="gemini-2.5-flash",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs only JSON objects."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the JSON response
        try:
            ai_response = json.loads(response.choices[0].message.content)
            return ai_response
        except json.JSONDecodeError:
            print("Error decoding JSON from OpenAI.")
            return None
    except Exception as e:
        log_exception("mainserver", log_file)

