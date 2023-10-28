from utils.consts import ContentConstants


class ContentUtils:
    @staticmethod
    def description_html_parser(text_description: str) -> str:
        """
        Parsing description text to html

        :param text_description:
        :return:
        """
        html_description = text_description.replace('\n', '<br>').replace("\"", "'").strip()
        return html_description

    @staticmethod
    def description_text_parser(html_description: str) -> str:
        """
        Parsing description html to regular text

        :param html_description:
        :return:
        """
        text_description = html_description.replace('<br>', '\n').replace("'", "\"").strip()
        return text_description

    @staticmethod
    def fix_characters(content: str) -> str:
        """
        Fixing common unwanted characters in content text

        :param content:
        :return:
        """
        updated_content = ""
        for error, fix in ContentConstants.FIXING_CHARACTERS.items():
            updated_content = content.replace(error, fix)
        return updated_content
