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

        self.map_zoom = 5
        self.map_ll = [37.977751, 55.757718]
        self.map_l = 'map'
        self.map_key = ''
        self.refresh_map()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up and self.map_zoom < 17:
            self.map_zoom += 1
        if event.key() == Qt.Key.Key_Down and self.map_zoom > 0:
            self.map_zoom -= 1
        self.refresh_map()

    def closeEvent(self, event):
        os.remove('tmp.png')
        event.accept()

    def refresh_map(self):
        map_params = {'size': '450,450', 'll': ','.join(map(str, self.map_ll)), 'l': self.map_l, 'z': self.map_zoom}
        response = requests.get('https://static-maps.yandex.ru/1.x/', params=map_params)
        with open('tmp.png', mode='wb') as tmp:
            tmp.write(response.content)

        pixmap = QPixmap()
        pixmap.load('tmp.png')
        self.map_label.setPixmap(pixmap)


def exception_hook(cls, exception, traceback):
    sys.__exception_hook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.__excepthook__ = exception_hook
    sys.exit(app.exec())
