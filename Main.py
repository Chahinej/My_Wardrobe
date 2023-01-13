from flask import Flask,render_template
import sqlite3
from flask_jwt_extended import JWTManager
from Auth import login_manager




app = Flask(__name__, template_folder='Templates')
login_manager.init_app(app)
app.config['JWT_SECRET_KEY'] = 'Web*Services1'
jwt = JWTManager(app)
def db_connection():
  conn = None
  try:
    conn = sqlite3.connect("wardrobe.sqlite")
  except sqlite3.Error as e:
    print(e)

  return conn


from Auth import Auth_bp
app.register_blueprint(Auth_bp, url_prefix='/api/Auth')

from mywardrobe import mywardrobe_bp
app.register_blueprint(mywardrobe_bp, url_prefix='/api/mywardrobe')



@app.route('/')
def index():
    return render_template('Menu.html')

if __name__ == "__main__" :
  app.run(port=80, debug=True)