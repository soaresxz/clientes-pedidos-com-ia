Sistema de Clientes e Pedidos (Tkinter)

Este é um aplicativo desktop simples criado com Python e Tkinter para gerenciar clientes e seus pedidos, utilizando um banco de dados SQLite.

Estrutura

main.py: Ponto de entrada da aplicação.

db.py: Gerenciamento da conexão e execução de comandos no banco de dados SQLite.

models.py: Camada de abstração para operações de CRUD (Clientes, Pedidos).

utils.py: Funções auxiliares (ex: validação de e-mail).

views/: Contém os módulos da interface gráfica (GUI).

client_list.py: Frame principal com a lista (Treeview) de clientes.

client_form.py: Janela (Toplevel) para adicionar/editar clientes.

order_form.py: Janela (Toplevel) para criar novos pedidos.

clientes_pedidos.db: Arquivo do banco de dados (criado na primeira execução).

app.log: Arquivo de log (criado na primeira execução).

Como Executar

Certifique-se de ter o Python 3 instalado.

(Opcional) Crie um ambiente virtual:

python -m venv .venv
source .venv/bin/activate  # (Linux/macOS)
.\.venv\Scripts\activate    # (Windows)


Execute o arquivo main.py:

python main.py


O banco de dados clientes_pedidos.db e o log app.log serão criados automaticamente no diretório.