from flask import Flask, render_template, request, redirect, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import MONGO_URI, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client['student_db']
collection = db['students']

# ---------- LOGIN ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin":
            session['user'] = username
            return redirect('/')
        else:
            flash("Invalid login")

    return render_template('login.html')

# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

# ---------- HOME ----------
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')

    students = list(collection.find())
    return render_template('index.html', students=students)

# ---------- ADD ----------
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student = {
            "name": request.form['name'],
            "email": request.form['email'],
            "course": request.form['course']
        }
        collection.insert_one(student)
        flash("Student added successfully")
        return redirect('/')

    return render_template('add.html')

# ---------- EDIT ----------
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_student(id):
    student = collection.find_one({"_id": ObjectId(id)})

    if request.method == 'POST':
        collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "name": request.form['name'],
                "email": request.form['email'],
                "course": request.form['course']
            }}
        )
        flash("Student updated")
        return redirect('/')

    return render_template('edit.html', student=student)

# ---------- DELETE ----------
@app.route('/delete/<id>')
def delete_student(id):
    collection.delete_one({"_id": ObjectId(id)})
    flash("Student deleted")
    return redirect('/')




@app.route('/search')
def search():
    if 'user' not in session:
        return redirect('/login')

    query = request.args.get('q')

    students = list(collection.find({
        "$or": [
            {"name": {"$regex": query, "$options": "i"}},
            {"email": {"$regex": query, "$options": "i"}},
            {"course": {"$regex": query, "$options": "i"}}
        ]
    }))

    return render_template('index.html', students=students)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    total_students = collection.count_documents({})
    courses = collection.distinct("course")

    data = {}
    for course in courses:
        data[course] = collection.count_documents({"course": course})

    return render_template('dashboard.html', total=total_students, data=data)




# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)
