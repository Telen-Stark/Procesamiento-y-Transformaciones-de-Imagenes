"""POOKIES ♡ Image Studio — desktop GUI for the original 24-bit BMP C/OpenMP project."""
import csv
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QFont, QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QFileDialog,
    QMessageBox, QComboBox, QSpinBox, QProgressBar, QTabWidget, QScrollArea,
    QLineEdit, QGroupBox, QCheckBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QTextEdit)

BASE = Path(__file__).resolve().parent
IMG = BASE / 'img'
ENGINE = BASE / 'pookies_engine.exe'
IMG.mkdir(exist_ok=True)
RESULTS = {
    'gray': ('img_grises.bmp', 'Escala de grises'),
    'hcolor': ('pookies_h_color.bmp', 'Espejo horizontal · color'),
    'hgray': ('pookies_h_gray.bmp', 'Espejo horizontal · grises'),
    'vcolor': ('pookies_v_color.bmp', 'Espejo vertical · color'),
    'vgray': ('pookies_v_gray.bmp', 'Espejo vertical · grises'),
    'bcolor': ('pookies_b_color.bmp', 'Desenfoque · color'),
    'bgray': ('pookies_b_gray.bmp', 'Desenfoque · grises'),
    'edge_x': ('pookies_edge_x.bmp', 'Bordes · Sobel X'),
    'edge_y': ('pookies_edge_y.bmp', 'Bordes · Sobel Y'),
}
ALL_OPS = [k for k in RESULTS if k != 'gray']
OP_CHOICES = [('all', '✦ Todas las transformaciones (8)'), ('gray', '♡ Escala de grises')] + [ (k, v[1]) for k, v in RESULTS.items() if k != 'gray']
PALETTE = '''
QMainWindow, QWidget#root { background-color: #fff5fa; }
QWidget { color: #703c58; font-family: 'Avenir Next', 'Helvetica Neue', Arial; font-size: 13px; }
QFrame#hero {background-color:#ffdce9; border:1px solid #f7bcd0; border-radius:20px; }
QFrame#panel, QFrame#preview { background-color:white; border:1px solid #f5d4e2; border-radius:17px; }
QLabel#heading { font-size:30px; font-weight:800; color:#a43d70; }
QLabel#subtitle { color:#9b7185; font-size:12px; }
QLabel#panelTitle { font-size:15px; font-weight:700; color:#963e6a; }
QLabel#image { background-color:#fff7fb; border:2px dashed #f6c6d9; border-radius:15px; color:#b27a97; }
QPushButton { background-color:#ffe7f0; border:1px solid #efbed2; color:#904568; padding:11px 14px; border-radius:11px; font-weight:700; }
QPushButton:hover { background-color:#ffd2e5; }
QPushButton:pressed { background-color:#ffc1da; }
QPushButton:disabled { background-color:#f7edf1; color:#b9a6af; border-color:#eedfe5; }
QPushButton#primary { background-color:#df6f9f; color:white; border:1px solid #d05b8c; font-size:14px; }
QPushButton#primary:hover { background-color:#c95c8b; }
QComboBox, QSpinBox, QLineEdit { background-color:white; border:1px solid #eec7d8; padding:8px 11px; border-radius:9px; min-height:18px; }
QComboBox::drop-down { border:0px; width:23px; }
QTabWidget::pane { border:0px; }
QTabBar::tab { padding:12px 22px; background:#ffe8f1; color:#99516f; border:1px solid #efccdb; border-top-left-radius:11px; border-top-right-radius:11px; margin-right:5px; font-weight:700; }
QTabBar::tab:selected { background:white; color:#a43d70; }
QProgressBar { background:#fbe6ee; border:none; border-radius:7px; min-height:14px; text-align:center; }
QProgressBar::chunk { background:#db7fa8; border-radius:7px; }
QTableWidget {background:white; alternate-background-color:#fff6fa; border:1px solid #f1d4df; border-radius:8px; gridline-color:#f3deea; }
QHeaderView::section {background:#ffe0eb; color:#824463; font-weight:700; padding:8px; border:0px; }
QTextEdit {background:white; border:1px solid #f0d4e0; border-radius:11px; padding:8px;}
'''


