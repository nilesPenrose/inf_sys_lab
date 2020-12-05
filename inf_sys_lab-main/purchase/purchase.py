from DBCM import UseDatabase, ConnectionErrors, SQLError
from flask import render_template, request, Blueprint, current_app, session
from check_auth import check_access

purchase_blueprint = Blueprint('purchase_blueprint', __name__, template_folder='templates')


@purchase_blueprint.route('/', methods=['GET', 'POST'])
@check_access("3")
def purchase():
    cart_size = get_full_cart_len()
    try:
        with UseDatabase(current_app.config['dbconfig']["Manager"]) as cursor:
            catalog = show_catalog(cursor)
            if 'choice' in request.form and request.form['choice'] == "Добавить":
                choice_name = request.form.get('choice_name')
                choice_id = request.form.get('choice_id')
                amount = request.form.get('amount')
                put_into_cart(amount, choice_id, choice_name)
                cart_size = get_full_cart_len()
                return render_template('catalog.html', catalog=catalog, in_cart=cart_size)

            elif 'show_cart' in request.form and request.form['show_cart'][0:16] == "Показать корзину":
                return render_template('cart.html', cart=session['cart'])

            elif 'purchase' in request.form and request.form['purchase'] == "Оформить заказ":
                return render_template('order.html', cart=session['cart'])

            elif 'exit' in request.form and request.form['exit'] == "Купить":
                save_cart(cursor)
                return render_template('res.html')

            elif 'delete' in request.form and request.form['delete'] == "Удалить":
                item_to_delete = request.form.get('item_to_delete')
                session['cart'] = delete_from_cart(item_to_delete)
                return render_template('cart.html', cart=session['cart'])

            else:
                return render_template('catalog.html', catalog=catalog, in_cart=cart_size)
    except ConnectionErrors as err:
        print("Connection error:", str(err))
        str_err = "Connection error: " + str(err)
        return render_template('catalog.html', message=str_err)
    except SQLError as err:
        print("Request error:", str(err))
        str_err = "Request error: " + str(err)
        return render_template('catalog.html', message=str_err)



def put_into_cart(amount, choice_id, choice_name):
    if 'cart' not in session:
        session['cart'] = []

    for value in session['cart']:
        if int(choice_id) == value['choice_id']:
            print("CHANGING")
            num = value['amount']
            session['cart'].remove(value)
            session['cart'] += [{
                'choice_id': int(choice_id),
                'choice_name': choice_name,
                'amount': int(amount) + num
            }]
            return

    session['cart'] += [{
        'choice_id': int(choice_id),
        'choice_name': choice_name,
        'amount': int(amount)
    }]
    return


def get_full_cart_len():
    if 'cart' not in session:
        session['cart'] = []
        return 0

    full_cart_len = 0
    for value in session['cart']:
        full_cart_len += value['amount']

    return full_cart_len


def show_catalog(cursor):
    SQL = f"""SELECT id_catalog, name, price
              FROM catalog"""
    cursor.execute(SQL)
    result = cursor.fetchall()
    res = []
    schema = ['id_catalog', 'name', 'price']
    for blank in result:
        res.append(dict(zip(schema, blank)))
    return res


def save_cart(cursor):
    cursor.execute("""TRUNCATE TABLE cart""")
    SQL = """INSERT INTO cart
             VALUES (NULL, %s, %s, %s)"""
    for i in range(len(session['cart'])):
        values = session['cart'][i].values()
        values = list(values)
        cursor.execute(SQL, (values[1], values[2], values[0],))
    return


def delete_from_cart(name):
    print(name)
    for value in session['cart']:
        if value['choice_name'] == name:
            session['cart'].remove(value)
            return session['cart']
    return session['cart']