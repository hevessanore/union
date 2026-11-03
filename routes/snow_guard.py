
# routes/snow_guard.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from routes.orders import send_email  # <-- Импорт функции отправки почты (я добавила это за тебя)

snow_guard_bp = Blueprint('snow_guard', __name__)

@snow_guard_bp.route('')  # итоговый путь: /snow_guard
def index():
    page_data = {"title": "Снегозадержатели"}
    return render_template('snow_guard.html', data=page_data)

@snow_guard_bp.route('/add-to-cart', methods=['POST'])  # итоговый путь: /snow_guard/add-to-cart
def add_to_cart():
    print("✅ МАРШРУТ add-to-cart СРАБОТАЛ! Получили данные.")
    
    quantity_str = request.form.get('quantity', '1')
    try:
        quantity = int(quantity_str)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    product_name = request.form.get('name', 'Товар без названия')

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        "name": product_name,
        "quantity": quantity
    })
    session.modified = True

    flash(f'«{product_name}» добавлен в корзину. Менеджер перезвонит для уточнения деталей.', 'success')
    
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('snow_guard.index'))

@snow_guard_bp.route('/remove-item', methods=['POST'])
def remove_item():
    index_str = request.form.get('index')
    if not index_str:
        flash('Не удалось определить товар для удаления.', 'danger')
        return redirect('/snow_guard/cart')

    try:
        index = int(index_str)
        if 'cart' in session and 0 <= index < len(session['cart']):
            removed = session['cart'].pop(index)
            session.modified = True
            flash(f'Товар "{removed["name"]}" удалён из корзины.', 'success')
        else:
            flash('Товар не найден в корзине.', 'danger')
    except ValueError:
        flash('Ошибка при удалении товара.', 'danger')

    return redirect('/snow_guard/cart')

@snow_guard_bp.route('/clear-cart', methods=['POST'])
def clear_cart():
    session['cart'] = []
    session.modified = True
    flash('Корзина очищена.', 'success')
    return redirect('/snow_guard/cart')

@snow_guard_bp.route('/cart', methods=['GET', 'POST'])  # итоговый путь: /snow_guard/cart
def cart():
    cart_items = session.get('cart', [])

    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')

        if not email or not phone or len(cart_items) == 0:
            flash('Заполните e-mail, телефон и добавьте товар в корзину', 'error')
            return redirect(url_for('snow_guard.cart'))
        
        # --- Собираем красивый текст заявки ---
        lines = [
            '=' * 50,
            '>>> НОВАЯ ЗАЯВКА (скопируй и перезвони):'
        ]
        for item in cart_items:
            lines.append(f'Товар: {item["name"]}, кол-во: {item["quantity"]} шт.')
        lines.append(f'Клиент: {phone}')
        lines.append(f'E-mail: {email}')
        lines.append('=' * 50)
        
        message_text = "\n".join(lines)
        # ---------------------------------------

        # 1. Печатаем в терминал (как было раньше - для быстрой проверки)
        print("\n" + message_text + "\n")

        # 2. Отправляем на почту (теперь заявка не пропадёт!)
        try:
            send_email(message_text)
            print("📩 Письмо успешно отправлено на почту.")
        except Exception as e:
            print(f"❌ Ошибка отправки письма: {e}")
            # Даже если почта не ушла, заявка уже есть в терминале и (если добавишь файл) в файле.

        session['cart'] = []
        session.modified = True
        flash('Заявка оформлена! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('snow_guard.index'))

    return render_template('cart.html', cart=cart_items)