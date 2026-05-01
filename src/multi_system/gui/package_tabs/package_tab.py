"""
Tab: 包管理器
"""

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from multi_system.program.packages.package_manager import PackageManager


class PackageTab(QWidget):
    def __init__(self):
        super().__init__()
        self._loaded = False
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # --- Manager selector ---
        top = QHBoxLayout()
        top.addWidget(QLabel("包管理器:"))
        self._manager_combo = QComboBox()
        self._manager_combo.setMinimumWidth(120)
        top.addWidget(self._manager_combo)
        self._detect_btn = QPushButton("检测")
        self._detect_btn.clicked.connect(self._detect_managers)
        top.addWidget(self._detect_btn)
        top.addStretch()
        layout.addLayout(top)

        # --- Search / Install ---
        search_row = QHBoxLayout()
        search_row.addWidget(QLabel("搜索/安装:"))
        self._pkg_edit = QLineEdit()
        self._pkg_edit.setPlaceholderText("包名...")
        search_row.addWidget(self._pkg_edit)
        self._search_btn = QPushButton("搜索包")
        self._search_btn.clicked.connect(self._search_package)
        search_row.addWidget(self._search_btn)
        self._install_btn = QPushButton("安装")
        self._install_btn.clicked.connect(self._install_package)
        search_row.addWidget(self._install_btn)
        layout.addLayout(search_row)

        # --- Toolbar ---
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.addAction("刷新", self._force_refresh)
        toolbar.addAction("列出已安装", self._list_packages)
        layout.addWidget(toolbar)

        # --- Table ---
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["包名", "版本", "管理器"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

        # --- Status ---
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._detect_managers()

    def _force_refresh(self):
        self._list_packages()

    def _detect_managers(self):
        self._manager_combo.clear()
        managers = PackageManager.detect_managers()
        for m in managers:
            self._manager_combo.addItem(m)
        if managers:
            self._status_label.setText(f"检测到 {len(managers)} 个包管理器: {', '.join(managers)}")
        else:
            self._status_label.setText("未检测到包管理器")

    def _list_packages(self):
        manager = self._manager_combo.currentText()
        if not manager:
            QMessageBox.information(self, "提示", "请先选择一个包管理器")
            return
        self._status_label.setText(f"正在列出 {manager} 已安装包...")
        pkgs = PackageManager.list_packages(manager)
        self._show_packages(pkgs)
        self._status_label.setText(f"{manager}: 共 {len(pkgs)} 个已安装包")

    def _search_package(self):
        manager = self._manager_combo.currentText()
        keyword = self._pkg_edit.text().strip()
        if not manager:
            QMessageBox.information(self, "提示", "请先选择一个包管理器")
            return
        if not keyword:
            return
        self._status_label.setText(f"正在搜索 {keyword}...")
        pkgs = PackageManager.search_package(manager, keyword)
        self._show_packages(pkgs)
        self._status_label.setText(f"搜索到 {len(pkgs)} 个结果")

    def _install_package(self):
        manager = self._manager_combo.currentText()
        package = self._pkg_edit.text().strip()
        if not manager:
            QMessageBox.information(self, "提示", "请先选择一个包管理器")
            return
        if not package:
            QMessageBox.information(self, "提示", "请输入包名")
            return
        reply = QMessageBox.warning(
            self,
            "确认安装",
            f"确定要使用 {manager} 安装 {package} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._status_label.setText(f"正在安装 {package}...")
        success = PackageManager.install(manager, package)
        if success:
            QMessageBox.information(self, "成功", f"{package} 安装成功")
            self._list_packages()
        else:
            QMessageBox.warning(self, "失败", f"{package} 安装失败")

    def _show_packages(self, pkgs):
        self._table.setRowCount(0)
        for p in pkgs:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(p.name))
            self._table.setItem(row, 1, QTableWidgetItem(p.version))
            self._table.setItem(row, 2, QTableWidgetItem(p.manager))
