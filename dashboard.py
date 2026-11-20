import customtkinter as ctk
from tkinter import Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def criar_dashboard(frame_pai):
    """
    Dashboard que mostra vendas com valores reais
    """
    
    # Limpar tela
    for widget in frame_pai.winfo_children():
        widget.destroy()

    ctk.CTkLabel(
        frame_pai,
        text="Dashboard de Vendas",
        font=ctk.CTkFont(size=26, weight="bold")
    ).pack(pady=20)

    try:
        from Back import cursor, con
        
        print("🔍 Tentando executar query...")
        
        # Primeiro, vamos testar se a tabela existe
        cursor.execute("SHOW TABLES LIKE 'itens_venda'")
        tabela_existe = cursor.fetchone()
        
        if not tabela_existe:
            print("❌ Tabela 'itens_venda' NÃO existe!")
            ctk.CTkLabel(
                frame_pai, 
                text="❌ Tabela de vendas não criada. Execute o SQL primeiro!",
                font=ctk.CTkFont(size=14),
                text_color="red"
            ).pack(pady=20)
            return
        
        print("✅ Tabela 'itens_venda' existe")
        
        # Query: Busca dados reais das vendas
        cursor.execute("""
            SELECT 
                iv.nome_produto,
                SUM(iv.quantidade) as total_vendido,
                SUM(iv.subtotal) as faturamento_total
            FROM itens_venda iv
            GROUP BY iv.nome_produto
            ORDER BY total_vendido DESC
        """)

        dados = cursor.fetchall()
        print(f"📊 Dados retornados: {len(dados)} registros")

        if not dados or len(dados) == 0:
            print("⚠️ Nenhuma venda registrada")
            ctk.CTkLabel(
                frame_pai, 
                text="Nenhuma venda registrada ainda.",
                font=ctk.CTkFont(size=14)
            ).pack(pady=20)
            return

        # Processa dados
        nomes = []
        quantidades = []
        faturamentos = []
        lucros = []
        
        total_vendas = 0
        total_faturamento = 0
        total_lucro = 0

        for row in dados:
            nome_produto = row[0]
            qtd = int(row[1]) if row[1] else 0
            faturamento = float(row[2]) if row[2] else 0
            
            print(f"  Processando: {nome_produto} - Qtd: {qtd} - Faturamento: R$ {faturamento}")
            
            # Buscar valor de custo do produto
            cursor.execute("""
                SELECT valor_custo FROM produto WHERE nome_produto = %s
            """, (nome_produto,))
            
            custo_result = cursor.fetchone()
            valor_custo = float(custo_result[0]) if custo_result and custo_result[0] else 0
            
            lucro = faturamento - (qtd * valor_custo)
            
            nomes.append(nome_produto)
            quantidades.append(qtd)
            faturamentos.append(faturamento)
            lucros.append(lucro)
            
            total_vendas += qtd
            total_faturamento += faturamento
            total_lucro += lucro

        print(f"\n💰 Totais: Vendas={total_vendas}, Faturamento=R${total_faturamento}, Lucro=R${total_lucro}")

        # ============================
        # CARDS SUPERIORES
        # ============================

        frame_cards = ctk.CTkFrame(frame_pai)
        frame_cards.pack(fill="x", padx=20, pady=10)

        def criar_card(titulo, valor, cor):
            """Cria um card de métrica"""
            f = ctk.CTkFrame(
                frame_cards,
                fg_color=("#F0F0F0", "#212121"),
                border_width=2,
                border_color=cor
            )
            f.pack(side="left", expand=True, fill="both", padx=10, pady=10)

            ctk.CTkLabel(
                f, 
                text=titulo, 
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("gray30", "gray70")
            ).pack(pady=8)
            
            ctk.CTkLabel(
                f,
                text=valor,
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color=cor
            ).pack(pady=8)

        criar_card("Total de Itens Vendidos", str(total_vendas), "#00B050")
        criar_card("Faturamento Total", f"R$ {total_faturamento:,.2f}".replace(",", "."), "#0070C0")
        criar_card("Lucro Total", f"R$ {total_lucro:,.2f}".replace(",", "."), "#FFC000")
        
        if nomes:
            criar_card("Produto Mais Vendido", nomes[0], "#FF6B6B")

        # ============================
        # FRAME DOS GRÁFICOS
        # ============================

        frame_graficos = ctk.CTkFrame(frame_pai)
        frame_graficos.pack(fill="both", expand=True, padx=20, pady=20)

        # ============================
        # GRÁFICO 1 - TOP 5 MAIS VENDIDOS
        # ============================

        fig1 = Figure(figsize=(6, 4), dpi=100, facecolor='white')
        ax1 = fig1.add_subplot(111)
        
        top_5_nomes = nomes[:5] if len(nomes) >= 5 else nomes
        top_5_qtd = quantidades[:5] if len(quantidades) >= 5 else quantidades
        
        cores_grafico = ['#0070C0', '#00B050', '#FFC000', '#FF6B6B', '#70AD47']
        ax1.bar(top_5_nomes, top_5_qtd, color=cores_grafico[:len(top_5_nomes)])
        ax1.set_title("Top 5 Produtos Mais Vendidos", fontsize=12, fontweight='bold')
        ax1.set_ylabel("Quantidade", fontsize=10)
        ax1.tick_params(axis='x', rotation=45, labelsize=9)
        ax1.grid(axis='y', alpha=0.3, linestyle='--')
        fig1.tight_layout()

        canvas1 = FigureCanvasTkAgg(fig1, master=frame_graficos)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side="left", fill="both", expand=True, padx=10)

        # ============================
        # GRÁFICO 2 - LUCRO POR PRODUTO
        # ============================

        fig2 = Figure(figsize=(6, 4), dpi=100, facecolor='white')
        ax2 = fig2.add_subplot(111)
        
        top_5_lucros = lucros[:5] if len(lucros) >= 5 else lucros
        
        cores_lucro = ['#00B050' if l > 0 else '#FF6B6B' for l in top_5_lucros]
        
        ax2.bar(top_5_nomes, top_5_lucros, color=cores_lucro)
        ax2.set_title("Lucro por Produto", fontsize=12, fontweight='bold')
        ax2.set_ylabel("Lucro (R$)", fontsize=10)
        ax2.tick_params(axis='x', rotation=45, labelsize=9)
        ax2.grid(axis='y', alpha=0.3, linestyle='--')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        fig2.tight_layout()

        canvas2 = FigureCanvasTkAgg(fig2, master=frame_graficos)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side="right", fill="both", expand=True, padx=10)

        # ============================
        # GRÁFICO 3 - FATURAMENTO
        # ============================

        frame_grafico3 = ctk.CTkFrame(frame_pai)
        frame_grafico3.pack(fill="both", expand=True, padx=20, pady=20)

        fig3 = Figure(figsize=(12, 4), dpi=100, facecolor='white')
        ax3 = fig3.add_subplot(111)
        
        top_5_faturamento = faturamentos[:5] if len(faturamentos) >= 5 else faturamentos
        
        ax3.bar(top_5_nomes, top_5_faturamento, color='#0070C0')
        ax3.set_title("Faturamento por Produto", fontsize=12, fontweight='bold')
        ax3.set_ylabel("Faturamento (R$)", fontsize=10)
        ax3.tick_params(axis='x', rotation=45, labelsize=9)
        ax3.grid(axis='y', alpha=0.3, linestyle='--')
        fig3.tight_layout()

        canvas3 = FigureCanvasTkAgg(fig3, master=frame_grafico3)
        canvas3.draw()
        canvas3.get_tk_widget().pack(fill="both", expand=True)

        print("✅ Dashboard renderizado com sucesso!")

    except Exception as e:
        print(f"❌ ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        
        ctk.CTkLabel(
            frame_pai, 
            text=f"❌ Erro: {str(e)}", 
            text_color="red",
            font=ctk.CTkFont(size=12)
        ).pack(pady=20)

def atualizar_dashboard(frame_pai):
    """Atualiza o dashboard com dados novos"""
    criar_dashboard(frame_pai)