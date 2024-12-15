import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



try:    
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['From'] = "ruprabhu@ucdavis.edu"
    msg['To'] = "ruprabhu@ucdavis.edu"       
    msg['Subject'] = "test subject"
    
    # see the code below to use template as body
    body_text = "Hi this is body text of email"
    body_html = "<p>Hi this is body text of email</p>"
    
    # Create the body of the message (a plain-text and an HTML version).
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(body_text, 'plain')
    part2 = MIMEText(body_html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    print("here")
    # Send the message via local SMTP server.
    
    mail = smtplib.SMTP("smtp.outlook.office365.com", 587, timeout=20)

    # if tls = True                
    mail.starttls()        

    recepient = ["ruprabhu@ucdavis.edu"]
    password = input("password: ")
    mail.login("ruprabhu@ucdavis.edu", password)        
    mail.sendmail("ruprabhu@ucdavis.edu", recepient, msg.as_string())        
    mail.quit()
    
except Exception as e:
    print(e)
    raise e