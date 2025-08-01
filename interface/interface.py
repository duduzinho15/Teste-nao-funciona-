# interface.py
import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QListWidgetItem, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette

class ApostaPro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('ApostaPro')
        self.setGeometry(100, 100, 800, 600)
        
        # Configurações de cor
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(20, 20, 30))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        self.setPalette(palette)
        
        # Layout principal
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Painel lateral
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout()
        sidebar.setStyleSheet("background-color: #1A1A2A;")
        
        self.sidebar_title = QLabel("ApostaPro")
        self.sidebar_title.setAlignment(Qt.AlignCenter)
        self.sidebar_title.setStyleSheet("color: white; font-size: 20px;")
        
        self.btn_dashboard = QPushButton("Dashboard")
        self.btn_dashboard.clicked.connect(self.show_dashboard)
        
        self.btn_jogos = QPushButton("Próximos Jogos")
        self.btn_jogos.clicked.connect(self.show_jogos)
        
        self.btn_perfil = QPushButton("Perfil")
        self.btn_perfil.clicked.connect(self.show_perfil)
        
        sidebar_layout.addWidget(self.sidebar_title)
        sidebar_layout.addWidget(self.btn_dashboard)
        sidebar_layout.addWidget(self.btn_jogos)
        sidebar_layout.addWidget(self.btn_perfil)
        sidebar.setLayout(sidebar_layout)
        
        # Conteúdo principal
        self.content = QWidget()
        self.content_layout = QVBoxLayout()
        
        self.dashboard_label = QLabel("Dashboard")
        self.dashboard_label.setAlignment(Qt.AlignCenter)
        self.dashboard_label.setStyleSheet("color: white; font-size: 24px;")
        self.dashboard_label.hide()
        
        self.jogos_label = QLabel("Próximos Jogos")
        self.jogos_label.setAlignment(Qt.AlignCenter)
        self.jogos_label.setStyleSheet("color: white; font-size: 24px;")
        self.jogos_label.hide()
        
        self.perfil_label = QLabel("Perfil")
        self.perfil_label.setAlignment(Qt.AlignCenter)
        self.perfil_label.setStyleSheet("color: white; font-size: 24px;")
        self.perfil_label.hide()
        
        self.content_layout.addWidget(self.dashboard_label)
        self.content_layout.addWidget(self.jogos_label)
        self.content_layout.addWidget(self.perfil_label)
        
        self.content.setLayout(self.content_layout)
        
        # Adicionar widgets ao layout principal
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Carregar jogos
        self.load_jogos()
    
    def load_jogos(self):
        conn = sqlite3.connect("aposta.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM jogos_futuros ORDER BY data LIMIT 10")
        jogos = cursor.fetchall()
        
        conn.close()
        
        self.list_jogos = QListWidget()
        self.list_jogos.setStyleSheet("background-color: #2A2A3A; color: white;")
        
        for jogo in jogos:
            item = QListWidgetItem(f"{jogo[3]} vs {jogo[4]} - {jogo[2]}")
            item.setData(Qt.UserRole, jogo)
            self.list_jogos.addItem(item)
        
        self.content_layout.addWidget(self.list_jogos)
    
    def show_dashboard(self):
        self.dashboard_label.show()
        self.jogos_label.hide()
        self.perfil_label.hide()
    
    def show_jogos(self):
        self.dashboard_label.hide()
        self.jogos_label.show()
        self.perfil_label.hide()
    
    def show_perfil(self):
        self.dashboard_label.hide()
        self.jogos_label.hide()
        self.perfil_label.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ApostaPro()
    ex.show()
    sys.exit(app.exec_())