from UI import *
import cv2
from PyQt5.QtWidgets import QApplication
import sys






if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PowerConsumptionApp()
    window.show()
    sys.exit(app.exec_())

    # Release resources when the application closes
    cap.release()