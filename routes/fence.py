# routes/fence.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify

fence_bp = Blueprint('fence', __name__, url_prefix='/fence')

def normalize_image(image):
    """Приводит путь к картинке к виду img/файл — файлы лежат в static/img/."""
    if not image:
        return ''
    image = image.strip().lstrip('/')
    if image.startswith('img/'):
        return image
    return 'img/' + image

# --- ДАННЫЕ КАТАЛОГА (только ограждения) ---
FENCES_CATALOG = {
    "f-001": {
        "title": "Кровельное ограждение тип 1",
        "image": "img/f_001.png",
        "price": 1200,
        "description": "Стальное ограждение для кровли, высота 900 мм, оцинкованный крепёж в комплекте."
    },
    "f-002": {
        "title": "Кровельное ограждение тип 2",
        "image": "img/f_002.png",
        "price": 1500,
        "description": "Усиленная конструкция для кровель с повышенной ветровой нагрузкой."
    }
}

# --- Каталог ограждений ---
@fence_bp.route('/')
@fence_bp.route('/catalog')
def catalog():
    return render_template('fences_catalog.html', items=FENCES_CATALOG)

# --- Паспорт конкретного ограждения ---
@fence_bp.route('/<code>')
def detail(code):
    item = FENCES_CATALOG.get(code)
    if not item:
        return redirect(url_for('fence.catalog'))
    return render_template('fence_passport.html', code=code, item=item)

# --- Добавить в корзину ---
@fence_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    quantity_str = request.form.get('quantity', '1')
    try:
        quantity = int(quantity_str)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    code = request.form.get('code', '')
    item = FENCES_CATALOG.get(code, {})
    name = item.get('title', 'Ограждение')
    image = item.get('image') or normalize_image(request.form.get('image', ''))
    price = item.get('price') or request.form.get('price') or None

    print(f"DEBUG fence add-to-cart: name={name!r}, image={image!r}, price={price!r}, code={code!r}")

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        "code": code if item else None,
        "name": name,
        "image": image,
        "price": price,
        "quantity": quantity
    })
    session.modified = True

    cart_count = len(session['cart'])

    # AJAX-запрос: отвечаем JSON, страница не перезагружается
    if request.form.get('ajax') == '1' or request.headers.get('X-Requested-With') == 'fetch':
        return jsonify(ok=True, name=name, cart_count=cart_count)

    # Обычный запрос: flash + возврат на ту же страницу
    flash('Товар добавлен в корзину. Менеджер перезвонит для уточнения деталей.', 'success')

    referrer = request.referrer
    if referrer:
        return redirect(referrer.split('#')[0])
    return redirect(url_for('fence.catalog'))