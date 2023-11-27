import json
from datetime import datetime

from flask import request, Response, jsonify

from manager import app
from manager.manager_api import ManagerAPI
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
        print(UpdateRequestData.parse_obj(request.data))
        authentication_token = str(json.loads(request.args['token']))
        if not manager_api.check_authentication_token(authentication_token=authentication_token):
            return Response(f"Wrong token `{authentication_token}`", status=401, mimetype='application/json')

        insert_type: str = json.loads(request.args['insert_type'])
        data: dict = json.loads(request.args['data'])

        image_data = None
        if 'image' in request.files:
            image_data = request.files['image'].read()

        updated_data = manager_api.update_data(insert_type=insert_type, data=data, image_data=image_data)
        return Response(updated_data, status=201, mimetype='application/json')
    except Exception as e:
        print(f"Error updating data, {str(e)}")
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/get_books')
def get_books():
    books = manager_api.get_books()
    if books:
        print(f"Return books {datetime.now()}")
        return jsonify({'books': books})
    else:
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
