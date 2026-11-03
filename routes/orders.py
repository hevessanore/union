# routes/orders.py
from flask import Blueprint, render_template, request, redirect, url_for
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

from config import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL

orders_bp = Blueprint('orders', __name__)

def send_email(message_text):
    # Тело письма — UTF‑8, кириллица тут разрешена
    msg = MIMEText(message_text, 'plain', 'utf-8')

    # Только латиница в заголовках — это обязательно для Gmail
    sender_name = "Union Site"
    msg['From'] = formataddr((sender_name, SENDER_EMAIL))
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = "New order from Union Site"

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        print("📩 Письмо успешно отправлено на почту.")
    except Exception as e:
        # Одна понятная ошибка — сразу видно, что не так
        print(f"❌ Ошибка отправки письма: {e}")

@orders_bp.route('/order', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        name = request.form.get('name', '')
        phone = request.form.get('phone', '')
        email = request.form.get('email', '')
        product_log = request.form.get('product_log', '')

        body = f"""Заявка с сайта ООО «Юнион»

Товар (лог): {product_log}
Имя: {name}
Телефон: {phone}
E-mail: {email}

Пожалуйста, свяжитесь с клиентом для уточнения заказа.
"""
        send_email(body)
        return redirect(url_for('orders.order_success'))

    product_log = request.args.get('log', '')
    return render_template('order.html', product_log=product_log)

@orders_bp.route('/order-success')
def order_success():
    return render_template('order_success.html')