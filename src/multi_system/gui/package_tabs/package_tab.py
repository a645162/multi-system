"""
Tab: 包管理器
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
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
        toolbar.addSeparator()
        toolbar.addAction("卸载", self._uninstall_selected)
        toolbar.addAction("更新", self._update_selected)
        toolbar.addAction("全部更新", self._update_all)
        layout.addWidget(toolbar)

        # --- Table ---
        self._table = QTableWidget(0, 3)
        self._table.setHorizontalHeaderLabels(["包名", "版本", "管理器"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._table)

        # --- Status ---
        self._status_label = QLabel("")
        layout.addWidget(self._status_label)

    def showEvent(self, event):
        super().showEvent(event)
        if not self._loaded:
            self._loaded = True
            self._detect_managers()

    # --- Context menu ---

    def _show_context_menu(self, pos):
        row = self._table.rowAt(pos.y())
        if row < 0:
            return
        self._table.selectRow(row)

        menu = QMenu(self)

        install_action = menu.addAction("安装")
        install_action.triggered.connect(self._install_package)

        uninstall_action = menu.addAction("卸载")
        uninstall_action.triggered.connect(self._uninstall_selected)

        update_action = menu.addAction("更新")
        update_action.triggered.connect(self._update_selected)

        menu.addSeparator()

        copy_name_action = menu.addAction("复制包名")
        pkg_name = self._table.item(row, 0).text() if self._table.item(row, 0) else ""
        copy_name_action.triggered.connect(lambda: self._copy_to_clipboard(pkg_name))

        detail_action = menu.addAction("显示详情")
        detail_action.triggered.connect(lambda: self._show_package_detail(row))

        menu.exec(self._table.viewport().mapToGlobal(pos))

    def _copy_to_clipboard(self, text: str):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(text)

    def _show_package_detail(self, row: int):
        name = self._table.item(row, 0).text() if self._table.item(row, 0) else ""
        version = self._table.item(row, 1).text() if self._table.item(row, 1) else ""
        manager = self._table.item(row, 2).text() if self._table.item(row, 2) else ""
        QMessageBox.information(
            self, "包详情",
            f"包名: {name}\n版本: {version}\n管理器: {manager}",
        )

    # --- Existing methods ---

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

    # --- New toolbar/context actions ---

    def _uninstall_selected(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "提示", "请先选择一个包")
            return
        row = rows[0].row()
        package = self._table.item(row, 0).text() if self._table.item(row, 0) else ""
        manager = self._table.item(row, 2).text() if self._table.item(row, 2) else ""
        if not package or not manager:
            return
        reply = QMessageBox.warning(
            self,
            "确认卸载",
            f"确定要使用 {manager} 卸载 {package} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._status_label.setText(f"正在卸载 {package}...")
        success = PackageManager.uninstall(manager, package)
        if success:
            QMessageBox.information(self, "成功", f"{package} 卸载成功")
            self._list_packages()
        else:
            QMessageBox.warning(self, "失败", f"{package} 卸载失败")

    def _update_selected(self):
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "提示", "请先选择一个包")
            return
        row = rows[0].row()
        package = self._table.item(row, 0).text() if self._table.item(row, 0) else ""
        manager = self._table.item(row, 2).text() if self._table.item(row, 2) else ""
        if not package or not manager:
            return
        reply = QMessageBox.warning(
            self,
            "确认更新",
            f"确定要使用 {manager} 更新 {package} 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._status_label.setText(f"正在更新 {package}...")
        success = PackageManager.update(manager, package)
        if success:
            QMessageBox.information(self, "成功", f"{package} 更新成功")
            self._list_packages()
        else:
            QMessageBox.warning(self, "失败", f"{package} 更新失败")

    def _update_all(self):
        manager = self._manager_combo.currentText()
        if not manager:
            QMessageBox.information(self, "提示", "请先选择一个包管理器")
            return
        reply = QMessageBox.warning(
            self,
            "确认全部更新",
            f"确定要使用 {manager} 更新所有包吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        self._status_label.setText("正在更新所有包...")
        success = PackageManager.update(manager)
        if success:
            QMessageBox.information(self, "成功", "全部更新成功")
            self._list_packages()
        else:
            QMessageBox.warning(self, "失败", "全部更新失败")

    def _show_packages(self, pkgs):
        self._table.setRowCount(0)
        for p in pkgs:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(p.name))
            self._table.setItem(row, 1, QTableWidgetItem(p.version))
            self._table.setItem(row, 2, QTableWidgetItem(p.manager))
