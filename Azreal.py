import streamlit as st
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
import sys

import pandas as pd

data = {"Col 1":[1,2,3,4],"Col 2":[5,6,7,8]}
df = pd.DataFrame(data)

if st.button("Send Email"):
  password = st.secrets["password"]
  Output_msg = df
  msg = MIMEMultipart()
  msg['Subject'] = "Azreal Notification"
  msg['From'] = 'dhruv.suresh2@gmail.com'
  html = """\
  <html>
    <head></head>
    <body>
      {0}
    </body>
  </html>
  """.format(Output_msg.to_html())
  part1 = MIMEText(html, 'html')
  msg.attach(part1)
  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.starttls()
  server.login('dhruv.suresh2@gmail.com', password)
  server.sendmail(msg['From'], 'f20180884g@alumni.bits-pilani.ac.in' , msg.as_string())
  server.close()
