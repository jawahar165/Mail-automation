import json
import re
import smtplib 
import email
import json
from email.mime.text import MIMEText
from time import sleep 
import sys


def write_logs(data, log_file):
    with open(log_file, "a", encoding="utf-8") as ad:
        ad.writelines(f"\n{data}")

def log_exception(module, log_file):
    exe_type, exe_ob, tb = sys.exc_info()
    line_no = tb.tb_lineno
    error_message = f"\nIN {module} LINE NO: {line_no} -->> {exe_ob}"
    with open(log_file, 'a', encoding='utf-8') as fp:
        fp.writelines(error_message)


def load_pending(PENDING_FILE):
    try: 
        with open(PENDING_FILE, "r") as f: 
            return json.load(f) 
    except FileNotFoundError: 
        return {} 
    
def save_pending(PENDING_FILE, data): 
    with open(PENDING_FILE, "w") as f: 
        json.dump(data, f, indent=2) 



def send_reply(EMAIL_ACCOUNT, SMTP_SERVER, PASSWORD, to_email, original_subject, reply_msg, log_file): 
    try:
        msg = MIMEText(reply_msg) 
        msg["Subject"] = f"Re: {original_subject}" 
        msg["From"] = EMAIL_ACCOUNT 
        msg["To"] = to_email 
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server: 
            server.login(EMAIL_ACCOUNT, PASSWORD) 
            server.send_message(msg) 
            write_logs(f" Reply sent successfully! {to_email}", log_file) 
    except Exception as e:
        log_exception("send_reply", log_file)



def extract_id_from_subject(subject): 

    match = re.search(r"Mail ID (.*?):", subject) 
    return match.group(1) if match else None 

def handle_approval(EMAIL_ACCOUNT, SMTP_SERVER, PASSWORD,pending_id, response, log_file, monitor_json_file): 
    try:
        all_pending = load_pending(monitor_json_file) 
        if pending_id not in all_pending: 
            write_logs(f" Pending ID {pending_id} not found.", log_file) 
            return 

        pending = all_pending[pending_id] 
        if "yes" in response.lower(): 
            write_logs(f"Approved: Sending reply for {pending['original_from']}", log_file) 
            send_reply(EMAIL_ACCOUNT, SMTP_SERVER, PASSWORD, 
                    pending["original_from"], 
                    pending["original_subject"],
                    pending["reply_text"],
                    log_file)
            pending["status"] = "approved" 
            save_pending(monitor_json_file, all_pending) 

        else: 
            write_logs(f"Denied reply for {pending['original_from']}", log_file) 
            pending["status"] = "denied" 
            save_pending(all_pending) 

    except Exception as e:
        log_exception("handle_approval", log_file)


def get_mail_body(msg): 
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8')

    else:
        body = msg.get_payload(decode=True).decode('utf-8')
    
    return body


def check_monitor_approvals(EMAIL_ACCOUNT, SMTP_SERVER, PASSWORD, mail, APPROVER_EMAIL,log_file ,monitor_json_file): 
    try:
        _, search_data = mail.search(None, '(UNSEEN SUBJECT "[APPROVAL REQUIRED]")') 
        for num in search_data[0].split(): 
            _, msg_data = mail.fetch(num, '(RFC822)') 
            raw_email = msg_data[0][1] 
            msg = email.message_from_bytes(raw_email) 
            subject = msg["Subject"] 
            from_ = msg["From"] 

            if APPROVER_EMAIL.lower() in from_.lower(): 
                body = get_mail_body(msg).strip().upper() 
                print(f"Approval mail from {from_}: {subject}") 
                if "YES" in body or "NO" in body: 
                    pending_id = extract_id_from_subject(subject) 

                    handle_approval(EMAIL_ACCOUNT, SMTP_SERVER, PASSWORD,pending_id, body, log_file, monitor_json_file) 
    except Exception as e:
        log_exception("check_monitor_approvals", log_file)

