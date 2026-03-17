set -e  # Parar se algum comando falhar

echo "🚀 Inicializando Airflow para Pipeline F1..."
echo ""

# ============================================================================
# 1. Definir variáveis de projeto
# ============================================================================

PROJECT_HOME="/Users/mateus/Desktop/pipeline_formula1"
PYTHON_BIN="$PROJECT_HOME/.venv/bin/python"
AIRFLOW_HOME="${AIRFLOW_HOME:-.}"

echo "📁 Variáveis de Projeto:"
echo "   PROJECT_HOME: $PROJECT_HOME"
echo "   PYTHON_BIN: $PYTHON_BIN"
echo "   AIRFLOW_HOME: $AIRFLOW_HOME"
echo ""

# ============================================================================
# 2. Criar variáveis de ambiente no Airflow
# ============================================================================

echo "⚙️ Configurando variáveis de ambiente do Airflow..."

# Check if airflow command exists
if ! command -v airflow &> /dev/null; then
    echo "❌ Airflow não está instalado. Instale com:"
    echo "   pip install apache-airflow"
    exit 1
fi

# Criar/atualizar variáveis
airflow variables set PROJECT_HOME "$PROJECT_HOME" 2>/dev/null || echo "   Variável PROJECT_HOME já existe"
airflow variables set PYTHON_BIN "$PYTHON_BIN" 2>/dev/null || echo "   Variável PYTHON_BIN já existe"

echo "   ✅ Variáveis criadas/atualizadas"
echo ""

# ============================================================================
# 3. Inicializar banco de dados do Airflow
# ============================================================================

echo "🗄️  Inicializando banco de dados do Airflow..."
airflow db migrate
echo "   ✅ Banco de dados inicializado"
echo ""

# ============================================================================
# 4. Criar usuário padrão (se não existir)
# ============================================================================

echo "👤 Criando usuário padrão..."

# Verificar se usuário 'airflow' já existe
if airflow users list | grep -q "airflow"; then
    echo "   ⚠️  Usuário 'airflow' já existe"
else
    airflow users create \
        --username airflow \
        --firstname Airflow \
        --lastname Admin \
        --role Admin \
        --email airflow@example.com \
        --password airflow
    echo "   ✅ Usuário criado (username: airflow, password: airflow)"
fi
echo ""

# ============================================================================
# 5. Verificar DAG
# ============================================================================

echo "📋 Verificando DAG..."
echo "   DAGs disponíveis:"
airflow dags list | grep f1_etl || echo "   ⚠️  DAG f1_etl_pipeline não encontrado"
echo ""

# ============================================================================
# 6. SUCESSO!
# ============================================================================

echo "✅ Airflow inicializado com sucesso!"
echo ""
echo "🎯 Próximos passos:"
echo ""
echo "1. Iniciar Airflow (choose um):"
echo "   a) Docker (recomendado):"
echo "      docker compose up -d"
echo ""
echo "   b) Standalone local:"
echo "      airflow standalone"
echo ""
echo "2. Acessar Airflow UI:"
echo "   http://localhost:8080"
echo ""
echo "3. Logar com:"
echo "   Username: airflow"
echo "   Password: airflow"
echo ""
echo "4. Ativar DAG 'f1_etl_pipeline' (toggle on/off)"
echo ""
