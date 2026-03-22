"""
JARVIS DASHBOARD - Interfaz gráfica principal
4 paneles: Chat, Code, Tasks, Resources + Panel de dispositivos
"""

import logging
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTextEdit, QLineEdit, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QTabWidget, QTableWidget,
    QTableWidgetItem, QProgressBar
)
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtChart import QChart, QChartView, QLineSeries
from datetime import datetime

logger = logging.getLogger(__name__)


class JarvisDashboard(QMainWindow):
    """Dashboard principal de Jarvis"""
    
    def __init__(self, core):
        super().__init__()
        self.core = core
        self.setWindowTitle("JARVIS FASE 2A - SIMBIOTE")
        self.setGeometry(100, 100, 1600, 900)
        
        # Crear UI
        self.create_ui()
        
        # Timer para actualizar métricas
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(1000)  # Actualizar cada segundo
        
        logger.info("✅ Dashboard creado")
    
    def create_ui(self):
        """Crear interfaz de usuario"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        # 1. Sidebar (izquierda)
        sidebar = self.create_sidebar()
        main_layout.addWidget(sidebar, 1)
        
        # 2. Splitter para 4 paneles principales
        splitter = QSplitter(Qt.Horizontal)
        
        # Chat Panel
        chat_panel = self.create_chat_panel()
        splitter.addWidget(chat_panel)
        
        # Code Panel
        code_panel = self.create_code_panel()
        splitter.addWidget(code_panel)
        
        # Tasks Panel
        tasks_panel = self.create_tasks_panel()
        splitter.addWidget(tasks_panel)
        
        # Resources Panel
        resources_panel = self.create_resources_panel()
        splitter.addWidget(resources_panel)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 2)
        splitter.setStretchFactor(2, 1)
        splitter.setStretchFactor(3, 1)
        
        main_layout.addWidget(splitter, 4)
        
        central_widget.setLayout(main_layout)
    
    def create_sidebar(self):
        """Crear sidebar con opciones"""
        sidebar = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("JARVIS")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)
        
        # Dispositivos
        devices_label = QLabel("📱 Dispositivos")
        devices_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(devices_label)
        
        self.devices_list = QListWidget()
        layout.addWidget(self.devices_list)
        
        # Skills
        skills_label = QLabel("⚡ Skills")
        skills_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(skills_label)
        
        self.skills_list = QListWidget()
        layout.addWidget(self.skills_list)
        
        # Botones
        refresh_btn = QPushButton("🔄 Refrescar")
        refresh_btn.clicked.connect(self.refresh_devices)
        layout.addWidget(refresh_btn)
        
        settings_btn = QPushButton("⚙️ Configuración")
        layout.addWidget(settings_btn)
        
        layout.addStretch()
        sidebar.setLayout(layout)
        return sidebar
    
    def create_chat_panel(self):
        """Crear panel de chat"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("💬 Chat con Jarvis")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Chat display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: Courier;")
        layout.addWidget(self.chat_display)
        
        # Input
        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Escribe tu comando...")
        self.chat_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.chat_input)
        
        send_btn = QPushButton("Enviar")
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
        widget.setLayout(layout)
        return widget
    
    def create_code_panel(self):
        """Crear panel de código"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("💻 Editor de Código")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Editor
        self.code_editor = QTextEdit()
        self.code_editor.setStyleSheet("background-color: #1e1e1e; color: #ffffff; font-family: Courier;")
        layout.addWidget(self.code_editor)
        
        # Botones
        button_layout = QHBoxLayout()
        run_btn = QPushButton("▶️ Ejecutar")
        run_btn.clicked.connect(self.run_code)
        button_layout.addWidget(run_btn)
        
        clear_btn = QPushButton("🗑️ Limpiar")
        clear_btn.clicked.connect(lambda: self.code_editor.clear())
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # Output
        self.code_output = QTextEdit()
        self.code_output.setReadOnly(True)
        self.code_output.setMaximumHeight(150)
        layout.addWidget(self.code_output)
        
        widget.setLayout(layout)
        return widget
    
    def create_tasks_panel(self):
        """Crear panel de tareas"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("✓ Tareas")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # Kanban board (simplificado)
        self.tasks_table = QTableWidget()
        self.tasks_table.setColumnCount(3)
        self.tasks_table.setHorizontalHeaderLabels(["To Do", "In Progress", "Done"])
        layout.addWidget(self.tasks_table)
        
        # Add task
        add_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("Nueva tarea...")
        add_layout.addWidget(self.task_input)
        
        add_btn = QPushButton("➕")
        add_btn.clicked.connect(self.add_task)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        widget.setLayout(layout)
        return widget
    
    def create_resources_panel(self):
        """Crear panel de recursos"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("📊 Recursos")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # CPU
        cpu_label = QLabel("CPU: 0%")
        self.cpu_label = cpu_label
        layout.addWidget(cpu_label)
        
        self.cpu_progress = QProgressBar()
        layout.addWidget(self.cpu_progress)
        
        # RAM
        ram_label = QLabel("RAM: 0 MB")
        self.ram_label = ram_label
        layout.addWidget(ram_label)
        
        self.ram_progress = QProgressBar()
        layout.addWidget(self.ram_progress)
        
        # Disk
        disk_label = QLabel("Disco: 0%")
        self.disk_label = disk_label
        layout.addWidget(disk_label)
        
        self.disk_progress = QProgressBar()
        layout.addWidget(self.disk_progress)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    @pyqtSlot()
    def send_message(self):
        """Enviar mensaje a Jarvis"""
        message = self.chat_input.text()
        if not message:
            return
        
        # Mostrar mensaje del usuario
        self.chat_display.append(f"<span style='color: #00ff00;'>Tú: {message}</span>")
        self.chat_input.clear()
        
        # Procesar con Jarvis
        response = self.core.process_command(message)
        
        # Mostrar respuesta
        self.chat_display.append(f"<span style='color: #00ffff;'>Jarvis: {response}</span>")
    
    @pyqtSlot()
    def run_code(self):
        """Ejecutar código"""
        code = self.code_editor.toPlainText()
        try:
            exec_globals = {}
            exec(code, exec_globals)
            self.code_output.setText("✅ Código ejecutado correctamente")
        except Exception as e:
            self.code_output.setText(f"❌ Error: {str(e)}")
    
    @pyqtSlot()
    def add_task(self):
        """Agregar tarea"""
        task = self.task_input.text()
        if task:
            self.chat_display.append(f"✓ Tarea agregada: {task}")
            self.task_input.clear()
    
    @pyqtSlot()
    def refresh_devices(self):
        """Refrescar lista de dispositivos"""
        self.devices_list.clear()
        devices = self.core.get_devices()
        
        for device_id, device_info in devices.items():
            item = QListWidgetItem(f"📱 {device_info['name']}")
            self.devices_list.addItem(item)
    
    @pyqtSlot()
    def update_metrics(self):
        """Actualizar métricas del sistema"""
        import psutil
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=0.1)
        self.cpu_label.setText(f"CPU: {cpu_percent}%")
        self.cpu_progress.setValue(int(cpu_percent))
        
        # RAM
        ram = psutil.virtual_memory()
        self.ram_label.setText(f"RAM: {ram.used // (1024**2)} MB / {ram.total // (1024**2)} MB")
        self.ram_progress.setValue(int(ram.percent))
        
        # Disk
        disk = psutil.disk_usage('/')
        self.disk_label.setText(f"Disco: {disk.percent}%")
        self.disk_progress.setValue(int(disk.percent))
    
    @pyqtSlot(dict)
    def on_device_discovered(self, device_info):
        """Callback cuando se descubre un dispositivo"""
        logger.info(f"📱 Dispositivo descubierto: {device_info['name']}")
        self.refresh_devices()
    
    @pyqtSlot(dict)
    def on_skill_generated(self, skill_info):
        """Callback cuando se genera una skill"""
        logger.info(f"⚡ Skill generada: {skill_info['name']}")
        self.refresh_devices()
    
    @pyqtSlot(dict)
    def on_message_received(self, message_info):
        """Callback cuando se recibe un mensaje"""
        pass
    
    @pyqtSlot(str)
    def on_sync_status_changed(self, status):
        """Callback cuando cambia el estado de sincronización"""
        logger.info(f"🔄 Sincronización: {status}")
