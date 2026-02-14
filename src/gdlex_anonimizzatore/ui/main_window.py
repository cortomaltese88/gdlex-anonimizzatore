from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QAction, QDesktopServices, QFont, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QDialog,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from gdlex_anonimizzatore.core.anonymize import apply_replacements
from gdlex_anonimizzatore.core.models import EntityFinding, EntityType, FileJob, FileStatus, Settings
from gdlex_anonimizzatore.core.recognizers import REPLACEMENT_BY_TYPE, detect_entities
from gdlex_anonimizzatore.core.report import generate_report
from gdlex_anonimizzatore.ui.state_helpers import file_actions_enabled, has_resettable_state


APP_DARK_QSS = """
QWidget {
    background-color: #1e1e1e;
    color: #e6e6e6;
}
QMainWindow {
    background-color: #1e1e1e;
}
QLabel {
    color: #e6e6e6;
}
QGroupBox {
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    margin-top: 8px;
    padding: 8px;
    font-weight: 600;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}
QPushButton {
    min-height: 30px;
    padding: 4px 12px;
    border: 1px solid #4b4b4b;
    border-radius: 4px;
    background-color: #2a2a2a;
    color: #ececec;
}
QPushButton:hover {
    background-color: #353535;
}
QPushButton:pressed {
    background-color: #1f1f1f;
}
QPushButton[variant="primary"] {
    background-color: #2d6cdf;
    border-color: #3e74d4;
    color: #ffffff;
}
QPushButton[variant="primary"]:hover {
    background-color: #3b79e6;
}
QPushButton[variant="primary"]:pressed {
    background-color: #2557b3;
}
QPushButton[variant="secondary"] {
    background-color: #3a3a3a;
    border-color: #5b5b5b;
    color: #f0f0f0;
}
QPushButton[variant="secondary"]:hover {
    background-color: #474747;
}
QPushButton[variant="secondary"]:pressed {
    background-color: #2f2f2f;
}
QPushButton[variant="danger"] {
    background-color: #a83a3a;
    border-color: #bf4d4d;
    color: #ffffff;
}
QPushButton[variant="danger"]:hover {
    background-color: #bf4d4d;
}
QPushButton[variant="danger"]:pressed {
    background-color: #8f2e2e;
}
QTableWidget {
    gridline-color: #3a3a3a;
    alternate-background-color: #242424;
    background-color: #1b1b1b;
    selection-background-color: #2d6cdf;
    selection-color: #ffffff;
    border: 1px solid #3a3a3a;
}
QTableWidget::item {
    padding: 6px;
}
QHeaderView::section {
    background-color: #2b2b2b;
    color: #f0f0f0;
    border: 1px solid #3c3c3c;
    padding: 7px 8px;
    font-weight: 600;
}
QPlainTextEdit, QTextEdit {
    background-color: #151515;
    color: #dcdcdc;
    border: 1px solid #3a3a3a;
}
QProgressBar {
    border: 1px solid #3b3b3b;
    border-radius: 4px;
    text-align: center;
    background: #1a1a1a;
    color: #e6e6e6;
}
QProgressBar::chunk {
    background-color: #2d6cdf;
}
"""


