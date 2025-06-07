"""
Augment VIP GUI Application
Modern PyQt6-based interface for VS Code management tools
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QLabel, QComboBox, QTextEdit,
                            QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QLinearGradient, QBrush, QPainter, QColor, QPen
from core_functions import (close_vscode, clean_vscode_database, 
                           modify_telemetry_ids, run_all_operations)


class GradientLabel(QLabel):
    """Custom label with animated gradient text"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.gradient_offset = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_gradient)
        self.timer.start(50)  # Update every 50ms for smooth animation
        
    def update_gradient(self):
        self.gradient_offset = (self.gradient_offset + 1) % 360
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Create gradient
        gradient = QLinearGradient(0, 0, self.width(), 0)
        
        # Animated colors
        hue1 = (self.gradient_offset) % 360
        hue2 = (self.gradient_offset + 120) % 360
        hue3 = (self.gradient_offset + 240) % 360
        
        gradient.setColorAt(0, QColor.fromHsv(hue1, 200, 255))
        gradient.setColorAt(0.5, QColor.fromHsv(hue2, 200, 255))
        gradient.setColorAt(1, QColor.fromHsv(hue3, 200, 255))
        
        painter.setPen(QPen(QBrush(gradient), 2))
        
        font = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font)
        
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())


class WorkerThread(QThread):
    """Worker thread for running operations without blocking UI"""
    finished = pyqtSignal(bool, str)
    
    def __init__(self, operation):
        super().__init__()
        self.operation = operation
        
    def run(self):
        try:
            success, message = self.operation()
            self.finished.emit(success, message)
        except Exception as e:
            self.finished.emit(False, f"Error: {str(e)}")


