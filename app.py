from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Database connection details
DB_HOST = '10.101.1.149'
DB_NAME = 'WEB_DEV'
DB_USER = 'postgres'  # Replace with your PostgreSQL username
DB_PASSWORD = 'bjir'  # Replace with your PostgreSQL password

def get_db_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    return conn
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch distinct department names
    cur.execute('SELECT DISTINCT departmentname FROM staging.vendor;')
    departments = cur.fetchall()
    
    # Fetch vendors
    cur.execute('SELECT id, departmentname, vendorname, email, kind, brandname, vendorname2 FROM staging.vendor;')
    vendors = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # Get the selected department from the query parameters
    selected_department = request.args.get('departmentname', 'All Departments')
    
    # Filter vendors by selected department if a department is selected
    if selected_department != 'All Departments':
        vendors = [vendor for vendor in vendors if vendor[1] == selected_department]
    
    return render_template('index.html', departments=departments, vendors=vendors, selected_department=selected_department)


@app.route('/add_vendor', methods=['GET', 'POST'])
def add_vendor():
    if request.method == 'POST':
        # Get form data
        departmentname = request.form['departmentname']
        vendorname = request.form['vendorname']
        email = request.form['email']
        kind = request.form['kind']
        brandname = request.form['brandname']
        vendorname2 = request.form['vendorname2']

        # Insert into database
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'INSERT INTO staging.vendor (departmentname, vendorname, email, kind, brandname, vendorname2)'
            'VALUES (%s, %s, %s, %s, %s, %s)',
            (departmentname, vendorname, email, kind, brandname, vendorname2)
        )
        conn.commit()
        cur.close()
        conn.close()

        flash('Vendor added successfully!', 'success')
        return redirect(url_for('index'))

    return render_template('add_vendor.html')


@app.route('/edit_vendor', methods=['GET', 'POST'])
def edit_vendor():
    vendorname = request.args.get('vendorname')  # Get vendor name from URL
    if not vendorname:
        return "Vendor name is required", 400  # Handle missing vendor name

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM staging.vendor WHERE vendorname = %s", (vendorname,))
    vendor = cursor.fetchone()

    print("Fetched vendor:", vendor)  # Debugging

    if not vendor:
        return "Vendor not found", 404  # Handle missing vendor

    if request.method == 'POST':
        departmentname = request.form['departmentname']
        email = request.form['email']
        kind = request.form['kind']
        brandname = request.form['brandname']
        vendorname2 = request.form['vendorname2']

        cursor.execute("""
            UPDATE staging.vendor
            SET departmentname = %s, email = %s, kind = %s, brandname = %s, vendorname2 = %s 
            WHERE vendorname = %s
        """, (departmentname, email, kind, brandname, vendorname2, vendorname))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('index'))

    cursor.close()
    conn.close()

    return render_template('edit_vendor.html', vendor=vendor)

if __name__ == '__main__':
    app.run(debug=True)
