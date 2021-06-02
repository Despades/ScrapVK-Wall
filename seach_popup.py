import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(747, 493)
        self.groupBox = QtWidgets.QGroupBox(Form)
        self.groupBox.setGeometry(QtCore.QRect(20, 10, 701, 441))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(16)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.listWidget = QtWidgets.QListWidget(self.groupBox)
        self.listWidget.setGeometry(QtCore.QRect(20, 30, 661, 391))
        self.listWidget.setObjectName("listWidget")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Результаты поиска"))
        self.groupBox.setTitle(_translate("Form", "Результаты поиска"))


class VkDespadesPopup(QtWidgets.QMainWindow):
    def __init__(self, data, parent = None):
        QtWidgets.QTabWidget.__init__(self, parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.search_list = data
        self.ui.listWidget.itemDoubleClicked.connect(self.getlink)
        self.get_search_list(self.search_list)
    
    def get_search_list(self, data):
        for item_wall in data:
            self.ui.listWidget.addItem(item_wall['text_article'] + '\n============================================\n\n')
        self.ui.groupBox.setTitle('Результаты поиска: найдено ' + str(len(data)) + ' записей')
        print('поиск завершен, найдено ' + str(len(data)) + ' записей')

    def getlink(self):
        n = self.ui.listWidget.currentRow()
        webbrowser.open_new_tab(self.search_list[n]['link'])
