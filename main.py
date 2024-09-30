import datetime
import json
import random
import sqlite3
import string
import threading
import webbrowser
import os

from flask import Flask, render_template, url_for, request, redirect, session, flash

app = Flask(__name__)
app.secret_key = 'isaiah41:10-12_zeerah_and_amaesty'
opened = False


def get_profile_picture():
    user_name = session["profile_name"]
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute("SELECT passport FROM members_details WHERE name = ?", (user_name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def generate_reference_id():
    ref = random.randint(100000, 999999)
    return ref


def get_current_date():
    date = datetime.date.today()
    return date


def open_browser():
    global opened
    if not opened:
        url = "http://127.0.0.1:5000"
        webbrowser.open_new(url)
        opened = True


@app.route('/stop_server', methods=['POST'])
def stop_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'Server shutting down...'


@app.route("/")
def login():
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()

    #  Execute an SQL CREATE TABLE statement to define the table's structure

    # create shares table
    cursor.execute('''CREATE TABLE IF NOT EXISTS shares
           (ref_num TEXT, 
           staff_name TEXT, 
           units_of_shares TEXT,
           total_shares)''')

    # Commit the changes to the database
    conn.commit()

    # create admin_credentials
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin_credentials 
       (name TEXT, 
       email TEXT, 
       password TEXT)''')

    # Commit the changes to the database
    conn.commit()

    # create list of contributions
    cursor.execute('''CREATE TABLE IF NOT EXISTS contribution_list 
       (name TEXT, 
       date_created TEXT)''')

    # Commit the changes to the database
    conn.commit()

    # create system_details
    cursor.execute('''CREATE TABLE IF NOT EXISTS system_details 
       (name TEXT, 
       email TEXT, 
       loan_charges REAL,
       withdrawal_charges REAL,
       loan_interest_rate REAL,
       minimum_shares REAL,
       amount_per_unit_share REAL,
       loan1 REAL,
       loan2 REAL,
       loan3 REAL,
       loan4 REAL,
       tm_credit1 REAL,
       tm_credit2 REAL,
       nt_credit1 REAL,
       nt_credit2 REAL)''')

    # Commit the changes to the database
    conn.commit()

    # create loan table
    cursor.execute('''CREATE TABLE IF NOT EXISTS loan 
           (ref_num TEXT, 
           name TEXT, 
           date TEXT,
           loan_amount REAL,
           monthly_deduction REAL,
           guarantor_1 TEXT,
           guarantor_2 TEXT)''')

    # Commit the changes to the database
    conn.commit()

    # create contribution table
    cursor.execute('''CREATE TABLE IF NOT EXISTS contribution 
              (ref_num TEXT,
              contribution_name TEXT, 
              name TEXT, 
              amount REAL,
              start TEXT,
              end TEXT,
              total_contributed REAL)''')

    # Commit the changes to the database
    conn.commit()

    # create shopping members_details
    cursor.execute('''CREATE TABLE IF NOT EXISTS members_details 
          (staff_id INT,
          name TEXT, 
          email TEXT,
          category TEXT,
          passport TEXT,
          date_of_birth TEXT,
          gender TEXT,
          monthly_contribution REAL,
          bank_name TEXT,
          account_num TEXt,
          account_name TEXT,
          current_balance REAL,
          total_loan_collected REAL,
          total_credit_purchase REAL,
          total_debt REAL,
          others REAL,
          frozen_amount REAL, 
          monthly_deduction REAL,
          UNIQUE(staff_id))''')

    # Commit the changes to the database
    conn.commit()

    # create shopping inventory
    cursor.execute('''CREATE TABLE IF NOT EXISTS inventory 
          (item_name TEXT, 
          bulk_price REAL,
          bulk_quantity REAL,
          unit_price REAL,
          unit_quantity REAL,
          UNIQUE(item_name))''')

    # Commit the changes to the database
    conn.commit()

    # create shopping cart table
    cursor.execute('''CREATE TABLE IF NOT EXISTS shopping_cart 
              (ref_num TEXT,
              staff_name TEXT,
              item_name TEXT, 
              item_type TEXT,
              item_price REAL,
              item_quantity INT,
              item_total_price REAL,
              purchase_type TEXT)
              ''')
    # Commit the changes to the database
    conn.commit()

    # create shopping credit_purchase
    cursor.execute('''CREATE TABLE IF NOT EXISTS credit_purchase 
                  (staff_name TEXT,
                  reference_code TEXT, 
                  credit_amount REAL,
                  monthly_credit_deduction REAL)
                  ''')
    # Commit the changes to the database
    conn.commit()

    try:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM admin_credentials''')
        if not cursor.fetchall():
            message = "No Admin Account Created Yet."
            return render_template("new_login.html", message=message)
    except:
        sqlite3.Error()
        pass
    return render_template("login_admin.html")


@app.route("/Admin_registration")
def register_admin():
    def caesar_cipher(text, shift_num):
        result = ""
        for char in text:
            shifted_char = 0
            if char.isalpha():
                shift_amount = shift_num % 26
                if char.islower():
                    shifted_char = chr(((ord(char) - ord('a') + shift_amount) % 26) + ord('a'))
                elif char.isupper():
                    shifted_char = chr(((ord(char) - ord('A') + shift_amount) % 26) + ord('A'))
                result += shifted_char
            else:
                result += char

        return result

    # Generate a random product key
    random_char = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=16))
    product_key = f"{random_char}"

    shift = 3
    encoded_string = caesar_cipher(product_key, shift)
    with open("encoded_key.txt", "w") as new:
        new.write(encoded_string)

    # Decode the encoded string
    decoded_string = caesar_cipher(encoded_string, -shift)
    credentials = {
        "key": f"{decoded_string}"
    }
    with open("key.json", "w") as file:
        json.dump(credentials, file)
    return render_template("admin_registration.html", product_key=encoded_string)


@app.route("/process new admin", methods=["POST"])
def process_new_admin_form():
    # get the data entered into the form.
    name = request.form.get("name").upper()
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirmPassword")
    key = request.form.get("license")
    loan_interest = 15
    minimum_shares = 10
    loan_charge = 500
    withdrawal_charge = 200
    unit_share = 5000
    loan1 = 8
    loan2 = 15
    loan3 = 18
    loan4 = 20
    tm_credit1 = 3
    tm_credit2 = 5
    nt_credit1 = 5
    nt_credit2 = 5

    with open('date.txt', 'w') as file:
        content = "YYYY, MM"
        file.write(content)

    with open("key.json", "r") as file:
        data = json.load(file)
        activation_key = data["key"]

    if password == confirm_password and key == activation_key:
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO admin_credentials (name, email, password) VALUES(?, ?, ?)''',
                       (name, email, password))
        conn.commit()

        cursor.execute('''INSERT INTO system_details (name, email, loan_charges, withdrawal_charges, loan_interest_rate,
        minimum_shares, amount_per_unit_share, loan1, loan2, loan3, loan4, tm_credit1, tm_credit2, nt_credit1, 
        nt_credit2) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (name, email, loan_charge,
                                                                             withdrawal_charge, loan_interest,
                                                                             minimum_shares, unit_share, loan1, loan2,
                                                                             loan3, loan4, tm_credit1, tm_credit2,
                                                                             nt_credit1, nt_credit2))
        conn.commit()
        conn.close()

    elif password != confirm_password:
        message = "Passwords do not match"
        with open("encoded_key.txt", "r") as new:
            product_key = new.readline()
        return render_template("admin_registration.html", message=message, key=product_key)

    else:
        message = "Wrong Activation key. Contact the Developer for help.".upper()
        with open("encoded_key.txt", "r") as new:
            product_key = new.readline()
        return render_template("admin_registration.html", message=message, key=product_key)

    # Redirect to the result page with data as URL parameters
    return redirect(url_for("login"))


