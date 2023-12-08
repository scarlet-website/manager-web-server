import json
from datetime import datetime
from time import sleep

from flask import request, Response, jsonify

from manager import app
from manager.manager_api import ManagerAPI
from objects.book import Book
from objects.update_request_data import UpdateRequestData

manager_api = ManagerAPI()


@app.route('/insert', methods=['POST'])
def insert():
    authentication_token = str(json.loads(request.args['token']))
    if not manager_api.check_authentication_token(authentication_token=authentication_token):
        return Response(f"Wrong token `{authentication_token}`", status=401, mimetype='application/json')

    insert_type: str = json.loads(request.args['insert_type'])
    data: dict = json.loads(request.args['data'])

    image_data = None
    if 'image' in request.files:
        image_data = request.files['image'].read()

    try:
        inserted_data = manager_api.insert_data(insert_type=insert_type, data=data, image_data=image_data)
        return Response(inserted_data, status=201, mimetype='application/json')
    except Exception as e:
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/update', methods=['POST'])
def update():
    try:

        json_data = json.loads(request.form.get('json_data'))

        request_data = UpdateRequestData.model_validate(json_data)
        authentication_token = request_data.token
        if not manager_api.check_authentication_token(authentication_token=authentication_token):
            return Response(f"Wrong token `{authentication_token}`", status=401, mimetype='application/json')

        insert_type: str = request_data.insert_type
        data: Book = request_data.data

        image_data = None
        if 'image' in request.files:
            image_data = request.files['image'].read()

        manager_api.update_data(insert_type=insert_type, data=data.model_dump(), image_data=image_data)
        return Response(f"{insert_type} updated successfully", status=201, mimetype='application/json')
    except Exception as e:
        print(f"Error updating data, {str(e)}")
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/get_books')
def get_books():
    books = manager_api.get_books()
    if books:
        print(f"Return books {datetime.now()}")
        sleep(1)
        return jsonify({'books': books})
    else:
        print("No books")
        return Response("No books found", status=204, mimetype='application/json')


@app.route('/reset_books_from_github')
def reset_books_from_github():
    if 'token' not in request.args.keys():
        return Response(f"No token given", status=401, mimetype='application/json')
    authentication_token = str(json.loads(request.args['token']))
    if not manager_api.check_authentication_token(authentication_token=authentication_token):
        return Response(f"Wrong token `{authentication_token}`", status=401, mimetype='application/json')

    try:
        manager_api.reset_books_from_github()
        return Response("Reset books from GitHub", status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(str(e), status=500, mimetype='application/json')
