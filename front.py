import customtkinter as ctk
from tkinter import ttk, messagebox
from Back import estoque, fornecedor, categoria, produto, venda, composicao
from dashboard import criar_dashboard

def abrir_gestor(janela_login):
    """Abre a janela principal do Gestor"""
    
    janela = ctk.CTk()
    janela.title("Gestor X")
    janela.geometry("1100x600")

    # ======================
    # LAYOUT PRINCIPAL
    # ======================

    menu = ctk.CTkFrame(janela, width=200)
    menu.pack(side="left", fill="y", padx=10, pady=10)

    conteudo = ctk.CTkFrame(janela)
    conteudo.pack(side="right", expand=True, fill="both", padx=10, pady=10)

    def limpar_conteudo():
        for widget in conteudo.winfo_children():
            widget.destroy()

    # ======================
    # DASHBOARD
    # ======================

    def tela_inicial():
        limpar_conteudo()
        criar_dashboard(conteudo)

    # ======================
    # ESTOQUE
    # ======================

    def tela_estoque():
        limpar_conteudo()

        ctk.CTkLabel(conteudo, text="Estoque", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        # Frame principal dividido em duas partes
        frame_esquerda = ctk.CTkFrame(conteudo)
        frame_esquerda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        frame_direita = ctk.CTkFrame(conteudo)
        frame_direita.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ===== LADO ESQUERDO: FORMULÁRIO =====

        ctk.CTkLabel(frame_esquerda, text="Adicionar Produto", font=("Arial", 14, "bold")).pack(pady=10)

        campos_info = [
            ("Nome do Produto", "nome"),
            ("Quantidade", "quantidade"),
            ("Custo Unitário (R$)", "custo"),
            ("Preço de Venda (R$)", "preco_venda"),
            ("Validade (YYYY-MM-DD)", "validade")
        ]

        entradas = {}

        ctk.CTkLabel(frame_esquerda, text="Categoria:", font=("Arial", 12)).pack(pady=5)
        combo_categoria = ctk.CTkComboBox(
            frame_esquerda, 
            values=[c[1] for c in categoria.obter_categorias()],
            width=300
        )
        combo_categoria.pack(pady=5)

        for label, chave in campos_info:
            ctk.CTkLabel(frame_esquerda, text=label, font=("Arial", 11)).pack(pady=5)
            entrada = ctk.CTkEntry(frame_esquerda, width=300)
            entrada.pack(pady=5)
            entradas[chave] = entrada

        # Botões de ação do formulário
        frame_botoes_form = ctk.CTkFrame(frame_esquerda)
        frame_botoes_form.pack(fill="x", pady=10)

        def limpar_formulario():
            for entrada in entradas.values():
                entrada.delete(0, "end")
            combo_categoria.set("")

        def adicionar_produto_estoque():
            # Validar campos
            if not all(entradas[k].get() for k in entradas):
                messagebox.showerror("Erro", "Preencha todos os campos")
                return

            # Obter ID da categoria
            cat = combo_categoria.get()
            id_cat = None
            if cat:
                for c in categoria.obter_categorias():
                    if c[1] == cat:
                        id_cat = c[0]
                        break

            # Adicionar ao banco
            if estoque.cadastro_estoque_completo(
                entradas["nome"].get(),
                entradas["quantidade"].get(),
                entradas["custo"].get(),
                entradas["preco_venda"].get(),
                entradas["validade"].get(),
                id_cat
            ):
                messagebox.showinfo("Sucesso", "Produto adicionado!")
                limpar_formulario()
                atualizar_tabela()
            else:
                messagebox.showerror("Erro", "Falha ao adicionar produto")

        ctk.CTkButton(
            frame_botoes_form,
            text="Adicionar",
            command=adicionar_produto_estoque,
            width=100,
            fg_color="green"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes_form,
            text="Limpar",
            command=limpar_formulario,
            width=100,
            fg_color="orange"
        ).pack(side="left", padx=5)

        # ===== LADO DIREITO: TABELA =====

        ctk.CTkLabel(frame_direita, text="Produtos em Estoque", font=("Arial", 14, "bold")).pack(pady=10)

        # Barra de pesquisa
        barra_pesquisa = ctk.CTkFrame(frame_direita)
        barra_pesquisa.pack(fill="x", padx=5, pady=5)

        pesquisa_entry = ctk.CTkEntry(barra_pesquisa, placeholder_text="Pesquisar...")
        pesquisa_entry.pack(side="left", fill="x", expand=True, padx=5)

        def pesquisar_produto():
            termo = pesquisa_entry.get()
            if not termo:
                atualizar_tabela()
                return

            tabela.delete(*tabela.get_children())
            dados = estoque.pesquisar_estoque(termo)
            for item in dados:
                tabela.insert("", "end", values=item)

        ctk.CTkButton(
            barra_pesquisa,
            text="Buscar",
            command=pesquisar_produto,
            width=80
        ).pack(side="right", padx=5)

        # Tabela
        tabela = ttk.Treeview(
            frame_direita,
            columns=("id","nome","quantidade","custo","preco_venda","validade","categoria"),
            show="headings",
            height=12
        )

        tabela.heading("id", text="ID")
        tabela.heading("nome", text="Nome")
        tabela.heading("quantidade", text="Qtd")
        tabela.heading("custo", text="Custo")
        tabela.heading("preco_venda", text="Preço Venda")
        tabela.heading("validade", text="Validade")
        tabela.heading("categoria", text="Categoria")

        tabela.column("id", width=30)
        tabela.column("nome", width=80)
        tabela.column("quantidade", width=50)
        tabela.column("custo", width=60)
        tabela.column("preco_venda", width=80)
        tabela.column("validade", width=70)
        tabela.column("categoria", width=70)

        tabela.pack(fill="both", expand=True, pady=10)

        # Frame de botões da tabela
        frame_botoes_tabela = ctk.CTkFrame(frame_direita)
        frame_botoes_tabela.pack(fill="x", pady=10)

        def editar_produto():
            sel = tabela.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um produto")
                return

            valores = tabela.item(sel)["values"]

            # Janela de edição
            janela_edit = ctk.CTkToplevel(janela)
            janela_edit.title("Editar Produto")
            janela_edit.geometry("350x550")

            ctk.CTkLabel(janela_edit, text="Categoria:", font=("Arial", 12)).pack(pady=5)
            combo_cat_edit = ctk.CTkComboBox(
                janela_edit, 
                values=[c[1] for c in categoria.obter_categorias()]
            )
            combo_cat_edit.set(valores[6] if valores[6] else "")
            combo_cat_edit.pack(pady=5)

            campos_edit = {}
            labels_edit = ["Nome", "Quantidade", "Custo Unitário", "Preço de Venda", "Validade (YYYY-MM-DD)"]

            for i, label in enumerate(labels_edit):
                ctk.CTkLabel(janela_edit, text=label).pack(pady=5)
                entrada = ctk.CTkEntry(janela_edit)
                entrada.insert(0, str(valores[i+1]))
                entrada.pack(pady=5)
                campos_edit[label] = entrada

            def salvar_edicao():
                cat = combo_cat_edit.get()
                id_cat = None
                if cat:
                    for c in categoria.obter_categorias():
                        if c[1] == cat:
                            id_cat = c[0]
                            break

                if estoque.atualizar_estoque(
                    valores[0],
                    campos_edit["Nome"].get(),
                    campos_edit["Quantidade"].get(),
                    campos_edit["Custo Unitário"].get(),
                    campos_edit["Preço de Venda"].get(),
                    campos_edit["Validade (YYYY-MM-DD)"].get(),
                    id_cat
                ):
                    atualizar_tabela()
                    janela_edit.destroy()
                    messagebox.showinfo("Sucesso", "Produto atualizado!")
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar")

            ctk.CTkButton(janela_edit, text="Salvar", command=salvar_edicao).pack(pady=15)

        def excluir_produto():
            sel = tabela.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um produto")
                return

            valores = tabela.item(sel)["values"]

            if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir?"):
                if estoque.excluir_estoque(valores[0]):
                    atualizar_tabela()
                    messagebox.showinfo("Sucesso", "Produto excluído!")
                else:
                    messagebox.showerror("Erro", "Falha ao excluir")

        ctk.CTkButton(
            frame_botoes_tabela,
            text="Editar",
            command=editar_produto,
            width=80
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes_tabela,
            text="Excluir",
            command=excluir_produto,
            width=80,
            fg_color="red"
        ).pack(side="left", padx=5)

        def atualizar_tabela():
            tabela.delete(*tabela.get_children())
            dados = estoque.obter_estoque()
            for item in dados:
                tabela.insert("", "end", values=item)

        atualizar_tabela()

    # ======================
    # FORNECEDOR
    # ======================

    def tela_fornecedor():
        limpar_conteudo()

        ctk.CTkLabel(conteudo, text="Fornecedores", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        frame_esquerda = ctk.CTkFrame(conteudo)
        frame_esquerda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        frame_direita = ctk.CTkFrame(conteudo)
        frame_direita.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ===== LADO ESQUERDO: FORMULÁRIO =====

        ctk.CTkLabel(frame_esquerda, text="Adicionar Fornecedor", font=("Arial", 14, "bold")).pack(pady=10)

        campos = ["Nome", "CPF/CNPJ", "Telefone", "Email", "CEP", "Cidade", "Número", "Estado"]
        entradas = {}

        for c in campos:
            ctk.CTkLabel(frame_esquerda, text=c, font=("Arial", 11)).pack(pady=5)
            e = ctk.CTkEntry(frame_esquerda, width=300)
            e.pack(pady=5)
            entradas[c] = e

        frame_botoes_form = ctk.CTkFrame(frame_esquerda)
        frame_botoes_form.pack(fill="x", pady=10)

        def limpar_formulario():
            for entrada in entradas.values():
                entrada.delete(0, "end")

        def adicionar_fornecedor_novo():
            if not all(entradas[k].get() for k in list(entradas.keys())[:6]):
                messagebox.showerror("Erro", "Preencha os campos obrigatórios")
                return
            
            if fornecedor.adicionar_fornecedor(
                entradas["Nome"].get(),
                entradas["CPF/CNPJ"].get() if entradas["CPF/CNPJ"].get() else None,
                entradas["Telefone"].get(),
                entradas["Email"].get(),
                entradas["CEP"].get(),
                entradas["Cidade"].get(),
                entradas["Número"].get() if entradas["Número"].get() else None,
                entradas["Estado"].get() if entradas["Estado"].get() else None
            ):
                messagebox.showinfo("Sucesso", "Fornecedor adicionado!")
                limpar_formulario()
                atualizar_tabela()
            else:
                messagebox.showerror("Erro", "Falha ao adicionar fornecedor")

        ctk.CTkButton(
            frame_botoes_form,
            text="Adicionar",
            command=adicionar_fornecedor_novo,
            width=100,
            fg_color="green"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes_form,
            text="Limpar",
            command=limpar_formulario,
            width=100,
            fg_color="orange"
        ).pack(side="left", padx=5)

        # ===== LADO DIREITO: TABELA =====

        ctk.CTkLabel(frame_direita, text="Lista de Fornecedores", font=("Arial", 14, "bold")).pack(pady=10)

        barra_pesquisa = ctk.CTkFrame(frame_direita)
        barra_pesquisa.pack(fill="x", padx=5, pady=5)

        pesquisa_entry = ctk.CTkEntry(barra_pesquisa, placeholder_text="Pesquisar...")
        pesquisa_entry.pack(side="left", fill="x", expand=True, padx=5)

        def pesquisar():
            termo = pesquisa_entry.get()
            if not termo:
                atualizar_tabela()
                return
            
            tabela.delete(*tabela.get_children())
            dados = fornecedor.pesquisar_fornecedor(termo)
            for item in dados:
                tabela.insert("", "end", values=item)

        ctk.CTkButton(
            barra_pesquisa,
            text="Buscar",
            command=pesquisar,
            width=80
        ).pack(side="right", padx=5)

        tabela = ttk.Treeview(
            frame_direita,
            columns=("id","nome","cpf_cnpj","telefone","email","cep","cidade","num","estado"),
            show="headings",
            height=12
        )

        tabela.heading("id", text="ID")
        tabela.heading("nome", text="Nome")
        tabela.heading("cpf_cnpj", text="CPF/CNPJ")
        tabela.heading("telefone", text="Telefone")
        tabela.heading("email", text="Email")
        tabela.heading("cep", text="CEP")
        tabela.heading("cidade", text="Cidade")
        tabela.heading("num", text="Nº")
        tabela.heading("estado", text="Estado")

        for col in tabela["columns"]:
            tabela.column(col, width=70)

        tabela.pack(fill="both", expand=True, pady=10)

        frame_botoes_tabela = ctk.CTkFrame(frame_direita)
        frame_botoes_tabela.pack(fill="x", pady=10)

        def editar():
            sel = tabela.selection()
            if not sel: 
                messagebox.showwarning("Aviso", "Selecione um fornecedor")
                return

            valores = tabela.item(sel)["values"]

            janela_edit = ctk.CTkToplevel(janela)
            janela_edit.title("Editar Fornecedor")
            janela_edit.geometry("350x550")

            campos_edit = {}
            for i, c in enumerate(campos):
                ctk.CTkLabel(janela_edit, text=c).pack(pady=5)
                e = ctk.CTkEntry(janela_edit)
                e.insert(0, str(valores[i+1]) if valores[i+1] else "")
                e.pack(pady=5)
                campos_edit[c] = e

            def salvar():
                if fornecedor.atualizar_fornecedor(
                    valores[0],
                    campos_edit["Nome"].get(),
                    campos_edit["CPF/CNPJ"].get() if campos_edit["CPF/CNPJ"].get() else None,
                    campos_edit["Telefone"].get(),
                    campos_edit["Email"].get(),
                    campos_edit["CEP"].get(),
                    campos_edit["Cidade"].get(),
                    campos_edit["Número"].get() if campos_edit["Número"].get() else None,
                    campos_edit["Estado"].get() if campos_edit["Estado"].get() else None
                ):
                    atualizar_tabela()
                    janela_edit.destroy()
                    messagebox.showinfo("Sucesso", "Fornecedor atualizado!")
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar")

            ctk.CTkButton(janela_edit, text="Salvar", command=salvar).pack(pady=15)

        def excluir():
            sel = tabela.selection()
            if not sel: 
                messagebox.showwarning("Aviso", "Selecione um fornecedor")
                return
            
            valores = tabela.item(sel)["values"]
            
            if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir?"):
                if fornecedor.excluir_fornecedor(valores[0]):
                    atualizar_tabela()
                    messagebox.showinfo("Sucesso", "Fornecedor excluído!")
                else:
                    messagebox.showerror("Erro", "Falha ao excluir")

        ctk.CTkButton(
            frame_botoes_tabela,
            text="Editar",
            command=editar,
            width=80
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes_tabela,
            text="Excluir",
            command=excluir,
            width=80,
            fg_color="red"
        ).pack(side="left", padx=5)

        def atualizar_tabela():
            tabela.delete(*tabela.get_children())
            dados = fornecedor.obter_fornecedor()
            for item in dados:
                tabela.insert("", "end", values=item)

        atualizar_tabela()

    # ======================
    # CATEGORIA
    # ======================

    def tela_categoria():
        limpar_conteudo()

        ctk.CTkLabel(conteudo, text="Categorias", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        frame_esquerda = ctk.CTkFrame(conteudo)
        frame_esquerda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        frame_direita = ctk.CTkFrame(conteudo)
        frame_direita.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ===== LADO ESQUERDO: FORMULÁRIO =====

        ctk.CTkLabel(frame_esquerda, text="Adicionar Categoria", font=("Arial", 14, "bold")).pack(pady=10)

        ctk.CTkLabel(frame_esquerda, text="Nome da Categoria:", font=("Arial", 11)).pack(pady=5)
        entrada_nome = ctk.CTkEntry(frame_esquerda, width=300)
        entrada_nome.pack(pady=5)

        frame_botoes_form = ctk.CTkFrame(frame_esquerda)
        frame_botoes_form.pack(fill="x", pady=10)

        def limpar_formulario():
            entrada_nome.delete(0, "end")

        def adicionar_categoria_novo():
            if not entrada_nome.get():
                messagebox.showerror("Erro", "Preencha o nome")
                return
            
            if categoria.adicionar_categoria(entrada_nome.get()):
                messagebox.showinfo("Sucesso", "Categoria adicionada!")
                limpar_formulario()
                atualizar_tabela()
            else:
                messagebox.showerror("Erro", "Falha ao adicionar")

        ctk.CTkButton(
            frame_botoes_form,
            text="Adicionar",
            command=adicionar_categoria_novo,
            width=100,
            fg_color="green"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes_form,
            text="Limpar",
            command=limpar_formulario,
            width=100,
            fg_color="orange"
        ).pack(side="left", padx=5)

        # ===== LADO DIREITO: TABELA =====

        ctk.CTkLabel(frame_direita, text="Lista de Categorias", font=("Arial", 14, "bold")).pack(pady=10)

        tabela = ttk.Treeview(
            frame_direita,
            columns=("id","nome"),
            show="headings",
            height=12
        )

        tabela.heading("id", text="ID")
        tabela.heading("nome", text="Nome")

        tabela.column("id", width=50)
        tabela.column("nome", width=400)

        tabela.pack(fill="both", expand=True, pady=10)

        frame_botoes_tabela = ctk.CTkFrame(frame_direita)
        frame_botoes_tabela.pack(fill="x", pady=10)

        def editar():
            sel = tabela.selection()
            if not sel: 
                messagebox.showwarning("Aviso", "Selecione uma categoria")
                return

            valores = tabela.item(sel)["values"]

            janela_edit = ctk.CTkToplevel(janela)
            janela_edit.title("Editar Categoria")
            janela_edit.geometry("300x150")

            ctk.CTkLabel(janela_edit, text="Nome da Categoria:").pack(pady=10)
            entrada = ctk.CTkEntry(janela_edit)
            entrada.insert(0, valores[1])
            entrada.pack(pady=10)

            def salvar():
                if categoria.atualizar_categoria(valores[0], entrada.get()):
                    atualizar_tabela()
                    janela_edit.destroy()
                    messagebox.showinfo("Sucesso", "Categoria atualizada!")
                else:
                    messagebox.showerror("Erro", "Falha ao atualizar")

            ctk.CTkButton(janela_edit, text="Salvar", command=salvar).pack(pady=10)

        def excluir():
            sel = tabela.selection()
            if not sel: 
                messagebox.showwarning("Aviso", "Selecione uma categoria")
                return
            
            valores = tabela.item(sel)["values"]
            
            if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir?"):
                if categoria.excluir_categoria(valores[0]):
                    atualizar_tabela()
                    messagebox.showinfo("Sucesso", "Categoria excluída!")
                else:
                    messagebox.showerror("Erro", "Falha ao excluir")

        ctk.CTkButton(
            frame_botoes_tabela,
            text="Editar",
            command=editar,
            width=80
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes_tabela,
            text="Excluir",
            command=excluir,
            width=80,
            fg_color="red"
        ).pack(side="left", padx=5)

        def atualizar_tabela():
            tabela.delete(*tabela.get_children())
            dados = categoria.obter_categorias()
            for item in dados:
                tabela.insert("", "end", values=item)

        atualizar_tabela()

    # ======================
    # VENDA
    # ======================

    def tela_venda():
        limpar_conteudo()

        ctk.CTkLabel(conteudo, text="Montar Pedido", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        frame_esquerda = ctk.CTkFrame(conteudo)
        frame_esquerda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        frame_direita = ctk.CTkFrame(conteudo)
        frame_direita.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ===== LADO ESQUERDO: SELEÇÃO DE ITENS =====

        ctk.CTkLabel(frame_esquerda, text="Itens Disponíveis", font=("Arial", 14, "bold")).pack(pady=10)

        tab_frame = ctk.CTkFrame(frame_esquerda)
        tab_frame.pack(fill="x", padx=5, pady=5)

        var_tab = ctk.StringVar(value="itens")

        def on_tab_change():
            if var_tab.get() == "itens":
                frame_itens.pack(fill="both", expand=True, padx=5, pady=5)
                frame_composicoes.pack_forget()
            else:
                frame_itens.pack_forget()
                frame_composicoes.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkRadioButton(tab_frame, text="Itens", variable=var_tab, value="itens", command=on_tab_change).pack(side="left", padx=10)
        ctk.CTkRadioButton(tab_frame, text="Composições", variable=var_tab, value="composicoes", command=on_tab_change).pack(side="left", padx=10)

        # FRAME ITENS
        frame_itens = ctk.CTkFrame(frame_esquerda)
        frame_itens.pack(fill="both", expand=True, padx=5, pady=5)

        ctk.CTkLabel(frame_itens, text="Selecione um item:").pack(pady=5)
        
        estoque_items = venda.obter_estoque()
        combo_itens = ctk.CTkComboBox(
            frame_itens, 
            values=[f"{item[1]} - R$ {item[3]:.2f}" for item in estoque_items],
            width=300
        )
        combo_itens.pack(pady=5)

        ctk.CTkLabel(frame_itens, text="Quantidade:").pack(pady=5)
        entrada_quantidade = ctk.CTkEntry(frame_itens, width=300)
        entrada_quantidade.insert(0, "1")
        entrada_quantidade.pack(pady=5)

        def adicionar_item():
            selecionado = combo_itens.get()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um item")
                return

            try:
                quantidade = float(entrada_quantidade.get())
                if quantidade <= 0:
                    messagebox.showerror("Erro", "Quantidade deve ser maior que 0")
                    return

                for item in estoque_items:
                    if selecionado.startswith(item[1]):
                        if quantidade > item[2]:
                            messagebox.showerror("Erro", f"Quantidade disponível: {item[2]}")
                            return

                        venda.adicionar_item_ao_lanche(
                            item[0],
                            item[1],
                            quantidade,
                            item[3]
                        )
                        atualizar_pedido()
                        entrada_quantidade.delete(0, "end")
                        entrada_quantidade.insert(0, "1")
                        messagebox.showinfo("Sucesso", f"{item[1]} adicionado!")
                        break
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida")

        ctk.CTkButton(frame_itens, text="Adicionar Item", command=adicionar_item).pack(pady=10)

        # FRAME COMPOSIÇÕES
        frame_composicoes = ctk.CTkFrame(frame_esquerda)

        ctk.CTkLabel(frame_composicoes, text="Selecione uma composição:").pack(pady=5)

        comp_items = composicao.obter_composicoes()
        combo_composicoes = ctk.CTkComboBox(
            frame_composicoes,
            values=[f"{c[1]} - R$ {c[4]:.2f}" if c[4] else f"{c[1]} - R$ {c[2]:.2f}" for c in comp_items],
            width=300
        )
        combo_composicoes.pack(pady=5)

        ctk.CTkLabel(frame_composicoes, text="Quantidade:").pack(pady=5)
        entrada_qtd_comp = ctk.CTkEntry(frame_composicoes, width=300)
        entrada_qtd_comp.insert(0, "1")
        entrada_qtd_comp.pack(pady=5)

        def adicionar_composicao():
            selecionado = combo_composicoes.get()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione uma composição")
                return

            try:
                quantidade = float(entrada_qtd_comp.get())
                if quantidade <= 0:
                    messagebox.showerror("Erro", "Quantidade deve ser maior que 0")
                    return

                for comp in comp_items:
                    nome_comp = comp[1]
                    if selecionado.startswith(nome_comp):
                        preco_venda = comp[4] if comp[4] else comp[2]
                        
                        venda.adicionar_item_ao_lanche(
                            comp[0],
                            f"{nome_comp}",
                            quantidade,
                            preco_venda
                        )
                        
                        atualizar_pedido()
                        entrada_qtd_comp.delete(0, "end")
                        entrada_qtd_comp.insert(0, "1")
                        messagebox.showinfo("Sucesso", f"Composição '{nome_comp}' adicionada!")
                        break
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida")

        ctk.CTkButton(frame_composicoes, text="Adicionar Composição", command=adicionar_composicao).pack(pady=10)

        # ===== LADO DIREITO: RESUMO DO PEDIDO =====

        ctk.CTkLabel(frame_direita, text="Seu Pedido", font=("Arial", 14, "bold")).pack(pady=10)

        tabela_pedido = ttk.Treeview(
            frame_direita,
            columns=("item","qtd","preco","subtotal"),
            show="headings",
            height=12
        )

        tabela_pedido.heading("item", text="Item")
        tabela_pedido.heading("qtd", text="Qtd")
        tabela_pedido.heading("preco", text="Preço")
        tabela_pedido.heading("subtotal", text="Subtotal")

        tabela_pedido.column("item", width=150)
        tabela_pedido.column("qtd", width=50)
        tabela_pedido.column("preco", width=80)
        tabela_pedido.column("subtotal", width=100)

        tabela_pedido.pack(fill="both", expand=True, pady=10)

        frame_total = ctk.CTkFrame(frame_direita)
        frame_total.pack(fill="x", pady=10)

        label_total = ctk.CTkLabel(
            frame_total, 
            text="Total: R$ 0.00", 
            font=("Arial", 16, "bold"),
            text_color="green"
        )
        label_total.pack(pady=10)

        label_lucro = ctk.CTkLabel(
            frame_total,
            text="Lucro estimado: R$ 0.00 (0%)",
            font=("Arial", 12),
            text_color="blue"
        )
        label_lucro.pack()

        frame_desconto = ctk.CTkFrame(frame_direita)
        frame_desconto.pack(fill="x", pady=10)

        ctk.CTkLabel(frame_desconto, text="Desconto (R$):").pack(side="left", padx=5)
        entrada_desconto = ctk.CTkEntry(frame_desconto, width=100)
        entrada_desconto.insert(0, "0")
        entrada_desconto.pack(side="left", padx=5)

        frame_botoes = ctk.CTkFrame(frame_direita)
        frame_botoes.pack(fill="x", pady=10)

        def atualizar_pedido():
            tabela_pedido.delete(*tabela_pedido.get_children())
            
            for item in venda.obter_itens_lanche():
                tabela_pedido.insert("", "end", values=(
                    item['nome_item'],
                    f"{item['quantidade']:.1f}",
                    f"R$ {item['preco_unitario']:.2f}",
                    f"R$ {item['subtotal']:.2f}"
                ))

            total = venda.atualizar_total()
            label_total.configure(text=f"Total: R$ {total:.2f}")

            lucro, percentual = venda.calcular_lucro()
            label_lucro.configure(text=f"Lucro estimado: R$ {lucro:.2f} ({percentual:.1f}%)")

        def remover_item():
            sel = tabela_pedido.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um item para remover")
                return

            items = tabela_pedido.get_children()
            indice = items.index(sel[0])
            
            venda.remover_item_do_lanche(indice)
            atualizar_pedido()

        def limpar_pedido():
            if messagebox.askyesno("Confirmar", "Deseja limpar todo o pedido?"):
                venda.limpar_lanche()
                atualizar_pedido()

        def finalizar_pedido():
            try:
                desconto = float(entrada_desconto.get())
            except ValueError:
                messagebox.showerror("Erro", "Desconto inválido")
                return

            sucesso, mensagem = venda.finalizar_venda(desconto=desconto)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                venda.limpar_lanche()
                atualizar_pedido()
                entrada_desconto.delete(0, "end")
                entrada_desconto.insert(0, "0")
            else:
                messagebox.showerror("Erro", mensagem)

        ctk.CTkButton(
            frame_botoes, 
            text="Remover Item", 
            command=remover_item,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes,
            text="Limpar Pedido",
            command=limpar_pedido,
            width=100,
            fg_color="orange"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes,
            text="Finalizar Venda",
            command=finalizar_pedido,
            width=100,
            fg_color="green"
        ).pack(side="left", padx=5)

        atualizar_pedido()

    # ======================
    # COMPOSIÇÃO
    # ======================

    def tela_composicao():
        limpar_conteudo()

        ctk.CTkLabel(conteudo, text="Composição de Produtos", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        frame_esquerda = ctk.CTkFrame(conteudo)
        frame_esquerda.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        frame_direita = ctk.CTkFrame(conteudo)
        frame_direita.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # ===== LADO ESQUERDO: FORMULÁRIO =====

        ctk.CTkLabel(frame_esquerda, text="Criar Composição", font=("Arial", 14, "bold")).pack(pady=10)

        ctk.CTkLabel(frame_esquerda, text="Nome da Composição:", font=("Arial", 11)).pack(pady=5)
        entrada_nome_comp = ctk.CTkEntry(frame_esquerda, width=300)
        entrada_nome_comp.pack(pady=5)

        ctk.CTkLabel(frame_esquerda, text="Preço de Venda Sugerido (R$):", font=("Arial", 11)).pack(pady=5)
        entrada_preco_venda_comp = ctk.CTkEntry(frame_esquerda, width=300)
        entrada_preco_venda_comp.pack(pady=5)

        ctk.CTkLabel(frame_esquerda, text="Preço de Venda Final (R$):", font=("Arial", 11)).pack(pady=5)
        entrada_preco_venda_final = ctk.CTkEntry(frame_esquerda, width=300)
        entrada_preco_venda_final.pack(pady=5)

        ctk.CTkLabel(frame_esquerda, text="Selecione um item:", font=("Arial", 11)).pack(pady=5)
        
        estoque_items = venda.obter_estoque()
        combo_itens = ctk.CTkComboBox(
            frame_esquerda, 
            values=[f"{item[1]} - R$ {item[3]:.2f}" for item in estoque_items],
            width=300
        )
        combo_itens.pack(pady=5)

        ctk.CTkLabel(frame_esquerda, text="Quantidade:", font=("Arial", 11)).pack(pady=5)
        entrada_quantidade = ctk.CTkEntry(frame_esquerda, width=300)
        entrada_quantidade.insert(0, "1")
        entrada_quantidade.pack(pady=5)

        frame_botoes_form = ctk.CTkFrame(frame_esquerda)
        frame_botoes_form.pack(fill="x", pady=10)

        def adicionar_item():
            selecionado = combo_itens.get()
            if not selecionado:
                messagebox.showwarning("Aviso", "Selecione um item")
                return

            try:
                quantidade = float(entrada_quantidade.get())
                if quantidade <= 0:
                    messagebox.showerror("Erro", "Quantidade deve ser maior que 0")
                    return

                for item in estoque_items:
                    if selecionado.startswith(item[1]):
                        if quantidade > item[2]:
                            messagebox.showerror("Erro", f"Quantidade disponível: {item[2]}")
                            return

                        venda.adicionar_item_ao_lanche(
                            item[0],
                            item[1],
                            quantidade,
                            item[3]
                        )
                        atualizar_composicao()
                        entrada_quantidade.delete(0, "end")
                        entrada_quantidade.insert(0, "1")
                        messagebox.showinfo("Sucesso", f"{item[1]} adicionado!")
                        break
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida")

        def limpar_formulario():
            entrada_nome_comp.delete(0, "end")
            entrada_preco_venda_comp.delete(0, "end")
            entrada_preco_venda_final.delete(0, "end")
            venda.limpar_lanche()
            atualizar_composicao()

        ctk.CTkButton(
            frame_botoes_form,
            text="Adicionar Item",
            command=adicionar_item,
            width=100,
            fg_color="green"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes_form,
            text="Limpar",
            command=limpar_formulario,
            width=100,
            fg_color="orange"
        ).pack(side="left", padx=5)

        # ===== LADO DIREITO: TABELA =====

        ctk.CTkLabel(frame_direita, text="Composição Atual", font=("Arial", 14, "bold")).pack(pady=10)

        tabela_composicao = ttk.Treeview(
            frame_direita,
            columns=("item","qtd","preco","subtotal"),
            show="headings",
            height=10
        )

        tabela_composicao.heading("item", text="Item")
        tabela_composicao.heading("qtd", text="Qtd")
        tabela_composicao.heading("preco", text="Preço")
        tabela_composicao.heading("subtotal", text="Subtotal")

        tabela_composicao.column("item", width=120)
        tabela_composicao.column("qtd", width=50)
        tabela_composicao.column("preco", width=80)
        tabela_composicao.column("subtotal", width=100)

        tabela_composicao.pack(fill="both", expand=True, pady=10)

        frame_totais = ctk.CTkFrame(frame_direita)
        frame_totais.pack(fill="x", pady=10)

        label_total_custo = ctk.CTkLabel(
            frame_totais, 
            text="Custo Total: R$ 0.00", 
            font=("Arial", 12, "bold"),
            text_color="blue"
        )
        label_total_custo.pack(pady=2)

        label_total = ctk.CTkLabel(
            frame_totais, 
            text="Total: R$ 0.00", 
            font=("Arial", 14, "bold"),
            text_color="green"
        )
        label_total.pack(pady=2)

        label_lucro = ctk.CTkLabel(
            frame_totais,
            text="Lucro estimado: R$ 0.00 (0%)",
            font=("Arial", 10),
            text_color="green"
        )
        label_lucro.pack()

        frame_botoes_tabela = ctk.CTkFrame(frame_direita)
        frame_botoes_tabela.pack(fill="x", pady=10)

        def remover_item():
            sel = tabela_composicao.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione um item para remover")
                return

            items = tabela_composicao.get_children()
            indice = items.index(sel[0])
            
            venda.remover_item_do_lanche(indice)
            atualizar_composicao()

        def atualizar_composicao():
            tabela_composicao.delete(*tabela_composicao.get_children())
            
            for item in venda.obter_itens_lanche():
                tabela_composicao.insert("", "end", values=(
                    item['nome_item'],
                    f"{item['quantidade']:.1f}",
                    f"R$ {item['preco_unitario']:.2f}",
                    f"R$ {item['subtotal']:.2f}"
                ))

            total = venda.atualizar_total()
            label_total.configure(text=f"Total: R$ {total:.2f}")

            custo_total = sum(
                item['quantidade'] * item['preco_unitario'] 
                for item in venda.obter_itens_lanche()
            )
            label_total_custo.configure(text=f"Custo Total: R$ {custo_total:.2f}")

            lucro, percentual = venda.calcular_lucro()
            label_lucro.configure(text=f"Lucro estimado: R$ {lucro:.2f} ({percentual:.1f}%)")

        def salvar_composicao():
            nome_comp = entrada_nome_comp.get()
            
            if not nome_comp:
                messagebox.showerror("Erro", "Digite um nome para a composição")
                return

            itens_lanche = venda.obter_itens_lanche()
            if not itens_lanche:
                messagebox.showerror("Erro", "Adicione pelo menos um item")
                return

            total = venda.atualizar_total()
            lucro, percentual = venda.calcular_lucro()

            try:
                preco_venda = float(entrada_preco_venda_comp.get()) if entrada_preco_venda_comp.get() else None
            except ValueError:
                messagebox.showerror("Erro", "Preço de venda sugerido inválido")
                return

            try:
                preco_venda_final = float(entrada_preco_venda_final.get()) if entrada_preco_venda_final.get() else None
            except ValueError:
                messagebox.showerror("Erro", "Preço de venda final inválido")
                return

            if preco_venda_final and preco_venda_final < total:
                messagebox.showwarning("Aviso", f"O preço final (R$ {preco_venda_final:.2f}) é menor que o custo total (R$ {total:.2f})")

            sucesso, mensagem = composicao.salvar_composicao(
                nome_comp,
                total,
                lucro,
                itens_lanche,
                preco_venda,
                preco_venda_final
            )

            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                venda.limpar_lanche()
                entrada_nome_comp.delete(0, "end")
                entrada_preco_venda_comp.delete(0, "end")
                entrada_preco_venda_final.delete(0, "end")
                atualizar_composicao()
                atualizar_tabela_composicoes()
            else:
                messagebox.showerror("Erro", mensagem)

        ctk.CTkButton(
            frame_botoes_tabela,
            text="Remover Item",
            command=remover_item,
            width=80
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes_tabela,
            text="Salvar Composição",
            command=salvar_composicao,
            width=150,
            fg_color="green"
        ).pack(side="left", padx=5)

        # ===== COMPOSIÇÕES SALVAS =====

        ctk.CTkLabel(frame_direita, text="Composições Salvas", font=("Arial", 14, "bold")).pack(pady=10)

        barra_pesquisa = ctk.CTkFrame(frame_direita)
        barra_pesquisa.pack(fill="x", padx=5, pady=5)

        pesquisa_entry = ctk.CTkEntry(barra_pesquisa, placeholder_text="Pesquisar...")
        pesquisa_entry.pack(side="left", fill="x", expand=True, padx=5)

        tabela_salvas = ttk.Treeview(
            frame_direita,
            columns=("id","nome","preco_custo","preco_venda_final"),
            show="headings",
            height=6
        )

        tabela_salvas.heading("id", text="ID")
        tabela_salvas.heading("nome", text="Nome")
        tabela_salvas.heading("preco_custo", text="Custo")
        tabela_salvas.heading("preco_venda_final", text="Preço Final")

        tabela_salvas.column("id", width=30)
        tabela_salvas.column("nome", width=150)
        tabela_salvas.column("preco_custo", width=100)
        tabela_salvas.column("preco_venda_final", width=100)

        tabela_salvas.pack(fill="both", expand=True, pady=5)

        frame_botoes_comp = ctk.CTkFrame(frame_direita)
        frame_botoes_comp.pack(fill="x", pady=5)

        def atualizar_tabela_composicoes():
            tabela_salvas.delete(*tabela_salvas.get_children())
            dados = composicao.obter_composicoes()
            print(f"DEBUG: Composições encontradas: {dados}")
            for item in dados:
                preco_venda_final = f"R$ {item[5]:.2f}" if item[5] else f"R$ {item[4]:.2f}" if item[4] else f"R$ {item[2]:.2f}"
                tabela_salvas.insert("", "end", values=(item[0], item[1], f"R$ {item[2]:.2f}", preco_venda_final))

        def pesquisar_comp():
            termo = pesquisa_entry.get()
            if not termo:
                atualizar_tabela_composicoes()
                return

            tabela_salvas.delete(*tabela_salvas.get_children())
            dados = composicao.pesquisar_composicao(termo)
            for item in dados:
                preco_venda_final = f"R$ {item[5]:.2f}" if item[5] else f"R$ {item[4]:.2f}" if item[4] else f"R$ {item[2]:.2f}"
                tabela_salvas.insert("", "end", values=(item[0], item[1], f"R$ {item[2]:.2f}", preco_venda_final))

        ctk.CTkButton(
            barra_pesquisa,
            text="Buscar",
            command=pesquisar_comp,
            width=80
        ).pack(side="right", padx=5)

        def visualizar_composicao():
            sel = tabela_salvas.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione uma composição")
                return

            valores = tabela_salvas.item(sel)["values"]
            id_comp = valores[0]

            janela_vis = ctk.CTkToplevel(janela)
            janela_vis.title(f"Composição: {valores[1]}")
            janela_vis.geometry("400x350")

            ctk.CTkLabel(janela_vis, text=f"Composição: {valores[1]}", font=("Arial", 14, "bold")).pack(pady=10)
            
            tabela_itens = ttk.Treeview(
                janela_vis,
                columns=("item","qtd","preco","subtotal"),
                show="headings"
            )

            tabela_itens.heading("item", text="Item")
            tabela_itens.heading("qtd", text="Qtd")
            tabela_itens.heading("preco", text="Preço")
            tabela_itens.heading("subtotal", text="Subtotal")

            tabela_itens.column("item", width=120)
            tabela_itens.column("qtd", width=50)
            tabela_itens.column("preco", width=80)
            tabela_itens.column("subtotal", width=100)

            tabela_itens.pack(fill="both", expand=True, pady=10)

            detalhes = composicao.obter_composicao_detalhes(id_comp)
            for item in detalhes:
                subtotal = item[2] * item[3]
                tabela_itens.insert("", "end", values=(item[1], f"{item[2]:.1f}", f"R$ {item[3]:.2f}", f"R$ {subtotal:.2f}"))

            frame_info = ctk.CTkFrame(janela_vis)
            frame_info.pack(fill="x", padx=10, pady=10)

            ctk.CTkLabel(frame_info, text=f"Custo Total: {valores[2]}", font=("Arial", 12, "bold"), text_color="blue").pack()
            ctk.CTkLabel(frame_info, text=f"Preço Final: {valores[3]}", font=("Arial", 12, "bold"), text_color="green").pack()

        def excluir_composicao():
            sel = tabela_salvas.selection()
            if not sel:
                messagebox.showwarning("Aviso", "Selecione uma composição")
                return

            valores = tabela_salvas.item(sel)["values"]

            if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir?"):
                if composicao.excluir_composicao(valores[0]):
                    atualizar_tabela_composicoes()
                    messagebox.showinfo("Sucesso", "Composição excluída!")
                else:
                    messagebox.showerror("Erro", "Falha ao excluir")

        ctk.CTkButton(
            frame_botoes_comp,
            text="Visualizar",
            command=visualizar_composicao,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            frame_botoes_comp,
            text="Excluir",
            command=excluir_composicao,
            width=100,
            fg_color="red"
        ).pack(side="left", padx=5)

        atualizar_composicao()
        atualizar_tabela_composicoes()

        def salvar_composicao(self, nome_composicao, preco_total, lucro_estimado, itens, preco_venda=None, preco_venda_final=None):
            """Salva uma nova composição com seus itens"""
            try:
                print(f"\n🔍 DEBUG: Salvando composição '{nome_composicao}'")
                print(f"  Preço Total: {preco_total}")
                print(f"  Lucro: {lucro_estimado}")
                print(f"  Itens: {len(itens)}")
                
                # Inserir composição
                self.cursor.execute('''
                    INSERT INTO composicao(nome_composicao, preco_total, lucro_estimado, preco_venda, preco_venda_final) 
                    VALUES(%s, %s, %s, %s, %s)
                ''', (nome_composicao, preco_total, lucro_estimado, preco_venda, preco_venda_final))
                
                self.con.commit()
                id_composicao = self.cursor.lastrowid
                print(f"✅ Composição ID {id_composicao} criada")

                # Inserir itens
                for item in itens:
                    print(f"  Inserindo item: {item['nome_item']} - Qtd: {item['quantidade']}")
                    
                    self.cursor.execute('''
                        INSERT INTO composicao_itens(id_composicao, id_item, quantidade, preco_unitario, subtotal)
                        VALUES(%s, %s, %s, %s, %s)
                    ''', (id_composicao, item['id_item'], item['quantidade'], item['preco_unitario'], item['subtotal']))

                self.con.commit()
                print(f"✅ {len(itens)} itens inseridos")
                
                return True, f"Composição '{nome_composicao}' salva com sucesso!"
                
            except Exception as e:
                print(f"❌ ERRO ao salvar composição: {str(e)}")
                import traceback
                traceback.print_exc()
                self.con.rollback()
                return False, f"Erro ao salvar: {e}"
    
        def obter_composicoes(self):
            """Retorna todas as composições salvas"""
            try:
                print("\n🔍 DEBUG: Buscando composições...")
                
                self.cursor.execute('''
                    SELECT id_composicao, nome_composicao, preco_total, lucro_estimado, preco_venda, preco_venda_final
                    FROM composicao
                    ORDER BY data_criacao DESC
                ''')
                
                resultado = self.cursor.fetchall()
                print(f"✅ Composições encontradas: {len(resultado)}")
                
                for comp in resultado:
                    print(f"  - ID: {comp[0]}, Nome: {comp[1]}, Preço: R$ {comp[2]}")
                
                return resultado
                
            except Exception as e:
                print(f"❌ ERRO ao obter composições: {str(e)}")
                import traceback
                traceback.print_exc()
                return []
    
    # ======================
    # MENU
    # ======================

    def sair():
        """Fecha o gestor e volta para login"""
        janela.destroy()
        janela_login.deiconify()

    ctk.CTkButton(menu, text="Dashboard", command=tela_inicial, width=150).pack(pady=10)
    ctk.CTkButton(menu, text="Estoque", command=tela_estoque, width=150).pack(pady=10)
    ctk.CTkButton(menu, text="Fornecedor", command=tela_fornecedor, width=150).pack(pady=10)
    ctk.CTkButton(menu, text="Categoria", command=tela_categoria, width=150).pack(pady=10)
    ctk.CTkButton(menu, text="Venda", command=tela_venda, width=150).pack(pady=10)
    ctk.CTkButton(menu, text="Composição", command=tela_composicao, width=150).pack(pady=10)
    ctk.CTkButton(menu, text="Sair", command=sair, width=150, fg_color="red").pack(pady=10)

    tela_inicial()
    janela.mainloop()