# Sistema de Clientes e Pedidos (Tkinter)

Este é um aplicativo desktop simples criado com Python e Tkinter para gerenciar clientes e seus pedidos, utilizando um banco de dados SQLite.

## Estrutura

* `main.py`: Ponto de entrada da aplicação.
* `db.py`: Gerenciamento da conexão e execução de comandos no banco de dados SQLite.
* `models.py`: Camada de abstração para operações de CRUD (Clientes, Pedidos).
* `utils.py`: Funções auxiliares (ex: validação de e-mail).
* `views/`: Contém os módulos da interface gráfica (GUI).
    * `client_list.py`: Frame principal com a lista (Treeview) de clientes.
    * `client_form.py`: Janela (Toplevel) para adicionar/editar clientes.
    * `order_form.py`: Janela (Toplevel) para criar novos pedidos.
    * `product_form`: Janela (Toplevel) para criar novos produtos.
    * `product_list`: Frame com lista (Treeview) de produtos.
* `clientes_pedidos.db`: Arquivo do banco de dados (criado na primeira execução).
* `app.log`: Arquivo de log (criado na primeira execução).

## Como Executar

1.  Certifique-se de ter o Python 3 instalado.

2.  (Opcional) Crie um ambiente virtual:

    ```bash
    # Linux/macOS
    python -m venv .venv
    source .venv/bin/activate
    
    # Windows
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3.  Execute o arquivo `main.py`:

    ```bash
    python main.py
    ```

4.  O banco de dados `clientes_pedidos.db` e o log `app.log` serão criados automaticamente no diretório.

---

## Prompts usados com o Gemini:

**Prompt 1 — Modelagem e DB**
> “Crie, para um app Tkinter, o esquema de SQLite com tabelas clientes (id, nome, email, telefone) e pedidos (id, cliente_id, data, total) e itens_pedido (id, pedido_id, produto, quantidade, preco_unit). Gere funções Python em db.py para inicializar o banco e executar comandos parametrizados com tratamento de erros.”

**Prompt 2 — Formulário de Cliente**
> “Gere um formulário Tkinter (janela Toplevel) para cadastrar/editar Clientes com campos nome, e-mail e telefone. Valide: nome obrigatório, e-mail em formato simples, telefone com 8–15 dígitos. Inclua botões Salvar/Cancelar e callbacks separados.”

**Prompt 3 — Lista de Clientes com busca**
> “Crie um frame Tkinter com Treeview para listar clientes, com barra de busca por nome/email e botões Novo/Editar/Excluir. Ao excluir, peça confirmação. Recarregue a lista após operações.”

**Prompt 4 — Pedido com itens**
> “Implemente uma janela Tkinter para criar Pedido: selecione Cliente (Combobox), campo Data (hoje por padrão), tabela de itens (produto/quantidade/preço), botões Adicionar/Remover item e cálculo automático do total. Salve em pedidos e itens_pedido de forma transacional.”

**Prompt 5 — UX e validações**
> “Melhore UX do app: mensagens amigáveis (messagebox), validações com feedback, prevenção de fechar janela com dados não salvos, e try/except com logs simples.”

**Prompt 6 — Dashboard inicial**
> “Crie uma tela inicial (Frame ou Toplevel) chamada Dashboard que exiba:
• total de clientes,
• total de pedidos no mês,
• ticket médio.
Use consultas SQLite agregadas e widgets Label para mostrar os números.
Inclua botão Atualizar para recalcular e mostre mensagens amigáveis via 
messagebox.”

**Prompt 7 — Relatorios e exportação**
> “Implemente uma janela ‘Relatórios’ com filtros por data inicial/final e cliente 
(Combobox).
Liste os pedidos filtrados em uma Treeview mostrando cliente, data, itens e total.
Adicione botões para Exportar CSV e Exportar PDF (usando reportlab) e abra o arquivo 
após gerar.
Use tratamento try/except e logging.”

**Prompt 8 — Análise IA**
> “Adicione botão ‘Analisar Pedidos’ que lê os 5 últimos pedidos do banco, gera um 
resumo textual e envia via API para ChatGPT ou Ollama local.
A IA deve retornar insights como ‘produtos mais vendidos’ ou ‘média de valor’.
Mostre o resultado em Text widget com rolagem.
Mantenha a função analisar_pedidos() em utils.py e registre no README o prompt 
usado.”

**Prompt 9 — Histórico de ações**
> “Adicione registro automático de ações (Criar, Editar, Excluir Cliente/Pedido) em 
logs/app.log com timestamp.
Crie janela ‘Histórico’ que lê esse arquivo e exibe os eventos em Listbox ou Text.
Inclua botão ‘Limpar Histórico’ com confirmação via messagebox.”

**Prompt 10 — Menu e melhoria de UI/UX**
> “Implemente menu principal (Menu bar) com opções:
• Clientes
• Pedidos
• Relatórios
• IA / Análises
• Sair
Bloqueie fechamento se houver alterações não salvas, exiba confirmações, e permita 
alternar tema claro/escuro via ttk.Style().
Mantenha estilo limpo e responsivo.”

