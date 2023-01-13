
from flask import  Blueprint, request, jsonify,render_template
import requests, sqlite3



mywardrobe_bp = Blueprint('mywardrobe', __name__)




def db_connection():
  conn = None
  try:
    conn = sqlite3.connect("wardrobe.sqlite")
  except sqlite3.Error as e:
    print(e)

  return conn


@mywardrobe_bp.route('/wardrobe', methods = ["GET", "POST"])

def clothes():
 
  conn = db_connection()
  cursor = conn.cursor()

  if request.method == "GET":
    cursor = conn.execute("SELECT * FROM wardrobe")
    wardrobe = [
      dict(id=row[0], Article=row[1], Color=row[2], Size=row[3], Material=row[4], Season=row[5] )
      for row in cursor.fetchall()
    ]
    if wardrobe is not None:
      return jsonify(wardrobe)

  if request.method == "POST":
    new_Article = request.form["Article"]
    new_Color = request.form["Color"]
    new_Size = request.form["Size"]
    new_Material = request.form["Material"]
    new_Season = request.form["Season"]

    sql = """INSERT INTO wardrobe (Article, Color, Size, Material, Season)
             VALUES(?,?,?,?,?)"""
    cursor = cursor.execute(sql, (new_Article, new_Color, new_Size, new_Material, new_Season))
    conn.commit()
    return f"Article with the iD: {cursor.lastrowid} created successfully", 201



@mywardrobe_bp.route('/wardrobe/<int:id>', methods=['GET', 'PUT', 'DELETE'])

def article_by_id(id):

  conn = db_connection()
  cursor = conn.cursor()
  item = None

  if request.method == 'GET':
    cursor.execute("SELECT * FROM wardrobe WHERE id=?", (id,))
    rows = cursor.fetchall()
    for i in rows:
      item = i
    if item is not None:
      return jsonify(item), 200
    else:
      return "Something wrong", 400
 

  if request.method == 'PUT':
    sql = """UPDATE wardrobe
             SET Article=?,
                 Color=?,
                 Size=?,
                 Material=?,
                 Season=?
              WHERE id = ?"""

    Article = request.form["Article"]
    Color = request.form['Color']
    Size = request.form['Size']
    Material = request.form['Material']
    Season = request.form['Season']
    
        
        
    updated_wardrobe = {
          'id' : id,
          "Article" : Article,
          "Color" : Color,
          "Size" : Size,
          "Material" : Material,
          "Season" : Season,
          
        }
    conn.execute(sql, (Article, Color, Size, Material,Season, id))
    conn.commit()
    return jsonify(updated_wardrobe)
  
  if request.method == 'DELETE':
    sql = """DELETE FROM wardobe WHERE id = ?"""
    conn.execute(sql, (id,))
    conn.commit()
    return "The Article with id: {} has been deleted .".format(id), 200



@mywardrobe_bp.route("/my_outfit", methods=["GET","POST"])
def my_outfit():
  WEATHER_API_KEY = '5ed49722431bccb9d76ee002147b7d05'
  city = request.form['city']
  weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&appid={WEATHER_API_KEY}'
  weather_response = requests.get(weather_url)
  weather_data = weather_response.json()
  temperature = weather_data['main']['temp']
  
  cold = (0, 10)
  mild = (11, 20)
  hot = (21, 40)

  if temperature <= cold[1]:
      season = 'Cold'
  elif temperature <= mild[1]:
      season = 'Mild'
  else:
      season = 'Hot'


  conn = db_connection()
  cursor = conn.cursor()
  cursor.execute(f"""
    SELECT top_clothes.Article
    FROM wardrobe 
    INNER JOIN wardrobe top_clothes ON top_clothes.Body_Part = 'Top'
    WHERE top_clothes.Season = '{season}'
    """)
  top_results = cursor.fetchall()
  top_clothes = list(set([top[0] for top in top_results])) if top_results else [('No matching top clothes found')]
  cursor.execute(f"""
    SELECT bottom_clothes.Article
    FROM wardrobe 
    INNER JOIN wardrobe bottom_clothes ON bottom_clothes.Body_Part = 'Bottom'
    WHERE bottom_clothes.Season = '{season}'
    """)
  bottom_results = cursor.fetchall()
  bottom_clothes = list(set([bottom[0] for bottom in bottom_results])) if bottom_results else [('No matching bottom clothes found')]
  return render_template('my_outfit.html', temperature=temperature, top_clothes=top_clothes,bottom_clothes=bottom_clothes,city=city)

