create database gestor_x;

-- =========================
-- TABELA: produto
-- =========================
CREATE TABLE produto (
    id_produto INT AUTO_INCREMENT PRIMARY KEY,
    nome_produto VARCHAR(150) NOT NULL,
    valor_venda DECIMAL(10,2) NOT NULL,
    valor_custo DECIMAL(10,2) NOT NULL
);
-- Tabela categorias
CREATE TABLE categorias (
    id_categoria INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL
);

-- Tabela estoque
CREATE TABLE estoque (
    id_item INT AUTO_INCREMENT PRIMARY KEY,
    nome_item VARCHAR(100) NOT NULL,
    custo_unitario DECIMAL(10,2),
    preco_venda DECIMAL(10,2),
    quantidade INT,
    validade DATE,
    id_categoria INT,
    FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
);

-- Tabela itens (ingredientes base)
CREATE TABLE itens (
    id_itens INT AUTO_INCREMENT PRIMARY KEY,
    nome_itens VARCHAR(100),
    nome_ingrediente VARCHAR(100)
);

-- Tabela composição
CREATE TABLE composicao (
    id_composicao INT AUTO_INCREMENT PRIMARY KEY,
    nome_composicao VARCHAR(100),
    descricao TEXT,
    preco_total DECIMAL(10,2),
    lucro_estimado DECIMAL(10,2),
    data_criacao DATE,
    preco_venda DECIMAL(10,2),
    preco_venda_final DECIMAL(10,2)
);

-- Tabela composicao_itens
CREATE TABLE composicao_itens (
    id_item_comp INT AUTO_INCREMENT PRIMARY KEY,
    id_composicao INT,
    id_item INT,
    quantidade INT,
    preco_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    FOREIGN KEY (id_composicao) REFERENCES composicao(id_composicao),
    FOREIGN KEY (id_item) REFERENCES estoque(id_item)
);

-- Tabela vendas
CREATE TABLE vendas (
    id_venda INT AUTO_INCREMENT PRIMARY KEY,
    data_venda DATE,
    total_venda DECIMAL(10,2),
    lucro_total DECIMAL(10,2)
);

-- Tabela itens_venda
CREATE TABLE itens_venda (
    id_item_venda INT AUTO_INCREMENT PRIMARY KEY,
    id_venda INT,
    id_produto INT,
    nome_produto VARCHAR(100),
    quantidade INT,
    valor_unitario DECIMAL(10,2),
    subtotal DECIMAL(10,2),
    FOREIGN KEY (id_venda) REFERENCES vendas(id_venda)
);

-- Tabela usuario
CREATE TABLE usuario (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    telefone VARCHAR(20),
    email VARCHAR(100),
    senha VARCHAR(255)
);

-- Tabela fornecedor
CREATE TABLE fornecedor (
    id_fornecedor INT AUTO_INCREMENT PRIMARY KEY,
    nome_fornecedor VARCHAR(100),
    cpf_cnpj VARCHAR(20),
    telefone VARCHAR(20),
    email VARCHAR(100),
    cep VARCHAR(10),
    cidade VARCHAR(100),
    num_local VARCHAR(20),
    estado VARCHAR(50)
);