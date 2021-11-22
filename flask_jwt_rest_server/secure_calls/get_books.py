from flask import request, g
from flask_json import FlaskJSON, JsonError, json_response, as_json
from tools.token_tools import create_token
from db_con import get_db_instance, get_db
global_db_con = get_db()

from tools.logging import logger

def handle_request():
    logger.debug("Get Books Handle Request")
    cur = global_db_con.cursor()
    book = cur.execute("select * from books;")
    return json_response( token = create_token(  g.jwt_data ) , books = book)

