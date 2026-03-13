# Pipeline ETL - Fórmula 1

Você tem aqui um pipeline completo que coleta dados públicos de Fórmula 1, organiza tudo direitinho e salva em um banco de dados para análise.

## O que esse projeto faz?

A gente busca dados de uma sessão de Fórmula 1 (qualificação ou treino) e coloca tudo organizado em PostgreSQL. No total você consegue:

- Informações dos pilotos (20 atletas com nome, time e país)
- Tempo de cada volta durante a sessão (116 voltas ao total)
- Telemetria completa (velocidade, aceleração, frenagem) gravada a cada instante (mais de 67 mil registros)

## Como funciona?

Funciona em três etapas bem claras: extração, transformação e carga de dados.

### Etapa 1: Extração (Extract)

"src/extract.py" busca os dados brutos direto da API pública OpenF1 (https://openf1.org/). Básico assim: você roda e a API te devolve JSON com tudo que precisa.

```bash
uv run python ./src/extract.py
```

Isso gera 5 arquivos JSON na pasta "data/raw/":

- drivers.json com os 20 pilotos
- laps_verstappen.json e laps_norris.json com as voltas de cada um (58 voltas cada)
- car_data_verstappen.json e car_data_norris.json com a telemetria (cerca de 33 mil registros em cada)

### Etapa 2: Transformação (Transform)

Aqui a gente usa "src/transform.py" para limpar os dados e converter para um formato mais otimizado chamado Parquet.

```bash
uv run python ./src/transform.py
```

Nessa etapa a gente:

- Remove dados duplicados
- Converte datas e números para o tipo certo
- Limpa registros que estão incompletos
- Salva tudo em Parquet (que é mais rápido que JSON e ocupa menos espaço)

Saem os arquivos Parquet organizados na pasta "data/transformed/".

### Etapa 3: Carga (Load)

"src/load.py" pega aqueles arquivos Parquet e coloca tudo dentro do PostgreSQL em tabelas bem organizadas.

```bash
uv run python ./src/load.py
```

Você fica com 3 tabelas no banco:

- drivers (20 linhas com info dos pilotos)
- laps (116 linhas com tempo de cada volta)
- car_data (67 mil+ linhas com a telemetria)

## Como começar?

### O que você precisa ter instalado

- Python 3.13 ou mais novo
- PostgreSQL 18 ou mais novo
- A ferramenta "uv" para gerenciar pacotes Python

### Passo 1: Entrar na pasta do projeto

```bash
cd /Users/mateus/Desktop/pipeline_formula1
```

### Passo 2: Configurar o arquivo ".env"

Crie um arquivo chamado ".env" na raiz do projeto com suas credenciais do PostgreSQL:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=f1_db
DB_USER=seu_usuario_aqui
DB_PASSWORD=sua_senha_aqui
```

### Passo 3: Criar o banco de dados (só na primeira vez)

```bash
psql -U seu_usuario_aqui -d postgres -c "CREATE DATABASE f1_db;"
```

### Passo 4: Rodar tudo

Execute nessa ordem:

```bash
uv run python ./src/extract.py    # Vai buscar os dados da API
uv run python ./src/transform.py  # Vai limpar e converter
uv run python ./src/load.py       # Vai salvar no banco
```

Pronto. Você tem todos os dados lá.

## Como consultar os dados?

Depois que tudo rodar, você pode conectar no banco e explorar:

```bash
# Conectar no banco
psql -U seu_usuario_aqui -d f1_db

# Ver as tabelas
\dt

# Contar quantos registros você tem
SELECT COUNT(*) FROM laps;
SELECT COUNT(*) FROM car_data;

# Ver os pilotos e quantas voltas cada um fez
SELECT full_name, COUNT(*) as total_voltas FROM drivers d
LEFT JOIN laps l ON d.driver_number = l.driver_number
GROUP BY full_name
ORDER BY total_voltas DESC;

# Ver a telemetria de um piloto no tempo
SELECT date, speed, throttle, brake FROM car_data
WHERE driver_number = 1
ORDER BY date
LIMIT 10;
```

## Automação com Apache Airflow

Se quiser que o pipeline rode automaticamente em um horário específico todo semana, a gente usa o Airflow.

### Primeira vez

```bash
# Inicializar Airflow
bash init_airflow.sh

# Subir tudo com Docker
docker compose up -d

# Acessar a interface
# http://localhost:8080
# Username: airflow
# Password: airflow
```

### O que o Airflow faz

- O pipeline roda automaticamente todo domingo às 10 da manhã (horário UTC)
- As 3 etapas (extração, transformação, carga) rodam na ordem correta
- Se algo falha, tenta de novo automaticamente
- Tem uma interface visual bem legal onde você vê tudo acontecendo
- Se der problema, você recebe notificação

A arquitetura fica assim:

```
EXTRACT_START → EXTRACT_DATA → EXTRACT_END
                                    |
                                    v
              TRANSFORM_START → TRANSFORM_DATA → TRANSFORM_END
                                                      |
                                                      v
                                  LOAD_START → LOAD_DATABASE → LOAD_END
                                                                    |
                                                                    v
                                                      PIPELINE_SUCCESS
```


## Estrutura do projeto

```
pipeline_formula1/
├── README.md                  ← Aqui, o arquivo de instruções
├── pyproject.toml            ← Lista de dependências
├── .env                       ← Seus dados de acesso ao banco (não compartilhe!)
├── .airflowignore            ← Configuração do Airflow
├── init_airflow.sh           ← Script que inicializa o Airflow
├── docker-compose.yaml       ← Container do Airflow
├── src/
│   ├── extract.py           ← Código que busca dados da API
│   ├── transform.py         ← Código que limpa os dados
│   └── load.py              ← Código que salva no banco
├── dags/
│   ├── f1_etl_pipeline.py   ← Orquestração Airflow
├── data/
│   ├── raw/                 ← JSONs que vêm da API
│   └── transformed/         ← Parquet limpos
```

## Dependências

Como instalar tudo em um comando:

```bash
uv sync
```

Se quiser ver exatamente o que vai instalar, aqui estão os principais:

- pandas (manipulação de dados)
- requests (fazer requisições HTTP)
- sqlalchemy (conectar com o banco de dados)
- psycopg2-binary (driver específico para PostgreSQL)
- python-dotenv (carregar variáveis de ambiente)
- pyarrow (trabalhar com arquivos Parquet)

## Mudanças e customizações

### Trabalhar com outro evento/sessão

Se quiser dados de um outro fim de semana de F1, é só mudar um número no arquivo "src/extract.py":

```python
SESSION_KEY = 9839  # Muda aqui para o ID da sessão que quer
```

### Adicionar mais pilotos

No mesmo arquivo, tem um dicionário assim:

```python
DRIVERS = {
    1: "verstappen",
    4: "norris",
    81: "bottas"       # Só adiciona aqui
}
```

### Limpar dados e reexecutar

A primeira vez que você roda, cria as tabelas. Nas próximas vezes, adiciona mais dados (pode ficar duplicado). Se quiser limpar:

```bash
psql -U seu_usuario_aqui -d f1_db -c "TRUNCATE TABLE drivers, laps, car_data CASCADE;"
```