@app.route("/Admin_dashboard", methods=["GET", "POST"])
def admin_dashboard():
    if request.method == "POST":
        user = request.form.get("email")
        user_password = request.form.get("password")

        # get info from database for verification.
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admin_credentials WHERE email = ?", (user,))
        data = cursor.fetchone()

        cursor.execute("SELECT * FROM system_details WHERE email = ?", (user,))
        item = cursor.fetchone()

        # Check if a record with the given 'name' exists
        if item is not None:
            loan_charges = round(int(item[2]), 2)
            withdrawal_charges = round(int(item[3]), 2)
            interest_rate = round(int(item[4]))
            minimum_shares = round(int(item[5]))
            unit_share = round(int(item[6]), 2)

        else:
            loan_charges = None
            withdrawal_charges = None
            interest_rate = None
            minimum_shares = None
            unit_share = None

        if data is not None:
            name = data[0]
            email = data[1]
            password = data[2]

            if email == user:
                if password == user_password:
                    # Store user data in the session
                    session['name'] = name
                    session['email'] = email
                    session['password'] = password
                    return render_template("admin_dashboard.html", name=name, email=email,
                                           loan_charges=loan_charges, withdrawal_charges=withdrawal_charges,
                                           interest_rate=interest_rate, minimum_shares=minimum_shares,
                                           unit_share=unit_share)
                else:
                    message = "Wrong Password"
                    return render_template("login_admin.html", message=message)
            else:
                message = "User does not exist."
                return render_template("login_admin.html", message=message)

    else:
        # If the user is already logged in, retrieve their data from the session
        if 'email' in session:
            user_email = session['email']
            # get info from database for verification.
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admin_credentials")
            data = cursor.fetchall()

            cursor.execute("SELECT * FROM system_details WHERE email = ?", (user_email,))
            item = cursor.fetchone()

            # Check if a record with the given 'name' exists

            if item is not None:
                loan_charges = round(int(item[2]), 2)
                withdrawal_charges = round(int(item[3]), 2)
                interest_rate = round(int(item[4]))
                minimum_shares = round(int(item[5]))
                unit_share = round(int(item[6]), 2)

            else:
                loan_charges = None
                withdrawal_charges = None
                interest_rate = None
                minimum_shares = None
                unit_share = None

            for rows in data:
                name = rows[0]
                email = rows[1]

                if email == user_email:
                    return render_template("admin_dashboard.html", name=name, email=email,
                                           loan_charges=loan_charges, withdrawal_charges=withdrawal_charges,
                                           interest_rate=interest_rate, minimum_shares=minimum_shares,
                                           unit_share=unit_share)


@app.route("/process_setup", methods=["POST"])
def process_setup():
    if request.method == "POST":
        # Get the data submitted in the form
        loan_charge = request.form["loan"]
        withdrawal_charge = request.form["withdrawal"]
        loan_interest = request.form["interest"]
        minimum_shares = request.form["min_shares"]
        unit_shares = request.form["amount"]
        loan1 = request.form["loan1"]
        loan2 = request.form["loan2"]
        loan3 = request.form["loan3"]
        loan4 = request.form["loan4"]
        tm_credit1 = request.form["tm_credit1"]
        tm_credit2 = request.form["tm_credit2"]
        nt_credit1 = request.form["nt_credit1"]
        nt_credit2 = request.form["nt_credit2"]

        if "email" in session:
            email = session["email"]

            # Connect to the database
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()

            # Update the system_details table for the logged-in user
            cursor.execute('''UPDATE system_details SET loan_charges = ?, withdrawal_charges = ?, loan_interest_rate 
            = ?, minimum_shares = ?, amount_per_unit_share = ?, loan1 = ?, loan2 = ?, loan3 = ?, loan4 = ?, 
            tm_credit1 = ?, tm_credit2 = ?, nt_credit1 = ?, nt_credit2 = ? WHERE email = ?''',
                           (loan_charge, withdrawal_charge, loan_interest, minimum_shares, unit_shares, loan1,
                            loan2, loan3, loan4, tm_credit1, tm_credit2, nt_credit1, nt_credit2, email))

            # Commit the changes and close the connection
            conn.commit()
            conn.close()

        return redirect(url_for("admin_dashboard"))


@app.route("/process_change_password", methods=["GET", "POST"])
def process_change_password():
    if request.method == "POST":
        if "email" in session:
            email = session["email"]
            password = session["password"]
            current = request.form["password"]
            new_password = request.form["newpassword"]
            confirm_password = request.form["renewpassword"]

            if new_password == confirm_password and current == password:
                conn = sqlite3.connect("app.db")
                cursor = conn.cursor()
                cursor.execute("UPDATE admin_credentials SET password = ? WHERE email = ?", (new_password, email))
                conn.commit()
                conn.close()
                session.clear()
                session.pop("email", None)
                return redirect(url_for("login"))

            elif new_password != confirm_password:
                flash("Passwords do not match.")
                message = "Passwords do not match."
                return redirect(url_for("admin_dashboard", message=message))

            elif current != password:
                flash("Current password is incorrect.")
                message = "Current password is incorrect."
                return redirect(url_for("admin_dashboard", messag=message))

            else:
                return redirect(url_for("login"))


