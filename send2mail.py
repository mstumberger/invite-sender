# Import os for working with folders
import os

# Import smtp lib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# Function send mail
def sendMail(server, port, sfrom, password, sto, subject, body, filepath):
    # Create a text/plain message
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sfrom
    msg['To'] = sto

    # The main body is just another attachment
    msg.attach(MIMEText(body))

    # PDF attachment
    if filepath:
        path, filename = os.path.split(filepath)
        fp = open(os.path.join(path, filename), 'rb')
        att = MIMEApplication(fp.read(), _subtype="pdf")
        fp.close()
        att.add_header('Content-Disposition', 'attachment; filename=%s' % filename)
        msg.attach(att)

    # send via Gmail server

    try:
        s = smtplib.SMTP(server, port)
        s.starttls()
        s.login(sfrom, password)
        s.sendmail(sfrom, sto, msg.as_string())
        s.quit()
        return "Successfully sent email to {}".format(sto)
    except Exception as e:
        return "Error: unable to send email. {}".format(e)
