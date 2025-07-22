# src/config.py

import os

# Caminho base do projeto (um nível acima de 'src')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diretórios para dados gerais (na raiz do projeto)
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Diretório do Banco de Dados (dentro de 'data')
DB_DIR = os.path.join(DATA_DIR, 'db')
DB_NAME = os.path.join(DB_DIR, 'historico_qr_codes.db')

# NOVO CAMINHO PARA SALVAR AS IMAGENS DO QR CODE (diretamente em 'data/images/')
# Ex: A:\Amaro Netto\AMARO BACKUP\Projetos\QRcodeGenerator\data\images\
QR_SAVE_DIR = os.path.join(DATA_DIR, 'images') 

# Diretório para ícones (dentro de 'data')
# Ex: A:\Amaro Netto\AMARO BACKUP\Projetos\QRcodeGenerator\data\icons\
ICONS_DIR = os.path.join(DATA_DIR, 'icons')
# Caminho completo para o arquivo do ícone da janela
ICON_PATH = os.path.join(ICONS_DIR, 'logo.png') # Espera um PNG. Se for ICO, mude para 'logo.ico'

# Diretório para arquivos temporários para clipboard (na raiz do projeto)
# Ex: A:\Amaro Netto\AMARO BACKUP\Projetos\QRcodeGenerator\temp_clipboard\
TEMP_CLIPBOARD_DIR = os.path.join(BASE_DIR, 'temp_clipboard')

# Garante que todos os diretórios necessários existam
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(QR_SAVE_DIR, exist_ok=True) # Garante que data/images seja criada
os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(TEMP_CLIPBOARD_DIR, exist_ok=True)