@app.route("/process_member_registration", methods=["GET", "POST"])
def process_member_registration():
    if request.method == "POST":
        # If the user is already logged in, retrieve their data from the session
        if 'email' in session:
            #  get data from form filled.
            member_name = request.form.get("fullname").title()
            member_email = request.form.get("email")
            title = request.form.get("title").title()
            name_with_title = title + ' ' + member_name
            staff_id = request.form.get("staff_id")
            category = request.form.get("category").title()
            dob = request.form.get("dob")
            gender = request.form.get("gridRadios")
            monthly_contribution = request.form.get("monthly_contribution")
            bank_name = request.form.get("bank").upper()
            account_num = request.form.get("accountNumber")
            account_name = request.form.get("accountName").title()
            current_balance = 0
            total_loan = 0
            total_credit = 0
            total_debt = 0
            others = 0
            frozen_amount = 0
            monthly_deduction = 0
            passport = None
            image = request.files['passport']
            if image.filename != '':
                # Save the image to the server
                image_path = os.path.join('static', 'uploads', image.filename)
                image.save(image_path)
                passport = image.filename

            # update database with the data from the form.

            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            try:
                cursor.execute('''INSERT INTO members_details (staff_id, name, email, category, passport, 
                date_of_birth, gender, monthly_contribution, bank_name, account_num, account_name, current_balance, 
                total_loan_collected, total_credit_purchase, total_debt, others, frozen_amount, monthly_deduction) 
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (staff_id, name_with_title,
                                                                                  member_email,
                                                                                  category, passport, dob, gender,
                                                                                  monthly_contribution,
                                                                                  bank_name, account_num, account_name,
                                                                                  current_balance, total_loan,
                                                                                  total_credit,
                                                                                  total_debt, others, frozen_amount,
                                                                                  monthly_deduction))
                conn.commit()
                conn.close()

                message = "success"
                flash(f"Successfully Registered {member_name}")
                return redirect(url_for("register_members", message=message))
            except sqlite3.IntegrityError:
                message = "error"
                flash(f"ERROR: User with ID Number {staff_id} already exist.")
                return redirect(url_for("register_members", message=message))


@app.route("/Members_registration")
def register_members():
    # If the user is already logged in, retrieve their data from the session
    if 'email' in session:
        name = session['name']
        return render_template("members_registration.html", name=name)


@app.route("/edit_member details")
def edit_member_details():
    if "email" in session:
        name = session["name"]
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT name, monthly_contribution, bank_name, account_num, account_name 
        FROM members_details''')
        data = cursor.fetchall()
        names = []
        for row in data:
            member = row[0]
            names.append(member)
        return render_template('edit_member_detail.html', name=name, names=names)


@app.route("/process edit members", methods=["GET", "POST"])
def process_edit_member():
    if request.method == "POST":
        name = request.form["staffName"]
        new_name = request.form["new_name"].title()
        new_title = request.form["new_title"].title()
        new_category = request.form["new_category"]
        dob = request.form.get("dob")
        current_balance = request.form["current_balance"]
        new_monthly_contribution = request.form["new_monthly_contribution"]
        new_bank = request.form["new_bank"]
        new_account_num = request.form["new_accountNumber"]
        new_account_name = request.form["new_accountName"]
        new_fullname = new_title + " " + new_name
        passport = None
        image = request.files['passport']
        if image.filename != '':
            # Save the image to the server
            image_path = os.path.join('static', 'uploads', image.filename)
            image.save(image_path)
            passport = image.filename

        # Add data to database update member record.

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''UPDATE members_details SET name = ?, category = ?, date_of_birth = ?, 
        monthly_contribution = ?, current_balance = ?, passport = ?, bank_name = ?, 
        account_num = ?, account_name = ? WHERE name = ?''', (new_fullname, new_category, dob, new_monthly_contribution,
                                                              current_balance, passport, new_bank, new_account_num,
                                                              new_account_name, name))
        conn.commit()
        conn.close()
        flash(f"{name} updated Successfully to {new_fullname}")
        return redirect(url_for('edit_member_details'))


@app.route("/Members_details")
def members_details():
    # If the user is already logged in, retrieve their data from the session
    if 'email' in session:
        name = session['name']
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT staff_id, name, email, category, monthly_contribution FROM members_details ORDER BY 
        staff_id ASC''')
        table_data = cursor.fetchall()
        conn.close()
        return render_template("members_details.html", name=name, data=table_data)


@app.route("/process_profile/<member_name>")
def process_profile(member_name):
    session["profile_name"] = member_name
    return redirect(url_for('member_profile'))


@app.route("/member_profile")
def member_profile():
    if 'email' in session:
        name = session["name"]
        user = session["profile_name"]

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM members_details WHERE name = ?''', (user,))
        data = cursor.fetchone()
        cursor.execute('''SELECT units_of_shares FROM shares WHERE staff_name = ?''', (user,))
        unit_of_shares = cursor.fetchone()
        shares = 0
        for units in unit_of_shares:
            current_shares = shares + int(units)
        if data:
            passport = get_profile_picture()
            return render_template("member_profile.html", name=name, user_name=user, passport=passport, data=data,
                                   shares=current_shares)
        else:
            message = "None"
            return render_template("member_profile.html", name=name, user_name=user, message=message)


@app.route("/add to inventory")
def add_to_inventory():
    if 'email' in session:
        name = session["name"]
        return render_template("add_to_inventory.html", name=name)


@app.route("/process_add_to_inventory", methods=["GET", "POST"])
def process_add_to_inventory():
    if request.method == "POST":
        item_name = request.form["item_name"].title()
        bulk_price = request.form["bulk_price"]
        bulk_quantity = request.form["bulk_quantity"]
        unit_price = request.form["unit_price"]
        unit_quantity = request.form["unit_quantity"]
        units = int(unit_quantity) * int(bulk_quantity)

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO inventory (item_name, bulk_price, bulk_quantity, unit_price, unit_quantity) 
        VALUES( ?, ?, ?, ?, ?)''', (item_name, bulk_price, bulk_quantity, unit_price, units))
        conn.commit()
        conn.close()
        flash(f"{item_name} was successfully added to your inventory.")
        return redirect(url_for('add_to_inventory'))


@app.route("/edit inventory")
def edit_inventory():
    if 'email' in session:
        name = session["name"]
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT item_name FROM inventory''')
        data = cursor.fetchall()
        conn.close()
        return render_template("edit_inventory.html", name=name, data=data)


@app.route("/process edit inventory", methods=["GET", "POST"])
def process_edit_inventory():
    if request.method == "POST":
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()

        item_name = request.form["item_name"]
        new_bulk_price = request.form["new_bulk_price"]
        new_bulk_quantity = request.form["new_bulk_quantity"]
        new_unit_price = request.form["new_unit_price"]
        new_unit_quantity = request.form["new_unit_quantity"]

        cursor.execute('''SELECT bulk_quantity, unit_price, unit_quantity FROM inventory WHERE item_name = ?''',
                       (item_name,))
        selected_item = cursor.fetchone()
        bulk_quantity = selected_item[0]
        unit_quantity = selected_item[1]
        bulk_quantity = int(bulk_quantity) + int(new_bulk_quantity)
        unit_quantity = int(unit_quantity) + (int(new_unit_quantity) * int(new_bulk_quantity))

        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''UPDATE inventory SET bulk_price = ?, bulk_quantity = ?, unit_price = ?, unit_quantity = ?
        WHERE item_name = ?''', (new_bulk_price, bulk_quantity, new_unit_price, unit_quantity, item_name))
        conn.commit()
        flash(f"{item_name} Successfully Updated.")
        return redirect(url_for('edit_inventory'))


