from flask import Flask,render_template,request
from flask_json import FlaskJSON, JsonError, json_response, as_json
import jwt

import datetime
import bcrypt


from db_con import get_db_instance, get_db

app = Flask(__name__)
FlaskJSON(app)

USER_PASSWORDS = { "cjardin": "strong password"}

IMGS_URL = {
            "DEV" : "/static",
            "INT" : "https://cis-444-fall-2021.s3.us-west-2.amazonaws.com/images",
            "PRD" : "http://d2cbuxq67vowa3.cloudfront.net/images",
	    "A2" : "https://i.imgur.com"
            }

CUR_ENV = "A2"
JWT_SECRET = None

global_db_con = get_db()


with open("secret", "r") as f:
    JWT_SECRET = f.read()

@app.route('/') #endpoint
def index():
    return 'Web App with Python Caprice!' + USER_PASSWORDS['cjardin']

@app.route('/buy') #endpoint
def buy():
    return 'Buy'

@app.route('/hello') #endpoint
def hello():
    return render_template('hello.html',img_url=IMGS_URL[CUR_ENV] ) 

@app.route('/back',  methods=['GET']) #endpoint
def back():
    return render_template('backatu.html',input_from_browser=request.args.get('usay', default = "nothing", type = str) )

@app.route('/backp',  methods=['POST']) #endpoint
def backp():
    print(request.form)
    salted = bcrypt.hashpw( bytes(request.form['fname'],  'utf-8' ) , bcrypt.gensalt(10))
    print(salted)

    print(  bcrypt.checkpw(  bytes(request.form['fname'],  'utf-8' )  , salted ))

    return render_template('backatu.html',input_from_browser= str(request.form) )

@app.route('/auth',  methods=['POST']) #endpoint
def auth():
        print(request.form)
        return json_response(data=request.form)



#Assigment 2
@app.route('/ss1') #endpoint
def ss1():
    return render_template('josh.html',img_url = IMGS_URL[CUR_ENV])

@app.route('/getTime') #endpoint
def get_time():
    return json_response(data={"password" : request.args.get('password'),
                                "class" : "cis44",
                                "serverTime":str(datetime.datetime.now())
                            }
                )

@app.route('/auth2') #endpoint
def auth2():
    jwt_str = jwt.encode({"username" : "cary",
                            "age" : "so young",
                            "books_ordered" : ['f', 'e'] } 
                            , JWT_SECRET, algorithm="HS256")
    #print(request.form['username'])
    return json_response(jwt=jwt_str)

@app.route('/exposejwt') #endpoint
def exposejwt():
    jwt_token = request.args.get('jwt')
    print(jwt_token)
    return json_response(output=jwt.decode(jwt_token, JWT_SECRET, algorithms=["HS256"]))


@app.route('/hellodb') #endpoint
def hellodb():
    cur = global_db_con.cursor()
    cur.execute("insert into music values( 'dsjfkjdkf', 1);")
    global_db_con.commit()
    return json_response(status="good")

#a3 code (full stack app)
user_token = None #represents server side copy of jwt

@app.route('/bookstore')
def bookstore():
    return render_template('bookstore.html');

@app.route("/authbookstorelogin",methods=["POST","GET"])
def authbookstorelogin():
    print ("Starting login...")
    username = request.form["username"]
    password = request.form["password"]
   
    cur = global_db_con.cursor()
    cur.execute(f"select * from users where username = '{username}';")
    user_record = cur.fetchone()
    if user_record is not None: #user exists
     if bcrypt.checkpw(bytes(password, "utf-8"), bytes(user_record[2], "utf-8")) == True: #password is valid

        user_token = jwt.encode({"id":user_record[0], "username":user_record[1]}, JWT_SECRET, algorithm = "HS256")
        print("Login OK.")
        return json_response(data = {"jwt": user_token})
     else: #password is invalid
        print("Incorrect password.")
        return json_response(data = {"message": "Incorrect password."})
    else: #user does not exist
       print("Incorrect username.")
       return json_response(data = {"message": "Incorrect username."})

@app.route("/getbooklist",methods=["GET"])
def getbooklist():
    print ("Getting booklist...")
    clientToken = jwt.decode(request.args.get("jwt"), JWT_SECRET, algorithms = ["HS256"])
    serverToken = jwt.decode(user_token, JWT_SECRET, algorithms = ["HS256"])
    if not (clientToken == serverToken): #ensure that user is logged in
     print("Invalid token.")
     return json_response(data = {"message": "Invalid token."})
    else:
     cur = global_db_con.cursor()
     cur.execute("select count(1) from books;")
     numRows = cur.fetchone()[0] #number of rows in the table
     i = 1
     message = '{"books":['
     while i <= numRows:
      cur.execute(f"select from books where id = '{i}';")
      currentBook = cur.fetchone()
      message += '{"id":"' + currentBook[0] + '","title":"' + currentBook[1] + '","price":' + str(currentBook[2]) + "}"
      if not i == numRows:
       message += ","
      i += 1
     print ("Sending booklist...")
     return json_response(data = json.loads(message)) 

app.run(host='0.0.0.0', port=80)

