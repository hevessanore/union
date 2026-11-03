# routes/fence.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash

fence_bp = Blueprint('fence', __name__, url_prefix='/fence')

@fence_bp.route('/')
def index():
    page_data = {
        "title": "Кровельные ограждения",
        "image_1": "img/f_001.png",
        "image_2": "img/f_002.png"
    }
    return render_template('fence.html', data=page_data)

@fence_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    print("✅ МАРШРУТ add-to-cart (ограждения) СРАБОТАЛ!")
    
    quantity_str = request.form.get('quantity', '1')
    try:
        quantity = int(quantity_str)
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    if 'cart' not in session:
        session['cart'] = []

    session['cart'].append({
        "name": "Кровельное ограждение (комплект)",
        "quantity": quantity
    })
    session.modified = True

    flash('Товар добавлен в корзину. Менеджер перезвонит для уточнения деталей.', 'success')
    
    referrer = request.referrer
    if referrer:
        return redirect(referrer)
    return redirect(url_for('fence.index'))