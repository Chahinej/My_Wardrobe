
from flask import Blueprint, request, jsonify,render_template
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_login import  LoginManager
import sqlite3
from passlib.hash import pbkdf2_sha256


Auth_bp = Blueprint('Auth', __name__)
login_manager = LoginManager()

@login_manager.user_loader
def load_user(User_id):
    conn = db_connection()
    cursor = conn.cursor()

    
    sql = "SELECT * FROM User_Data WHERE id=?"
    cursor.execute(sql, (User_id,))
    result = cursor.fetchone()

    
    if result:
        return result
    return None

def db_connection():
  conn = None
  try:
    conn = sqlite3.connect("wardrobe.sqlite")
  except sqlite3.Error as e:
    print(e)

  return conn






@Auth_bp.route('/Users', methods=['GET'])
def Users_List():
  conn = db_connection()
  cursor = conn.cursor()
    
  if request.method == "GET":
    cursor = conn.execute("SELECT * FROM User_Data")
    User_Data = [
      dict(User_Id=row[0], Full_Name=row[1], Username=row[2], Email=row[3], Password=row[4])
      for row in cursor.fetchall()
    ]
    if User_Data is not None:
      return jsonify(User_Data)


@Auth_bp.route('/register', methods=['POST'])
def register():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        Full_Name=request.form["Full_Name"] 
        Username=request.form["Username"]
        Email=request.form["Email"]
        Password=request.form["Password"]
        
        sql = "SELECT * FROM User_Data WHERE Username=?"
        cursor.execute(sql, (Username,))
        result = cursor.fetchone()
        if result:
            return jsonify({"error": "Username already in use"}), 400
        
        sql = "SELECT * FROM User_Data WHERE Email=?"
        cursor.execute(sql, (Email,))
        result = cursor.fetchone()
        if result:
            return jsonify({"error": "Email already in use"}), 400

        sql = "SELECT * FROM User_Data WHERE Full_Name=?"
        cursor.execute(sql, (Full_Name,))
        result = cursor.fetchone()
        if result:
            return jsonify({"error": "Full name already in use"}), 400



        password_hashed = pbkdf2_sha256.hash(Password)

        sql = """INSERT INTO User_Data (Full_Name, Username, Email, Password) VALUES (?,?,?,?)"""
        cursor.execute(sql, (Full_Name,Username, Email, password_hashed))
        conn.commit()

        return  render_template('login.html')
    


@Auth_bp.route('/login', methods=["GET","POST"])
def login():
    conn = db_connection()
    cursor = conn.cursor()
    
    if request.method == "POST":
        Username=request.form["Username"]
        Password=request.form["Password"]

        cursor.execute("SELECT * FROM User_Data WHERE Username=?", (Username,))
        User_Data = cursor.fetchone()

        if User_Data is None:
            return "User does not exist", 404

        password_hashed = User_Data[4]
        if pbkdf2_sha256.verify(Password, password_hashed):
            access_token = create_access_token(identity=Username)
            response = jsonify({'access_token': access_token, 'expiration_time': 3000, 'Username' : Username})
            response.set_cookie('access_token', access_token, max_age=3000)
            return render_template('my_outfit.html')

@Auth_bp.route('/logout')
def logout():
    response = jsonify({'message': 'Successfully logged out'})
    response.set_cookie('access_token', '', expires=0)
    return render_template('Login.html')        
  
@Auth_bp.route('/protected', methods=['GET'])
@jwt_required
def protected():
    current_user = get_jwt_identity()
    return jsonify({'logged_in_as': current_user}), 200


@Auth_bp.route("/Register_Form")
def registration():
  return render_template("Register.html")


@Auth_bp.route("/Login_Form")
def User_login():
  return render_template("Login.html")

@Auth_bp.route('/Dashboard')
def dashboard():
    access_token = request.args.get('access_token')
    expiration_time = request.args.get('expiration_time')
    Username = request.args.get('Username')
    if access_token or expiration_time:
        return jsonify({'message': 'Missing required query parameters'}), 400
    
    return render_template('my_outfit.html', access_token=access_token, expiration_time=expiration_time, Username=Username)