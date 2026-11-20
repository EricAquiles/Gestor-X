import mysql.connector
import unicodedata
import re

def conectar():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="aqswde123",
        database="gestor_x"
    )

con = conectar()
cursor = con.cursor()

from decimal import Decimal

def converter_decimal(valor):
    """Converte Decimal para float se necessário"""
    if isinstance(valor, Decimal):
        return float(valor)
    return valor

def padronizar_texto(texto: str) -> str:
    if not isinstance(texto, str):
        raise ValueError("O valor deve ser um texto")

    texto = texto.strip()
    texto = texto.upper()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode('utf-8')
    texto = re.sub(r'[^A-Z0-9\s]', '', texto)
    texto = re.sub(r'\s+', ' ', texto)
    return texto

def confirmacao_login(usuario, senha):
    """Verifica login no banco de dados"""
    try:
        cursor.execute(
            "SELECT id, nome FROM usuario WHERE nome = %s AND senha = %s",
            (usuario, senha)
        )
        resultado = cursor.fetchone()
        return resultado
    except Exception as e:
        print(f"Erro ao verificar login: {e}")
        return None

class Estoque:
    def __init__(self, cursor, con):
        self.cursor = cursor
        self.con = con

    def obter_estoque(self):
        """Retorna todos os produtos do estoque com preco_venda"""
        try:
            self.cursor.execute('''
                SELECT e.id_item, e.nome_item, e.quantidade, e.custo_unitario, e.preco_venda, e.validade, c.nome
                FROM estoque e
                LEFT JOIN categorias c ON e.id_categoria = c.id_categoria
            ''')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter estoque: {e}")
            return []

    def obter_categorias(self):
        """Retorna todas as categorias"""
        try:
            self.cursor.execute('SELECT id_categoria, nome FROM categorias')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter categorias: {e}")
            return []

    def obter_por_id(self, id_item):
        """Retorna um produto específico"""
        try:
            self.cursor.execute('''
                SELECT e.id_item, e.nome_item, e.quantidade, e.custo_unitario, e.preco_venda, e.validade, c.nome
                FROM estoque e
                LEFT JOIN categorias c ON e.id_categoria = c.id_categoria
                WHERE e.id_item = %s
            ''', (id_item,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Erro ao obter produto: {e}")
            return None

    def cadastro_estoque_completo(self, nome_item, quantidade, custo_unitario, preco_venda, validade, id_categoria=None):
        """Insere um novo produto completo no estoque"""
        try:
            nome_itens = padronizar_texto(nome_item)
            self.cursor.execute('''
                INSERT INTO estoque(nome_item, quantidade, custo_unitario, preco_venda, validade, id_categoria) 
                VALUES(%s, %s, %s, %s, %s, %s)
            ''', (nome_itens, quantidade, custo_unitario, preco_venda, validade, id_categoria))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao cadastrar produto: {e}")
            self.con.rollback()
            return False

    def atualizar_estoque(self, id_item, nome_item, quantidade, custo_unitario, preco_venda, validade, id_categoria=None):
        """Atualiza um produto do estoque"""
        try:
            nome_itens = padronizar_texto(nome_item)
            self.cursor.execute('''
                UPDATE estoque 
                SET nome_item = %s, quantidade = %s, custo_unitario = %s, preco_venda = %s, validade = %s, id_categoria = %s 
                WHERE id_item = %s
            ''', (nome_itens, quantidade, custo_unitario, preco_venda, validade, id_categoria, id_item))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar produto: {e}")
            self.con.rollback()
            return False

    def excluir_estoque(self, id_item):
        """Deleta um produto do estoque"""
        try:
            self.cursor.execute('DELETE FROM estoque WHERE id_item = %s', (id_item,))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir produto: {e}")
            self.con.rollback()
            return False

    def pesquisar_estoque(self, termo):
        """Pesquisa produtos por nome"""
        try:
            termo_padrao = padronizar_texto(termo)
            self.cursor.execute('''
                SELECT e.id_item, e.nome_item, e.quantidade, e.custo_unitario, e.preco_venda, e.validade, c.nome
                FROM estoque e
                LEFT JOIN categorias c ON e.id_categoria = c.id_categoria
                WHERE e.nome_item LIKE %s
            ''', (f"%{termo_padrao}%",))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao pesquisar: {e}")
            return []


class Fornecedor:
    def __init__(self, cursor, con):
        self.cursor = cursor
        self.con = con

    def obter_fornecedor(self):
        """Retorna todos os fornecedores"""
        try:
            self.cursor.execute('''
                SELECT id_fornecedor, nome_fornecedor, cpf_cnpj, telefone, email, cep, cidade, num_local, estado 
                FROM fornecedor
            ''')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter fornecedores: {e}")
            return []

    def adicionar_fornecedor(self, nome_fornecedor, cpf_cnpj, telefone, email, cep, cidade, num_local, estado):
        """Adiciona um novo fornecedor"""
        try:
            nome = padronizar_texto(nome_fornecedor)
            self.cursor.execute('''
                INSERT INTO fornecedor(nome_fornecedor, cpf_cnpj, telefone, email, cep, cidade, num_local, estado) 
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
            ''', (nome, cpf_cnpj, telefone, email, cep, cidade, num_local, estado))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao adicionar fornecedor: {e}")
            self.con.rollback()
            return False

    def atualizar_fornecedor(self, id_fornecedor, nome_fornecedor, cpf_cnpj, telefone, email, cep, cidade, num_local, estado):
        """Atualiza um fornecedor"""
        try:
            nome = padronizar_texto(nome_fornecedor)
            self.cursor.execute('''
                UPDATE fornecedor 
                SET nome_fornecedor = %s, cpf_cnpj = %s, telefone = %s, email = %s, cep = %s, cidade = %s, num_local = %s, estado = %s 
                WHERE id_fornecedor = %s
            ''', (nome, cpf_cnpj, telefone, email, cep, cidade, num_local, estado, id_fornecedor))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar fornecedor: {e}")
            self.con.rollback()
            return False

    def excluir_fornecedor(self, id_fornecedor):
        """Deleta um fornecedor"""
        try:
            self.cursor.execute('DELETE FROM fornecedor WHERE id_fornecedor = %s', (id_fornecedor,))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir fornecedor: {e}")
            self.con.rollback()
            return False

    def pesquisar_fornecedor(self, termo):
        """Pesquisa fornecedores por nome ou cidade"""
        try:
            termo_padrao = padronizar_texto(termo)
            self.cursor.execute('''
                SELECT id_fornecedor, nome_fornecedor, cpf_cnpj, telefone, email, cep, cidade, num_local, estado 
                FROM fornecedor 
                WHERE nome_fornecedor LIKE %s OR cidade LIKE %s
            ''', (f"%{termo_padrao}%", f"%{termo_padrao}%"))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao pesquisar fornecedor: {e}")
            return []


class Categoria:
    def __init__(self, cursor, con):
        self.cursor = cursor
        self.con = con

    def obter_categorias(self):
        """Retorna todas as categorias"""
        try:
            self.cursor.execute('SELECT id_categoria, nome FROM categorias')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter categorias: {e}")
            return []

    def adicionar_categoria(self, nome):
        """Adiciona uma nova categoria"""
        try:
            nome_padrao = padronizar_texto(nome)
            self.cursor.execute('INSERT INTO categorias(nome) VALUES(%s)', (nome_padrao,))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao adicionar categoria: {e}")
            self.con.rollback()
            return False

    def atualizar_categoria(self, id_categoria, nome):
        """Atualiza uma categoria"""
        try:
            nome_padrao = padronizar_texto(nome)
            self.cursor.execute('UPDATE categorias SET nome = %s WHERE id_categoria = %s', (nome_padrao, id_categoria))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar categoria: {e}")
            self.con.rollback()
            return False

    def excluir_categoria(self, id_categoria):
        """Deleta uma categoria"""
        try:
            self.cursor.execute('DELETE FROM categorias WHERE id_categoria = %s', (id_categoria,))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir categoria: {e}")
            self.con.rollback()
            return False


class Produto:
    def __init__(self, cursor, con):
        self.cursor = cursor
        self.con = con

    def obter_produtos(self):
        """Retorna todos os produtos"""
        try:
            self.cursor.execute('SELECT id_produto, nome_produto, valor_venda, valor_custo FROM produto')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter produtos: {e}")
            return []

    def adicionar_produto(self, nome_produto, valor_venda, valor_custo):
        """Adiciona um novo produto"""
        try:
            nome = padronizar_texto(nome_produto)
            self.cursor.execute(
                'INSERT INTO produto(nome_produto, valor_venda, valor_custo) VALUES(%s, %s, %s)',
                (nome, valor_venda, valor_custo)
            )
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao adicionar produto: {e}")
            self.con.rollback()
            return False

    def atualizar_produto(self, id_produto, nome_produto, valor_venda, valor_custo):
        """Atualiza um produto"""
        try:
            nome = padronizar_texto(nome_produto)
            self.cursor.execute(
                'UPDATE produto SET nome_produto = %s, valor_venda = %s, valor_custo = %s WHERE id_produto = %s',
                (nome, valor_venda, valor_custo, id_produto)
            )
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar produto: {e}")
            self.con.rollback()
            return False

    def excluir_produto(self, id_produto):
        """Deleta um produto"""
        try:
            self.cursor.execute('DELETE FROM produto WHERE id_produto = %s', (id_produto,))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir produto: {e}")
            self.con.rollback()
            return False

    def pesquisar_produto(self, termo):
        """Pesquisa produtos por nome"""
        try:
            termo_padrao = padronizar_texto(termo)
            self.cursor.execute(
                'SELECT id_produto, nome_produto, valor_venda, valor_custo FROM produto WHERE nome_produto LIKE %s',
                (f"%{termo_padrao}%",)
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao pesquisar produto: {e}")
            return []


class Venda:
    def __init__(self, cursor, con):
        self.cursor = cursor
        self.con = con
        self.itens_selecionados = []
        self.valor_total = 0

    def obter_produtos(self):
        """Retorna todos os produtos disponíveis"""
        try:
            self.cursor.execute('SELECT id_produto, nome_produto, valor_venda FROM produto')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter produtos: {e}")
            return []

    def obter_estoque(self):
        """Retorna todos os itens do estoque com preco_venda"""
        try:
            self.cursor.execute('''
                SELECT id_item, nome_item, quantidade, preco_venda, custo_unitario 
                FROM estoque 
                WHERE quantidade > 0
            ''')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter estoque: {e}")
            return []

    def adicionar_item_ao_lanche(self, id_item, nome_item, quantidade, preco_unitario):
        """Adiciona um item ao lanche"""
        try:
            from decimal import Decimal
            
            # Converter Decimal para float se necessário
            if isinstance(preco_unitario, Decimal):
                preco_unitario = float(preco_unitario)
            
            quantidade = float(quantidade)
            
            item = {
                'id_item': id_item,
                'nome_item': nome_item,
                'quantidade': quantidade,
                'preco_unitario': preco_unitario,
                'subtotal': quantidade * preco_unitario
            }
            
            self.itens_selecionados.append(item)
            self.atualizar_total()
            return True
        except Exception as e:
            print(f"Erro ao adicionar item ao lanche: {e}")
            return False

    def remover_item_do_lanche(self, indice):
        """Remove um item da lista do lanche"""
        if 0 <= indice < len(self.itens_selecionados):
            self.itens_selecionados.pop(indice)
            self.atualizar_total()
            return True
        return False

    def atualizar_total(self):
        """Calcula o valor total do lanche baseado no preço de venda"""
        self.valor_total = sum(item['subtotal'] for item in self.itens_selecionados)
        return self.valor_total

    def obter_itens_lanche(self):
        """Retorna os itens adicionados ao lanche"""
        return self.itens_selecionados

    def limpar_lanche(self):
        """Limpa todos os itens do lanche"""
        self.itens_selecionados = []
        self.valor_total = 0

    def finalizar_venda(self, forma_pagamento="dinheiro", desconto=0):
        """Finaliza a venda e registra no banco de dados"""
        try:
                if not self.itens_selecionados:
                    return False, "Nenhum item no lanche"

                valor_final = self.valor_total - desconto

                # Calcular lucro total
                custo_total = 0
                for item in self.itens_selecionados:
                    # Buscar custo do item no estoque
                    self.cursor.execute('''
                        SELECT custo_unitario FROM estoque WHERE nome_item = %s
                    ''', (item['nome_item'],))
                    
                    resultado = self.cursor.fetchone()
                    if resultado:
                        valor_custo = float(resultado[0])
                        custo_total += valor_custo * item['quantidade']

                lucro_total = valor_final - custo_total

                # 1️⃣ Inserir venda
                self.cursor.execute('''
                    INSERT INTO vendas (total_venda, lucro_total)
                    VALUES (%s, %s)
                ''', (valor_final, lucro_total))
                self.con.commit()

                id_venda = self.cursor.lastrowid
                print(f"✅ Venda ID {id_venda} criada com sucesso")

                # 2️⃣ Inserir itens da venda
                for item in self.itens_selecionados:
                    print(f"  Inserindo item: {item['nome_item']} - Qtd: {item['quantidade']}")
                    
                    self.cursor.execute('''
                        INSERT INTO itens_venda (id_venda, nome_produto, quantidade, valor_unitario, subtotal)
                        VALUES (%s, %s, %s, %s, %s)
                    ''', (
                        id_venda,
                        item['nome_item'],
                        item['quantidade'],
                        item['preco_unitario'],
                        item['subtotal']
                    ))

                self.con.commit()
                print(f"✅ {len(self.itens_selecionados)} itens inseridos")

                # 3️⃣ Atualizar quantidade do estoque
                for item in self.itens_selecionados:
                    self.cursor.execute('''
                        UPDATE estoque 
                        SET quantidade = quantidade - %s 
                        WHERE nome_item = %s
                    ''', (item['quantidade'], item['nome_item']))

                self.con.commit()
                print(f"✅ Estoque atualizado")

                self.limpar_lanche()
                
                mensagem = f"Venda finalizada! Total: R$ {valor_final:.2f} | Lucro: R$ {lucro_total:.2f}"
                print(f"✅ {mensagem}")
                return True, mensagem

        except Exception as e:
            print(f"❌ Erro ao finalizar venda: {str(e)}")
            import traceback
            traceback.print_exc()
            self.con.rollback()
            return False, f"Erro ao finalizar venda: {e}"
        

    def calcular_lucro(self):
        """Calcula o lucro estimado (preço de venda - custo)"""
        custo_total = 0
        
        # Para cada item, buscar o custo no banco
        for item in self.itens_selecionados:
            self.cursor.execute('''
                SELECT custo_unitario FROM estoque WHERE id_item = %s
            ''', (item['id_item'],))
            resultado = self.cursor.fetchone()
            if resultado:
                custo_unitario = float(resultado[0])
                custo_total += custo_unitario * item['quantidade']
        
        lucro = self.valor_total - custo_total
        percentual = (lucro / self.valor_total * 100) if self.valor_total > 0 else 0
        return lucro, percentual
        
class Composicao:
    def __init__(self, cursor, con):
        self.cursor = cursor
        self.con = con

    def obter_composicoes(self):
        """Retorna todas as composições salvas"""
        try:
            self.cursor.execute('''
                SELECT id_composicao, nome_composicao, preco_total, lucro_estimado, preco_venda, preco_venda_final
                FROM composicao
                ORDER BY data_criacao DESC
            ''')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter composições: {e}")
            return []

    def obter_composicao_detalhes(self, id_composicao):
        """Retorna os detalhes de uma composição específica"""
        try:
            self.cursor.execute('''
                SELECT ci.id_item, e.nome_item, ci.quantidade, ci.preco_unitario
                FROM composicao_itens ci
                JOIN estoque e ON ci.id_item = e.id_item
                WHERE ci.id_composicao = %s
            ''', (id_composicao,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao obter detalhes: {e}")
            return []

    def salvar_composicao(self, nome_composicao, preco_total, lucro_estimado, itens, preco_venda=None, preco_venda_final=None):
        """Salva uma nova composição com seus itens"""
        try:
            self.cursor.execute('''
                INSERT INTO composicao(nome_composicao, preco_total, lucro_estimado, preco_venda, preco_venda_final) 
                VALUES(%s, %s, %s, %s, %s)
            ''', (nome_composicao, preco_total, lucro_estimado, preco_venda, preco_venda_final))
            
            id_composicao = self.cursor.lastrowid

            for item in itens:
                self.cursor.execute('''
                    INSERT INTO composicao_itens(id_composicao, id_item, quantidade, preco_unitario, subtotal)
                    VALUES(%s, %s, %s, %s, %s)
                ''', (id_composicao, item['id_item'], item['quantidade'], item['preco_unitario'], item['subtotal']))

            self.con.commit()
            return True, f"Composição '{nome_composicao}' salva com sucesso!"
        except Exception as e:
            print(f"Erro ao salvar composição: {e}")
            self.con.rollback()
            return False, f"Erro ao salvar: {e}"

    def atualizar_composicao(self, id_composicao, nome_composicao, preco_total, lucro_estimado, preco_venda=None, preco_venda_final=None):
        """Atualiza uma composição existente"""
        try:
            self.cursor.execute('''
                UPDATE composicao 
                SET nome_composicao = %s, preco_total = %s, lucro_estimado = %s, preco_venda = %s, preco_venda_final = %s
                WHERE id_composicao = %s
            ''', (nome_composicao, preco_total, lucro_estimado, preco_venda, preco_venda_final, id_composicao))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao atualizar composição: {e}")
            self.con.rollback()
            return False

    def excluir_composicao(self, id_composicao):
        """Deleta uma composição e seus itens"""
        try:
            self.cursor.execute('DELETE FROM composicao_itens WHERE id_composicao = %s', (id_composicao,))
            self.cursor.execute('DELETE FROM composicao WHERE id_composicao = %s', (id_composicao,))
            self.con.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir composição: {e}")
            self.con.rollback()
            return False

    def pesquisar_composicao(self, termo):
        """Pesquisa composições por nome"""
        try:
            self.cursor.execute('''
                SELECT id_composicao, nome_composicao, preco_total, lucro_estimado, preco_venda, preco_venda_final
                FROM composicao 
                WHERE nome_composicao LIKE %s
                ORDER BY data_criacao DESC
            ''', (f"%{termo}%",))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao pesquisar: {e}")
            return []


# Instâncias globais
estoque = Estoque(cursor, con)
fornecedor = Fornecedor(cursor, con)
categoria = Categoria(cursor, con)
produto = Produto(cursor, con)
venda = Venda(cursor, con)
composicao = Composicao(cursor, con)