@app.route("/transactions section")
def transactions():
    if 'email' in session:
        name = session["name"]
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM system_details WHERE name = ?''', (name,))
        data = cursor.fetchone()
        cursor.execute('''SELECT name From members_details''')
        names = cursor.fetchall()
        cursor.execute('''SELECT item_name FROM inventory''')
        data2 = cursor.fetchall()
        conn.close()
        loan_charge = data[2]
        withdrawal_charge = data[3]
        interest = data[4]
        unit_share = data[6]
        return render_template('transactions.html', name=name, loan_charge=loan_charge,
                               withdrawal_charge=withdrawal_charge,
                               interest=interest, unit_share=unit_share, names=names, data=data2)


@app.route("/make deposit", methods=["GET", "POST"])
def make_deposit():
    if request.method == "POST":
        get_current_date()
        staff_name = request.form["staffName"]
        amount = request.form["deposit_amount"]

        if staff_name.lower() != "choose staff name" and amount.isdigit():
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute('''SELECT current_balance FROM members_details WHERE name = ?''', (staff_name,))
            current_balance = int(cursor.fetchone()[0]) + int(amount)
            # current_balance = int(current_balance) + amount
            cursor.execute('''UPDATE members_details SET current_balance = ? WHERE name = ?''',
                           (current_balance, staff_name))
            conn.commit()
            conn.close()

            flash(f'Deposit Transaction Successful.\n {staff_name} Was Credited With {amount}.')
            return redirect(url_for('transactions'))
        else:
            flash(f'ERROR! Invalid Input.')
            return redirect(url_for('transactions'))


@app.route("/make withdrawal", methods=["GET", "POST"])
def make_withdrawal():
    if request.method == "POST":
        name = session["name"]
        staff_name = request.form["staffName"]
        amount = request.form["withdrawal_amount"]

        if staff_name.lower() != "choose staff name" and amount.isdigit():

            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute('''SELECT current_balance, frozen_amount FROM members_details WHERE name = ?''',
                           (staff_name,))
            data = cursor.fetchone()
            current_balance = int(data[0])
            frozen_amount = int(data[1])
            # if current_balance > (int(amount) + frozen_amount):
            #     cursor.execute('''SELECT withdrawal_charges FROM system_details WHERE name = ?''', (name,))
            #     withdrawal_charges = int(cursor.fetchone()[0])
            #     current_balance = current_balance - withdrawal_charges - int(amount)
            #     # current_balance = int(current_balance) + amount
            #     cursor.execute('''UPDATE members_details SET current_balance = ? WHERE name = ?''',
            #                    (current_balance, staff_name))
            #     conn.commit()
            #     conn.close()
            #
            #     flash(f'Withdrawal Transaction Successful.\n {staff_name} Was Debited With NGN{amount}. '
            #           f'NGN{withdrawal_charges}'
            #           f' Transaction charge was deducted from the account')
            #     return redirect(url_for('transactions'))
            # else:
            #     flash(f"Transaction Failed.\n {staff_name}'s Current Balance is NGN{current_balance}.")
            #     return redirect(url_for('transactions'))
            cursor.execute('''SELECT withdrawal_charges FROM system_details WHERE name = ?''', (name,))
            withdrawal_charges = int(cursor.fetchone()[0])
            current_balance = current_balance - withdrawal_charges - int(amount)
            # current_balance = int(current_balance) + amount
            cursor.execute('''UPDATE members_details SET current_balance = ? WHERE name = ?''',
                           (current_balance, staff_name))
            conn.commit()
            conn.close()

            flash(f'Withdrawal Transaction Successful.\n {staff_name} Was Debited With NGN{amount}. '
                  f'NGN{withdrawal_charges}'
                  f' Transaction charge was deducted from the account')
            return redirect(url_for('transactions'))
        else:
            flash(f'ERROR! Invalid Input.')
            return redirect(url_for('transactions'))


@app.route("/process cart", methods=["GET", "POST"])
def process_shopping_cart():
    # update the members details database
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE members_details SET monthly_deduction = 0, others = 0 ''')
    conn.commit()

    if request.method == "POST":
        if 'add_to_cart' in request.form:
            staff_name = session["profile_name"]
            item = request.form["item"]
            item_type = request.form["item_type"].lower()
            purchase_type = request.form["purchase_type"]
            quantity = request.form["quantity"]

            if (item.lower != "select item" and item_type.lower() != "select item type" and
                    purchase_type.lower() != "select purchase type" and quantity.isdigit()):
                # get item details from db
                conn = sqlite3.connect("app.db")
                cursor = conn.cursor()
                cursor.execute('''SELECT * FROM inventory WHERE item_name = ?''', (item,))
                item_details = cursor.fetchone()
                bulk_price = int(item_details[1])
                # bulk_quantity = int(item_details[2])
                unit_price = int(item_details[3])
                # unit_quantity = int(item_details[4])
                ref_num = generate_reference_id()

                if item_type == "bulk":
                    item_price = bulk_price
                    total_price = item_price * int(quantity)

                else:
                    item_price = unit_price
                    total_price = item_price * int(quantity)

                cursor.execute('''INSERT INTO shopping_cart (ref_num, staff_name, item_name, item_type, 
                item_price, item_quantity, item_total_price, purchase_type) VALUES(?, ?, ?, ?, ?, ?, ?, ?)''',
                               (ref_num, staff_name, item, item_type, item_price,
                                quantity, total_price, purchase_type))
                conn.commit()
                flash(f'{item} Was Successful Added To Your Cart')
                return redirect(url_for('shopping_cart'))
            else:
                flash('ERROR! Ensure All Entries Are Entered Correctly.')
                return redirect(url_for('shopping_cart'))

        elif 'checkout' in request.form:
            if 'email' in session:
                name = session["name"]
                user = session["profile_name"]
                conn = sqlite3.connect("app.db")
                cursor = conn.cursor()
                cursor.execute('''SELECT staff_id, email, category FROM members_details WHERE name = ?''', (user,))
                data1 = cursor.fetchone()
                staff_id = data1[0]
                email = data1[1]
                category = data1[2]
                cursor.execute('''SELECT * FROM shopping_cart WHERE staff_name = ?''', (user,))
                data = cursor.fetchall()

                total_credit_purchase = 0
                total_cash_purchase = 0
                total_purchase = 0
                for rows in data:
                    if rows[1] == user:
                        if rows[7] == "Credit":
                            total_credit_purchase = total_credit_purchase + int(rows[6])
                            total_purchase = total_purchase + int(rows[6])
                        else:
                            total_cash_purchase = total_cash_purchase + int(rows[6])
                            total_purchase = total_purchase + int(rows[6])
                if data:
                    passport = get_profile_picture()
                    return render_template("checkout.html", name=name, user_name=user, passport=passport, data=data,
                                           total_purchase=total_purchase, total_cash_purchase=total_cash_purchase,
                                           total_credit_purchase=total_credit_purchase, staff_id=staff_id, email=email,
                                           category=category)
                else:
                    passport = get_profile_picture()
                    return render_template("checkout.html", name=name, user_name=user, passport=passport, data=data,
                                           total_purchase=total_purchase, total_cash_purchase=total_cash_purchase,
                                           total_credit_purchase=total_credit_purchase, staff_id=staff_id, email=email,
                                           category=category)

        elif 'proceed' in request.form:
            if 'email' in session:
                name = session["name"]
                user = session["profile_name"]
                conn = sqlite3.connect("app.db")
                cursor = conn.cursor()
                cursor.execute('''SELECT * FROM shopping_cart WHERE staff_name = ?''', (user,))
                data = cursor.fetchall()

                total_credit_purchase = 0
                total_cash_purchase = 0
                total_purchase = 0
                for rows in data:
                    if rows[1] == user:
                        if rows[7] == "Credit":
                            total_credit_purchase = total_credit_purchase + int(rows[6])
                            total_purchase = total_purchase + int(rows[6])
                        else:
                            total_cash_purchase = total_cash_purchase + int(rows[6])
                            total_purchase = total_purchase + int(rows[6])

                # check staff category and decide monthly deduction based on the duration.
                conn = sqlite3.connect("app.db")
                cursor = conn.cursor()
                cursor.execute('''SELECT total_credit_purchase, total_debt, category, monthly_deduction 
                FROM members_details WHERE name = ?''', (user,))
                responses = cursor.fetchone()
                credit = responses[0]
                debt = responses[1]
                category = str(responses[2])

                credit_purchase = credit + total_credit_purchase
                total_debt = debt + total_credit_purchase
                cursor.execute('''SELECT tm_credit1, tm_credit2, nt_credit1, nt_credit2 FROM system_details 
                WHERE name = ?''', (name,))
                details = cursor.fetchone()

                deduction = 0
                if category.lower() == "non teaching" and total_credit_purchase <= 50000:
                    duration = int(details[2])
                    deduction = round(total_credit_purchase / duration)

                elif category.lower() == "non teaching" and total_credit_purchase > 50000:
                    duration = int(details[3])
                    deduction = round(total_credit_purchase / duration)

                elif ((category.lower() == "teaching" or category.lower() == "management") and
                      total_credit_purchase <= 50000):
                    duration = int(details[0])
                    deduction = round(total_credit_purchase / duration)

                elif ((category.lower() == "teaching" or category.lower() == "management") and
                      total_credit_purchase > 50000):
                    duration = int(details[1])
                    deduction = round(total_credit_purchase / duration)

                cursor.execute("UPDATE members_details SET total_credit_purchase = ?, total_debt = ?"
                               "WHERE name = ?", (credit_purchase, total_debt, user))
                ref_code = generate_reference_id()
                conn.commit()

                cursor.execute('''INSERT INTO credit_purchase(staff_name, reference_code, credit_amount, 
                monthly_credit_deduction) VALUES(?, ?, ?, ?)''', (user, ref_code, total_credit_purchase,
                                                                  deduction))
                conn.commit()

                cursor.execute('''DELETE FROM credit_purchase WHERE credit_amount <= 0''')
                conn.commit()

                cursor.execute("DELETE FROM shopping_cart WHERE staff_name = ?", (user,))
                conn.commit()
                conn.close()
                return redirect(url_for('member_profile'))

        else:
            if 'profile_name' in session:
                user = session['profile_name']
                conn = sqlite3.connect("app.db")
                cursor = conn.cursor()
                cursor.execute('''DELETE FROM shopping_cart WHERE staff_name = ?''', (user,))
                conn.commit()
                flash(f"{user}'s Shopping Cart Has been Emptied")
                return redirect(url_for('shopping_cart'))
            else:
                flash('Ensure All Entries Are Correct')
                return redirect(url_for('shopping_cart'))
    else:
        if 'email' in session:
            name = session["name"]
            user = session["profile_name"]
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute('''SELECT staff_id, email, category FROM members_details WHERE name = ?''', (user,))
            data1 = cursor.fetchone()
            staff_id = data1[0]
            email = data1[1]
            category = data1[2]
            cursor.execute('''SELECT * FROM shopping_cart WHERE staff_name = ?''', (user,))
            data = cursor.fetchall()

            total_credit_purchase = 0
            total_cash_purchase = 0
            total_purchase = 0
            for rows in data:
                if rows[1] == user:
                    if rows[7] == "Credit":
                        total_credit_purchase = total_credit_purchase + int(rows[6])
                        total_purchase = total_purchase + int(rows[6])
                    else:
                        total_cash_purchase = total_cash_purchase + int(rows[6])
                        total_purchase = total_purchase + int(rows[6])
            if data:
                passport = get_profile_picture()
                return render_template("checkout.html", name=name, user_name=user, passport=passport, data=data,
                                       total_purchase=total_purchase, total_cash_purchase=total_cash_purchase,
                                       total_credit_purchase=total_credit_purchase, staff_id=staff_id, email=email,
                                       category=category)
            else:
                passport = get_profile_picture()
                return render_template("checkout.html", name=name, user_name=user, passport=passport, data=data,
                                       total_purchase=total_purchase, total_cash_purchase=total_cash_purchase,
                                       total_credit_purchase=total_credit_purchase, staff_id=staff_id, email=email,
                                       category=category)


