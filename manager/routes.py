import json
from datetime import datetime

from flask import request, Response, jsonify, send_from_directory

from manager import app
from manager.manager_api import ManagerAPI
from objects.book import Book
from objects.delete_request_data import DeleteRequestData
from objects.update_request_data import UpdateRequestData
from utils.consts import ServerConsts
from utils.exceptions import NotValidEmailAddressException

manager_api = ManagerAPI()


@app.route('/insert', methods=['POST'])
def insert():
    try:
        json_data = json.loads(request.form.get('json_data'))

        authentication_token = json_data['token']
        if not manager_api.check_authentication_token(authentication_token=authentication_token):
            return Response(f"Wrong token `{authentication_token}`", status=401, mimetype='application/json')

        insert_type: str = json_data['insert_type']
        data = json_data['data']

        image_data = None
        if 'image' in request.files:
            image_data = request.files['image'].read()

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


@app.route('/delete', methods=['POST'])
def delete():
    try:
        print("DELETE")
        json_data = json.loads(request.form.get('json_data'))
        request_data = DeleteRequestData.model_validate(json_data)
        authentication_token = request_data.token
        if not manager_api.check_authentication_token(authentication_token=authentication_token):
            return Response(f"Wrong token `{authentication_token}`", status=401, mimetype='application/json')

        insert_type: str = request_data.insert_type
        item_id: str = request_data.item_id
        product_id_key = manager_api.get_product_id_key_by_insert_type(insert_type=insert_type)
        manager_api.delete_data(insert_type=insert_type, data={product_id_key: item_id})
        return Response(f"{insert_type} deleted successfully", status=201, mimetype='application/json')
    except Exception as e:
        print(f"Error updating data, {str(e)}")
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/get_books')
def get_books():
    parse_info = request.args.get("parse_info")
    books = manager_api.get_books(parse_info)
    if books:
        print(f"Return books {datetime.now()}")
        return jsonify({'books': books})
    else:
        manager_api.reset_books_from_github()  # Temporary solution
        print("No books")
        return Response("No books found", status=204, mimetype='application/json')


@app.route('/get_banners')
def get_banners():
    banners = manager_api.get_banners()
    if banners:
        print(f"Return banners {datetime.now()}")
        return jsonify({'banners': banners})
    else:
        print("No banners")
        return Response("No books found", status=204, mimetype='application/json')


@app.route('/get_image/<filename>')
def get_book_image(filename):
    try:
        print(f"Getting image file name: `{filename}`...")
        # return send_from_directory("", filename)
        return send_from_directory(ServerConsts.IMAGES_PATH, filename)
    except Exception as e:
        print(f"Error get image `{filename}`, except: {str(e)}")


@app.route('/reset_books_from_github')
def reset_books_from_github():
    if 'token' not in request.args.keys():
        return Response(f"No token given", status=401, mimetype='application/json')
    authentication_token = request.args['token']
    if not manager_api.check_authentication_token(authentication_token=authentication_token):
        return Response(f"Wrong token `{authentication_token}`", status=401, mimetype='application/json')

    try:
        manager_api.reset_books_from_github()
        return Response("Reset books from GitHub", status=200, mimetype='application/json')
    except Exception as e:
        print(e)
        return Response(str(e), status=500, mimetype='application/json')


@app.route('/add_email_to_newsletter', methods=['POST'])
def add_email_to_newsletter():
    try:
        json_data = json.loads(request.data)
        email = json_data.get("email")
        manager_api.add_email_to_newsletter(email=email)
        return jsonify(json_data), 200
    except NotValidEmailAddressException:
        error_desc = 'Invalid email address'
        print(error_desc)
        return Response(error_desc, status=400, mimetype='application/json')
    except Exception as e:
        error_desc = f'Internal Server Error, except: {str(e)}'
        print(error_desc)
        return Response(error_desc, status=500, mimetype='application/json')


@app.route('/get_newsletter_emails', methods=['POST'])
def get_newsletter_emails():
    json_data = json.loads(request.data)
    if 'token' not in json_data.keys():
        return Response(f"No token given", status=401, mimetype='application/json')
    authentication_token = json_data.get('token')
    if not manager_api.check_authentication_token(authentication_token=authentication_token):
        return Response(f"Wrong token `{authentication_token}`", status=401, mimetype='application/json')

    try:
        news_letters = manager_api.get_newsletters_emails()
        print(f"Return news_letters {datetime.now()}")
        return jsonify({'news_letters': news_letters})
    except Exception as e:
        error_desc = f'Internal Server Error, except: {str(e)}'
        print(error_desc)
        return Response(error_desc, status=500, mimetype='application/json')
