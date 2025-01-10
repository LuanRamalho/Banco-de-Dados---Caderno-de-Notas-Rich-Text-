import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QWidget, QToolBar, QAction, QTextEdit, QColorDialog,
    QInputDialog, QFileDialog, QMessageBox, QLabel
)
from PyQt5.QtGui import QIcon, QTextCursor, QFont, QTextCharFormat, QTextListFormat
from PyQt5.QtCore import Qt, QDateTime

DATABASE_FILE = "notes_database.json"


class NoteEditor(QMainWindow):
    def __init__(self, note_data=None, save_callback=None):
        super().__init__()
        self.save_callback = save_callback
        self.note_data = note_data or {"content": "", "created_at": QDateTime.currentDateTime().toString("dd-MM-yyyy HH:mm")}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Editor de Nota")
        self.setGeometry(100, 100, 1024, 768)
        self.setStyleSheet("background-color: #ECFFAA; font-family: Arial; font-size: 14px;")

        # Layout principal
        layout = QVBoxLayout()
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setLayout(layout)

        # Exibir data e hora de criação
        created_at_label = QLabel(f"Data de criação: {self.note_data.get('created_at', 'Desconhecida')}")
        created_at_label.setStyleSheet("color: #495057; font-weight: bold;")
        layout.addWidget(created_at_label)

        # Caixa de texto
        self.textEdit = QTextEdit(self)
        self.textEdit.setStyleSheet("background-color: #FFFFFF; border: 1px solid #ced4da; border-radius: 5px;")
        if "content" in self.note_data and self.note_data["content"]:
            # Carrega o conteúdo em RTF/HTML, se disponível
            self.textEdit.setHtml(self.note_data["content"])
        else:
            # Carrega como texto simples, se vazio
            self.textEdit.setPlainText(self.note_data.get("content", ""))
        layout.addWidget(self.textEdit)

        # Barra de ferramentas
        toolbar = QToolBar("Barra de Ferramentas", self)
        toolbar.setStyleSheet("background-color: #F2C7FF; border: none;")
        layout.addWidget(toolbar)
        self.addToolbarAction(toolbar, "Cor", "color.png", self.changeColor)
        self.addToolbarAction(toolbar, "Aumentar Fonte", "font_increase.png", self.increaseFont)
        self.addToolbarAction(toolbar, "Diminuir Fonte", "font_decrease.png", self.decreaseFont)
        self.addToolbarAction(toolbar, "Negrito", "bold.png", self.toggleBold)
        self.addToolbarAction(toolbar, "Itálico", "italic.png", self.toggleItalic)
        self.addToolbarAction(toolbar, "Sublinhado", "underline.png", self.toggleUnderline)
        self.addToolbarAction(toolbar, "Riscado", "strikethrough.png", self.toggleStrikeThrough)
        self.addToolbarAction(toolbar, "Hiperlink", "link.png", self.insertHyperlink)
        self.addToolbarAction(toolbar, "Sobrescrito", "superscript.png", self.toggleSuperscript)
        self.addToolbarAction(toolbar, "Subscrito", "subscript.png", self.toggleSubscript)
        self.addToolbarAction(toolbar, "Alinhar Esquerda", "align_left.png", lambda: self.alignText(Qt.AlignLeft))
        self.addToolbarAction(toolbar, "Alinhar Centro", "align_center.png", lambda: self.alignText(Qt.AlignCenter))
        self.addToolbarAction(toolbar, "Alinhar Direita", "align_right.png", lambda: self.alignText(Qt.AlignRight))
        self.addToolbarAction(toolbar, "Justificar", "justify.png", lambda: self.alignText(Qt.AlignJustify))
        self.addToolbarAction(toolbar, "Lista de Pontos", "bullet_list.png", self.insertBulletList)
        self.addToolbarAction(toolbar, "Lista de Números", "number_list.png", self.insertNumberList)
        self.addToolbarAction(toolbar, "Salvar", "save.png", self.saveNote)

    def addToolbarAction(self, toolbar, name, icon, method):
        action = QAction(QIcon(icon), name, self)
        action.triggered.connect(method)
        toolbar.addAction(action)

    def changeColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.textEdit.setTextColor(color)

    def increaseFont(self):
        font = self.textEdit.currentFont()
        font.setPointSize(font.pointSize() + 1)
        self.textEdit.setCurrentFont(font)

    def decreaseFont(self):
        font = self.textEdit.currentFont()
        font.setPointSize(max(font.pointSize() - 1, 1))
        self.textEdit.setCurrentFont(font)

    def toggleBold(self):
        fmt = self.textEdit.currentCharFormat()
        fmt.setFontWeight(QFont.Bold if fmt.fontWeight() != QFont.Bold else QFont.Normal)
        self.textEdit.mergeCurrentCharFormat(fmt)

    def toggleItalic(self):
        fmt = self.textEdit.currentCharFormat()
        fmt.setFontItalic(not fmt.fontItalic())
        self.textEdit.mergeCurrentCharFormat(fmt)

    def toggleUnderline(self):
        fmt = self.textEdit.currentCharFormat()
        fmt.setFontUnderline(not fmt.fontUnderline())
        self.textEdit.mergeCurrentCharFormat(fmt)

    def toggleStrikeThrough(self):
        fmt = self.textEdit.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.textEdit.mergeCurrentCharFormat(fmt)

    def insertHyperlink(self):
        url, ok = QInputDialog.getText(self, "Inserir Hiperlink", "URL:")
        if ok and url:
            cursor = self.textEdit.textCursor()
            cursor.insertHtml(f'<a href="{url}">{url}</a>')

    def toggleSuperscript(self):
        fmt = self.textEdit.currentCharFormat()
        fmt.setVerticalAlignment(
            QTextCharFormat.AlignSuperScript
            if fmt.verticalAlignment() != QTextCharFormat.AlignSuperScript
            else QTextCharFormat.AlignNormal
        )
        self.textEdit.mergeCurrentCharFormat(fmt)

    def toggleSubscript(self):
        fmt = self.textEdit.currentCharFormat()
        fmt.setVerticalAlignment(
            QTextCharFormat.AlignSubScript
            if fmt.verticalAlignment() != QTextCharFormat.AlignSubScript
            else QTextCharFormat.AlignNormal
        )
        self.textEdit.mergeCurrentCharFormat(fmt)

    def alignText(self, alignment):
        self.textEdit.setAlignment(alignment)

    def insertBulletList(self):
        cursor = self.textEdit.textCursor()
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDisc)
        cursor.insertList(list_format)

    def insertNumberList(self):
        cursor = self.textEdit.textCursor()
        list_format = QTextListFormat()
        list_format.setStyle(QTextListFormat.ListDecimal)
        cursor.insertList(list_format)

    def saveNote(self):
        # Salva o conteúdo da nota em formato HTML (Rich Text Format)
        self.note_data["content"] = self.textEdit.toHtml()  # Salva o texto formatado em HTML
        if self.save_callback:
            self.save_callback(self.note_data)
        self.close()



