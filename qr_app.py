import qrcode
import sqlite3
import datetime
import os
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk # Importar Image e ImageTk do Pillow

# --- Funções do Gerador de QR Code e Banco de Dados (adaptadas) ---

DB_NAME = 'historico_qr_codes.db'
QR_DIR = 'qr_codes'

def criar_tabela():
    """Cria a tabela de historico_qr_codes se ela não existir."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historico_qr_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            texto_qr TEXT NOT NULL,
            nome_arquivo TEXT NOT NULL,
            caminho_completo TEXT NOT NULL,
            data_criacao TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def gerar_qr_code_e_salvar(texto, nome_arquivo_base="qr_code"):
    """
    Gera um QR Code a partir de um texto, o salva como imagem e retorna o caminho.
    """
    if not os.path.exists(QR_DIR):
        os.makedirs(QR_DIR)

    # Adiciona um timestamp ao nome do arquivo para evitar sobrescrever
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo_completo = f"{nome_arquivo_base}_{timestamp}.png"
    caminho_completo = os.path.join(QR_DIR, nome_arquivo_completo)

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
        img.save(caminho_completo)
        return caminho_completo
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar QR Code: {e}")
        return None

def registrar_historico(texto_qr, nome_arquivo, caminho_completo):
    """Registra a geração do QR Code no banco de dados."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico_qr_codes (texto_qr, nome_arquivo, caminho_completo, data_criacao) VALUES (?, ?, ?, ?)",
                   (texto_qr, nome_arquivo, caminho_completo, data_hora_atual))
    conn.commit()
    conn.close()

def buscar_historico():
    """Retorna todos os registros do histórico."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, texto_qr, nome_arquivo, caminho_completo, data_criacao FROM historico_qr_codes ORDER BY data_criacao DESC")
    registros = cursor.fetchall()
    conn.close()
    return registros

# --- Funções da Interface Gráfica ---

class QRGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Gerador de QR Code")
        master.geometry("800x600") # Tamanho inicial da janela

        # Garante que a tabela do BD e o diretório de QRs existam
        criar_tabela()
        if not os.path.exists(QR_DIR):
            os.makedirs(QR_DIR)

        # Frame principal para organizar o layout
        self.main_frame = tk.Frame(master, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Seção de Geração de QR Code ---
        self.generation_frame = tk.LabelFrame(self.main_frame, text="Gerar Novo QR Code", padx=10, pady=10)
        self.generation_frame.pack(pady=10, fill=tk.X)

        tk.Label(self.generation_frame, text="Texto/URL:").grid(row=0, column=0, sticky="w", pady=5)
        self.text_input = tk.Entry(self.generation_frame, width=50)
        self.text_input.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.generation_frame, text="Nome do Arquivo:").grid(row=1, column=0, sticky="w", pady=5)
        self.filename_input = tk.Entry(self.generation_frame, width=50)
        self.filename_input.grid(row=1, column=1, padx=5, pady=5)
        self.filename_input.insert(0, "meu_qr_code") # Valor padrão

        self.generate_button = tk.Button(self.generation_frame, text="Gerar QR Code", command=self.handle_generate_qr)
        self.generate_button.grid(row=2, column=0, columnspan=2, pady=10)

        # Área para exibir o QR Code
        self.qr_label = tk.Label(self.generation_frame)
        self.qr_label.grid(row=3, column=0, columnspan=2, pady=10)

        # --- Seção de Histórico ---
        self.history_frame = tk.LabelFrame(self.main_frame, text="Histórico de QR Codes", padx=10, pady=10)
        self.history_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.history_listbox = tk.Listbox(self.history_frame, height=10)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self.display_selected_qr)

        self.scrollbar = tk.Scrollbar(self.history_frame, orient="vertical", command=self.history_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=self.scrollbar.set)

        self.refresh_history_button = tk.Button(self.history_frame, text="Atualizar Histórico", command=self.populate_history)
        self.refresh_history_button.pack(pady=5)

        # Inicializa o histórico ao iniciar o aplicativo
        self.populate_history()

    def handle_generate_qr(self):
        """Lida com a ação de gerar um QR Code."""
        texto = self.text_input.get()
        nome_arquivo_base = self.filename_input.get()

        if not texto:
            messagebox.showwarning("Atenção", "Por favor, digite o texto ou URL para gerar o QR Code.")
            return

        if not nome_arquivo_base:
            nome_arquivo_base = "qr_code" # Garante um nome base

        caminho_qr_gerado = gerar_qr_code_e_salvar(texto, nome_arquivo_base)

        if caminho_qr_gerado:
            nome_arquivo_final = os.path.basename(caminho_qr_gerado)
            registrar_historico(texto, nome_arquivo_final, caminho_qr_gerado)
            self.display_qr_image(caminho_qr_gerado)
            self.populate_history() # Atualiza o histórico na lista
            messagebox.showinfo("Sucesso", f"QR Code gerado e salvo como:\n{caminho_qr_gerado}")

    def display_qr_image(self, image_path):
        """Exibe a imagem do QR Code na interface."""
        try:
            img = Image.open(image_path)
            # Redimensiona a imagem para caber na interface, se necessário
            img.thumbnail((200, 200), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.qr_label.config(image=photo)
            self.qr_label.image = photo # Manter uma referência para evitar que a imagem seja coletada pelo garbage collector
        except FileNotFoundError:
            self.qr_label.config(image='') # Limpa a imagem se o arquivo não for encontrado
            messagebox.showerror("Erro", f"Arquivo não encontrado: {image_path}")
        except Exception as e:
            self.qr_label.config(image='') # Limpa a imagem em caso de erro
            messagebox.showerror("Erro", f"Erro ao carregar imagem: {e}")

    def populate_history(self):
        """Preenche a Listbox com os itens do histórico."""
        self.history_listbox.delete(0, tk.END) # Limpa a lista atual
        registros = buscar_historico()
        if not registros:
            self.history_listbox.insert(tk.END, "Nenhum QR Code gerado ainda.")
        else:
            for registro in registros:
                # Exibe uma string formatada na listbox
                self.history_listbox.insert(tk.END, f"ID: {registro[0]} | Texto: {registro[1][:30]}... | Criado em: {registro[4]}")
            self.history_data = registros # Guarda os dados completos para fácil acesso

    def display_selected_qr(self, event):
        """Exibe o QR Code selecionado na Listbox."""
        selected_indices = self.history_listbox.curselection()
        if not selected_indices:
            return

        index = selected_indices[0]
        # Pega os dados completos do registro usando o índice
        selected_record = self.history_data[index]
        caminho_completo = selected_record[3] # O 4º item (índice 3) é o caminho_completo

        self.display_qr_image(caminho_completo)
        # Opcional: preencher campos de texto com os dados do item selecionado
        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, selected_record[1]) # Texto do QR
        self.filename_input.delete(0, tk.END)
        # Extrai o nome do arquivo sem o timestamp e extensão para exibir no campo
        original_filename = selected_record[2].rsplit('_', 2)[0] if '_' in selected_record[2] else selected_record[2].replace(".png", "")
        self.filename_input.insert(0, original_filename)


# --- Execução da Aplicação ---
if __name__ == "__main__":
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()