
import email
from email.header import decode_header
import uuid
import json
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


def load_pending(monitor_json_file):
    try: 
        with open(monitor_json_file, "r") as f: 
            return json.load(f) 
    except FileNotFoundError: 
        return {} 
    
def save_pending(monitor_json_file, data): 
    with open(monitor_json_file, "w") as f: 
        json.dump(data, f, indent=2) 



def fetch_email(mail, monitor_uuid, since_date_str, log_file, monitor_json_file):
    try:
        email_messages = []
        status, messages = mail.search(None, 'UNSEEN', 'SINCE', since_date_str)

        if status == 'OK' and messages[0]:
            uids = messages[0].split()
            for uid in uids:
                if uid in monitor_uuid:
                    continue
                monitor_uuid.append(uid)

                # Fetch and process the message
                status, msg_data = mail.fetch(uid, '(INTERNALDATE RFC822)')
                if status == 'OK':
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            # Parse the email message from bytes
                            msg = email.message_from_bytes(response_part[1])
                            
                            # Extract headers
                            subject, encoding = decode_header(msg["Subject"])[0]
                            from_address = msg["From"]
                            
                            if "APPROVAL REQUIRED" in subject:
                                mail.store(uid, '-FLAGS', '\\Seen')
                                continue
                            mail.store(uid, '+FLAGS', '\\Seen')
                            write_logs(f"new messsage found from {from_address} - {subject}", log_file)
                            # Extract plain text body
                            body = ""
                            if msg.is_multipart():
                                for part in msg.walk():
                                    if part.get_content_type() == "text/plain":
                                        body = part.get_payload(decode=True).decode('utf-8')
                                        break
                            else:
                                body = msg.get_payload(decode=True).decode('utf-8')
                            
                            pending_id = str(uuid.uuid4()) 
                            pending = { "id": pending_id, "original_from": from_address, "original_subject": subject, "original_text": body, "reply_text": "", "status": "waiting" } 
                            email_messages.append(pending)

                            all_pending = load_pending(monitor_json_file) 
                            all_pending[pending_id] = pending 
                            save_pending(monitor_json_file,all_pending) # Send approval request 

    except Exception as e:
        log_exception("imaplib.IMAP4.error", log_file)
        
    return email_messages