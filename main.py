import sys, os, requests
from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi('ui.ui', self)

        self.press_delta = 0.1
        self.size_map = '450,450'
        self.key = '03ed6b30-9245-4897-8428-d44545081a7c'
        self.key = '92bf06ed-e9bb-4a7b-8b91-23cf32fb910d'

        self.map_zoom = 5
        self.map_ll = [37.617531, 55.756086]
        self.map_l = 'map'
        self.map_key = ''
        self.current_theme = 'light'
        self.refresh_map()

        self.theme_button.clicked.connect(self.change_theme)
        self.theme_button.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def wheelEvent(self, event):
        if event.angleDelta().y() > 0 and self.map_zoom < 17:
            self.map_zoom += 1
        elif event.angleDelta().y() < 0 and self.map_zoom > 0:
            self.map_zoom -= 1
        self.refresh_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Left:
            self.map_ll[0] -= self.press_delta
        if event.key() == Qt.Key.Key_Right:
            self.map_ll[0] += self.press_delta
        if event.key() == Qt.Key.Key_Up:
            self.map_ll[1] += self.press_delta
        if event.key() == Qt.Key.Key_Down:
            self.map_ll[1] -= self.press_delta
        self.refresh_map()

    def closeEvent(self, event):
        os.remove('tmp.png')
        event.accept()

    def refresh_map(self):
        map_params = {'apikey': self.key, 'size': self.size_map, 'll': ','.join(map(str, self.map_ll)),
                      'maptype': self.map_l, 'z': self.map_zoom, 'theme': self.current_theme}
        response = requests.get('https://static-maps.yandex.ru/v1', params=map_params)
        # print(response.url)
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')
        self.map_label.setPixmap(pixmap)

    def change_theme(self):
        if self.current_theme == 'light':
            self.current_theme = 'dark'
            self.theme_button.setText('Dark')
            self.setStyleSheet("background-color: rgb(75, 75, 75)")
            self.theme_button.setStyleSheet('color:white')
        else:
            self.current_theme = 'light'
            self.theme_button.setText('Light')
            self.setStyleSheet("background-color: rgb(255, 255, 255)")
            self.theme_button.setStyleSheet('color:black')
        self.refresh_map()


def exception_hook(cls, exception, traceback):
    sys.__exception_hook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.__excepthook__ = exception_hook
    sys.exit(app.exec())
