import sys
import io

# Configura encoding UTF-8 para o console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from utils.sheets_handler import SheetsHandler

# Configurações
CREDENTIALS_PATH = r"c:\Users\mateu\Desktop\Trabalho-SSP\Tela de Registro\mortes-transito-teste-269b498650f1.json"
SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1QfHHUbFhdLeMX41zEzY5IMCBpLkx9zzCCgsa_mnOasg/edit?usp=sharing"

print("=" * 60)
print("TESTE DE CONEXÃO - GOOGLE SHEETS")
print("=" * 60)
print()

# Cria o handler
print("1. Criando handler...")
handler = SheetsHandler(CREDENTIALS_PATH, SPREADSHEET_URL)
print("   ✅ Handler criado")
print()

# Autentica
print("2. Autenticando com Google...")
sucesso_auth, msg_auth = handler.autenticar()
if sucesso_auth:
    print(f"   ✅ {msg_auth}")
else:
    print(f"   ❌ ERRO: {msg_auth}")
    exit(1)
print()

# Carrega planilha
print("3. Carregando planilha...")
sucesso_load, msg_load = handler.carregar_planilha()
if sucesso_load:
    print(f"   ✅ {msg_load}")
else:
    print(f"   ❌ ERRO: {msg_load}")
    exit(1)
print()

# Mostra informações
print("4. Informações da planilha:")
info = handler.obter_info_planilha()
print(f"   📊 Nome: {info['nome_planilha']}")
print(f"   📈 Total de registros: {info['total_registros']}")
print(f"   🏙️  Municípios únicos: {info['municipios_unicos']}")
if info['ultima_data']:
    print(f"   📅 Última data: {info['ultima_data'].strftime('%d/%m/%Y')}")
print()

print("=" * 60)
print("TESTE CONCLUÍDO COM SUCESSO! ✅")
print("=" * 60)
print()
print("Você pode usar o sistema normalmente agora!")
print("Execute: python main.py")
print()
