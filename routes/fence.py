# routes/fence.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from catalog_data import FENCES_CATALOG
from passport_helpers import build_variant_data

fence_bp = Blueprint('fence', __name__, url_prefix='/fence')


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
    variants = item.get('variants', {})
    first_key = next(iter(variants), '')
    return render_template('passport.html', code=code, item=item,
                           first_key=first_key, prefix='fence',
                           variant_data=build_variant_data(item))


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
    price = item.get('price') or request.form.get('price') or None
    variant = request.form.get('variant', '')
    color = request.form.get('color', '')

    print(f"DEBUG fence add-to-cart: name={name!r}, price={price!r}, code={code!r}, variant={variant!r}, color={color!r}")

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        "code": code if item else None,
        "name": name,
        "variant": variant,
        "color": color,
        "price": price,
        "quantity": quantity
    })
    session.modified = True

    if request.form.get('ajax') == '1' or request.headers.get('X-Requested-With') == 'fetch':
        return jsonify(ok=True, name=name, cart_count=len(session['cart']))

    flash('Товар добавлен в корзину. Менеджер перезвонит для уточнения деталей.', 'success')

    referrer = request.referrer
    if referrer:
        return redirect(referrer.split('#')[0])
    return redirect(url_for('fence.catalog'))