@app.route("/catch details", methods=["GET", "POST"])
def catch_details():
    if 'email' in session:
        customer_name = request.form["staffName"]
        if customer_name.lower() != "choose staff name":
            session["profile_name"] = customer_name
            return redirect(url_for('shopping_cart'))
        else:
            flash("Please Select A Valid Name To Continue Shopping.")
            return redirect(url_for('transactions'))


@app.route("/delete item/<ref_num>", methods=["GET", "POST"])
def delete_item(ref_num):
    if 'email' in session:
        user = session["profile_name"]
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''DELETE FROM shopping_cart WHERE staff_name = ? AND ref_num = ?''', (user, ref_num))
        conn.commit()

        return redirect(url_for('process_shopping_cart'))


@app.route("/shopping")
def shopping_cart():
    if 'email' in session:
        name = session["name"]
        customer_name = session["profile_name"]
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT item_name FROM inventory''')
        data2 = cursor.fetchall()
        cursor.execute('''SELECT name From members_details''')
        names = cursor.fetchall()
        conn.close()
        return render_template('shopping.html', name=name, names=names, customer_name=customer_name, data=data2)


@app.route("/get loan", methods=["GET", "POST"])
def get_loan():
    if request.method == "POST":
        name = session["name"]
        staff_name = request.form["staff_name"]
        loan_amount = request.form["loan_amount"]
        guarantor1 = request.form["guarantor1"]
        guarantor2 = request.form["guarantor2"]
        if staff_name.lower() == "choose staff name":
            flash('Please Select A Valid Staff Name.')
            return redirect(url_for('transactions'))
        if not loan_amount.isdigit():
            flash('Enter Valid Loan Amount.')
            return redirect(url_for('transactions'))
        if not guarantor1.isdigit():
            flash('Enter Valid Guarantor-1 ID Number.')
            return redirect(url_for('transactions'))
        if not guarantor2.isdigit():
            flash('Enter Valid Guarantor-2 ID Number.')
            return redirect(url_for('transactions'))
        if guarantor1 == guarantor2:
            flash('Your Guarantors Must Not Be The Same')
            return redirect(url_for('transactions'))
        else:
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            # getting details for guarantor 1
            cursor.execute('''SELECT name, current_balance, frozen_amount FROM members_details WHERE staff_id = ?''',
                           (guarantor1,))
            data1 = cursor.fetchone()
            guarantor1_name = data1[0]
            guarantor1_current_balance = data1[1]

            # get guarantor_1 shares details
            cursor.execute('''SELECT total_shares FROM shares WHERE staff_name = ?''', (guarantor1_name,))
            shares_details = cursor.fetchall()
            total_shares_1 = 0
            if shares_details:
                for shares in shares_details:
                    total_shares_1 = int(total_shares_1) + int(shares[0])

            # getting details for guarantor 2
            cursor.execute('''SELECT name, current_balance, frozen_amount FROM members_details WHERE staff_id = ?''',
                           (guarantor2,))
            data2 = cursor.fetchone()
            guarantor2_name = data2[0]
            guarantor2_current_balance = data2[1]

            # get guarantor_2 shares details
            cursor.execute('''SELECT total_shares FROM shares WHERE staff_name = ?''', (guarantor2_name,))
            shares_details = cursor.fetchall()
            total_shares_2 = 0
            if shares_details:
                for shares in shares_details:
                    total_shares_2 = int(total_shares_2) + int(shares[0])

            # getting details for staff collecting the loan.
            cursor.execute('''SELECT staff_id, category, email FROM members_details WHERE name = ?''', (staff_name,))
            data3 = cursor.fetchone()
            staff_id = data3[0]
            category = data3[1]
            email = data3[2]

            # get loan charges and interest rate:
            cursor.execute('''SELECT loan_charges, loan_interest_rate FROM system_details WHERE name = ?''', (name,))
            data4 = cursor.fetchone()
            charges = data4[0]
            interest = data4[1]

            interest_on_loan = int(interest) / 100 * int(loan_amount)
            total_loan_amount = interest_on_loan + int(loan_amount)

            # check if member is eligible for the loan
            if int(guarantor1_current_balance) + total_shares_1 >= int(total_loan_amount) / 2 and \
                    int(guarantor2_current_balance) + total_shares_2 >= int(total_loan_amount) / 2:
                data = [staff_id, category, email, loan_amount, guarantor1_name, guarantor2_name, charges, interest,
                        interest_on_loan, total_loan_amount]
                for_session = [staff_name, loan_amount, guarantor1_name, guarantor2_name, charges, interest_on_loan,
                               total_loan_amount, total_shares_1, total_shares_2]
                session["data"] = for_session
                session["profile_name"] = staff_name
                passport = get_profile_picture()
                return render_template("loan_summary.html", name=name, user_name=staff_name,
                                       passport=passport, data=data)

            else:
                flash('Loan Not Approved')
                return redirect(url_for('transactions'))