def panel(title):
    f = QFrame(objectName='panel')
    lay = QVBoxLayout(f)
    lay.setContentsMargins(18, 17, 18, 17)
    lay.setSpacing(11)
    t = QLabel(title, objectName='panelTitle')
    lay.addWidget(t)
    return f, lay


def button(text, callback, primary=False):
    b = QPushButton(text)
    if primary: b.setObjectName('primary')
    b.clicked.connect(callback)
    b.setCursor(Qt.PointingHandCursor)
    return b


class ProcessingWorker(QThread):
    progress = Signal(int, int, str)
    completed = Signal(object)
    failed = Signal(str)

    def __init__(self, mode, names, threads, kernel):
        super().__init__()
        self.mode = mode
        self.names = names
        self.threads = threads
        self.kernel = kernel

    def run(self):
        try:
            entries = []
            archive_root = BASE / 'resultados'
            archive_root.mkdir(exist_ok=True)
            for i, name in enumerate(self.names, 1):
                # Remove old generated files so errors cannot masquerade as successful new results.
                for filename, _ in RESULTS.values():
                    p = IMG / filename
                    if p.exists(): p.unlink()
                cmd = [str(ENGINE), self.mode, str(self.threads), name, str(self.kernel)]
                p = subprocess.run(cmd, cwd=BASE, text=True, capture_output=True)
                if p.returncode != 0:
                    raise RuntimeError(f'Imagen: {name}\n{p.stderr.strip() or p.stdout.strip() or "Fallo el motor"}')
                line = next((x for x in p.stdout.splitlines() if x.startswith('OK|')), None)
                if not line:
                    raise RuntimeError('No se recibio un tiempo valido del motor C.\n' + p.stdout)
                secs = float(line.split('|')[3])
                keys = ALL_OPS if self.mode == 'all' else [self.mode]
                destination = archive_root / Path(name).stem
                destination.mkdir(parents=True, exist_ok=True)
                produced = {}
                for key in keys:
                    fname, _ = RESULTS[key]
                    src = IMG / fname
                    if not src.is_file() or src.stat().st_size <= 54:
                        raise RuntimeError(f'Falta el resultado {fname} de {name}')
                    output = destination / fname
                    shutil.copy2(src, output)
                    produced[key] = output
                entry = dict(name=name, seconds=secs, threads=self.threads,
                             kernel=self.kernel, operation=self.mode,
                             outputs=produced, timestamp=datetime.now().isoformat(timespec='seconds'))
                entries.append(entry)
                self.progress.emit(i, len(self.names), name)
            self.completed.emit(entries)
        except Exception as exc:
            self.failed.emit(str(exc))


