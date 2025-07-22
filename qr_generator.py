import qrcode
import sqlite3
import datetime
import os

def criar_tabela():
    """Cria a tabela de historico_qr_codes se ela não existir."""
    conn = sqlite3.connect('historico_qr_codes.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_qr_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto_qr TEXT NOT NULL,
            nome_arquivo TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def gerar_qr_code(texto, nome_arquivo="qr_code"):
    """
    Gera um QR Code a partir de um texto e o salva como imagem.
    Retorna o caminho completo do arquivo gerado.
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(texto)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Garante que o diretório 'qr_codes' exista
        if not os.path.exists('qr_codes'):
            os.makedirs('qr_codes')

        caminho_arquivo = os.path.join('qr_codes', f"{nome_arquivo}.png")
        img.save(caminho_arquivo)
        print(f"QR Code salvo como: {caminho_arquivo}")
        return caminho_arquivo
    except Exception as e:
        print(f"Erro ao gerar QR Code: {e}")
        return None

def registrar_historico(texto_qr, nome_arquivo):
    """Registra a geração do QR Code no banco de dados."""
    conn = sqlite3.connect('historico_qr_codes.db')
    cursor = conn.cursor()
    data_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico_qr_codes (texto_qr, nome_arquivo, data_criacao) VALUES (?, ?, ?)",
                   (texto_qr, nome_arquivo, data_hora_atual))
    conn.commit()
    conn.close()
    print("Registro adicionado ao histórico.")

def visualizar_historico():
    """Exibe todos os QR Codes gerados e seus detalhes do histórico."""
    conn = sqlite3.connect('historico_qr_codes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, texto_qr, nome_arquivo, data_criacao FROM historico_qr_codes ORDER BY data_criacao DESC")
    registros = cursor.fetchall()
    conn.close()

    if not registros:
        print("\nO histórico de QR Codes está vazio.")
        return

    print("\n--- Histórico de QR Codes ---")
    for registro in registros:
        print(f"ID: {registro[0]}")
        print(f"Texto: {registro[1]}")
        print(f"Arquivo: {registro[2]}")
        print(f"Data de Criação: {registro[3]}")
        print("---------------------------")

def main():
    criar_tabela()

    while True:
        print("\n--- Gerador de QR Code ---")
        print("1. Gerar novo QR Code")
        print("2. Visualizar histórico")
        print("3. Sair")

        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            texto_input = input("Digite o texto ou URL para o QR Code: ")
            nome_arq_input = input("Digite um nome para o arquivo (ex: meu_site, meu_cartao - sem extensão): ")
            caminho_gerado = gerar_qr_code(texto_input, nome_arq_input)
            if caminho_gerado:
                # O caminho gerado já inclui o nome do diretório e a extensão .png
                # Então, para o registro, queremos apenas o nome do arquivo final
                nome_arquivo_final = os.path.basename(caminho_gerado)
                registrar_historico(texto_input, nome_arquivo_final)
        elif escolha == '2':
            visualizar_historico()
        elif escolha == '3':
            print("Saindo do programa.")
            break
        else:
            print("Opção inválida. Por favor, tente novamente.")

if __name__ == "__main__":
    main()