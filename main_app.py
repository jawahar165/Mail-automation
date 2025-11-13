import imaplib
import time
from email.parser import BytesHeaderParser
from email.policy import default
import datetime
import email
from email.header import decode_header
import sys
import json
from models.mail_classification import classify_email_response
from utils.request_mail_approval import send_approval_request
from utils.fetch_unseen_mail import fetch_email
import uuid, os
from utils.check_approval import check_monitor_approvals

PENDING_FILE = os.path.join("data", "PENDING__log_file.json")

def write_logs(data, log_file):
    with open(log_file, "a", encoding="utf-8") as ad:
        ad.writelines(f"\n{data}")

def log_exception(module, log_file):
    exe_type, exe_ob, tb = sys.exc_info()
    line_no = tb.tb_lineno
    error_message = f"\nIN {module} LINE NO: {line_no} -->> {exe_ob}"
    with open(log_file, 'a', encoding='utf-8') as fp:
        fp.writelines(error_message)


def load_pending(monitor_json_file):
    try: 
        with open(monitor_json_file, "r") as f: 
            return json.load(f) 
    except FileNotFoundError: 
        return {} 

def save_pending(monitor_json_file, data): 
    with open(monitor_json_file, "w") as f: 
        json.dump(data, f, indent=2) 


def connect_to_imap():
    """Establishes a secure connection to the IMAP server."""
    try:
        # Use IMAP4_SSL for a secure connection over SSL/TLS
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        print("mail server connected")
        # Log in to the server
        mail.login(USERNAME, PASSWORD)
        print(f"Logged in as {USERNAME}")

        return mail
    
    except imaplib.IMAP4.error as e:
        log_exception("connect_to_imap", log_file)
        return None
    except Exception as e:
        log_exception("connect_to_imap", log_file)
        return None
    
def close_connection(mail_server):
    """Closes the mailbox and logs out from the server."""
    if mail_server:
        mail_server.close()  # Close the selected mailbox
        mail_server.logout() # Log out and terminate the connection
        print("Connection closed")


def monitor_new_emails_only(USER_MAIL,PASSWORD, APPROVER_EMAIL, SMTP_SERVER, mail, since_date_str, log_file,monitor_json_file):
    # write_logs(f"new messsage found from {from_address}")

    mail.select("INBOX", readonly=False)
    monitor_uuid = []
    email_messages = []

    try:
        while True:
            # Check for messages using the UID search criteria
            # Search for messages with UID greater than or equal to our baseline
            unseen_mails = fetch_email(mail, monitor_uuid, since_date_str, log_file, monitor_json_file)
            if unseen_mails:
                for mail_data in unseen_mails:
                    pending_id = mail_data["id"]
                    from_ = mail_data["original_from"]
                    subject = mail_data["original_subject"]

                    clasify_response = classify_email_response(mail_data, log_file)
                    if clasify_response and clasify_response['reply_needed'].lower() == 'yes':
                        write_logs(f"classified {clasify_response}", log_file)
                        mail_data["reply_text"] = clasify_response['reply_draft']
                        
                        all_pending_id = load_pending(monitor_json_file)
                        all_pending_id[pending_id] = mail_data 
                        save_pending(monitor_json_file,all_pending_id)

                        send_approval_request(USER_MAIL,PASSWORD, SMTP_SERVER,APPROVER_EMAIL, pending_id, from_, subject, mail_data["reply_text"], log_file) 
            check_monitor_approvals(USER_MAIL,SMTP_SERVER, PASSWORD,  mail, APPROVER_EMAIL, log_file, monitor_json_file )

            # Keep the connection alive
            mail.noop()
            time.sleep(1) # Adjust interval as needed

    except KeyboardInterrupt:
        log_exception("monitor_new_emails_only", log_file)
    finally:
        write_logs("MAIL LOGOUT", log_file)
        mail.logout()


if __name__ =="__main__":
    
    IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.<server>.com")
    IMAP_PORT = int(os.environ.get("IMAP_PORT", "993"))
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.<server>.com")
    USERNAME = os.environ.get("EMAIL_USERNAME", "<user@domain.com>")
    PASSWORD = os.environ.get("EMAIL_PASSWORD", "<APP Password>")
    APPROVER_EMAIL = os.environ.get("APPROVER_EMAIL", "<approver@domain.com>")
    PENDING_FILE = os.environ.get("PENDING_FILE", os.path.join("data", "PENDING__log_file.json"))
    LOG_FILE = os.environ.get("LOG_FILE", "log.txt")

    cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=1)
    since_date_str = cutoff_time.strftime("%d-%b-%Y")

    mail_server = connect_to_imap()
    monitor_new_emails_only(USERNAME,PASSWORD, APPROVER_EMAIL, SMTP_SERVER, mail_server, since_date_str, LOG_FILE, PENDING_FILE)

