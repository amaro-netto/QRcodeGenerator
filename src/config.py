# src/config.py

import os

# Caminho base do projeto (um nível acima de 'src')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Diretórios para dados
DATA_DIR = os.path.join(BASE_DIR, 'data')
DB_DIR = os.path.join(DATA_DIR, 'db')
DB_NAME = os.path.join(DB_DIR, 'historico_qr_codes.db')

# Diretórios para imagens
IMAGES_DIR = os.path.join(BASE_DIR, 'images')

# Diretório para arquivos temporários (clipboard)
TEMP_CLIPBOARD_DIR = os.path.join(BASE_DIR, 'temp_clipboard')

# Certifique-se de que os diretórios existam
os.makedirs(DB_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(TEMP_CLIPBOARD_DIR, exist_ok=True)