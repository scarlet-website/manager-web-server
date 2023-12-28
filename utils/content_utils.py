import base64
import os
import uuid

from utils.consts import ContentConsts, ServerConsts
from utils.exceptions import NotValidEmailAddressException


class ContentUtils:
    @staticmethod
    def info_html_parser(text_info: str) -> str:
        """
        Parsing description text to html

        :param text_info:
        :return:
        """
        for key, value in ContentConsts.REPLACE_INFO_PARSER_TO_HTML.items():
            text_info = text_info.replace(key, value)
        html_info = text_info.strip()
        return html_info

    @staticmethod
    def info_text_parser(html_info: str) -> str:
        """
        Parsing description html to regular text

        :param html_info:
        :return:
        """
        for key, value in ContentConsts.REPLACE_INFO_PARSER_TO_TEXT.items():
            html_info = html_info.replace(key, value)
        text_info = html_info.strip()
        return text_info

    @staticmethod
    def fix_characters(content: str) -> str:
        """
        Fixing common unwanted characters in content text

        :param content:
        :return:
        """
        updated_content = ""
        for error, fix in ContentConsts.FIXING_CHARACTERS.items():
            updated_content = content.replace(error, fix)
        return updated_content

    @staticmethod
    def generate_product_id() -> str:
        """
        Generate product id
        :return:
        """
        product_id = str(uuid.uuid4().int)[:ContentConsts.LENGTH_OF_PRODUCT_ID]
        return product_id

    @staticmethod
    def add_image(image_data: bytes, file_name: str):
        print("Start content_utils add_image")
        try:
            image_data = "data:image/jpeg;base64," + base64.b64encode(image_data).decode('ascii')
            if not os.path.exists(ServerConsts.IMAGES_PATH):
                os.mkdir(ServerConsts.IMAGES_PATH)
            ContentUtils.delete_image_if_exists(image_file_name=file_name)
            path = os.path.join(ServerConsts.IMAGES_PATH, file_name)
            with open(path, "wb") as f:
                f.write(base64.b64decode(image_data.split(',')[1]))
                print(f"Saved image at {path}")
            return path
        except Exception as e:
            print(f"Error saving image: `{file_name}`, except: {str(e)}")
            raise e

    @staticmethod
    def get_image_file_name(insert_type: str, item_id: str) -> str:
        file_name = f"{insert_type}_{item_id}.jpeg"
        return file_name

    @staticmethod
    def delete_image_if_exists(image_file_name):
        file_path = None
        try:
            file_path = os.path.join(ServerConsts.IMAGES_PATH, image_file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Removed image {file_path} successfully")
            else:
                print(f"Image file {file_path} doesn't exist")
        except Exception as e:
            print(f"Error deleting image `{file_path}`, except: {str(e)}")

    @staticmethod
    def check_valid_email_address(email: str):
        try:
            name, domain = email.split("@")
            if not name or not domain:
                raise NotValidEmailAddressException
        except Exception as e:
            desc = f"Not valid email address: `{email}`"
            print(f"desc, except: {str(e)}")
            raise NotValidEmailAddressException(desc)
