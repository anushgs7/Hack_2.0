import smtplib
import os
from email.message import EmailMessage


SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


class EmailSender:

    def __init__(self, user_email):
        self.user_email = user_email

        self.sender_email = os.getenv("SMTP_EMAIL")
        self.sender_password = os.getenv("SMTP_PASSWORD")

    # --------------------------------------------------

    def send_report(self, report_file_path):
        """
        Send the generated session report to the user.
        """

        if not self.sender_email or not self.sender_password:
            raise RuntimeError(
                "SMTP_EMAIL and SMTP_PASSWORD environment variables must be set."
            )

        msg = EmailMessage()

        msg["Subject"] = "Your Attention Session Report"
        msg["From"] = self.sender_email
        msg["To"] = self.user_email

        msg.set_content(
            "Your attention session analysis report is attached.\n\n"
            "This report summarizes attention flow, idle distribution, "
            "application usage, and fragmentation events."
        )

        # --------------------------------------------------
        # Attach Report
        # --------------------------------------------------

        with open(report_file_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(report_file_path)

        msg.add_attachment(
            file_data,
            maintype="text",
            subtype="plain",
            filename=file_name
        )

        # --------------------------------------------------
        # Send Email
        # --------------------------------------------------

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:

            smtp.starttls()

            smtp.login(self.sender_email, self.sender_password)

            smtp.send_message(msg)
