# routes/snow_guard.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from routes.orders import send_email

snow_guard_bp = Blueprint('snow_guard', __name__)


def normalize_image(image):
    """Приводит путь к картинке к виду img/файл — файлы лежат в static/img/."""
    if not image:
        return ''
    image = image.strip().lstrip('/')
    if image.startswith('img/'):
        return image
    return 'img/' + image


# --- ДАННЫЕ КАТАЛОГА (только снегозадержатели) ---
SNOW_GUARD_CATALOG = {
    "sg-001": {
        "title": "Трубчатый снегозадержатель 3 м",
        "image": "img/sg_001.png",
        "description": "Стальная труба Ø25 мм, длина 3 м, комплект крепежа на 4 опоры, оцинкованная сталь.",
        "variants": {
            "standard": {"label": "Стандарт", "note": "полимерное покрытие, толщина 0,5 мм"},
            "premium":  {"label": "Премиум",  "note": "усиленное покрытие, толщина 0,7 мм"}
        },
        "colors": [
            {"name": "Шоколадный RAL-8017", "hex": "#66472d"},
            {"name": "Вишня RAL-3005",     "hex": "#834646"},
            {"name": "Синий RAL-5005",    "hex": "#2A77CF"},
            {"name": "Зелёный мох RAL-6005",    "hex": "#366844"}
        ]
    },
    "sg-002": {
        "title": "Пластинчатый снегозадержатель (уголок) 1 м",
        "image": "img/sg_002.png",
        "description": "Оцинкованная сталь 2 мм, длина 1 м, универсальный крепёж под металлочерепицу и профлист.",
        "variants": {
            "standard": {"label": "Стандарт", "note": "полимерное покрытие, толщина 0,5 мм"},
            "premium":  {"label": "Премиум",  "note": "усиленное покрытие, толщина 0,7 мм"}
        },
        "colors": [
            {"name": "Шоколадный RAL-8017", "hex": "#66472d"},
            {"name": "Вишня RAL-3005",     "hex": "#834646"},
            {"name": "Синий RAL-5005",    "hex": "#2A77CF"},
            {"name": "Зелёный мох RAL-6005",    "hex": "#366844"}
        ]
    },
    "sg-003": {
        "title": "Решётчатый снегозадержатель 2 м",
        "image": "img/sg_003.png",
        "description": "Усиленная решётка 2 м, оцинкованная сталь, комплект крепежа, подходит для крутых скатов.",
        "variants": {
            "standard": {"label": "Стандарт", "note": "полимерное покрытие, толщина 0,5 мм"},
            "premium":  {"label": "Премиум",  "note": "усиленное покрытие, толщина 0,7 мм"}
        },
        "colors": [
            {"name": "Шоколадный RAL-8017", "hex": "#66472d"},
            {"name": "Вишня RAL-3005",     "hex": "#834646"},
            {"name": "Синий RAL-5005",    "hex": "#2A77CF"},
            {"name": "Зелёный мох RAL-6005",    "hex": "#366844"}
        ]
    }
}


# --- Каталог снегозадержателей ---
@snow_guard_bp.route('')
@snow_guard_bp.route('/catalog')
def catalog():
    return render_template('snow_guard_catalog.html', items=SNOW_GUARD_CATALOG)


# --- Паспорт конкретного снегозадержателя ---
@snow_guard_bp.route('/<code>')
def detail(code):
    item = SNOW_GUARD_CATALOG.get(code)
    if not item:
        return redirect(url_for('snow_guard.catalog'))
    # Дефолтные тип и цвет — первый вариант из карточки, чтобы в корзину уехал выбор
    first_variant = next(iter(item.get('variants', {}).values()), {}).get('label', '')
    first_color = item['colors'][0]['name'] if item.get('colors') else ''
    return render_template('snow_guard_passport.html', code=code, item=item,
                           first_variant=first_variant, first_color=first_color)


# --- Добавить в корзину ---
@snow_guard_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    quantity_str = request.form.get('quantity', '1')
    try:
        quantity = int(quantity_str)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    # Приоритет: артикул из каталога, иначе название/картинка/цена из формы
    code = request.form.get('code', '')
    item = SNOW_GUARD_CATALOG.get(code, {})
    name = item.get('title') or request.form.get('name', 'Товар без названия')
    image = item.get('image') or normalize_image(request.form.get('image', ''))
    price = item.get('price') or request.form.get('price') or None
    variant = request.form.get('variant', '')
    color = request.form.get('color', '')

    # Отладка: видно в терминале, что пришло из формы
    print(f"DEBUG add-to-cart: name={name!r}, image={image!r}, price={price!r}, code={code!r}, variant={variant!r}, color={color!r}")

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        "code": code if item else None,
        "name": name,
        "image": image,
        "variant": variant,
        "color": color,
        "price": price,
        "quantity": quantity
    })
    session.modified = True

    cart_count = len(session['cart'])

    # AJAX-запрос: отвечаем JSON, страница не перезагружается
    if request.form.get('ajax') == '1' or request.headers.get('X-Requested-With') == 'fetch':
        return jsonify(ok=True, name=name, cart_count=cart_count)

    # Обычный запрос: flash + возврат на ту же страницу
    flash(f'«{name}» добавлен в корзину. Менеджер перезвонит для уточнения деталей.', 'success')

    referrer = request.referrer
    if referrer:
        return redirect(referrer.split('#')[0])
    return redirect(url_for('snow_guard.catalog'))


# --- Удалить один товар из корзины ---
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


# --- Очистить корзину ---
@snow_guard_bp.route('/clear-cart', methods=['POST'])
def clear_cart():
    session['cart'] = []
    session.modified = True
    flash('Корзина очищена.', 'success')
    return redirect('/snow_guard/cart')


# --- Корзина и оформление заявки ---
@snow_guard_bp.route('/cart', methods=['GET', 'POST'])
def cart():
    cart_items = session.get('cart', [])

    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')

        if not email or not phone or len(cart_items) == 0:
            flash('Заполните e-mail, телефон и добавьте товар в корзину', 'error')
            return redirect(url_for('snow_guard.cart'))

        lines = [
            '=' * 50,
            '>>> НОВАЯ ЗАЯВКА (скопируй и перезвони):'
        ]
        for item in cart_items:
            opts = []
            if item.get('variant'):
                opts.append(f"тип: {item['variant']}")
            if item.get('color'):
                opts.append(f"цвет: {item['color']}")
            opt_info = f", {', '.join(opts)}" if opts else ''
            if item.get('price'):
                price_info = f', цена: {item["price"]} руб.'
            else:
                price_info = ', цена по запросу'
            lines.append(f'Товар: {item["name"]} (арт. {item.get("code") or "-"}), кол-во: {item["quantity"]} шт.{opt_info}{price_info}')

        lines.append(f'Клиент: {phone}')
        lines.append(f'E-mail: {email}')
        lines.append('=' * 50)

        message_text = "\n".join(lines)

        print("\n" + message_text + "\n")

        try:
            send_email(message_text)
            print("📩 Письмо успешно отправлено на почту.")
        except Exception as e:
            print(f"❌ Ошибка отправки письма: {e}")

        session['cart'] = []
        session.modified = True
        flash('Заявка оформлена! Мы свяжемся с вами в ближайшее время.', 'success')
        return redirect(url_for('snow_guard.catalog'))

    return render_template('cart.html', cart=cart_items)