class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.database = self.loadDatabase()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("OneNote Simples")
        self.setGeometry(100, 100, 1024, 768)
        self.setStyleSheet("background-color: #E1FFFC; font-family: Arial; font-size: 14px;")

        # Layout principal
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Barra de busca
        self.searchBar = QLineEdit(self)
        self.searchBar.setPlaceholderText("Buscar...")
        self.searchBar.setStyleSheet("background-color: #ffffff; border: 1px solid #ced4da; border-radius: 5px; padding: 5px;")
        self.searchBar.textChanged.connect(self.filterNotes)
        layout.addWidget(self.searchBar)

        # Árvore de cadernos
        self.tree = QTreeWidget(self)
        self.tree.setHeaderLabels(["Cadernos"])
        self.tree.setStyleSheet("background-color: #98FFB3; border: 1px solid #ced4da; border-radius: 5px;")
        layout.addWidget(self.tree)
        self.tree.itemDoubleClicked.connect(self.openNote)

        # Botões de ação
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        add_notebook_btn = QPushButton("Novo Caderno", self)
        add_notebook_btn.setStyleSheet("background-color: #007bff; color: white; border-radius: 5px; padding: 5px 10px;")
        add_notebook_btn.clicked.connect(self.addNotebook)
        button_layout.addWidget(add_notebook_btn)

        add_section_btn = QPushButton("Nova Seção", self)
        add_section_btn.setStyleSheet("background-color: #17a2b8; color: white; border-radius: 5px; padding: 5px 10px;")
        add_section_btn.clicked.connect(self.addSection)
        button_layout.addWidget(add_section_btn)

        add_note_btn = QPushButton("Nova Nota", self)
        add_note_btn.setStyleSheet("background-color: #28a745; color: white; border-radius: 5px; padding: 5px 10px;")
        add_note_btn.clicked.connect(self.addNote)
        button_layout.addWidget(add_note_btn)

        add_edit_btn = QPushButton("Editar", self)
        add_edit_btn.setStyleSheet("background-color: #A79900; color: white; border-radius: 5px; padding: 5px 10px;")
        add_edit_btn.clicked.connect(self.editItem)
        button_layout.addWidget(add_edit_btn)

        add_delete_btn = QPushButton("Excluir", self)
        add_delete_btn.setStyleSheet("background-color: #B20000; color: white; border-radius: 5px; padding: 5px 10px;")
        add_delete_btn.clicked.connect(self.deleteItem)
        button_layout.addWidget(add_delete_btn)

        self.populateTree()
        self.show()

    def loadDatabase(self):
        if os.path.exists(DATABASE_FILE):
            with open(DATABASE_FILE, "r") as f:
                return json.load(f)
        return {}

    def saveDatabase(self):
        with open(DATABASE_FILE, "w") as f:
            json.dump(self.database, f, indent=4)

    def populateTree(self):
        self.tree.clear()
        for notebook, sections in self.database.items():
            notebook_item = QTreeWidgetItem([notebook])
            self.tree.addTopLevelItem(notebook_item)
            for section, notes in sections.items():
                section_item = QTreeWidgetItem([section])
                notebook_item.addChild(section_item)
                for note in notes:
                    note_item = QTreeWidgetItem([note["title"]])
                    note_item.setData(0, Qt.UserRole, note)
                    section_item.addChild(note_item)

    def addNotebook(self):
        name, ok = QInputDialog.getText(self, "Novo Caderno", "Nome do Caderno:")
        if ok and name:
            self.database[name] = {}
            self.saveDatabase()
            self.populateTree()

    def addSection(self):
        item = self.tree.currentItem()
        if item and not item.parent():
            notebook = item.text(0)
            name, ok = QInputDialog.getText(self, "Nova Seção", "Nome da Seção:")
            if ok and name:
                self.database[notebook][name] = []
                self.saveDatabase()
                self.populateTree()

    def addNote(self):
        item = self.tree.currentItem()
        if item and item.parent():  # Verifica se o item tem um pai (seção está dentro de um caderno)
            parent = item.parent()
            if not parent.parent():  # Verifica se o pai do item é um caderno
                notebook = parent.text(0)  # Pai do item (caderno)
                section = item.text(0)     # Item selecionado (seção)
                title, ok = QInputDialog.getText(self, "Nova Nota", "Título da Nota:")
                if ok and title:
                    note_data = {
                        "title": title,
                        "content": "",
                        "created_at": QDateTime.currentDateTime().toString("dd-MM-yyyy HH:mm")
                    }
                    self.database[notebook][section].append(note_data)
                    self.saveDatabase()
                    self.populateTree()
                return
        QMessageBox.warning(self, "Erro", "Selecione uma seção dentro de um caderno para adicionar uma nova nota.")



    def editItem(self):
        item = self.tree.currentItem()
        if item:
            parent = item.parent()
            if parent:
                if parent.parent():
                    notebook = parent.parent().text(0)
                    section = parent.text(0)
                    old_title = item.text(0)
                    new_title, ok = QInputDialog.getText(self, "Editar Nota", "Novo Título da Nota:", text=old_title)
                    if ok and new_title:
                        notes = self.database[notebook][section]
                        for note in notes:
                            if note["title"] == old_title:
                                note["title"] = new_title
                                break
                else:
                    notebook = parent.text(0)
                    old_section = item.text(0)
                    new_section, ok = QInputDialog.getText(self, "Editar Seção", "Novo Nome da Seção:", text=old_section)
                    if ok and new_section:
                        self.database[notebook][new_section] = self.database[notebook].pop(old_section)
            else:
                old_notebook = item.text(0)
                new_notebook, ok = QInputDialog.getText(self, "Editar Caderno", "Novo Nome do Caderno:", text=old_notebook)
                if ok and new_notebook:
                    self.database[new_notebook] = self.database.pop(old_notebook)
            self.saveDatabase()
            self.populateTree()

    def deleteItem(self):
        item = self.tree.currentItem()
        if item:
            parent = item.parent()
            if parent:
                if parent.parent():
                    notebook = parent.parent().text(0)
                    section = parent.text(0)
                    note_title = item.text(0)
                    notes = self.database[notebook][section]
                    self.database[notebook][section] = [note for note in notes if note["title"] != note_title]
                else:
                    notebook = parent.text(0)
                    section = item.text(0)
                    del self.database[notebook][section]
            else:
                notebook = item.text(0)
                del self.database[notebook]
            self.saveDatabase()
            self.populateTree()

    def openNote(self, item, column):
        if item.parent() and item.parent().parent():
            note_data = item.data(0, Qt.UserRole)
            editor = NoteEditor(note_data, save_callback=self.saveNoteContent)
            editor.show()


    def saveNoteContent(self, note_data):
        for notebook, sections in self.database.items():
            for section, notes in sections.items():
                for i, note in enumerate(notes):
                    if note["title"] == note_data["title"]:
                        self.database[notebook][section][i] = note_data
                        self.saveDatabase()
                        self.populateTree()
                        return

    def filterNotes(self):
        query = self.searchBar.text().lower()
        for i in range(self.tree.topLevelItemCount()):
            notebook_item = self.tree.topLevelItem(i)
            # Filtra cadernos
            notebook_item.setHidden(query not in notebook_item.text(0).lower())
            
            # Filtra seções dentro de cadernos
            for j in range(notebook_item.childCount()):
                section_item = notebook_item.child(j)
                section_item.setHidden(query not in section_item.text(0).lower())
                
                # Filtra notas dentro das seções
                for k in range(section_item.childCount()):
                    note_item = section_item.child(k)
                    note_item.setHidden(query not in note_item.text(0).lower())



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_app = MainApp()
    sys.exit(app.exec_())
