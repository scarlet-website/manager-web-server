import uuid

from utils.consts import ContentConsts


class ContentUtils:
    @staticmethod
    def info_html_parser(text_info: str) -> str:
        """
        Parsing description text to html

        :param text_info:
        :return:
        """
        for key, value in ContentConsts.REPLACE_INFO_PARSER_TO_HTML:
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
