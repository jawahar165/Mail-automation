import smtplib 
from email.mime.text import MIMEText
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


def send_approval_request(EMAIL_ACCOUNT, PASSWORD,SMTP_SERVER,  to_email, pending_id, original_from, subject, reply_msg, log_file): 
    try:
        msg_body = f""" Approval Request ID: {pending_id} Original From: {original_from} Subject: {subject} --- Draft Reply --- {reply_msg} Please reply to this email with: YES - to approve sending the reply NO - to deny it """ 
        
        msg = MIMEText(msg_body) 
        msg["Subject"] = f"[APPROVAL REQUIRED] Mail ID {pending_id}: {subject}" 
        msg["From"] = EMAIL_ACCOUNT 
        msg["To"] = to_email 
        
        with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server: 
            server.login(EMAIL_ACCOUNT, PASSWORD) 
            server.send_message(msg) 
            write_logs(f"Approval request sent to {to_email}", log_file) 
    
    except Exception as e:
        log_exception("send_approval_request", log_file)