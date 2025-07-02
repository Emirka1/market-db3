from flask import Flask, render_template, redirect
import psycopg2

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        dbname="base",
        user="postgres",
        password="20062007",
        host="localhost",
        port="5432"
    )

@app.route('/items')
def show_items():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT items2.id, название, цена, описание, image_url, count, postavshic
            FROM items2
            JOIN quantity ON items2.id = quantity.id
        """)
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('items.html', items=items)
    except:
        return "Ошибка при загрузке товаров"

@app.route('/buys')
def show_buys():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.id, b.товар, b.стоимость, u.username, u.balance
            FROM buys b
            LEFT JOIN users u ON b.users_id = u.users_id
        """)
        buys = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('buys.html', buys=buys)
    except Exception as e:
        return f"Ошибка при загрузке покупок: {e}"

@app.route('/buy/<int:item_id>')
def buy(item_id):
    try:
        user_id = 1  

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT count FROM quantity WHERE id = %s", (item_id,))
        quantity_result = cursor.fetchone()

        cursor.execute("SELECT название, цена FROM items2 WHERE id = %s", (item_id,))
        item_result = cursor.fetchone()

        cursor.execute("SELECT balance FROM users WHERE users_id = %s", (user_id,))
        balance_result = cursor.fetchone()

        if quantity_result and quantity_result[0] > 0 and item_result and balance_result:
            название, цена = item_result
            balance = balance_result[0]

            if balance >= цена:
                cursor.execute("UPDATE quantity SET count = count - 1 WHERE id = %s", (item_id,))
                cursor.execute("UPDATE users SET balance = balance - %s WHERE users_id = %s", (цена, user_id))
                cursor.execute("""
                    INSERT INTO buys (товар, стоимость, users_id)
                    VALUES (%s, %s, %s)
                """, (название, цена, user_id))

                conn.commit()

        cursor.close()
        conn.close()
    except Exception as e:
        return f"Ошибка при покупке: {e}"

    return redirect('/items')

if __name__ == '__main__':
    app.run(debug=True)






