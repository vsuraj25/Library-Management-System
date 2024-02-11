from flask import *
import os
import psycopg2
from psycopg2 import sql
import requests
from dotenv import load_dotenv
from exceptions import TooMuchDebt, NoBooksFoundFrappe

# Load .env file    
load_dotenv()

webapp_root = 'webapp'

static_dir_path = os.path.join(webapp_root, 'static')
template_dir_path = os.path.join(webapp_root, 'templates')

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET_KEY")

def db_conn():
    # Get the connection string from the environment variable
    connection_string = os.environ.get("DATABASE_URL")

    # Connect to the Postgres database
    conn = psycopg2.connect(connection_string)
    return conn

def load_book_table():
    conn = db_conn()
    cur  = conn.cursor()
    cur.execute(
    '''CREATE TABLE IF NOT EXISTS books_data(id SERIAL,
            book_name TEXT NOT NULL PRIMARY KEY,
            author_name TEXT,
            publisher_name TEXT,
            num_pages INT,
            stock INT DEFAULT 1,
            rent_fee INT DEFAULT 100,
            registered_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP);''')
    cur.execute('''CREATE TABLE IF NOT EXISTS transaction_data(issue_id SERIAL PRIMARY KEY,
        member_name TEXT NOT NULL,
        book_name TEXT NOT NULL,
        phone TEXT,
        rent INT,
        payment_status BOOLEAN DEFAULT FALSE,
        issue_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        returned BOOLEAN DEFAULT FALSE,
        return_date TIMESTAMP WITH TIME ZONE 
        );''')
    cur.execute('''SELECT * FROM books_data ORDER BY registered_date DESC;''')
    data = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return data

def load_members_table():
    conn = db_conn()
    cur  = conn.cursor()
    cur.execute('''SELECT * FROM members_data ORDER BY registered_date DESC;''')
    data = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return data

def load_transaction_table():
    conn = db_conn()
    cur  = conn.cursor()
    cur.execute('''SELECT * FROM transaction_data ORDER BY issue_date DESC;''')
    data = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return data

@app.route('/')
def home():
    return render_template('index.html', data = load_book_table())

@app.route('/members_table')
def members_table():
    return render_template('members_table.html', data = load_members_table())

@app.route('/transaction_table')
def transaction_table():
    return render_template('transaction_table.html', data = load_transaction_table())

@app.route('/load_add_book')
def load_add_book():
    return render_template("add_book.html")

@app.route('/load_remove_book')
def load_remove_book():
    return render_template("remove_book.html")

@app.route('/load_update_book')
def load_update_book():
    return render_template("update_book.html")

@app.route('/load_add_member')
def load_add_member():
    return render_template("add_member.html")

@app.route('/load_update_member')
def load_update_member():
    return render_template("update_member.html")

@app.route('/load_remove_member')
def load_remove_member():
    return render_template("remove_member.html")

@app.route('/load_issue_member')
def load_issue_member():
    conn = db_conn()
    cur  = conn.cursor()
    cur.execute('''SELECT book_name FROM books_data;''')
    books_data = cur.fetchall()
    cur.execute('''SELECT member_name FROM members_data;''')
    members_data = cur.fetchall()
    return render_template("issue_book.html", books_data = books_data, members_data = members_data)

@app.route('/load_return_book')
def load_return_book():
    conn = db_conn()
    cur  = conn.cursor()
    cur.execute('''SELECT issue_id FROM transaction_data;''')
    issue_ids = cur.fetchall()
    return render_template("return_book.html", issue_ids = issue_ids)

@app.route('/load_search_frappe_books')
def search_frappe_books():
    return render_template("frappe_import.html")

@app.route('/add_book', methods=["POST", "GET"])   
def add_book():
    conn = db_conn()
    cur = conn.cursor()

    book_name = request.form['bookName']
    author_name = request.form['authorName']
    publisher_name = request.form['publisherName']
    num_pages = request.form['numPages']
    stock = request.form['stock']
    rent_fee = request.form['rentFee']

    cur.execute(
        f'''INSERT INTO books_data(book_name, author_name, publisher_name, num_pages, stock, rent_fee)
            VALUES
            ('{book_name}', '{author_name}', '{publisher_name}', '{num_pages}', {stock}, {rent_fee});'''
        )
    
    conn.commit()
    cur.close()
    conn.close()
    return render_template('index.html', data = load_book_table())

@app.route('/remove_book', methods=["POST", "GET"])   
def remove_book():
    conn = db_conn()
    cur = conn.cursor()

    filter = request.form.get('filter')
    value = request.form['inputValue']

    cur.execute(
        f'''DELETE FROM books_data WHERE {filter} = '{value}';'''
        )
    conn.commit()
    cur.close()
    conn.close()
    return render_template('index.html', data = load_book_table())

@app.route('/update_book', methods=["POST", "GET"])   
def update_book():
    conn = db_conn()
    cur = conn.cursor()

    filter = request.form.get('filter')
    value = request.form['inputValue']
    author_name = request.form['authorName']
    publisher_name = request.form['publisherName']
    num_pages = request.form['numPages']
    stock = request.form['stock']
    rent_fee = request.form['rentFee']

    cur.execute(
        f'''UPDATE books_data SET  author_name = '{author_name}',publisher_name = '{publisher_name}', num_pages = {num_pages}, stock = {stock}, rent_fee = {rent_fee}
            WHERE {filter} = '{value}';'''
        )
    conn.commit()
    cur.close()
    conn.close()
    return render_template('index.html', data = load_book_table())

