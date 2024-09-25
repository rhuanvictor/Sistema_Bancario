import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow
import db

if __name__ == "__main__":
    db.init_db()

    app = QApplication(sys.argv)

    # Definir o ícone para o aplicativo
    app.setWindowIcon(QIcon("bank.ico"))  # Substitua pelo caminho correto do ícone

    main_window = MainWindow()
    main_window.show()

    sys.exit(app.exec())