@app.route("/process_get_loan", methods=["GET", "POST"])
def complete_get_loan():
    if request.method == "POST":
        name = session["name"]
        data = session["data"]
        staff_name = data[0]
        loan_amount = int(data[1])
        guarantor1_name = data[2]
        guarantor2_name = data[3]
        charges = int(data[4])
        total_loan_amount = int(data[6])
        total_shares_1 = int(data[7])
        total_shares_2 = int(data[8])

        # getting details for guarantor 2
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT frozen_amount FROM members_details WHERE name = ?''', (guarantor1_name,))
        data1 = cursor.fetchone()
        frozen_amount = int(data1[0])

        if total_shares_1 >= int(total_loan_amount) / 2:
            new_frozen_amount = frozen_amount + 0
        else:
            new_frozen_amount = frozen_amount + ((int(total_loan_amount) / 2) - total_shares_1)

        # update guarantor 1 details
        cursor.execute('''UPDATE members_details SET frozen_amount = ? WHERE name = ?''',
                       (new_frozen_amount, guarantor1_name))
        conn.commit()

        # getting details for guarantor 2
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT frozen_amount FROM members_details WHERE name = ?''', (guarantor2_name,))
        data2 = cursor.fetchone()
        frozen_amount = int(data2[0])
        if total_shares_2 >= int(total_loan_amount) / 2:
            new_frozen_amount = frozen_amount + 0
        else:
            new_frozen_amount = frozen_amount + ((int(total_loan_amount) / 2) - total_shares_2)

        # update guarantor 2 details
        cursor.execute('''UPDATE members_details SET frozen_amount = ? WHERE name = ?''',
                       (new_frozen_amount, guarantor2_name))
        conn.commit()

        # update the loan collector details.
        conn = sqlite3.connect("app.db")
        cursor = conn.cursor()
        cursor.execute('''SELECT category, total_loan_collected, total_debt, current_balance FROM members_details 
                WHERE name = ?''', (staff_name,))
        data3 = cursor.fetchone()
        staff_total_loan_collected = int(data3[1])
        total_debt = int(data3[2])
        current_balance = int(data3[3])

        # update the loan collector details in members_details.
        staff_total_loan_collected = staff_total_loan_collected + total_loan_amount
        total_debt = total_debt + total_loan_amount
        current_balance = current_balance - charges
        cursor.execute('''UPDATE members_details SET total_loan_collected = ?, total_debt = ?, current_balance = ?
                WHERE name = ?''', (staff_total_loan_collected, total_debt, current_balance, staff_name))
        conn.commit()

        # getting values for duration from system_details table
        cursor.execute('''SELECT loan1, loan2, loan3, loan4 FROM system_details WHERE name = ?''', (name,))
        data4 = cursor.fetchone()
        if loan_amount <= 100000:
            duration = int(data4[0])
        elif loan_amount <= 300000:
            duration = int(data4[1])
        elif loan_amount <= 500000:
            duration = int(data4[2])
        else:
            duration = int(data4[3])

        # update the loan table
        monthly_deduction = total_loan_amount / duration
        ref_num = generate_reference_id()
        date = get_current_date()

        # insert details into the loan table in database
        cursor.execute('''INSERT INTO loan(ref_num, name, date, loan_amount, monthly_deduction, guarantor_1, 
        guarantor_2) VALUES(?, ?, ?, ?, ?, ?, ?)''', (ref_num, staff_name, date, total_loan_amount,
                                                      monthly_deduction, guarantor1_name, guarantor2_name))
        conn.commit()

        flash('Your Loan Transaction Was Completed Successfully.')
        return redirect(url_for('transactions'))


@app.route("/buy shares", methods=["GET", "POST"])
def buy_shares():
    if request.method == "POST":
        name = session["name"]
        get_current_date()
        staff_name = request.form["staff_name"]
        units_of_shares = request.form["units"]
        ref_num = generate_reference_id()

        if staff_name.lower() != "choose staff name" and units_of_shares.isdigit():
            conn = sqlite3.connect("app.db")
            cursor = conn.cursor()
            cursor.execute('''SELECT minimum_shares, amount_per_unit_share FROM system_details WHERE name = ?''',
                           (name,))
            data = cursor.fetchone()
            minimum_shares = int(data[0])
            amount_per_unit_shares = int(data[1])
            if int(units_of_shares) >= minimum_shares:
                total_shares = amount_per_unit_shares * int(units_of_shares)
                cursor.execute('''INSERT INTO shares(ref_num, staff_name, units_of_shares, total_shares) 
                VALUES(?, ?, ?, ?)''', (ref_num, staff_name, units_of_shares, total_shares))
                conn.commit()
                flash(f'{staff_name} Has Successfully Purchased {units_of_shares} Shares worth {total_shares}')
                return redirect(url_for('transactions'))
            else:
                flash(f'Dear {staff_name}, Your Transaction Failed. Ensure Entries Are Correct. '
                      f'NOTE: Minimum Shares of {minimum_shares} and Above')
                return redirect(url_for('transactions'))
        else:
            flash('ERROR! Ensure Entries Are Correct')
            return redirect(url_for('transactions'))