@app.route('/add_member', methods=["POST", "GET"])   
def add_member():
    conn = db_conn()
    cur = conn.cursor()

    cur.execute(
    '''CREATE TABLE IF NOT EXISTS members_data(id SERIAL,
            member_name TEXT NOT NULL PRIMARY KEY,
            phone TEXT,
            registered_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP);''')

    member_name = request.form['memberName']
    phone = request.form['phone']
    try:
        cur.execute(
            f'''INSERT INTO members_data(member_name, phone)
                VALUES
                ('{member_name}', '{phone}');'''
            )
        
        conn.commit()
    except Exception as e:
        print(e)
        conn.commit()
        pass

    cur.close()
    conn.close()
    return render_template('members_table.html', data = load_members_table())

@app.route('/remove_member', methods=["POST", "GET"])   
def remove_member():
    conn = db_conn()
    cur = conn.cursor()

    filter = request.form.get('filter')
    value = request.form['inputValue']

    cur.execute(
        f'''DELETE FROM members_data WHERE {filter} = '{value}';'''
        )
    conn.commit()
    cur.close()
    conn.close()
    return render_template('members_table.html', data = load_members_table())

@app.route('/update_member', methods=["POST", "GET"])   
def update_member():
    conn = db_conn()
    cur = conn.cursor()

    filter = request.form.get('filter')
    value = request.form['inputValue']
    phone = request.form['phone']

    cur.execute(
        f'''UPDATE members_data SET phone = '{phone}'
            WHERE {filter} = '{value}';'''
        )
    conn.commit()
    cur.close()
    conn.close()
    return render_template('members_table.html', data = load_members_table())

@app.route('/issue_book', methods=["POST", "GET"])   
def issue_book():
    conn = db_conn()
    cur = conn.cursor()

    book_name = request.form.get('bookName')
    member_name = request.form.get('memberName')
    cur.execute(f"SELECT phone FROM members_data WHERE member_name = '{member_name}';")
    phone = cur.fetchall()[0][0]
    cur.execute(f"SELECT rent_fee FROM books_data WHERE book_name = '{book_name}';")
    rent = cur.fetchall()[0][0]
    
    try:
        cur.execute(f"SELECT rent FROM transaction_data WHERE member_name = '{member_name}' and payment_status = False;")
        total_rent = cur.fetchall()
        if len(total_rent) >= 1:
            list_of_rents = [tup[0] for tup in total_rent]
            if sum(list_of_rents) + rent >= 500:
                return render_template("404.html", custom_error = TooMuchDebt().message)
            
        cur.execute('''CREATE TABLE IF NOT EXISTS transaction_data(issue_id SERIAL PRIMARY KEY,
            member_name TEXT NOT NULL,
            book_name TEXT NOT NULL,
            phone TEXT,
            rent INT,
            payment_status BOOLEAN DEFAULT FALSE,
            issue_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            returned BOOLEAN DEFAULT FALSE,
            return_date TIMESTAMP WITH TIME ZONE 
            );''')
        cur.execute(
                f'''INSERT INTO transaction_data(member_name, book_name, phone, rent)
                    VALUES
                    ('{member_name}','{book_name}', '{phone}', '{rent}');'''
                )
        conn.commit()
        cur.close()
        conn.close()
        return render_template('transaction_table.html', data = load_transaction_table())
    except Exception as e:
        raise e

    

@app.route('/return_book', methods=["POST", "GET"])   
def return_book():
    conn = db_conn()
    cur = conn.cursor()

    issue_id = request.form.get('issueId')
    payment_status = request.form.get('paymentStatus')
    return_status = request.form.get('returnStatus')
    if payment_status == "True":
        payment_status = True
    else:
        payment_status = False

    if return_status == "True":
        return_status = True
    else:
        return_status = False

    cur.execute(
        f'''UPDATE transaction_data SET payment_status = {payment_status}, returned = {return_status}, return_date = CURRENT_TIMESTAMP
            WHERE issue_id = '{issue_id}';'''
        )

    conn.commit()
    cur.close()
    conn.close()
    return render_template('transaction_table.html', data = load_transaction_table())

@app.route('/search_frappe_books', methods=["POST", "GET"])   
def search_frappe_book():
    search = request.form['searchQuery']
    res = requests.get(f"https://frappe.io/api/method/frappe-library?title={search}")
    result = res.json()['message']
    data = [(book["title"], book["authors"],book["publisher"], book["  num_pages"]) for book in result]
    session['data'] = data  # Store data in the session
    num_books = len(result)
    if num_books == 0:
        return render_template("404.html", custom_error = NoBooksFoundFrappe().message)
    else:
        return render_template("frappe_import_results.html", data = data, num_books = num_books)

@app.route('/import_frappe_data', methods=["POST", "GET"])   
def import_frappe_data():
    data = session.get('data')
    if len(data) >= 0:
        conn = db_conn()
        cur = conn.cursor()
        for book in data:
            try:
                cur.execute(
                    f'''INSERT INTO books_data(book_name, author_name, publisher_name, num_pages)
                        VALUES
                        {book};'''
                    )
                conn.commit()
            except Exception as e:
                print(e)
                conn.commit()
                pass    
        conn.commit()
        cur.close()
        conn.close()
    return render_template('index.html', data = load_book_table())


if __name__ == '__main__':
    app.run(debug=True)