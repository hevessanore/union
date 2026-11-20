# passport_helpers.py — общие функции для паспортов товаров
from flask import url_for


def _static(path):
    """Путь из catalog_data → реальный URL статики. Пусто/нет файла — None."""
    if not path:
        return None
    return url_for('static', filename=path.lstrip('/'))


def build_variant_data(item):
    """Собирает для JS: описание, характеристики, цену и картинки каждого варианта.
    Картинки: указанные в "images" варианта, иначе общая "image" товара."""
    base_desc = item.get('description', '')
    base_specs = item.get('characteristics', {})
    base_price = item.get('price')
    base_img = _static(item.get('image'))

    data = {}
    for key, v in item.get('variants', {}).items():
        images = {}
        for slug, path in (v.get('images') or {}).items():
            url = _static(path)
            if url:
                images[slug] = url
        data[key] = {
            "description": v.get('description', base_desc),
            "characteristics": v.get('characteristics', base_specs),
            "price": v.get('price', base_price),
            "images": images or ({"*": base_img} if base_img else {}),
        }
    return data