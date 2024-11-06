from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QMessageBox, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QColor
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QGraphicsBlurEffect, QTableWidgetItem
from pymongo import MongoClient
import sys
import bcrypt
import re

# Conexão apontando para o mongoDB

db = client['BooksDB']
collection = db['users'] 

class ParallaxBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(800, 600)

        # Definindo a velocidade das camadas do grid
        self.speed_layer1 = 0.5
        self.speed_layer2 = 1.0

        # Posições iniciais para efeito parallax
        self.offset_layer1 = 0
        self.offset_layer2 = 0

        # Timer para mover as camadas
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_background)
        self.timer.start(30)

        # Adicionar as camadas de desfoque nas laterais
        self.left_blur = QLabel(self)
        self.right_blur = QLabel(self)

        # Configuração do efeito de desfoque
        blur_effect = QGraphicsBlurEffect()
        blur_effect.setBlurRadius(20)

        # Ajustando o tamanho e posição das camadas de desfoque
        self.left_blur.setGeometry(0, 0, 50, self.height())
        self.right_blur.setGeometry(self.width() - 50, 0, 50, self.height())

        # Aplicando o desfoque nas camadas laterais
        self.left_blur.setGraphicsEffect(blur_effect)
        self.right_blur.setGraphicsEffect(blur_effect)

        # Definindo fundo transparente para o efeito de desfoque
        self.left_blur.setStyleSheet("background-color: rgba(0, 0, 0, 60);")
        self.right_blur.setStyleSheet("background-color: rgba(0, 0, 0, 100);")

    def animate_background(self):
        """Anima o deslocamento das camadas de fundo para efeito parallax."""
        self.offset_layer1 += self.speed_layer1
        self.offset_layer2 += self.speed_layer2

        # Resetando o offset para que o movimento seja contínuo
        if self.offset_layer1 >= 40:  # largura de uma célula do grid
            self.offset_layer1 = 0
        if self.offset_layer2 >= 40:
            self.offset_layer2 = 0

        self.update()

    def paintEvent(self, event):
        """Desenha o fundo com linhas de grid para cada camada."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Define o fundo com a cor #1C1E22
        painter.fillRect(self.rect(), QColor("#1C1E22"))

        # Cor do grid (azul elétrico claro)
        grid_color = QColor(58, 124, 165, 150)

        # Desenhando primeira camada de grid com movimento
        self.draw_grid(painter, grid_color, int(self.offset_layer1), 40)

        # Desenhando segunda camada de grid com movimento
        self.draw_grid(painter, grid_color.darker(120), int(self.offset_layer2), 20)

    def draw_grid(self, painter, color, offset, spacing):
        """Desenha uma camada do grid com uma cor, offset e espaçamento especificados."""
        painter.setPen(color)
        width = self.width()
        height = self.height()

        # Desenhar linhas verticais
        for x in range(-spacing, width + spacing, spacing):
            painter.drawLine(int(x + offset), 0, int(x + offset), height)

        # Desenhar linhas horizontais
        for y in range(-spacing, height + spacing, spacing):
            painter.drawLine(0, int(y + offset), width, int(y + offset))

###CLASSE DA JANELA DE CADASTRO
class SignUpWindow(QMainWindow):


    def __init__(self): ###inicia as funções nesta janela
        super().__init__()
        uic.loadUi("frm_contas.ui", self)
         # Conectar à collection do MongoDB
        self.collection = collection

        # Configurar o fundo ParallaxBackground
        self.parallax_background = ParallaxBackground(self)
        self.layout().addWidget(self.parallax_background)
        self.parallax_background.lower()  # Garante que o objeto fique no fundo
        # Conectar o botão para abrir a janela de cadastro
        self.btn_login.clicked.connect(self.show_signin_window)
        self.btn_cadastrar.clicked.connect(self.cadastrar_usuario)

    def show_signin_window(self):
        # Fecha a janela de cadastro e abre a de login
        self.close()
        self.signup_window = MainWindow()  # Instancia a janela main de login
        self.signup_window.show()

    def cadastrar_usuario(self):
        
        # Obter os valores dos campos
        usuario = self.txt_usuario.text()
        senha = self.txt_senha.text()
        email = self.txt_email.text()
        confirmar_senha = self.txt_confirmarSenha.text()
        tipo = self.cmb_tipo.currentText()

        # Validação da senha com regex
        if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$", senha):
            QMessageBox.warning(self, 'Erro', 'A senha deve ter pelo menos 8 caracteres, incluindo letras e números.')
            return

        # Confirmar se as senhas coincidem
        if senha != confirmar_senha:
            QMessageBox.warning(self, 'Erro', 'As senhas não coincidem.')
            return

        # Criptografar a senha com bcrypt
        senha_inserida = senha.encode('utf-8')  # Converter para bytes para o bcrypt
        senha_hash = bcrypt.hashpw(senha_inserida, bcrypt.gensalt())

        # Inserir dados na coleção users
        user_data = {
            'usuario': usuario,
            'senha': senha_hash,  # armazenar o hash, não a senha em texto simples
            'email': email,
            'role': tipo
        }

        # Inserir no MongoDB
        self.collection.insert_one(user_data)
        QMessageBox.information(self, 'Sucesso', 'Usuário cadastrado com sucesso!')

        # Limpar os campos
        self.txt_usuario.clear()
        self.txt_senha.clear()
        self.txt_email.clear()
        self.txt_confirmarSenha.clear()

    

####CLASSE DA JANELA DE LOGIN
class MainWindow(QMainWindow):
    def __init__(self): ###inicia as funções nesta janela
        super().__init__()
    
        # Carrega a UI
        uic.loadUi("frm_login.ui", self)

        # Configurar o fundo ParallaxBackground
        self.parallax_background = ParallaxBackground(self)
        self.layout().addWidget(self.parallax_background)
        self.parallax_background.lower()  # Garante que o objeto fique no fundo

        # Conectar à collection do MongoDB
        self.collection = collection
        # Aponta o btn para o método correspondente
        self.btn_cadastro.clicked.connect(self.show_signup_window)
        self.btn_login.clicked.connect(self.verificar_usuario)

    def show_signup_window(self):
        # Fecha a janela de login e abre a de cadastro
        self.close()
        self.signup_window = SignUpWindow()  # Instancia a janela de cadastro
        self.signup_window.show()

    
    ###### VERIFICA O LOGIN #########
    def verificar_usuario(self):
        usuario = self.txt_usuario.text()
        senha_inserida = self.txt_senha.text()

        # Buscar usuário no MongoDB
        user_data = self.collection.find_one({"usuario": usuario})

        # Verifica a senha
        senha_hash = user_data['senha']  # Obtém o hash da senha do banco de dados
        if isinstance(senha_hash, str):  # Verifica se o hash está como string
            senha_hash = senha_hash.encode('utf-8')  # Converte para bytes se necessário

        if bcrypt.checkpw(senha_inserida.encode('utf-8'), senha_hash):
            QMessageBox.information(self, 'Sucesso', 'Login realizado com sucesso!')
            # Carregar a próxima interface
            self.open_books_window()  # Chamar método para abrir a nova janela
            self.close()
        else:
            QMessageBox.warning(self, 'Erro', 'Senha incorreta.')

    def open_books_window(self):

        self.close()
        self.books_window = Books()  # Criar nova janela

        self.books_window.show()  # Mostrar a nova janela

##Classe da janela de livros

class Books(QMainWindow):
    def __init__(self,):
        super().__init__()
        uic.loadUi("frm_books.ui", self)

        # Conectar à collection do MongoDB
        self.collection = db['Books']  # Conectando à coleção de livros

        # Configurar o fundo ParallaxBackground
        self.parallax_background = ParallaxBackground(self)
        self.layout().addWidget(self.parallax_background)
        self.parallax_background.lower()  # Garante que o objeto fique no fundo

        # Configurações do QTableWidget
        self.tbl_books.setColumnCount(5)  # Número de colunas a exibir
        self.tbl_books.setHorizontalHeaderLabels(["Título", "Autor", "Ano", "Páginas", "ISBN", "Editar", "Excluir"])

        # Carregar dados dos livros ao abrir a janela
        self.load_books()

        # Conectar botões de ação
        self.btn_add_book.clicked.connect(self.add_book)
        self.tbl_books.itemChanged.connect(self.edit_book)  # Salva mudanças feitas diretamente na célula
        self.tbl_books.cellClicked.connect(self.delete_book)  # A coluna de exclusão pode acionar essa função

    def load_books(self):
        """Carrega os livros do MongoDB para a tabela."""
        self.tbl_books.setRowCount(0)  # Limpa as linhas antes de carregar novos dados


        
        for i, book in enumerate(self.collection.find()):
                # Adiciona uma nova linha na tabela para cada livro
                self.tbl_books.insertRow(i)
                self.tbl_books.setItem(i, 0, QTableWidgetItem(book["titulo"]))
                self.tbl_books.setItem(i, 1, QTableWidgetItem(book["autor"]))
                #self.tbl_books.setItem(i, 2, QTableWidgetItem(str(book["ano_lancamento"]))) BUGADO
                #self.tbl_books.setItem(i, 3, QTableWidgetItem(str(book["numero_paginas"])))
                self.tbl_books.setItem(i, 4, QTableWidgetItem(book["isbn"]))


    def add_book(self):
        """Adiciona um novo livro ao MongoDB e à tabela."""
        titulo = self.txt_titulo.text()
        autor = self.txt_autor.text()
        ano_lancamento = int(self.txt_ano.text())
        numero_paginas = int(self.txt_paginas.text())
        isbn = self.txt_isbn.text()
        foto_capa = self.txt_foto.text()


        # Adiciona ao MongoDB
        new_book = {
            "titulo": titulo,
            "autor": autor,
            "ano_lancamento": ano_lancamento,
            "numero_paginas": numero_paginas,
            "isbn": isbn,
            "foto_capa" : foto_capa

        }
        self.collection.insert_one(new_book)

        # Limpa campos de entrada
        self.txt_titulo.clear()
        self.txt_autor.clear()
        self.txt_ano.clear()
        self.txt_paginas.clear()
        self.txt_isbn.clear()
        self.txt_foto.clear()

        # Recarrega a tabela
        self.load_books()

    def edit_book(self, item):
        """Edita um livro quando o item na tabela é alterado."""
        row = item.row()
        column = item.column()
        livro_id = self.tbl_books.item(row, 0).text()  # Assume que o ID é exibido na primeira coluna

        # Atualiza o campo editado no MongoDB
        field_map = {0: "titulo", 1: "autor", 2: "ano_lancamento", 3: "numero_paginas", 4: "isbn"}
        field = field_map[column]
        new_value = item.text()

        # Verifica se é numérico para ano e páginas
        if field in ["ano_lancamento", "numero_paginas"]:
            new_value = int(new_value)

        # Atualiza no MongoDB
        self.collection.update_one({"_id": livro_id}, {"$set": {field: new_value}})

    def delete_book(self, row, column):
        """Remove o livro selecionado."""
        if column == 5:  # Suponha que a coluna 5 é destinada a deletar
            livro_id = self.tbl_books.item(row, 0).text()
            self.collection.delete_one({"_id": livro_id})
            self.load_books()  # Recarrega para remover da tabela

            
    def show_signin_window(self):
        # Fecha a janela de cadastro e abre a de login
        self.close()
        self.signup_window = MainWindow()  # Instancia a janela main de login
        self.signup_window.show()
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
