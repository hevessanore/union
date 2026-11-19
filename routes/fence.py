# routes/fence.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

fence_bp = Blueprint('fence', __name__, url_prefix='/fence')

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

# --- Корзина ---
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

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        "code": code,
        "name": name,
        "quantity": quantity
    })
    session.modified = True

    flash('Товар добавлен в корзину. Менеджер перезвонит для уточнения деталей.', 'success')

    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('fence.catalog'))
