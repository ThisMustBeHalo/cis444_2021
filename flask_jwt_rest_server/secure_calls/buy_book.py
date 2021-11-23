from flask import request, g
from flask_json import FlaskJSON, JsonError, json_response, as_json
from tools.token_tools import create_token
from db_con import get_db_instance, get_db
global_db_con = get_db()

from tools.logging import logger

def handle_request():
    logger.debug("Buy Book Handle Request")
    cur = global_db_con.cursor()
    purchased_book = request.args.get("book_id")
    cur.execute(f"select * from books where id = '{purchased_book}';")
    book_data = cur.fetchone()
    user_data = g.jwt_data
    book_title = book_data[1]
    #username = user_data['username']
    cur.execute(f"insert into purchases (book_title,customer) values ('{book_title}','{user_data}');")
    global_db_con.commit()
    print ("Purchase successful.")
    return json_response( token = create_token(user_data) , info = {'book_name': book_title,'user': user_data})