from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QSpacerItem,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("KiCad Snapshot")
        self.setMinimumSize(920, 560)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(18)

        title = QLabel("KiCad Snapshot")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)

        subtitle = QLabel("Mock: Startup Screen / CLI + Project Selection")
        subtitle.setStyleSheet("color: #666666;")

        root_layout.addWidget(title)
        root_layout.addWidget(subtitle)

        content = QGridLayout()
        content.setHorizontalSpacing(18)
        content.setVerticalSpacing(18)
        root_layout.addLayout(content)

        cli_box = QGroupBox("1) KiCad CLI")
        cli_layout = QVBoxLayout(cli_box)
        cli_layout.setSpacing(10)

        path_row = QHBoxLayout()
        path_label = QLabel("Detected kicad-cli path")
        path_input = QLineEdit("C:/Program Files/KiCad/8.0/bin/kicad-cli.exe")
        path_input.setReadOnly(True)
        browse_btn = QPushButton("Browse...")
        path_row.addWidget(path_label)
        path_row.addWidget(path_input, 1)
        path_row.addWidget(browse_btn)

        status = QLabel("Status: OK (version 8.0.5)")
        status.setStyleSheet("color: #2b7a0b;")

        cli_layout.addLayout(path_row)
        cli_layout.addWidget(status)

        project_box = QGroupBox("2) Project")
        project_layout = QVBoxLayout(project_box)
        project_layout.setSpacing(10)

        project_hint = QLabel("Choose from recent projects or open a new one")
        project_hint.setStyleSheet("color: #666666;")

        recent_list = QListWidget()
        for text in [
            "D:/kicad/board_a/board_a.kicad_pro",
            "D:/kicad/sensor_x/sensor_x.kicad_pro",
            "C:/work/pcb/amp/amp.kicad_pro",
        ]:
            item = QListWidgetItem(text)
            recent_list.addItem(item)

        actions = QHBoxLayout()
        open_btn = QPushButton("Open Project...")
        remove_btn = QPushButton("Remove from list")
        actions.addWidget(open_btn)
        actions.addWidget(remove_btn)
        actions.addItem(QSpacerItem(10, 10))
        actions.addStretch(1)

        project_layout.addWidget(project_hint)
        project_layout.addWidget(recent_list, 1)
        project_layout.addLayout(actions)

        next_box = QGroupBox("3) Next")
        next_layout = QVBoxLayout(next_box)
        next_layout.setSpacing(10)

        next_hint = QLabel(
            "You can proceed only if kicad-cli version is confirmed."
        )
        next_hint.setWordWrap(True)

        proceed_btn = QPushButton("Continue to Snapshot / Compare")
        proceed_btn.setEnabled(False)

        next_layout.addWidget(next_hint)
        next_layout.addWidget(proceed_btn)

        content.addWidget(cli_box, 0, 0)
        content.addWidget(project_box, 1, 0)
        content.addWidget(next_box, 0, 1)

        content.setRowStretch(1, 1)
        content.setColumnStretch(0, 3)
        content.setColumnStretch(1, 2)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #dddddd;")
        root_layout.addWidget(divider)

        footer = QLabel("Mock UI only. No functionality wired yet.")
        footer.setStyleSheet("color: #999999;")
        footer.setAlignment(Qt.AlignRight)
        root_layout.addWidget(footer)

        self.setCentralWidget(root)


def main() -> None:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
