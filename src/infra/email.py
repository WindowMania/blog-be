import abc
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailContext:
    @abc.abstractmethod
    def send_simple_text_email(self, to: str, title: str, message: str):
        raise NotImplementedError


class SmtpGmail(EmailContext):
    SMTP_SSL_PORT = 465  # SSL connection
    SMTP_SERVER = "smtp.gmail.com"

    def __init__(self, me: str, password: str):
        self.me = me
        self.password = password
        self.context = ssl.create_default_context()

    def send_simple_text_email(self, to: str, title: str, message: str):
        with smtplib.SMTP_SSL(SmtpGmail.SMTP_SERVER, SmtpGmail.SMTP_SSL_PORT, context=self.context) as server:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = title
            msg['From'] = self.me
            msg['To'] = to
            part1 = MIMEText(message)
            msg.attach(part1)
            server.login(self.me, self.password)
            server.sendmail(self.me, to, msg.as_string())


class MockSmtpGmail(SmtpGmail):

    def send_simple_text_email(self, to: str, title: str, message: str):
        pass