class ReviewDialog(QDialog):
    def __init__(self, job: FileJob, settings: Settings, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.job = job
        self.settings = settings
        self.setWindowTitle(f"Revisione entità - {job.input_path.name}")
        self.resize(900, 480)

        layout = QVBoxLayout(self)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Valore originale", "Tipo", "Sostituzione", "Anonimizza"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        layout.addWidget(self.table)

        btn_row = QHBoxLayout()
        add_btn = QPushButton("Aggiungi riga")
        add_btn.clicked.connect(self.add_manual_row)
        remove_btn = QPushButton("Rimuovi riga")
        remove_btn.clicked.connect(self.remove_selected)
        whitelist_btn = QPushButton("Aggiungi a whitelist sessione")
        whitelist_btn.clicked.connect(self.add_to_whitelist)
        save_btn = QPushButton("Salva")
        save_btn.clicked.connect(self.accept)
        btn_row.addWidget(add_btn)
        btn_row.addWidget(remove_btn)
        btn_row.addWidget(whitelist_btn)
        btn_row.addStretch()
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

        self.load_findings()

    def load_findings(self) -> None:
        self.table.setRowCount(0)
        for finding in self.job.findings:
            self._add_row(finding)

    def _add_row(self, finding: EntityFinding) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(finding.value))
        self.table.setItem(row, 1, QTableWidgetItem(finding.entity_type.value))
        self.table.setItem(row, 2, QTableWidgetItem(finding.replacement))
        chk = QCheckBox()
        chk.setChecked(finding.anonymize)
        self.table.setCellWidget(row, 3, chk)

    def add_manual_row(self) -> None:
        finding = EntityFinding(value="", entity_type=EntityType.MANUALE, start=0, end=0, replacement="[MASK]", manual=True)
        self._add_row(finding)

    def remove_selected(self) -> None:
        rows = sorted({idx.row() for idx in self.table.selectedIndexes()}, reverse=True)
        for row in rows:
            self.table.removeRow(row)

    def add_to_whitelist(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            return
        value_item = self.table.item(row, 0)
        if value_item and value_item.text().strip():
            self.settings.session_whitelist.add(value_item.text().strip())

    def get_findings(self) -> list[EntityFinding]:
        out: list[EntityFinding] = []
        for row in range(self.table.rowCount()):
            value = (self.table.item(row, 0).text() if self.table.item(row, 0) else "").strip()
            type_text = (self.table.item(row, 1).text() if self.table.item(row, 1) else "MANUALE").strip()
            repl = (self.table.item(row, 2).text() if self.table.item(row, 2) else "").strip()
            chk = self.table.cellWidget(row, 3)
            anonymize = bool(chk.isChecked()) if isinstance(chk, QCheckBox) else True
            if not value:
                continue
            try:
                entity_type = EntityType(type_text)
            except ValueError:
                entity_type = EntityType.MANUALE
            start = self.job.original_text.find(value)
            end = start + len(value) if start >= 0 else 0
            out.append(
                EntityFinding(
                    value=value,
                    entity_type=entity_type,
                    start=start,
                    end=end,
                    replacement=repl or REPLACEMENT_BY_TYPE.get(entity_type, "[MASK]"),
                    anonymize=anonymize,
                    manual=(entity_type == EntityType.MANUALE),
                )
            )
        return out


class AIAssistDialog(QDialog):
    def __init__(self, output_path: Path, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.output_path = output_path
        self.setWindowTitle("AI Assist (manuale)")
        self.resize(800, 600)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Prompt suggerito"))
        self.prompt_box = QTextEdit()
        self.prompt_box.setPlainText(
            "Questo testo è già anonimizzato. Rifinisci solo stile e chiarezza senza reintrodurre dati personali."
        )
        layout.addWidget(self.prompt_box)

        layout.addWidget(QLabel("Incolla qui il testo rifinito da ChatGPT"))
        self.refined_box = QTextEdit()
        layout.addWidget(self.refined_box)

        save_btn = QPushButton("Salva come _anonimizzato_ai")
        save_btn.clicked.connect(self.save_ai_output)
        layout.addWidget(save_btn)

    def save_ai_output(self) -> None:
        refined = self.refined_box.toPlainText()
        if not refined.strip():
            QMessageBox.warning(self, "AI assist", "Incolla prima il testo rifinito.")
            return
        target = self.output_path.with_name(f"{self.output_path.stem}_ai{self.output_path.suffix}")
        target.write_text(refined, encoding="utf-8")
        QMessageBox.information(self, "AI assist", f"Salvato: {target}")
        self.accept()


class DropTableWidget(QTableWidget):
    def __init__(self, parent: "MainWindow") -> None:
        super().__init__(0, 6, parent)
        self.main_window = parent
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def dragEnterEvent(self, event):  # type: ignore[override]
        if self.main_window.has_valid_drop(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):  # type: ignore[override]
        if self.main_window.has_valid_drop(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):  # type: ignore[override]
        self.main_window.handle_drop(event)


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = Settings()
        self.jobs: list[FileJob] = []
        self.is_busy = False
        self.setWindowTitle("GDLEX Anonimizzatore v0.1")
        self.resize(1200, 760)
        self.setAcceptDrops(True)
        self._build_ui()
        self._build_menu()

    def _build_ui(self) -> None:
        central = QWidget()
        main_layout = QVBoxLayout(central)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Aggiungi file")
        self.btn_remove = QPushButton("Rimuovi selezionati")
        self.btn_analyze = QPushButton("Analizza")
        self.btn_execute = QPushButton("Esegui")
        self.btn_reset = QPushButton("Pulisci")
        self.btn_output = QPushButton("Scegli output folder")
        self.btn_open_output = QPushButton("Apri cartella output")
        self.btn_report = QPushButton("Genera report")
        self.btn_ai = QPushButton("AI assist (manuale)")

        self.btn_add.setProperty("variant", "secondary")
        self.btn_analyze.setProperty("variant", "primary")
        self.btn_execute.setProperty("variant", "primary")
        self.btn_reset.setProperty("variant", "danger")
        for btn in [
            self.btn_add,
            self.btn_remove,
            self.btn_analyze,
            self.btn_execute,
            self.btn_reset,
            self.btn_output,
            self.btn_open_output,
            self.btn_report,
            self.btn_ai,
        ]:
            btn_layout.addWidget(btn)
        main_layout.addLayout(btn_layout)

        self.table = DropTableWidget(self)
        self.table.setHorizontalHeaderLabels(["File", "Tipo", "Stato", "Entità trovate", "Output", "Apri"])
        self.table.setAlternatingRowColors(True)
        self.table.setMinimumWidth(900)
        self.table.setColumnWidth(0, 360)
        self.table.setColumnWidth(4, 280)

        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        main_layout.addWidget(self.table)

        self.progress = QProgressBar()
        self.status_lbl = QLabel("Pronto")
        main_layout.addWidget(self.progress)
        main_layout.addWidget(self.status_lbl)

        self.log_box = QPlainTextEdit()
        self.log_box.setReadOnly(True)
        mono_font = QFont("Monospace")
        mono_font.setStyleHint(QFont.StyleHint.Monospace)
        mono_font.setPointSizeF(10.5)
        self.log_box.setFont(mono_font)

        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout(log_group)
        toggle_row = QHBoxLayout()
        self.toggle_log_btn = QToolButton()
        self.toggle_log_btn.setText("Nascondi")
        self.toggle_log_btn.clicked.connect(self.toggle_log)
        toggle_row.addWidget(self.toggle_log_btn)
        toggle_row.addStretch()
        log_layout.addLayout(toggle_row)
        log_layout.addWidget(self.log_box)
        main_layout.addWidget(log_group)

        self.setCentralWidget(central)

        self.btn_add.clicked.connect(self.pick_files)
        self.btn_remove.clicked.connect(self.remove_selected)
        self.btn_analyze.clicked.connect(self.analyze_jobs)
        self.btn_execute.clicked.connect(self.execute_jobs)
        self.btn_reset.clicked.connect(self.reset_session)
        self.btn_output.clicked.connect(self.choose_output)
        self.btn_open_output.clicked.connect(self.open_output_folder)
        self.btn_report.clicked.connect(self.create_report)
        self.btn_ai.clicked.connect(self.ai_assist)
        self.update_action_states()

    def _build_menu(self) -> None:
        menu_file = self.menuBar().addMenu("File")
        close_action = QAction("Esci", self)
        close_action.triggered.connect(self.close)
        menu_file.addAction(close_action)

        menu_help = self.menuBar().addMenu("Aiuto")
        about_action = QAction("Informazioni...", self)
        about_action.triggered.connect(self.show_about_dialog)
        menu_help.addAction(about_action)

    def show_about_dialog(self) -> None:
        try:
            app_version = version("gdlex-anonimizzatore")
        except PackageNotFoundError:
            app_version = "0.1.0"
        QMessageBox.information(
            self,
            "Informazioni",
            f"GDLEX Anonimizzatore\nVersione: {app_version}\nSTUDIO GD LEX",
        )

    def update_action_states(self) -> None:
        enabled = file_actions_enabled(len(self.jobs), self.is_busy)
        self.btn_remove.setEnabled(enabled)
        self.btn_analyze.setEnabled(enabled)
        self.btn_execute.setEnabled(enabled)
        self.btn_output.setEnabled(enabled)
        self.btn_open_output.setEnabled(enabled)
        self.btn_report.setEnabled(enabled)
        self.btn_ai.setEnabled(enabled)
        self.btn_reset.setEnabled(not self.is_busy)

    def dragEnterEvent(self, event):  # type: ignore[override]
        if self.has_valid_drop(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):  # type: ignore[override]
        if self.has_valid_drop(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):  # type: ignore[override]
        self.handle_drop(event)

    def has_valid_drop(self, event) -> bool:
        mime_data = event.mimeData()
        if not mime_data or not mime_data.hasUrls():
            return False
        for url in mime_data.urls():
            if url.isLocalFile() and Path(url.toLocalFile()).suffix.lower() == ".txt":
                return True
        return False

    def handle_drop(self, event) -> None:
        paths = self._extract_txt_paths_from_event(event)
        added = self.add_files(paths)
        if added > 0:
            self.log(f"Drop: aggiunti {added} file")
            event.acceptProposedAction()
        else:
            self.log("Drop: nessun file valido")
            event.ignore()

    def _extract_txt_paths_from_event(self, event) -> list[Path]:
        mime_data = event.mimeData()
        if not mime_data or not mime_data.hasUrls():
            return []
        return [
            Path(url.toLocalFile())
            for url in mime_data.urls()
            if url.isLocalFile() and Path(url.toLocalFile()).suffix.lower() == ".txt"
        ]

    def log(self, message: str) -> None:
        self.log_box.appendPlainText(message)

    def toggle_log(self) -> None:
        visible = self.log_box.isVisible()
        self.log_box.setVisible(not visible)
        self.toggle_log_btn.setText("Mostra" if visible else "Nascondi")

    def pick_files(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Seleziona file TXT", "", "Text files (*.txt)")
        added = self.add_files([Path(f) for f in files])
        if files:
            self.log(f"Picker: aggiunti {added} file")

    def add_files(self, paths: list[Path]) -> int:
        added = 0
        for path in paths:
            if path.suffix.lower() != ".txt":
                continue
            if any(job.input_path == path for job in self.jobs):
                continue
            self.jobs.append(FileJob(input_path=path))
            added += 1
        if added:
            self.refresh_table()
            self.update_action_states()
        return added

    def remove_selected(self) -> None:
        rows = sorted({idx.row() for idx in self.table.selectedIndexes()}, reverse=True)
        for row in rows:
            self.jobs.pop(row)
        self.refresh_table()
        self.update_action_states()

    def reset_session(self) -> None:
        if self.is_busy:
            QMessageBox.warning(self, "Reset", "Operazione in corso")
            return

        should_confirm = has_resettable_state(
            len(self.jobs),
            bool(self.log_box.toPlainText().strip()),
            self.progress.value(),
            self.status_lbl.text(),
        )
        if should_confirm:
            answer = QMessageBox.question(
                self,
                "Conferma reset",
                "Vuoi davvero pulire lo stato della sessione corrente?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                return

        self.jobs.clear()
        self.settings.session_whitelist.clear()
        self.settings.societa_session_mapping.clear()
        self.settings.output_folder = None
        self.table.clearContents()
        self.table.setRowCount(0)
        self.progress.setValue(0)
        self.status_lbl.setText("Pronto")
        self.log_box.clear()
        self.log("Stato resettato.")
        self.update_action_states()

    def refresh_table(self) -> None:
        self.table.setRowCount(0)
        for idx, job in enumerate(self.jobs):
            self.table.insertRow(idx)
            self.table.setItem(idx, 0, QTableWidgetItem(str(job.input_path)))
            self.table.setItem(idx, 1, QTableWidgetItem(job.file_type))
            self.table.setItem(idx, 2, QTableWidgetItem(job.status.value))
            self.table.setItem(idx, 3, QTableWidgetItem(str(len(job.findings))))
            self.table.setItem(idx, 4, QTableWidgetItem(str(job.output_path) if job.output_path else ""))
            open_btn = QPushButton("Apri")
            open_btn.clicked.connect(lambda _, p=job.output_path: self.open_file(p))
            self.table.setCellWidget(idx, 5, open_btn)

    def _target_jobs(self) -> list[FileJob]:
        selected_rows = sorted({idx.row() for idx in self.table.selectedIndexes()})
        if not selected_rows:
            return self.jobs
        return [self.jobs[row] for row in selected_rows if 0 <= row < len(self.jobs)]

    def analyze_jobs(self) -> None:
        targets = self._target_jobs()
        total = len(targets)
        if not total:
            return
        self.is_busy = True
        self.update_action_states()
        self.progress.setRange(0, total)
        try:
            for i, job in enumerate(targets, start=1):
                try:
                    job.original_text = job.input_path.read_text(encoding="utf-8")
                    job.findings = detect_entities(job.original_text, self.settings)
                    job.status = FileStatus.ANALYZED
                    self.status_lbl.setText(f"Analizzato: {job.input_path.name}")
                    dlg = ReviewDialog(job, self.settings, self)
                    if dlg.exec():
                        job.findings = dlg.get_findings()
                except Exception as exc:  # noqa: BLE001
                    job.status = FileStatus.ERROR
                    job.error = str(exc)
                    self.log(f"Errore analisi {job.input_path}: {exc}")
                self.progress.setValue(i)
        finally:
            self.is_busy = False
            self.refresh_table()
            self.update_action_states()

    def execute_jobs(self) -> None:
        targets = self._target_jobs()
        total = len(targets)
        if not total:
            return
        self.is_busy = True
        self.update_action_states()
        self.progress.setRange(0, total)
        try:
            for i, job in enumerate(targets, start=1):
                try:
                    if job.status not in {FileStatus.ANALYZED, FileStatus.PROCESSED}:
                        job.status = FileStatus.SKIPPED
                        job.error = "File non analizzato"
                        continue
                    text = job.original_text or job.input_path.read_text(encoding="utf-8")
                    processed = apply_replacements(text, job.findings)
                    out_dir = self.settings.output_folder or job.input_path.parent
                    out_dir.mkdir(parents=True, exist_ok=True)
                    output_name = f"{job.input_path.stem}_anonimizzato{job.input_path.suffix}"
                    output_path = out_dir / output_name
                    output_path.write_text(processed, encoding="utf-8")
                    job.output_path = output_path
                    job.status = FileStatus.PROCESSED
                    self.status_lbl.setText(f"Elaborato: {job.input_path.name}")
                except Exception as exc:  # noqa: BLE001
                    job.status = FileStatus.ERROR
                    job.error = str(exc)
                    self.log(f"Errore esecuzione {job.input_path}: {exc}")
                self.progress.setValue(i)
        finally:
            self.is_busy = False
            self.refresh_table()
            self.update_action_states()

    def choose_output(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella output")
        if folder:
            self.settings.output_folder = Path(folder)
            self.log(f"Output folder: {folder}")

    def open_output_folder(self) -> None:
        folder = self.settings.output_folder
        if folder is None:
            if self.jobs:
                folder = self.jobs[0].input_path.parent
            else:
                return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder)))

    def open_file(self, path: Path | None) -> None:
        if path and path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def create_report(self) -> None:
        if not self.jobs:
            return
        destination = self.settings.output_folder or self.jobs[0].input_path.parent
        path = generate_report(self.jobs, self.settings, destination)
        self.log(f"Report generato: {path}")
        QMessageBox.information(self, "Report", f"Report generato:\n{path}")

    def ai_assist(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "AI assist", "Seleziona un file elaborato.")
            return
        job = self.jobs[row]
        if job.status != FileStatus.PROCESSED or not job.output_path:
            QMessageBox.warning(self, "AI assist", "Esegui prima l'anonimizzazione.")
            return
        dialog = AIAssistDialog(job.output_path, self)
        dialog.exec()


def apply_dark_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorRole.AlternateBase, Qt.GlobalColor.darkGray)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, Qt.GlobalColor.darkGray)
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Highlight, Qt.GlobalColor.darkCyan)
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
    app.setPalette(palette)

    base_font = app.font()
    base_font.setPointSizeF(11.0)
    app.setFont(base_font)
    app.setStyleSheet(APP_DARK_QSS)
