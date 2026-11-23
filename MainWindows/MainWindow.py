import sys
from datetime import date
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem, QFrame, QLineEdit,
    QComboBox, QTextEdit, QFormLayout, QDialog, QDialogButtonBox, QMessageBox)


class FormularioIncidencia(QDialog):
    def __init__(self, parent=None, incidencia=None):
        super().__init__(parent)
        self.setWindowTitle('Editar incidencia' if incidencia else 'Crear nueva incidencia')
        self.setMinimumWidth(440)
        self.nombre = QLineEdit()
        self.motivo = QTextEdit()
        self.motivo.setFixedHeight(100)
        self.estado = QComboBox()
        self.estado.addItems(['Por iniciar', 'En curso', 'Finalizado'])
        self.prioridad = QComboBox()
        self.prioridad.addItems(['Baja', 'Media', 'Alta'])
        self.categoria = QLineEdit()
        self.responsable = QLineEdit()
        layout = QVBoxLayout(self)
        form = QFormLayout()
        for texto, campo in [('Nombre *', self.nombre), ('Motivo *', self.motivo),
                             ('Estado', self.estado), ('Prioridad', self.prioridad),
                             ('Categoría *', self.categoria), ('Responsable *', self.responsable)]:
            form.addRow(texto, campo)
        layout.addLayout(form)
        botones = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        botones.accepted.connect(self.validar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)
        if incidencia:
            self.nombre.setText(incidencia['nombre'])
            self.motivo.setPlainText(incidencia['motivo'])
            self.estado.setCurrentText(incidencia['estado'])
            self.prioridad.setCurrentText(incidencia['prioridad'])
            self.categoria.setText(incidencia['categoria'])
            self.responsable.setText(incidencia['responsable'])

    def validar(self):
        if not all([self.nombre.text().strip(), self.motivo.toPlainText().strip(),
                    self.categoria.text().strip(), self.responsable.text().strip()]):
            QMessageBox.warning(self, 'Faltan datos', 'Completa todos los campos obligatorios (*).')
            return
        self.accept()

    def datos(self):
        return dict(nombre=self.nombre.text().strip(), motivo=self.motivo.toPlainText().strip(),
                    estado=self.estado.currentText(), prioridad=self.prioridad.currentText(),
                    categoria=self.categoria.text().strip(), responsable=self.responsable.text().strip())


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Gestor de incidencias')
        self.resize(1050, 650)
        self.incidencias = [
            dict(id='001', nombre='Falta confirmación', motivo='No se ha recibido la confirmación necesaria para continuar con la solicitud.', estado='En curso', prioridad='Media', fecha='20/10/2026', categoria='Gestión', responsable='Equipo de soporte'),
            dict(id='002', nombre='Sobrecalentamiento', motivo='El ordenador se apaga por temperatura elevada.', estado='Por iniciar', prioridad='Alta', fecha='20/10/2026', categoria='Hardware', responsable='Soporte técnico'),
            dict(id='003', nombre='Caída de internet', motivo='No hay conexión en la oficina.', estado='Finalizado', prioridad='Alta', fecha='21/10/2026', categoria='Redes', responsable='Equipo de redes'),
            dict(id='004', nombre='Borrado accidental de archivos', motivo='Se han eliminado archivos compartidos.', estado='En curso', prioridad='Media', fecha='22/10/2026', categoria='Software', responsable='Equipo de soporte'),
        ]
        self.siguiente_id = 5
        self.actual = None
        self.construir_interfaz()
        self.actualizar_lista()
        self.actual = self.incidencias[0]
        self.mostrar_detalle()

    def construir_interfaz(self):
        raiz = QWidget()
        self.setCentralWidget(raiz)
        principal = QVBoxLayout(raiz)
        principal.setContentsMargins(12, 12, 12, 12)
        principal.setSpacing(10)

        barra = QHBoxLayout()
        for texto, accion in [('Incidencias', self.mostrar_todas),
                              ('Crear nueva incidencia', self.crear),
                              ('Filtrar incidencias', self.alternar_filtros)]:
            boton = QPushButton(texto)
            boton.setObjectName('navegacion')

            barra.addWidget(boton)
        principal.addLayout(barra)

        self.panel_filtros = QFrame()
        filtros = QHBoxLayout(self.panel_filtros)
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText('Buscar por nombre, ID o responsable...')
        self.filtro_estado = QComboBox()
        self.filtro_estado.addItems(['Todos los estados', 'Por iniciar', 'En curso', 'Finalizado'])
        self.filtro_prioridad = QComboBox()
        self.filtro_prioridad.addItems(['Todas las prioridades', 'Baja', 'Media', 'Alta'])
        limpiar = QPushButton('Limpiar filtros')

        filtros.addWidget(self.busqueda, 2)
        filtros.addWidget(self.filtro_estado, 1)
        filtros.addWidget(self.filtro_prioridad, 1)
        filtros.addWidget(limpiar)

        self.panel_filtros.hide()
        principal.addWidget(self.panel_filtros)

        cuerpo = QHBoxLayout()
        principal.addLayout(cuerpo, 1)
        izquierda = QFrame()
        izquierda.setObjectName('panel')
        il = QVBoxLayout(izquierda)
        titulo_lista = QLabel('Bandeja de incidencias')
        titulo_lista.setObjectName('encabezado')
        il.addWidget(titulo_lista)
        self.lista = QListWidget()
        self.lista.setFocusPolicy(Qt.NoFocus)
        self.lista.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        il.addWidget(self.lista)
        self.contador = QLabel()
        il.addWidget(self.contador)
        cuerpo.addWidget(izquierda, 2)

        derecha = QFrame()
        derecha.setObjectName('panel')
        dl = QVBoxLayout(derecha)
        cabecera = QHBoxLayout()
        titulo_detalle = QLabel('Detalle de la incidencia')
        titulo_detalle.setObjectName('titulo')
        cabecera.addWidget(titulo_detalle)
        cabecera.addStretch()
        editar = QPushButton('Editar')

        eliminar = QPushButton('Eliminar')
        eliminar.setObjectName('peligro')

        cabecera.addWidget(editar)
        cabecera.addWidget(eliminar)
        dl.addLayout(cabecera)
        self.campos = {}
        for campo, etiqueta in [('nombre', 'Nombre de la incidencia'), ('id', 'ID'),
                                ('motivo', 'Motivo de la incidencia'), ('estado', 'Estado'),
                                ('prioridad', 'Prioridad'), ('fecha', 'Fecha'),
                                ('categoria', 'Categoría'), ('responsable', 'Responsable')]:
            encabezado = QLabel(etiqueta)
            encabezado.setObjectName('encabezado')
            valor = QLabel('—')
            valor.setWordWrap(True)
            valor.setObjectName('valor')
            dl.addWidget(encabezado)
            dl.addWidget(valor)
            self.campos[campo] = valor
        dl.addStretch()
        cuerpo.addWidget(derecha, 3)

        self.setStyleSheet('''
            QWidget {font-family: Arial; font-size: 13px; color: #25324a;}
            QMainWindow, QWidget#central {background: #f4f7fc;}
            QFrame#panel {background: white; border: 1px solid #dce5f4; border-radius: 7px;}
            QLabel#encabezado {background: #c9daf8; padding: 8px; font-weight: bold;}
            QLabel#titulo {font-size: 18px; font-weight: bold;}
            QLabel#valor {background: white; padding: 7px;}
            QPushButton {background: #e9effa; padding: 9px 12px; border: 1px solid #cbd7ec; border-radius: 4px;}
            QPushButton:hover {background: #d3e2ff;}
            QPushButton#navegacion {background: #0000ff; color: white; font-weight: bold; border: 0;}
            QPushButton#navegacion:hover {background: #263ee8;}
            QPushButton#peligro {color: #b02c2c;}
            QListWidget {border: 0; background: white;}
            QListWidget::item {padding: 10px; border-bottom: 1px solid #e8edf5;}
            QListWidget::item:selected {background: #c9daf8; color: #172747;}
            QLineEdit, QComboBox, QTextEdit {padding: 7px; border: 1px solid #cbd7ec; border-radius: 4px; background: white;}
        ''')

    def actualizar_lista(self, *_):
        anterior = self.actual['id'] if self.actual else None
        self.lista.blockSignals(True)
        self.lista.clear()
        texto = self.busqueda.text().strip().lower()
        estado = self.filtro_estado.currentText()
        prioridad = self.filtro_prioridad.currentText()
        visibles = [i for i in self.incidencias
                    if (not texto or texto in (i['nombre'] + ' ' + i['id'] + ' ' + i['responsable']).lower())
                    and (estado == 'Todos los estados' or i['estado'] == estado)
                    and (prioridad == 'Todas las prioridades' or i['prioridad'] == prioridad)]
        for incidencia in visibles:
            item = QListWidgetItem(f"{incidencia['nombre']}\n#{incidencia['id']}  ·  {incidencia['estado']}  ·  {incidencia['prioridad']}  ·  {incidencia['fecha']}")
            item.setData(Qt.UserRole, incidencia['id'])
            self.lista.addItem(item)
        self.lista.blockSignals(False)
        self.contador.setText(f'{len(visibles)} incidencia(s) encontrada(s)' if visibles else 'Sin resultados')
        indice = next((n for n, i in enumerate(visibles) if i['id'] == anterior), 0)
        if visibles:
            self.lista.setCurrentRow(indice)
        else:
            self.actual = None
            self.mostrar_detalle()

    def seleccionar(self, item, _anterior):
        identificador = item.data(Qt.UserRole) if item else None
        self.actual = next((i for i in self.incidencias if i['id'] == identificador), None)
        self.mostrar_detalle()

    def mostrar_detalle(self):
        for campo, etiqueta in self.campos.items():
            etiqueta.setText(str(self.actual[campo]) if self.actual else '—')

    def crear(self):
        dialogo = FormularioIncidencia(self)
        if dialogo.exec() == QDialog.Accepted:
            nueva = dialogo.datos()
            nueva.update(id=f'{self.siguiente_id:03d}', fecha=date.today().strftime('%d/%m/%Y'))
            self.siguiente_id += 1
            self.incidencias.append(nueva)
            self.limpiar_filtros()
            self.seleccionar_por_id(nueva['id'])
            QMessageBox.information(self, 'Correcto', 'Incidencia creada correctamente.')

    def editar(self):
        if not self.actual:
            QMessageBox.warning(self, 'Selecciona una incidencia', 'Primero selecciona una incidencia.')
            return
        dialogo = FormularioIncidencia(self, self.actual)
        if dialogo.exec() == QDialog.Accepted:
            self.actual.update(dialogo.datos())
            self.actualizar_lista()
            QMessageBox.information(self, 'Correcto', 'Incidencia actualizada correctamente.')

    def eliminar(self):
        if not self.actual:
            QMessageBox.warning(self, 'Selecciona una incidencia', 'Primero selecciona una incidencia.')
            return
        respuesta = QMessageBox.question(self, 'Confirmar eliminación',
            f"¿Eliminar la incidencia {self.actual['id']}?", QMessageBox.Yes | QMessageBox.No)
        if respuesta == QMessageBox.Yes:
            self.incidencias.remove(self.actual)
            self.actual = None
            self.actualizar_lista()

    def seleccionar_por_id(self, identificador):
        for n in range(self.lista.count()):
            if self.lista.item(n).data(Qt.UserRole) == identificador:
                self.lista.setCurrentRow(n)
                return

    def alternar_filtros(self):
        self.panel_filtros.setVisible(not self.panel_filtros.isVisible())

    def limpiar_filtros(self):
        self.busqueda.clear()
        self.filtro_estado.setCurrentIndex(0)
        self.filtro_prioridad.setCurrentIndex(0)
        self.actualizar_lista()

    def mostrar_todas(self):
        self.limpiar_filtros()
        self.panel_filtros.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
