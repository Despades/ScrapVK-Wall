import re
import argparse

txt_id_ptrn_link = r"(?:https?:\/\/)(?:vk.com\/(?!club|public|id|event))" r"(?P<id>(?![_.])(?!club|public|id|event)[a-z0-9_.]*" r"[a-z][a-z0-9_.]*)"
num_id_ptrn_link = r"^(?:https?:\/\/)?(?:vk.com\/)?(?P<type>club|public|id|event)" r"(?P<id>\d+)$"

TXT_ID_REGEXP = re.compile(txt_id_ptrn_link)
NUM_ID_REGEXP = re.compile(num_id_ptrn_link)

def url_validator(arg):
    """ Check correctness of url argument """
    #пишем костыль, на случай если именная ссылка содержит начало вида club_
    if arg.find('https://vk.com/club_') != -1 or arg.find('https://vk.com/club-') != -1:
        return {"type": 'named-link', "id": arg.split('/')[-1]}
    else:
        arg = arg.lower()

        # If url looks like http(s)://vk.com/named-link
        symbolic_id = TXT_ID_REGEXP.match(arg)
        if symbolic_id:
            url = symbolic_id.groupdict()
            url["type"] = 'named-link'
            return url

        # If url looks like http[s]://vk.com/id123456
        numeric_id = NUM_ID_REGEXP.match(arg)
        if numeric_id:
            url = numeric_id.groupdict()
            return url

    #raise argparse.ArgumentTypeError("{} - invalid url address".format(arg))

#функция смены стиля элемента
def set_styles(object, condition = False):
    if not condition:
        object.setStyleSheet('''
            QLineEdit {
                color: #000000;
                border: 2px solid gray;
                border-radius: 10px;
                padding: 0 8px;
                background: #ffffff;
                font: 16, Times New Roman;
            }
        ''')
    else:
        object.setStyleSheet('''
            QLineEdit {
                color: #ffffff;
                border: 2px solid gray;
                border-radius: 10px;
                padding: 0 8px;
                background: #eb555f;
                font: 16, Times New Roman;
            }
        ''')
