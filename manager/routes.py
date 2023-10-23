import json

from flask import request, Response

from db.db_utils import DBUtils
from manager import app
from objects.book import Book


@app.route('/insert')
def insert():
    book: dict = json.loads(request.args['book'])
    db_utils = DBUtils()
    try:
        inserted_data = db_utils.insert_data(table_name="books", data=book)
        return Response(inserted_data, status=201, mimetype='application/json')
    except Exception as e:
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/get_all_books')
def get_all_books():
    db_utils = DBUtils()
    books = db_utils.get_all_table_data(table_name='books', data_object_type=Book)
    if books:
        return Response(str([book.dict() for book in books]), status=200, mimetype='application/json')
    else:
        return Response("No books found", status=204, mimetype='application/json')
