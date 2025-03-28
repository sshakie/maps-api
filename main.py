import sys, os, random
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow

from geocoder import *


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('ui.ui', self)

        self.press_delta = 0.1
        self.size_map = '450,450'
        self.key = '03ed6b30-9245-4897-8428-d44545081a7c'

        self.map_zoom = 5
        self.map_ll = [37.617531, 55.756086]
        self.current_theme = 'light'
        self.points_on_map = []
        self.index_points = dict()
        self.refresh_map()

        self.theme_button.clicked.connect(self.change_theme)
        self.theme_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.search_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.search_button.clicked.connect(self.search_object)
        self.searchEdit.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.clear_button.clicked.connect(self.clear_point)
        self.clear_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.map_ll[0] -= self.press_delta
        if event.key() == Qt.Key.Key_Right:
            self.map_ll[0] += self.press_delta
        if event.key() == Qt.Key.Key_Up:
            self.map_ll[1] += self.press_delta
        if event.key() == Qt.Key.Key_Down:
            self.map_ll[1] -= self.press_delta
        if event.key() == Qt.Key.Key_Return:
            self.search_object()
        if event.key() == Qt.Key.Key_Tab:
            self.searchEdit.setFocus()
        if event.key() == Qt.Key.Key_Escape:
            self.searchEdit.clearFocus()
        if event.key() == Qt.Key.Key_PageUp and self.map_zoom < 17:
            self.map_zoom += 1
        if event.key() == Qt.Key.Key_PageDown and self.map_zoom > 1:
            self.map_zoom -= 1
        self.refresh_map()
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        if not self.searchEdit.geometry().contains(event.pos()):
            self.searchEdit.clearFocus()
        super().mousePressEvent(event)

    def closeEvent(self, event):
        os.remove('tmp.png')
        event.accept()

    def focusOutEvent(self, event):
        self.deselect()
        super().focusOutEvent(event)

    def refresh_map(self):
        map_params = {'apikey': self.key, 'size': self.size_map, 'll': ','.join(map(str, self.map_ll)),
                      'z': self.map_zoom, 'theme': self.current_theme}
        if self.points_on_map:
            map_params['pt'] = '~'.join(self.points_on_map)
        response = requests.get('https://static-maps.yandex.ru/v1', params=map_params)
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')
        self.map_label.setPixmap(pixmap)

    def change_theme(self):
        if self.current_theme == 'light':
            self.current_theme = 'dark'
            self.theme_button.setText('⬜')
            self.setStyleSheet("background-color: rgb(75, 75, 75)")
            self.theme_button.setStyleSheet('color:white')
            self.search_button.setStyleSheet('color:white')
            self.searchEdit.setStyleSheet('color:white')
            self.label.setStyleSheet('color:white')
            self.label_2.setStyleSheet('color:white')
            self.label_3.setStyleSheet('color:white')
            self.clear_button.setStyleSheet('color:white')
            self.addressEdit.setStyleSheet('color:white')
        else:
            self.current_theme = 'light'
            self.theme_button.setText('⬛')
            self.setStyleSheet("background-color: rgb(255, 255, 255)")
            self.theme_button.setStyleSheet('color:black')
            self.search_button.setStyleSheet('color:black')
            self.searchEdit.setStyleSheet('color:black')
            self.label.setStyleSheet('color:black')
            self.label_2.setStyleSheet('color:black')
            self.label_3.setStyleSheet('color:black')
            self.clear_button.setStyleSheet('color:black')
            self.addressEdit.setStyleSheet('color:black')
        self.refresh_map()

    def search_object(self):
        object_name = self.searchEdit.text()
        if object_name:
            self.info = get_object_info(object_name)
            self.map_ll = list(map(float, self.info[0].split(',')))
            self.map_zoom = 17

            self.address = self.info[2]['metaDataProperty']['GeocoderMetaData']['Address']['Components']
            a = [i['name'] for i in self.address]
            self.address = ', '.join([a[0], a[-1], a[1], a[2], a[3]])
            if self.show_postal.isChecked():
                try:
                    self.address += f', {self.info[2]['metaDataProperty']['GeocoderMetaData']['Address']['postal_code']}'
                except Exception:
                    print(
                        '-----\n(Почтовый индекс у данного адреса не доступен, попробуйте вбить более общий адрес (если честно сам до сих пор не понимаю как это работает))')
                    print(
                        '(Пример, на котором работает: Музей Московского Уголовного Розыска (МУРа), Петровка, 38, Москва)\n-----')
            self.addressEdit.setPlainText(self.address)

            if f'{self.map_ll[0]},{self.map_ll[1]}' not in ''.join(self.points_on_map):
                colors = ['wt', 'do', 'db', 'bl', 'gn', 'dg', 'gr', 'lb', 'nt', 'or', 'pn', 'rd', 'vv', 'yw']
                self.points_on_map.append(f'{self.map_ll[0]},{self.map_ll[1]},pm{random.choice(colors)}s')
                self.index_points[object_name] = len(self.points_on_map) - 1
            self.refresh_map()

    def clear_point(self):
        object_name = self.searchEdit.text()
        if object_name:
            try:
                self.points_on_map.pop(self.index_points[object_name])
                self.addressEdit.setPlainText('')
                self.searchEdit.setText('')
            except Exception:
                pass
            self.refresh_map()


def exception_hook(cls, exception, traceback):
    sys.__exception_hook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.__excepthook__ = exception_hook
    sys.exit(app.exec())
