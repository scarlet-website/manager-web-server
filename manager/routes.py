import json
import os
from datetime import datetime

import requests
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

        manager_api.delete_data(insert_type=insert_type, data={"CatalogNumber": item_id})
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
        email = request.args.get("email")
        manager_api.add_email_to_newsletter(email=email)
        return Response(f"Added newsletter, email: `{email}`", status=200, mimetype='application/json')
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
    if 'token' not in request.args.keys():
        return Response(f"No token given", status=401, mimetype='application/json')
    authentication_token = request.args['token']
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


@app.route('/purchase', methods=['POST'])
def purchase():
    try:
        rivhit_url = "https://icredit.rivhit.co.il/API/PaymentPageRequest.svc"
        redirect_url = "https://www.scarlet-publishing.com/pages/order_confirm.php"
        group_private_token = os.getenv(key="group_private_token")

        items = request.json.get('Items')
        details = request.json.get('details')
        books = manager_api.get_books()

        if not items or len(items) == 0 or not books:
            print('No books to purchase')
            return Response('No books to purchase', status=400, mimetype='application/json')

        purchased_items = []
        bad_request = False
        purchased_item = dict()

        for book in items:
            api_book = next((b for b in books if str(b['CatalogNumber']) == str(book['CatalogNumber'])), None)
            if not api_book:
                print(f"Book with CatalogNumber {book['CatalogNumber']} not found")
                bad_request = True
                break  # Move the break statement here

            api_book.pop("ImageData")

            purchased_item = {
                **api_book,
                'Quantity': book['Quantity'],
            }
            purchased_items.append(purchased_item)

        print(f"purchased_items: {purchased_items}")

        if bad_request:
            return Response(f"Book not found", status=400, mimetype='application/json')

        rivhit_json = {
            'GroupPrivateToken': group_private_token,
            'RedirectURL': redirect_url,
            'ExemptVAT': False,
            'MaxPayments': 12,
            'Items': purchased_items,
            **details,
        }

        print(f"rivhit_json: {rivhit_json}")

        rivhit_response = requests.post(
            f"{rivhit_url}/GetUrl",
            json=rivhit_json
        )
        print(f"headers: ", {rivhit_response.headers})
        response_url = rivhit_response.headers
        print(f"response_url: {response_url}")
        return jsonify({'iframe_url': response_url}), 200

    except Exception as e:
        print(f"Error: {e}")
        return Response('Internal Server Error', status=500, mimetype='application/json')