class Pookies(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('POOKIES ♡ Image Studio')
        self.resize(1230, 820)
        self.setMinimumSize(960, 650)
        self.selected = None
        self.current_result = None
        self.gallery = {}
        self.records = []
        self.worker = None
        self.setup_ui()

    def setup_ui(self):
        root = QWidget(objectName='root')
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(24, 19, 24, 19)
        layout.setSpacing(15)
        hero = QFrame(objectName='hero')
        hl = QVBoxLayout(hero)
        hl.setContentsMargins(24, 16, 24, 17)
        title = QLabel('POOKIES  ♡  image studio', objectName='heading')
        hl.addWidget(title)
        hl.addWidget(QLabel('✦ Tu pequeño laboratorio de magia digital · BMP + C + OpenMP', objectName='subtitle'))
        layout.addWidget(hero)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.make_studio(), '♡  Estudio')
        self.tabs.addTab(self.make_benchmarks(), '✦  Pruebas y rendimiento')
        self.tabs.addTab(self.make_gallery_tab(), '✿  Galería')
        layout.addWidget(self.tabs)
        self.statusBar().showMessage('♡ Lista para crear. Selecciona una imagen BMP para comenzar.')

    def preview(self, text):
        lab = QLabel(text, objectName='image')
        lab.setAlignment(Qt.AlignCenter)
        lab.setMinimumHeight(240)
        lab.setWordWrap(True)
        lab.setProperty('preview_path', None)
        return lab

    def make_studio(self):
        root = QWidget()
        main = QVBoxLayout(root)
        main.setContentsMargins(3, 18, 3, 8)
        main.setSpacing(15)
        previews = QHBoxLayout()
        left, ll = panel('♡  Tu imagen original')
        self.original_preview = self.preview('♡\n\nAquí aparecerá tu imagen BMP')
        ll.addWidget(self.original_preview, 1)
        self.source_label = QLabel('Aún no has elegido ninguna imagen', objectName='subtitle')
        self.source_label.setWordWrap(True)
        ll.addWidget(self.source_label)
        ll.addWidget(button('✿ Elegir imagen BMP', self.choose))
        right, rl = panel('✧  Resultado mágico')
        self.result_preview = self.preview('✧\n\nTu transformación aparecerá aquí')
        rl.addWidget(self.result_preview, 1)
        self.result_label = QLabel('No hay resultados todavía', objectName='subtitle')
        rl.addWidget(self.result_label)
        rl.addWidget(button('♡ Guardar resultado como…', self.save_result))
        previews.addWidget(left, 1)
        previews.addWidget(right, 1)
        main.addLayout(previews, 1)
        control, cl = panel('🎀  Magic controls')
        settings = QHBoxLayout()
        o = QVBoxLayout()
        o.addWidget(QLabel('Transformación'))
        self.op = QComboBox()
        for code, label in OP_CHOICES: self.op.addItem(label, code)
        self.op.currentIndexChanged.connect(self.refresh_gallery)
        o.addWidget(self.op)
        settings.addLayout(o, 4)
        th = QVBoxLayout()
        th.addWidget(QLabel('Threads'))
        self.threads = QSpinBox()
        self.threads.setRange(1, 256)
        self.threads.setValue(8)
        th.addWidget(self.threads)
        settings.addLayout(th, 1)
        ker = QVBoxLayout()
        ker.addWidget(QLabel('Kernel desenfoque'))
        self.kernel = QSpinBox()
        self.kernel.setRange(1, 99)
        self.kernel.setValue(15)
        ker.addWidget(self.kernel)
        settings.addLayout(ker, 1)
        cl.addLayout(settings)
        actions = QHBoxLayout()
        self.run_button = button('♡ ¡Transformar!', self.run_single, True)
        actions.addWidget(self.run_button, 3)
        self.hist_button = button('✿ Ver histograma', self.histogram)
        actions.addWidget(self.hist_button, 1)
        self.clear_button = button('🧹 Limpiar todo', self.clear_all)  # <-- Agrega esta línea
        actions.addWidget(self.clear_button, 1)
        cl.addLayout(actions)
        self.progress = QProgressBar()
        self.progress.hide()
        cl.addWidget(self.progress)
        self.time_label = QLabel('⏱ Tiempo de procesamiento: —', objectName='subtitle')
        cl.addWidget(self.time_label)
        main.addWidget(control)
        gallery_row = QHBoxLayout()
        gallery_row.addWidget(QLabel('♡ Galería de resultados:'))
        self.gallery_selector = QComboBox()
        self.gallery_selector.currentIndexChanged.connect(self.show_gallery)
        gallery_row.addWidget(self.gallery_selector, 1)
        main.addLayout(gallery_row)
        return root

    def make_benchmarks(self):
        root = QWidget()
        lay = QVBoxLayout(root)
        lay.setContentsMargins(3, 18, 3, 8)
        a, al = panel('✦ Prueba las 10 imágenes grandes')
        al.addWidget(QLabel('Las imágenes deben llamarse uno.bmp, dos.bmp… diez.bmp y estar en animales2/img/'))
        row = QHBoxLayout()
        self.batch_button = button('🎀 Procesar 10 BMP (8 transformaciones)', self.run_batch, True)
        row.addWidget(self.batch_button, 2)
        self.export_button = button('↓ Exportar CSV', self.export_csv)
        row.addWidget(self.export_button)
        al.addLayout(row)
        self.batch_progress = QProgressBar()
        self.batch_progress.hide()
        al.addWidget(self.batch_progress)
        self.batch_status = QLabel('Los 80 resultados se guardarán en la carpeta resultados/', objectName='subtitle')
        al.addWidget(self.batch_status)
        lay.addWidget(a)
        b, bl = panel('♡ Registro de tiempos · C/OpenMP')
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(['Fecha y hora', 'Imagen', 'Operación', 'Threads', 'Tiempo (s)'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        bl.addWidget(self.table)
        lay.addWidget(b, 1)
        c, co = panel('✿ Cómo comparar hilos')
        co.addWidget(QLabel('Repite el lote con 1, 2, 4, 8, 12, 16… threads. Exporta CSV y compara los tiempos del mismo conjunto de imágenes.'))
        co.addWidget(QLabel('Nota: cada imagen se procesa con 8 secciones OpenMP; las 10 imágenes del lote se ejecutan sucesivamente.'))
        lay.addWidget(c)
        return root

    def make_gallery_tab(self):
        root = QWidget()
        lay = QVBoxLayout(root)
        lay.setContentsMargins(3, 18, 3, 8)
        lay.setSpacing(12)

        top, tl = panel('✿ Todas las imágenes convertidas')
        row = QHBoxLayout()
        row.addWidget(QLabel('Explora las transformaciones guardadas en resultados/', objectName='subtitle'), 1)
        row.addWidget(button('↻ Actualizar galería', self.populate_gallery_grid))
        tl.addLayout(row)
        lay.addWidget(top)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: transparent; }')
        
        self.gallery_container = QWidget()
        self.gallery_container.setStyleSheet('background: transparent;')
        self.gallery_grid = QGridLayout(self.gallery_container)
        self.gallery_grid.setSpacing(14)
        scroll.setWidget(self.gallery_container)
        
        lay.addWidget(scroll, 1)
        self.populate_gallery_grid()
        return root

    def populate_gallery_grid(self):
        # Limpiar tarjetas anteriores
        while self.gallery_grid.count():
            item = self.gallery_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        archive_root = BASE / 'resultados'
        if not archive_root.exists():
            self.gallery_grid.addWidget(QLabel('Aún no hay imágenes en resultados/'), 0, 0)
            return

        # Mapear nombres de archivo a sus etiquetas legibles
        name_map = {fname: desc for fname, desc in RESULTS.values()}
        images = sorted(archive_root.rglob('*.bmp'), key=lambda p: p.stat().st_mtime, reverse=True)

        if not images:
            self.gallery_grid.addWidget(QLabel('Aún no hay imágenes convertidas ♡'), 0, 0)
            return

        cols = 4
        for idx, img_path in enumerate(images):
            card = QFrame(objectName='panel')
            cl = QVBoxLayout(card)
            cl.setContentsMargins(12, 12, 12, 12)
            cl.setSpacing(6)

            thumb = QLabel(objectName='image')
            thumb.setFixedSize(230, 170)
            thumb.setAlignment(Qt.AlignCenter)
            pix = QPixmap(str(img_path))
            if not pix.isNull():
                thumb.setPixmap(pix.scaled(QSize(214, 154), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            cl.addWidget(thumb, alignment=Qt.AlignCenter)

            title = QLabel(name_map.get(img_path.name, img_path.name))
            title.setStyleSheet('font-weight: 700; color: #963e6a;')
            cl.addWidget(title)

            origin = QLabel(f'Origen: {img_path.parent.name}.bmp', objectName='subtitle')
            cl.addWidget(origin)

            save_btn = button('♡ Guardar', lambda _, p=img_path: self.save_specific_image(p))
            cl.addWidget(save_btn)

            self.gallery_grid.addWidget(card, idx // cols, idx % cols)

    def save_specific_image(self, img_path):
        path, _ = QFileDialog.getSaveFileName(self, 'Guardar imagen', img_path.name, 'BMP (*.bmp)')
        if path:
            shutil.copy2(img_path, path)

    def clear_all(self):
        reply = QMessageBox.question(
            self,
            'Limpiar todo',
            '¿Deseas limpiar las imágenes actuales, el historial de tiempos y la carpeta de resultados?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        # 1. Limpiar pestaña Estudio
        self.selected = None
        self.current_result = None
        self.gallery = {}
        
        self.original_preview.clear()
        self.original_preview.setText('♡\n\nAquí aparecerá tu imagen BMP')
        self.original_preview.setProperty('preview_path', None)
        self.source_label.setText('Aún no has elegido ninguna imagen')

        self.result_preview.clear()
        self.result_preview.setText('✧\n\nTu transformación aparecerá aquí')
        self.result_preview.setProperty('preview_path', None)
        self.result_label.setText('No hay resultados todavía')

        self.gallery_selector.clear()
        self.time_label.setText('⏱ Tiempo de procesamiento: —')

        # 2. Limpiar pestaña Pruebas y rendimiento
        self.records.clear()
        self.table.setRowCount(0)
        self.batch_status.setText('Los 80 resultados se guardarán en la carpeta resultados/')

        # 3. Limpiar archivos de resultados y actualizar pestaña Galería
        archive_root = BASE / 'resultados'
        if archive_root.exists():
            shutil.rmtree(archive_root)
            archive_root.mkdir(exist_ok=True)
        
        if hasattr(self, 'populate_gallery_grid'):
            self.populate_gallery_grid()

        self.statusBar().showMessage('♡ Todo limpio. Listo para empezar de nuevo.')

    def show_image(self, label, path):
        path = Path(path)
        pix = QPixmap(str(path))
        if pix.isNull():
            label.setText('No se pudo visualizar esta imagen BMP')
            return
        label.setProperty('preview_path', str(path))
        area = label.size() - QSize(24, 24)
        label.setPixmap(pix.scaled(area, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        # Refresh previews without distortion when the window is resized.
        for label in (getattr(self, 'original_preview', None), getattr(self, 'result_preview', None)):
            if label is not None and label.property('preview_path'):
                self.show_image(label, label.property('preview_path'))

    def choose(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Elegir BMP original', str(IMG), 'Archivos BMP (*.bmp *.BMP)')
        if not path: return
        src = Path(path)
        dst = IMG / src.name
        if src.resolve() != dst.resolve():
            if dst.exists():
                answer = QMessageBox.question(self, 'Archivo existente', 'Ya existe ese archivo en img/. ¿Deseas reemplazarlo?')
                if answer != QMessageBox.Yes: return
            shutil.copy2(src, dst)
        self.selected = dst.name
        self.source_label.setText(self.selected)
        self.show_image(self.original_preview, dst)
        self.statusBar().showMessage('♡ Imagen cargada: ' + dst.name)

    def requirements(self):
        if not ENGINE.exists():
            QMessageBox.critical(self, 'Falta compilar el motor', 'No encuentro pookies_engine. Compila pookies_engine.c con Clang y OpenMP siguiendo INSTRUCCIONES.txt.')
            return False
        return True

    def run_single(self):
        if not self.selected:
            QMessageBox.information(self, 'Falta una imagen', 'Primero selecciona una imagen BMP ♡')
            return
        if not self.requirements(): return
        self.start_worker(self.op.currentData(), [self.selected])

    def run_batch(self):
        if not self.requirements(): return
        names = ['uno.bmp', 'dos.bmp', 'tres.bmp', 'cuatro.bmp', 'cinco.bmp', 'seis.bmp', 'siete.bmp', 'ocho.bmp', 'nueve.bmp', 'diez.bmp']
        missing = [n for n in names if not (IMG / n).is_file()]
        if missing:
            QMessageBox.warning(self, 'Faltan imágenes', 'Coloca estas imágenes en img/:\n'+'\n'.join(missing))
            return
        self.start_worker('all', names)

    def start_worker(self, mode, names):
        if self.worker and self.worker.isRunning(): return
        self.run_button.setEnabled(False)
        self.batch_button.setEnabled(False)
        self.progress.show(); self.progress.setRange(0, len(names)); self.progress.setValue(0)
        self.batch_progress.show(); self.batch_progress.setRange(0, len(names)); self.batch_progress.setValue(0)
        self.worker = ProcessingWorker(mode, names, self.threads.value(), self.kernel.value())
        self.worker.progress.connect(self.on_progress)
        self.worker.completed.connect(self.finished)
        self.worker.failed.connect(self.failed)
        self.worker.start()
        self.statusBar().showMessage('✿ Procesando…')

    def on_progress(self, current, total, name):
        self.progress.setValue(current)
        self.batch_progress.setValue(current)
        self.batch_status.setText(f'Procesadas {current}/{total}: {name}')

    def cleanup_worker(self):
        self.run_button.setEnabled(True)
        self.batch_button.setEnabled(True)

    def finished(self, entries):
        self.cleanup_worker()
        for entry in entries:
            self.records.append(entry)
            row = self.table.rowCount()
            self.table.insertRow(row)
            for j, value in enumerate([entry['timestamp'], entry['name'], entry['operation'], str(entry['threads']), f"{entry['seconds']:.6f}"]):
                self.table.setItem(row, j, QTableWidgetItem(value))
        if entries:
            self.populate_gallery_grid()
            last = entries[-1]
            self.gallery = last['outputs']
            self.gallery_selector.blockSignals(True)
            self.gallery_selector.clear()
            for key in self.gallery:
                self.gallery_selector.addItem(RESULTS[key][1], key)
            self.gallery_selector.blockSignals(False)
            self.show_gallery()
            self.time_label.setText(f"⏱ Última imagen: {last['seconds']:.6f} s · {last['threads']} threads")
            total = sum(e['seconds'] for e in entries)
            self.batch_status.setText(f'♡ ¡Listo! {len(entries)} imágenes · {total:.6f} s sumados del motor C')
            self.statusBar().showMessage('♡ ¡Proceso terminado! Resultados guardados en resultados/')
            if len(entries)>1:
                QMessageBox.information(self, '¡Listo! ♡', f"Se procesaron {len(entries)} imágenes y se guardaron 8 resultados por imagen.\nTiempo acumulado C: {total:.6f} segundos.")

    def failed(self, detail):
        self.cleanup_worker()
        self.statusBar().showMessage('No se pudo completar el procesamiento')
        QMessageBox.critical(self, 'Error del motor C', detail)

    def show_gallery(self, *_):
        key = self.gallery_selector.currentData()
        if key in self.gallery:
            self.current_result = Path(self.gallery[key])
            self.result_label.setText(f'{RESULTS[key][1]} · {self.current_result.name}')
            self.show_image(self.result_preview, self.current_result)

    def refresh_gallery(self, *_):
        pass

    def save_result(self):
        if not self.current_result or not self.current_result.is_file():
            QMessageBox.information(self, 'Sin resultados', 'Primero transforma una imagen ♡')
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Guardar resultado', self.current_result.name, 'BMP (*.bmp)')
        if path: shutil.copy2(self.current_result, path)

    def export_csv(self):
        if not self.records:
            QMessageBox.information(self, 'Sin mediciones', 'Primero ejecuta una prueba ♡')
            return
        path, _ = QFileDialog.getSaveFileName(self, 'Exportar mediciones', str(BASE/'pookies_tiempos.csv'), 'CSV (*.csv)')
        if not path: return
        with open(path,'w',newline='',encoding='utf-8-sig') as f:
            w=csv.writer(f)
            w.writerow(['fecha','imagen','operacion','threads','kernel','tiempo_segundos'])
            for r in self.records: w.writerow([r['timestamp'],r['name'],r['operation'],r['threads'],r['kernel'],f"{r['seconds']:.6f}"])
        QMessageBox.information(self, 'CSV guardado', 'Archivo exportado para tu Wiki ♡')

    def histogram(self):
        path = self.current_result or (IMG / self.selected if self.selected else None)
        if not path or not Path(path).exists():
            QMessageBox.information(self, 'Sin imagen', 'Selecciona o transforma una imagen primero ♡')
            return
        try:
            from PIL import Image
            from PySide6.QtCharts import QChart, QChartView, QLineSeries, QValueAxis
            im = Image.open(path).convert('RGB')
            h = im.histogram()
            dialog = QMainWindow(self)
            dialog.setWindowTitle('♡ Histograma RGB')
            dialog.resize(800,480)
            chart = QChart()
            chart.setTitle(Path(path).name)
            for off, name, color in [(0,'Rojo','#d96078'),(256,'Verde','#87ad7d'),(512,'Azul','#7b9ed7')]:
                s = QLineSeries(); s.setName(name)
                for i,v in enumerate(h[off:off+256]):s.append(i,float(v))
                from PySide6.QtGui import QColor, QPen
                s.setPen(QPen(QColor(color),1.6))
                chart.addSeries(s)
            chart.createDefaultAxes()
            dialog.setCentralWidget(QChartView(chart))
            dialog.show()
            self.hist_window = dialog
        except Exception as e:
            QMessageBox.warning(self, 'Histograma no disponible', str(e))


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # consistent pastel appearance in light/dark macOS
    app.setStyleSheet(PALETTE)
    window = Pookies()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__': main()