class AugmentVIPGUI(QMainWindow):
    """Main GUI application window"""
    
    def __init__(self):
        super().__init__()
        self.current_language = "en"
        self.translations = {
            "en": {
                "title": "Augment-VIP",
                "welcome": "Welcome",
                "language": "Language",
                "fix_all_config": "Fix All VSCode Config",
                "close_vscode": "Close VSCode",
                "clean_database": "Clean VSCode Database",
                "modify_telemetry": "Modify VSCode Telemetry ID",
                "version": "v0.0.1",
                "working": "Working...",
                "success": "Success",
                "error": "Error",
                "operation_completed": "Operation completed successfully!",
                "operation_failed": "Operation failed!",
                "confirm_close": "This will close all VS Code windows. Continue?",
                "confirm_all": "This will close VS Code and modify all configurations. Continue?"
            },
            "zh": {
                "title": "Augment-VIP",
                "welcome": "欢迎使用",
                "language": "语言",
                "fix_all_config": "一键修改所有配置",
                "close_vscode": "关闭VSCode",
                "clean_database": "清理VSCode数据库",
                "modify_telemetry": "修改VSCode遥测ID",
                "version": "v0.0.1",
                "working": "处理中...",
                "success": "成功",
                "error": "错误",
                "operation_completed": "操作成功完成！",
                "operation_failed": "操作失败！",
                "confirm_close": "这将关闭所有VS Code窗口。继续吗？",
                "confirm_all": "这将关闭VS Code并修改所有配置。继续吗？"
            }
        }
        self.init_ui()
        
    def tr(self, key):
        """Get translated text"""
        return self.translations[self.current_language].get(key, key)
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Augment-VIP")
        self.setFixedSize(420, 620)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f0f0f0, stop:1 #e0e0e0);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6c5ce7, stop:1 #5a4fcf);
                color: white;
                border: none;
                border-radius: 15px;
                padding: 12px 20px;
                font-size: 13px;
                font-weight: bold;
                margin: 5px;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7c6ce7, stop:1 #6a5fcf);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5c4ce7, stop:1 #4a3fcf);
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
            QComboBox {
                background: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                min-height: 16px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #666;
                margin-right: 5px;
            }
            QTextEdit {
                background: white;
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
            QLabel {
                color: #333;
            }
        """)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Language selector
        lang_layout = QHBoxLayout()
        lang_layout.addStretch()

        lang_label = QLabel(self.tr("language") + ":")
        lang_label.setFont(QFont("Arial", 10))
        lang_label.setStyleSheet("color: #666; margin-right: 5px;")

        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["English", "中文"])
        self.lang_combo.setFixedWidth(100)
        self.lang_combo.currentTextChanged.connect(self.change_language)

        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # Title with gradient animation
        self.title_label = GradientLabel(self.tr("title"))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFixedHeight(60)
        layout.addWidget(self.title_label)
        
        # Welcome text
        self.welcome_label = QLabel(self.tr("welcome"))
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.welcome_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.welcome_label)
        
        # Buttons
        self.fix_all_btn = QPushButton(self.tr("fix_all_config"))
        self.fix_all_btn.clicked.connect(self.fix_all_config)
        self.fix_all_btn.setMinimumHeight(45)
        layout.addWidget(self.fix_all_btn)

        self.close_vscode_btn = QPushButton(self.tr("close_vscode"))
        self.close_vscode_btn.clicked.connect(self.close_vscode_action)
        self.close_vscode_btn.setMinimumHeight(45)
        layout.addWidget(self.close_vscode_btn)

        self.clean_db_btn = QPushButton(self.tr("clean_database"))
        self.clean_db_btn.clicked.connect(self.clean_database)
        self.clean_db_btn.setMinimumHeight(45)
        layout.addWidget(self.clean_db_btn)

        self.modify_id_btn = QPushButton(self.tr("modify_telemetry"))
        self.modify_id_btn.clicked.connect(self.modify_telemetry)
        self.modify_id_btn.setMinimumHeight(45)
        layout.addWidget(self.modify_id_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 8px;
                text-align: center;
                background: white;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6c5ce7, stop:1 #5a4fcf);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Output text area
        self.output_text = QTextEdit()
        self.output_text.setMaximumHeight(150)
        self.output_text.setPlaceholderText("Operation results will appear here...")
        layout.addWidget(self.output_text)
        
        # Version label
        self.version_label = QLabel(self.tr("version"))
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.version_label.setFont(QFont("Arial", 10))
        self.version_label.setStyleSheet("color: #888;")
        layout.addWidget(self.version_label)
        
    def change_language(self, language):
        """Change the interface language"""
        if language == "中文":
            self.current_language = "zh"
        else:
            self.current_language = "en"
        self.update_ui_text()
        
    def update_ui_text(self):
        """Update all UI text with current language"""
        self.welcome_label.setText(self.tr("welcome"))
        self.fix_all_btn.setText(self.tr("fix_all_config"))
        self.close_vscode_btn.setText(self.tr("close_vscode"))
        self.clean_db_btn.setText(self.tr("clean_database"))
        self.modify_id_btn.setText(self.tr("modify_telemetry"))
        self.version_label.setText(self.tr("version"))
        
    def set_buttons_enabled(self, enabled):
        """Enable or disable all buttons"""
        self.fix_all_btn.setEnabled(enabled)
        self.close_vscode_btn.setEnabled(enabled)
        self.clean_db_btn.setEnabled(enabled)
        self.modify_id_btn.setEnabled(enabled)
        
    def show_progress(self, show=True):
        """Show or hide progress bar"""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            
    def run_operation(self, operation, confirm_message=None):
        """Run an operation in a separate thread"""
        if confirm_message:
            reply = QMessageBox.question(self, "Confirm", confirm_message,
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply != QMessageBox.StandardButton.Yes:
                return
                
        self.set_buttons_enabled(False)
        self.show_progress(True)
        self.output_text.append(f"\n{self.tr('working')}")
        
        self.worker = WorkerThread(operation)
        self.worker.finished.connect(self.operation_finished)
        self.worker.start()
        
    def operation_finished(self, success, message):
        """Handle operation completion"""
        self.set_buttons_enabled(True)
        self.show_progress(False)
        
        if success:
            self.output_text.append(f"\n✅ {self.tr('success')}: {message}")
            QMessageBox.information(self, self.tr("success"), self.tr("operation_completed"))
        else:
            self.output_text.append(f"\n❌ {self.tr('error')}: {message}")
            QMessageBox.critical(self, self.tr("error"), self.tr("operation_failed"))
            
    def fix_all_config(self):
        """Fix all VS Code configuration"""
        self.run_operation(run_all_operations, self.tr("confirm_all"))
        
    def close_vscode_action(self):
        """Close VS Code"""
        self.run_operation(close_vscode, self.tr("confirm_close"))
        
    def clean_database(self):
        """Clean VS Code database"""
        self.run_operation(clean_vscode_database)
        
    def modify_telemetry(self):
        """Modify telemetry IDs"""
        self.run_operation(modify_telemetry_ids)


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("Augment-VIP")
    app.setApplicationVersion("0.0.1")
    
    window = AugmentVIPGUI()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
