# -*- coding: utf-8 -*-

"""
libs for GUI - https://www.pythonguis.com/faq/pyqt-vs-tkinter/

PyQT library/framework - free-to-use, licensed under GNU General Public License (GPL) v3
 - can be used in commercial apps, users can be charged for copies of the app
 - source code sharing is needed (using GPL libs means derived work) !!!
 - PySide = alternative, where code sharing is not required

script to executable 
- https://www.geeksforgeeks.org/convert-python-script-to-exe-file/
- https://datatofish.com/executable-pyinstaller/
"""


from PyQt6.QtWidgets import QApplication, QWidget


# One (and only one) QApplication instance per application.
app = QApplication([])

# Create a Qt widget, which will be our window.
window = QWidget()
window.show()  # widgets without a parent are invisible by default

# Start the event loop.
app.exec()
