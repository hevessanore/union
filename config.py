import os

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

SENDER_EMAIL = os.getenv("SHOP_EMAIL")
SENDER_PASSWORD = os.getenv("SHOP_APP_PASSWORD")
RECEIVER_EMAIL = "1111.union@mail.ru"