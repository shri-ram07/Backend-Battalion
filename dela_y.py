

from PyQt5.QtCore import QTimer, QEventLoop


def delay(delay_time_in_ms):
    loop = QEventLoop()  # Create a local event loop
    timer = QTimer()
    timer.timeout.connect(loop.quit)  # Quit the loop after timeout
    timer.start(delay_time_in_ms)  # Start the timer
    loop.exec_()  # Execute the local event loop

