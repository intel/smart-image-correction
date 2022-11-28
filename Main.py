import sys
from PyQt5.QtWidgets import QApplication, QMainWindow,QDialog
import ImageAlignment
from Display import Display
import ImgEnhance

class parentWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.main_ui = ImageAlignment.Ui_MainWindow()
        self.main_ui.setupUi(self)

class childWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child=ImgEnhance.Ui_Dialog()
        self.child.setupUi(self)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = parentWindow()
    child = childWindow()

    btn = window.main_ui.imgEnhance_button
    btn.clicked.connect(child.show)

    display = Display(window.main_ui, window, child.child,child)
    
    window.show()
    sys.exit(app.exec_())




