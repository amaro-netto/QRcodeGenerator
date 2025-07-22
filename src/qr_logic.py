# src/qr_logic.py

import qrcode
import datetime
import os
import re
from PIL import Image, ImageTk
from src.config import IMAGES_DIR # Importa IMAGES_DIR de config

def sanitize_filename(filename):
    """Remove caracteres inválidos para nomes de arquivo."""
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    cleaned_filename = re.sub(invalid_chars, '', filename)
    cleaned_filename = cleaned_filename.strip().replace(' ', '_')
    return cleaned_filename

def gerar_qr_code_e_salvar(texto, nome_arquivo_base="qr_code", cor_frente="black", cor_fundo="white", nivel_erro="L", caminho_personalizado=None, caminho_logo=None):
    """
    Gera um QR Code a partir de um texto, o salva como imagem e retorna o caminho.
    Permite personalizar cores, nível de correção de erro e adicionar um logo.
    """
    error_correction_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }
    error_level = error_correction_map.get(nivel_erro, qrcode.constants.ERROR_CORRECT_L)

    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=error_level,
            box_size=10,
            border=4,
        )
        qr.add_data(texto)
        qr.make(fit=True)

        img_qr = qr.make_image(fill_color=cor_frente, back_color=cor_fundo).convert("RGBA")

        if caminho_logo and os.path.exists(caminho_logo):
            try:
                logo = Image.open(caminho_logo).convert("RGBA")
                qr_width, qr_height = img_qr.size
                logo_size = int(qr_width * 0.25)

                logo.thumbnail((logo_size, logo_size), Image.LANCZOS)

                logo_width, logo_height = logo.size
                pos_x = (qr_width - logo_width) // 2
                pos_y = (qr_height - logo_height) // 2

                img_qr.paste(logo, (pos_x, pos_y), logo)

            except Exception as e:
                print(f"Aviso: Não foi possível aplicar o logo. Erro: {e}")
        
        # Salvar a imagem final
        if caminho_personalizado:
            final_path = caminho_personalizado
        else:
            # Usa o diretório de imagens de config.py
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo_completo = f"{sanitize_filename(nome_arquivo_base)}_{timestamp}.png"
            final_path = os.path.join(IMAGES_DIR, nome_arquivo_completo)

        img_qr.save(final_path)
        return final_path
    except Exception as e:
        print(f"Erro ao gerar QR Code: {e}")
        return None

# A função get_qr_image_for_display não é mais necessária aqui, pois a lógica de exibição está em qr_app.py