@app.route("/contribution")
def contribution():
    name = session["name"]
    date = get_current_date()
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT staff_id, name, category, email FROM members_details''')
    data = cursor.fetchall()
    conn.close()
    return render_template('contribution.html', name=name, date=date, data=data)


@app.route('/process_contribution', methods=['GET', 'POST'])
def process_contribution():
    contribution_name = request.form.get('name')
    contribution_amount = request.form.get('amount')
    start_date = request.form.get('start')
    end_date = request.form.get('dob')
    date_created = get_current_date()
    selected_members_json = request.form.get('selectedMembers')
    selected_members = json.loads(selected_members_json)

    for name in selected_members:
        print(name)
        ref_num = generate_reference_id()
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        columns = "ref_num, contribution_name, name, amount, start, end, total_contributed"
        insert_into_table = f'INSERT INTO contribution({columns}) VALUES(?, ?, ?, ?, ?, ?, ?)'
        cursor.execute(insert_into_table, (ref_num, contribution_name, name, contribution_amount, start_date, end_date,
                                           contribution_amount))
        conn.commit()

    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO contribution_list(name, date_created) VALUES(?, ?)''', (contribution_name,
                                                                                          date_created))
    conn.commit()
    conn.close()
    flash('Contribution Created Successfully.')
    return redirect(url_for('contribution'))


@app.route('/delete_contribution')
def delete_contribution():
    name = session["name"]
    date = get_current_date()
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM contribution_list')
    data = cursor.fetchall()
    flash("You cannot undelete a Contribution once you delete it.")
    return render_template('delete_contribution.html', name=name, date=date, data=data)


@app.route('/process_delete', methods=["GET", "POST"])
def process_delete():
    if request.method == "POST":
        name = request.form["contribution_name"]
        agreement = request.form.get("checkbox")

        if agreement == 'on':
            conn = sqlite3.connect('app.db')
            cursor = conn.cursor()
            cursor.execute('''DELETE FROM contribution WHERE contribution_name = ?''', (name,))
            conn.commit()
            cursor.execute('''DELETE FROM contribution_list WHERE name = ?''', (name,))
            conn.commit()
        return redirect(url_for('contribution'))


@app.route('/generate_schedule')
def generate_schedule():
    if 'name' in session:
        name = session['name']
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT staff_id, name, monthly_contribution, total_loan_collected, total_credit_purchase, 
        others, monthly_deduction FROM members_details WHERE staff_id NOT IN (2, 37, 40, 67)''')
        data = cursor.fetchall()
        total_deduction = 0
        for item in data:
            total_deduction += int(item[6])
        date = get_current_date()
        year = date.year
        month = date.month
        current_date = f'{month}, {year}'
        with open('date.txt', 'r') as file:
            content = file.read()
        if current_date == f'{content.split(', ')[1]}, {content.split(',')[0]}':
            return render_template('schedule.html', name=name, date=current_date, data=data,
                                   total=round(total_deduction, 2))
        else:
            return render_template('update_schedule.html', name=name, date=current_date, data=data,
                                   total=round(total_deduction, 2))


@app.route('/process_generate_schedule', methods=["GET", "POST"])
def process_generate_schedule():
    if "generate_schedule" in request.form:
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT staff_id, name, monthly_contribution, total_loan_collected, total_credit_purchase, 
                others, monthly_deduction FROM members_details''')
        data = cursor.fetchall()
        total_deduction = 0
        for item in data:
            total_deduction += int(item[6])
        return redirect(url_for('generate_schedule'))

    elif "update" in request.form:
        with open('date.txt', 'w') as file:
            file.write(f'{get_current_date().year}, {get_current_date().month}')

        # update the members details database
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute('''UPDATE members_details SET monthly_deduction = 0, others = 0 ''')
        conn.commit()

        # get current details from members details table
        cursor.execute('''SELECT name, monthly_contribution, current_balance, monthly_deduction FROM members_details''')
        response = cursor.fetchall()
        for data in response:
            name = data[0]
            current_balance = int(data[1]) + int(data[2])
            monthly_deduction = int(data[3]) + int(data[1])

            # update the members details database
            cursor.execute('''UPDATE members_details SET current_balance = ?, monthly_deduction = ? WHERE name = ?''',
                           (current_balance,
                            monthly_deduction,
                            name))
            conn.commit()

        # get current details from loan table
        cursor.execute('''SELECT * FROM loan''')
        response_1 = cursor.fetchall()
        for rows in response_1:
            ref_num = rows[0]
            staff_name = rows[1]
            loan = int(rows[3])
            deduction = int(rows[4])

            if loan <= deduction:
                deduction = loan
                loan = 0
                # get current details from members details table
                cursor.execute('''SELECT monthly_contribution, current_balance, total_loan_collected,
                total_credit_purchase, total_debt, others, monthly_deduction FROM members_details WHERE name = ?''',
                               (staff_name,))
                response_2 = cursor.fetchone()
                total_loan_collected = int(response_2[2]) - deduction
                total_debt = int(response_2[4], ) - deduction
                monthly_deduction = int(response_2[6]) + deduction

                # update the members details database
                cursor.execute('''UPDATE members_details SET total_loan_collected = ?, total_debt = ?, 
                monthly_deduction = ? WHERE name = ?''', (total_loan_collected,
                                                          total_debt, monthly_deduction, staff_name))
                conn.commit()

                # update the loan database
                cursor.execute('''UPDATE loan SET loan_amount = ?, monthly_deduction = ? WHERE ref_num = ?''',
                               (loan, deduction, ref_num))
                conn.commit()
            else:
                loan = loan - deduction
                # get current details from members details table
                cursor.execute('''SELECT monthly_contribution, current_balance, total_loan_collected,
                total_credit_purchase, total_debt, others, monthly_deduction FROM members_details WHERE
                name = ?''', (staff_name,))
                response_2 = cursor.fetchone()
                total_loan_collected = int(response_2[2]) - deduction
                total_debt = int(response_2[4], ) - deduction
                monthly_deduction = int(response_2[6]) + deduction

                # update the members details database
                cursor.execute('''UPDATE members_details SET total_loan_collected = ?, total_debt = ?, 
                monthly_deduction = ? WHERE name = ?''', (total_loan_collected,
                                                          total_debt, monthly_deduction, staff_name))
                conn.commit()

                # update the loan database
                cursor.execute('''UPDATE loan SET loan_amount = ?, monthly_deduction = ? WHERE ref_num = ?''',
                               (loan, deduction, ref_num))
                conn.commit()

        # get current details from credit purchase table
        cursor.execute('''SELECT * FROM credit_purchase''')
        response_3 = cursor.fetchall()
        for items in response_3:
            ref_num = items[1]
            staff_name = items[0]
            credit_amount = int(items[2])
            monthly_credit_deduction = int(items[3])

            if credit_amount <= monthly_credit_deduction:
                monthly_credit_deduction = credit_amount
                credit_amount = 0
                # get current details from members details table
                cursor.execute('''SELECT total_credit_purchase, total_debt, others, monthly_deduction 
                        FROM members_details WHERE name = ?''',
                               (staff_name,))
                response_2 = cursor.fetchone()
                total_credit_purchase = int(response_2[0]) - monthly_credit_deduction
                total_debt = int(response_2[1], ) - monthly_credit_deduction
                monthly_deduction = int(response_2[3]) + monthly_credit_deduction

                # update the members details database
                cursor.execute('''UPDATE members_details SET total_credit_purchase = ?,
                        total_debt = ?, monthly_deduction = ? WHERE name = ?''', (total_credit_purchase,
                                                                                  total_debt, monthly_deduction,
                                                                                  staff_name))
                conn.commit()

                # update the credit purchase database
                cursor.execute('''UPDATE credit_purchase SET credit_amount = ?, 
                        monthly_credit_deduction = ? WHERE reference_code = ?''',
                               (credit_amount, monthly_credit_deduction, ref_num))
                conn.commit()
            else:
                credit_amount = credit_amount - monthly_credit_deduction
                # get current details from members details table
                cursor.execute('''SELECT total_credit_purchase, total_debt, others, monthly_deduction 
                FROM members_details WHERE name = ?''', (staff_name,))
                response_2 = cursor.fetchone()
                total_credit_purchase = int(response_2[0]) - monthly_credit_deduction
                total_debt = int(response_2[1], ) - monthly_credit_deduction
                monthly_deduction = int(response_2[3]) + monthly_credit_deduction

                # update the members details database
                cursor.execute('''UPDATE members_details SET total_credit_purchase = ?, total_debt = ?, 
                monthly_deduction = ? WHERE name = ?''', (total_credit_purchase, total_debt,
                                                          monthly_deduction, staff_name))
                conn.commit()

                # update the credit purchase database
                cursor.execute('''UPDATE credit_purchase SET credit_amount = ?, monthly_credit_deduction = ? 
                WHERE reference_code = ?''', (credit_amount, monthly_credit_deduction, ref_num))
                conn.commit()

        # get current details from contribution table
        cursor.execute('''SELECT * FROM contribution''')
        response_4 = cursor.fetchall()
        for report in response_4:
            year = int(get_current_date().year)
            month = int(get_current_date().month)
            end_date = str(report[5]).split("-")
            end_year = int(end_date[0])
            end_month = int(end_date[1])
            ref_num = report[0]
            staff_name = report[2]

            if year <= end_year and month <= end_month:
                total_contribution = int(report[6]) + int(report[3])
                amount = int(report[3])

                # get current details from members details table
                cursor.execute('''SELECT others, monthly_deduction FROM members_details WHERE name = ?''',
                               (staff_name,))
                response_2 = cursor.fetchone()
                others = int(response_2[0]) + amount
                monthly_deduction = int(response_2[1]) + amount

                # update the members details database
                cursor.execute('''UPDATE members_details SET others = ?, monthly_deduction = ? WHERE name = ?''',
                               (others, monthly_deduction, staff_name))
                conn.commit()

                # update the credit purchase database
                cursor.execute('''UPDATE contribution SET total_contributed = ? WHERE ref_num = ?''',
                               (total_contribution, ref_num))
                conn.commit()

            else:
                # update the credit purchase database
                amount = 0
                cursor.execute('''UPDATE contribution SET amount = ? WHERE ref_num = ?''',
                               (amount, ref_num))
                conn.commit()

        cursor.execute('''DELETE FROM loan WHERE loan_amount <= 0''')
        conn.commit()

        cursor.execute('''DELETE FROM credit_purchase WHERE credit_amount <= 0''')
        conn.commit()

        cursor.execute('''DELETE FROM contribution WHERE amount <= 0''')
        conn.commit()

        return redirect(url_for('generate_schedule'))


