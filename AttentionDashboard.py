import sys
import csv
import hashlib
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QMessageBox,
    QTextEdit
)

from Attention_Engine.UI_Controller import UI_Controller


USERS_FILE = Path("users.csv")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def ensure_user_file():
    if not USERS_FILE.exists():
        with open(USERS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["email", "password"])


def register_user(email, password):

    with open(USERS_FILE, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["email"] == email:
                return False

    with open(USERS_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([email, hash_password(password)])

    return True


def authenticate_user(email, password):

    with open(USERS_FILE, "r") as f:
        reader = csv.DictReader(f)

        for row in reader:
            if row["email"] == email and row["password"] == hash_password(password):
                return True

    return False


class AttentionDashboard(QWidget):

    def __init__(self):

        super().__init__()

        ensure_user_file()

        self.controller = UI_Controller()

        self.user_email = None

        self.init_ui()

    # --------------------------------------------------

    def init_ui(self):

        self.setWindowTitle("Attention Mapping Dashboard")

        layout = QVBoxLayout()

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

        login_button = QPushButton("Login")
        signup_button = QPushButton("Sign Up")

        login_button.clicked.connect(self.login)
        signup_button.clicked.connect(self.signup)

        self.start_button = QPushButton("Start Session")
        self.stop_button = QPushButton("Stop Session")

        self.start_button.clicked.connect(self.start_session)
        self.stop_button.clicked.connect(self.stop_session)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        layout.addWidget(QLabel("Attention Mapping Tool"))

        layout.addWidget(self.email_input)
        layout.addWidget(self.password_input)

        layout.addWidget(login_button)
        layout.addWidget(signup_button)

        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)

        layout.addWidget(QLabel("Session Data"))
        layout.addWidget(self.output)

        self.setLayout(layout)

    # --------------------------------------------------

    def login(self):

        email = self.email_input.text()
        password = self.password_input.text()

        if authenticate_user(email, password):

            self.user_email = email

            QMessageBox.information(self, "Login", "Login successful")

        else:

            QMessageBox.warning(self, "Login", "Invalid credentials")

    # --------------------------------------------------

    def signup(self):

        email = self.email_input.text()
        password = self.password_input.text()

        if register_user(email, password):

            QMessageBox.information(self, "Signup", "Account created")

        else:

            QMessageBox.warning(self, "Signup", "User already exists")

    # --------------------------------------------------

    def start_session(self):

        if not self.user_email:

            QMessageBox.warning(self, "Error", "Please login first")
            return

        self.controller.start_session(self.user_email)

        QMessageBox.information(self, "Session", "Tracking started")

    # --------------------------------------------------

    def stop_session(self):

        self.controller.stop_session()

        QMessageBox.information(self, "Session", "Tracking stopped")

        self.display_session_data()

    # --------------------------------------------------

    def display_session_data(self):

        app_data = self.controller.get_app_sessions()
        afk_data = self.controller.get_idle_sessions()
        attention_data = self.controller.get_attention_timeline()

        text = "Application Sessions:\n"

        for row in app_data:
            text += str(row) + "\n"

        text += "\nAFK Sessions:\n"

        for row in afk_data:
            text += str(row) + "\n"

        text += "\nAttention Timeline:\n"

        for row in attention_data:
            text += str(row) + "\n"

        self.output.setText(text)


def main():

    app = QApplication(sys.argv)

    window = AttentionDashboard()

    window.resize(600, 600)

    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
