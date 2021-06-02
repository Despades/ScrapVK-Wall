import sys
import requests
import datetime
import time
import webbrowser
from PyQt5 import QtGui, QtCore, QtWidgets
import json
import pyexcel#для корректной работы с сохранением данных в xlsx-файл требуется дополнительно установить плагин pyexcel-xlsx. напрямую импортировать в файл приложения его не нужно
from support_module import url_validator, set_styles
from VKUI3 import Ui_MainWindow
from seach_popup import VkDespadesPopup


class VkDespades(QtWidgets.QMainWindow):
    def __init__(self, my_addedtoken, parent = None):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.my_addedtoken = my_addedtoken #используемый нами токен
        self.wallURL = [] #массив, который будет содержать словари с информацией о записях на стене
        self.title = '' #переменная, получающая имя группы/пользователя
        self.offset = 0 #смещение, необходимое для выборки определенного подмножества записей (vk api)
        self.count = 100 #количество записей, которое необходимо получить. Максимальное значение: 100 (vk api)
        self.versionVKAPI = 5.126 #используемая версия vk api
        self.errorCondition = False #переменная для задания стиля поля ввода
        #self.exPopup = VkDespadesPopup(self.wallURL) #свойство,хранящее всплывающее окно
        self.exPopup = None
        self.setWindowIcon(QtGui.QIcon('vk.png'))
        set_styles(self.ui.lineEdit)#инициализируем стили поля ввода и поля поиска
        set_styles(self.ui.lineSearch)
        self.ui.pushButton.clicked.connect(self.processingURL)
        self.ui.listWidget.itemDoubleClicked.connect(self.getInfoID)#сигнал для открытия в браузере выбранной записи
        self.ui.topLikesButton.clicked.connect(self.sorted_wallURL)#сигнал для сортировки
        self.ui.saveButton.clicked.connect(self.save_datafile)
        self.ui.searchButton.clicked.connect(self.seach_popup_window)

    #функция работы со всплывающем окном
    def seach_popup_window(self):
        if len(self.ui.lineSearch.text()) > 0 and len(self.wallURL) > 0:
            search_word = self.ui.lineSearch.text().strip()
            search_result_list = []
            print('начинаем поиск по записям...')
            for item in self.wallURL:
                if item['text_article'].find(search_word) != -1:
                    search_result_list.append(item)
            if len(search_result_list) > 0:       
                self.exPopup = VkDespadesPopup(search_result_list)
                self.exPopup.show()
                set_styles(self.ui.lineSearch)
                self.ui.lineSearch.setPlaceholderText('поиск по записям')
            else:
                print('по вашему запросу ничего не найдено')
                set_styles(self.ui.lineSearch, True)
                self.ui.lineSearch.setPlaceholderText('не найдено')
        else:
            #self.ui.lineSearch.setPlaceholderText('введите корректный url')
            print('нет данных для поиска')

    #если массив содержит данные то можем сохранить по нажатию на кнопку "сохранить данные" поставив соответствующую галочку
    def save_datafile(self):
        if len(self.wallURL) > 0:
            if self.ui.checkJSON.isChecked():#в json-файл
                self.write_json(self.wallURL, self.title)
            if self.ui.checkExcel.isChecked():#в excel
                self.write_excel(self.wallURL, self.title)
        else:
            print('нет данных')

    #метод выбора нужной записи и её открытия в браузере
    def getInfoID(self):
        #spisok = self.ui.listWidget
        n = self.ui.listWidget.currentRow()
        #print(self.wallURL[n]['text_article'])
        #print(self.ui.listWidget.item(n).text())#получаем текст из списка
        #print(spisok.currentItem().text()) #так мы получаем напрямую текст без необходимости в порядковом номере
        webbrowser.open_new_tab(self.wallURL[n]['link'])

    #метод запроса на определения id по именованной ссылке
    def get_groupID(self, screen_name):
        r = requests.get('https://api.vk.com/method/utils.resolveScreenName', params={'screen_name': screen_name, 'access_token': self.my_addedtoken, 'v': self.versionVKAPI})
        response = r.json()
        time.sleep(.33)
        return response['response']['object_id']

    #метод валидации введенной ссылки по нажатию кнопки "Получить записи"
    def processingURL(self):
        input_link = self.ui.lineEdit.text()#получаем введенную в поле ссылку
        res_dic = url_validator(input_link)
        self.ui.lineEdit.clear()
        #print(res_dic)
        if len(input_link) > 0 and res_dic != None:
            if self.errorCondition:
                self.errorCondition = False
                set_styles(self.ui.lineEdit)
            if res_dic['type'] == 'named-link':#если именованная
                input_id = self.get_groupID(res_dic['id'])
                #self.get_request(input_id)
            else:#если сразу имеет id
                input_id = res_dic['id']
                #self.get_request(input_id)
            self.get_request(input_id)
            self.ui.lineEdit.setPlaceholderText('введите ссылку на группу или пользователя')
        else:
            self.errorCondition = True
            set_styles(self.ui.lineEdit, self.errorCondition)
            self.ui.lineEdit.setPlaceholderText('введите корректный url')

    #метод инициализации запроса на получение записей, их количества и имени пользователя/группы
    def get_request(self, input_id):
        if self.ui.checkGroup.isChecked():
            input_id = int('-' + str(input_id))
            user_name = None
        if self.ui.checkUser.isChecked():
            user_name = self.get_infoUser(input_id)
        #если были данные - обнуляем их перед новым запросом
        if len(self.wallURL) > 0:
            self.offset = 0
            self.wallURL = []
            self.ui.listWidget.clear()
        r = requests.get('https://api.vk.com/method/wall.get', params = {
            'owner_id': input_id,
            'count': self.count,
            'access_token': self.my_addedtoken,
            'extended': 1,
            'v': self.versionVKAPI
        })
        response = r.json()
        post_count = response['response']['count'] #количество постов в группе или профиле
        group_name = response['response']['groups'][0]['name'] #название сообщества, используется в заголовке только если не задействована переменная user_name
        print('Количество постов на стене:', post_count)
        self.title = user_name or group_name
        self.ui.groupBox.setTitle('Количество постов на стене "' + self.title + '": ' + str(post_count))
        time.sleep(0.33) #необходимая пауза для работы с vk api
        self.full_listWall(post_count, input_id)#метод для второго этапа работы по получению записей со вторым запросом после паузы на предыдущей строчке кода
        

    #метод получения имени пользователя 
    def get_infoUser(self, input_id):
        r = requests.get('https://api.vk.com/method/users.get', params = {
            'user_ids': input_id,
            'access_token': self.my_addedtoken,
            'fields': 'first_name, last_name',
            'v': self.versionVKAPI
        })
        user_info = r.json()
        user_name = user_info['response'][0]['first_name'] + ' ' + user_info['response'][0]['last_name'] #формируем строку с полным именем пользователя
        time.sleep(.33)
        return user_name

    #метод перебора и получения всех записей через циклы
    def full_listWall(self, post_count, input_id):
        while self.offset < post_count:
            r = requests.get('https://api.vk.com/method/wall.get', params = {
                'owner_id': input_id,
                'count': self.count,
                'offset': self.offset,
                'access_token': self.my_addedtoken,
                'v': self.versionVKAPI
            })
            response = r.json()
            #запускаем цикл, содержащийся в методе range_wall для обработки ответа
            if post_count - self.offset > 100:
                self.range_wall(response, 100)
                self.offset = self.offset + 100
            else:
                self.range_wall(response, post_count - self.offset)#когда остаётся перебрать менее 100 записей, устанавливаем диапазон от 0 до post_count - self.offset
                self.offset = self.offset + (post_count - self.offset)
            time.sleep(.33)
        print('Все записи получены!')
        #self.ui.lineEdit.clear() #очищаем поле ввода

    def range_wall(self, response, stopItem):
        for i in range(0, stopItem):
            #получаем необходимые поля с данными
            try:
                post_date = datetime.datetime.utcfromtimestamp(response['response']['items'][i]['date']).strftime("%d.%m.%Y") #дата и время публикации в Unix-формате
            except:
                post_date = ''
            try:    
                text_article = response['response']['items'][i]['text'] #текст
            except:
                text_article = 'описание отсутствует'
            try:    
                post_id = response['response']['items'][i]['id'] #id поста в сообществе
            except:
                post_id = 0
            try:
                group_id = response['response']['items'][i]['owner_id'] #id сообщества . В версиях API ниже 5.7 вместо поля owner_id приходит to_id.
            except:
                group_id = 0
            try:
                likes_count = response['response']['items'][i]['likes']['count'] #количество лайков
            except:
                likes_count = 0
            try:    
                repost_count = response['response']['items'][i]['reposts']['count']  #количество репостов
            except:
                repost_count = 0
            link = 'https://vk.com/wall' + str(group_id) + '_' + str(post_id) #ссылка на запись
            
            #формируем элемент вспомогательного списка wallURL в виде словаря
            item_data_wall = {
                'post_date': post_date,
                'text_article': text_article,
                'likes_count': likes_count,
                'repost_count': repost_count,
                'link': link
            }

            print('получен пост с id', post_id, 'ссылка:', link)
            self.wallURL.append(item_data_wall) #добавление элементов во вспомогательный список (нужен для сортировки и открытия ссылок)
            self.ui.listWidget.addItem('пост с от '+ str(post_date) + ':\n' + '\t-количество лайков: ' + str(likes_count) + ',\n' + '\t-количество репостов: ' + str(repost_count) + '\nОписание: ' + text_article[:150] + '...' + '\n============================================\n\n') #добавляем данную строку в массив, который выводится в окно приложения
    
    #метод сортировки массива
    def sorted_wallURL(self):
        if len(self.wallURL) > 0:
            if self.ui.checkLike.isChecked():
                self.wallURL = sorted(self.wallURL, key = lambda x: x['likes_count'], reverse = True)
            if self.ui.checkRepost.isChecked():
                self.wallURL = sorted(self.wallURL, key = lambda x: x['repost_count'], reverse = True)

            self.ui.listWidget.clear()
            for item in self.wallURL:
                self.ui.listWidget.addItem('пост от '+ item['post_date'] + ':\n' + '\t-количество лайков: ' + str(item['likes_count']) + ',\n' + '\t-количество репостов: ' + str(item['repost_count']) + '\nОписание: ' + item['text_article'][:150] + '...' + '\n============================================\n\n')
        else:
            print('нет данных')

    # метод записи в json-файл полученных данных
    def write_json(self, input_data, input_name):
        with open('wall_data_{}.json'.format(input_name.replace(' ', '_')), 'w', encoding='utf-8') as file: #чтобы был русский текст, указываем данные параметры encoding и ensure_ascii
            json.dump(input_data, file, indent=4, ensure_ascii=False)

    #метод записи в xlsx-файл (Excel) полученных данных
    def write_excel(self, input_data, input_name):
        data_excel = {'info': [['дата', 'лайки', 'репосты', 'ссылка', 'текст']]}
        data_excel_name = 'wall_data.{}.xlsx'.format(input_name.replace(' ', '_'))
        for item in input_data:
            data_excel['info'].append([
                item['post_date'],
                item['likes_count'],
                item['repost_count'],
                item['link'],
                item['text_article']
            ])
        pyexcel.save_book_as(bookdict = data_excel, dest_file_name = data_excel_name)

despadezToken = 'bd31ffb49d662e6dcd2c867d22e7e93f3ea81f7654aa9433795c9ee7430da9958ee951f062dc7383ec9f8'
oldToken = '9c2b1ec8fdb173573b407dc987c412a71820d4e454662f867adaebfd318ff247c4a76f93579ec99a87843'

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    myVKapp = VkDespades(despadezToken)# введите сюда свой токен str
    myVKapp.show()
    sys.exit(app.exec_())