@app.route('/dividend')
def dividend():
    name = session["name"]
    date = get_current_date()
    conn = sqlite3.connect("app.db")
    cursor = conn.cursor()
    cursor.execute('''SELECT staff_id, name, category, email FROM members_details''')
    data = cursor.fetchall()
    cursor.execute('''SELECT units_of_shares FROM shares''')
    shares = cursor.fetchall()
    total_units = 0
    for item in shares:
        total_units += int(item[0])
        conn.close()
    return render_template('dividend.html', name=name, date=date, data=data, total_units=total_units)


@app.route('/process_dividend', methods=["GET", "POST"])
def process_dividend():
    if request.method == "POST":

        # create dividend table
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS dividend 
               (name TEXT, 
               units REAL, 
               amount REAL,
               date TEXT)''')
        conn.commit()
        units = 0
        amount = 0
        date = get_current_date()
        cursor.execute('''SELECT name FROM members_details''')
        names = cursor.fetchall()
        for name in names:
            name = name[0]
            cursor.execute('''INSERT INTO dividend(name, units, amount, date) VALUES(?, ?, ?, ?)''', (name,
                                                                                                      units, amount,
                                                                                                      date))
            conn.commit()

        # get data from form
        amount = float(request.form['dividend_amount'])

        # # get data to calculate premium
        cursor.execute('''SELECT units_of_shares FROM shares''')
        shares = cursor.fetchall()
        total_units = 0
        for item in shares:
            total_units += int(item[0])
        premium = amount / total_units

        cursor.execute('''select ref_num, staff_name, units_of_shares FROM shares''')
        response = cursor.fetchall()

        grand = [amount, total_units]
        session["grand"] = grand

        for rows in response:
            name = rows[1]
            units_of_shares = int(rows[2])
            shareholder_dividend = round(premium * units_of_shares, 2)
            cursor.execute('''SELECT units, amount FROM dividend WHERE name = ?''', (name,))
            item = cursor.fetchone()
            current_units = int(item[0])
            current_dividend = int(item[1])
            units_of_shares = units_of_shares + current_units
            shareholder_dividend = shareholder_dividend + current_dividend

            cursor.execute('''UPDATE dividend SET units = ?, amount = ? WHERE name = ? ''', (units_of_shares,
                                                                                             shareholder_dividend,
                                                                                             name))
            conn.commit()

    return redirect(url_for('share_dividend'))


@app.route('/share_dividend')
def share_dividend():
    if 'name' in session:
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT * FROM dividend''')
        data = cursor.fetchall()
        date = get_current_date()
        year = date.year
        grand = session['grand']
        cursor.execute('''DELETE FROM dividend WHERE date = ?''', (date,))
        conn.commit()
        return render_template('dividend_summary.html', data=data, date=year, grand=grand)


if __name__ == "__main__":
    opened = False
    threading.Timer(1, open_browser).start()
    app.run(host='127.0.0.1', port=5000, debug=True)
