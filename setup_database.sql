-- =====================================================
-- Script de criacao do banco de dados MySQL
-- Sistema de Cadastro de Mortes no Transito
-- =====================================================

CREATE DATABASE IF NOT EXISTS mortes_transito
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE mortes_transito;

-- =====================================================
-- Tabelas de Lookup
-- =====================================================

CREATE TABLE IF NOT EXISTS tipos_acidente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tipos_veiculo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS municipios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL UNIQUE
);

-- =====================================================
-- Tabelas Principais
-- =====================================================

CREATE TABLE IF NOT EXISTS ocorrencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_fato DATE,
    hora_fato TIME,
    dia_semana VARCHAR(20),
    mes_referencia VARCHAR(20),
    id_municipio INT,
    logradouro VARCHAR(500),
    subtipo_local VARCHAR(100),
    id_tipo_acidente INT,
    latitude DECIMAL(10, 7),
    longitude DECIMAL(10, 7),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_municipio) REFERENCES municipios(id),
    FOREIGN KEY (id_tipo_acidente) REFERENCES tipos_acidente(id)
);

CREATE TABLE IF NOT EXISTS vitimas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_ocorrencia INT NOT NULL,
    nome VARCHAR(200),
    sexo VARCHAR(20),
    data_nascimento DATE,
    idade INT,
    cpf VARCHAR(14),
    filiacao VARCHAR(200),
    possui_cnh VARCHAR(10),
    e_condutor BOOLEAN,
    exame_alcoolemia VARCHAR(10),
    uso_capacete VARCHAR(10),
    id_veiculo_vitima INT,
    id_veiculo_envolvido INT,
    data_obito DATE,
    local_morte VARCHAR(100),
    num_laudo_iml VARCHAR(100),
    natureza_laudo VARCHAR(200),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_ocorrencia) REFERENCES ocorrencias(id),
    FOREIGN KEY (id_veiculo_vitima) REFERENCES tipos_veiculo(id),
    FOREIGN KEY (id_veiculo_envolvido) REFERENCES tipos_veiculo(id)
);

-- =====================================================
-- Dados iniciais - Tipos de Acidente
-- =====================================================

INSERT INTO tipos_acidente (descricao) VALUES
    ('Atropelamento'),
    ('Atropelamento com Animais'),
    ('Capotamento'),
    ('Choque'),
    ('Colisão'),
    ('Colisão/Animal'),
    ('Queda'),
    ('Tombamento'),
    ('NI'),
    ('Outro');

-- =====================================================
-- Dados iniciais - Tipos de Veiculo
-- =====================================================

INSERT INTO tipos_veiculo (descricao) VALUES
    ('Motocicleta'),
    ('Carro/Automóvel'),
    ('Pedestre'),
    ('Bicicleta'),
    ('Caminhão'),
    ('Ônibus'),
    ('Carroça'),
    ('Van'),
    ('Trator'),
    ('Animal/Cavalo'),
    ('Animal/Gado'),
    ('Animal/Cachorro'),
    ('Choque/Poste'),
    ('Choque/Árvore'),
    ('Choque/Muro'),
    ('Colisão/Ponte'),
    ('NI'),
    ('Outro');

-- =====================================================
-- Dados iniciais - Municipios (exemplos)
-- Adicione os municipios do seu estado/regiao
-- =====================================================

INSERT INTO municipios (nome) VALUES
    ('Teresina'),
    ('Parnaíba'),
    ('Picos'),
    ('Piripiri'),
    ('Floriano'),
    ('Campo Maior'),
    ('Barras'),
    ('União'),
    ('Altos'),
    ('José de Freitas'),
    ('Pedro II'),
    ('Oeiras'),
    ('Esperantina'),
    ('Luzilândia'),
    ('Batalha'),
    ('Corrente'),
    ('São Raimundo Nonato'),
    ('Bom Jesus'),
    ('Uruçuí'),
    ('Valença do Piauí');

-- =====================================================
-- Verificacao
-- =====================================================

SELECT 'Tipos de Acidente' AS tabela, COUNT(*) AS registros FROM tipos_acidente
UNION ALL
SELECT 'Tipos de Veiculo', COUNT(*) FROM tipos_veiculo
UNION ALL
SELECT 'Municipios', COUNT(*) FROM municipios;
