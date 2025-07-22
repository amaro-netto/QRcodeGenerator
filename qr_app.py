import qrcode
import sqlite3
import datetime
import os
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser, ttk
from PIL import Image, ImageTk

# --- Funções do Gerador de QR Code e Banco de Dados ---

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
            data_criacao TEXT NOT NULL,
            cor_frente TEXT,      -- Nova coluna para cor da frente
            cor_fundo TEXT,       -- Nova coluna para cor de fundo
            nivel_erro TEXT       -- Nova coluna para nível de erro
        )
    ''')
    conn.commit()
    conn.close()

def migrar_tabela():
    """Adiciona colunas para cor e nível de erro se não existirem."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE historico_qr_codes ADD COLUMN cor_frente TEXT")
        conn.commit()
        print("Coluna 'cor_frente' adicionada com sucesso.")
    except sqlite3.OperationalError as e:
        if "duplicate column name: cor_frente" not in str(e): print(f"Erro ao adicionar coluna cor_frente: {e}")

    try:
        cursor.execute("ALTER TABLE historico_qr_codes ADD COLUMN cor_fundo TEXT")
        conn.commit()
        print("Coluna 'cor_fundo' adicionada com sucesso.")
    except sqlite3.OperationalError as e:
        if "duplicate column name: cor_fundo" not in str(e): print(f"Erro ao adicionar coluna cor_fundo: {e}")

    try:
        cursor.execute("ALTER TABLE historico_qr_codes ADD COLUMN nivel_erro TEXT")
        conn.commit()
        print("Coluna 'nivel_erro' adicionada com sucesso.")
    except sqlite3.OperationalError as e:
        if "duplicate column name: nivel_erro" not in str(e): print(f"Erro ao adicionar coluna nivel_erro: {e}")
    finally:
        conn.close()


def gerar_qr_code_e_salvar(texto, nome_arquivo_base="qr_code", cor_frente="black", cor_fundo="white", nivel_erro="L"):
    """
    Gera um QR Code a partir de um texto, o salva como imagem e retorna o caminho.
    Permite personalizar cores e nível de correção de erro.
    """
    if not os.path.exists(QR_DIR):
        os.makedirs(QR_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo_completo = f"{nome_arquivo_base}_{timestamp}.png"
    caminho_completo = os.path.join(QR_DIR, nome_arquivo_completo)

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

        img = qr.make_image(fill_color=cor_frente, back_color=cor_fundo)
        img.save(caminho_completo)
        return caminho_completo
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao gerar QR Code: {e}")
        return None

def registrar_historico(texto_qr, nome_arquivo, caminho_completo, cor_frente, cor_fundo, nivel_erro):
    """Registra a geração do QR Code no banco de dados, incluindo cores e nível de erro."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    data_hora_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO historico_qr_codes (texto_qr, nome_arquivo, caminho_completo, data_criacao, cor_frente, cor_fundo, nivel_erro) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (texto_qr, nome_arquivo, caminho_completo, data_hora_atual, cor_frente, cor_fundo, nivel_erro))
    conn.commit()
    conn.close()

def buscar_historico():
    """Retorna todos os registros do histórico, incluindo novas colunas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, texto_qr, nome_arquivo, caminho_completo, data_criacao, cor_frente, cor_fundo, nivel_erro FROM historico_qr_codes ORDER BY data_criacao DESC")
    registros = cursor.fetchall()
    conn.close()
    return registros

def deletar_registro_historico(registro_id):
    """Deleta um registro do histórico pelo ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM historico_qr_codes WHERE id = ?", (registro_id,))
    conn.commit()
    conn.close()

# --- Funções da Interface Gráfica ---

class QRGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Gerador de QR Code")
        master.geometry("800x700") # Ajustei a altura, pode ser que precise de mais ou menos

        criar_tabela()
        migrar_tabela()
        if not os.path.exists(QR_DIR):
            os.makedirs(QR_DIR)

        self.front_color_hex = tk.StringVar(value="black")
        self.back_color_hex = tk.StringVar(value="white")
        self.error_level_var = tk.StringVar(value="L")

        self.main_frame = tk.Frame(master, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Seção de Geração de QR Code ---
        # Usaremos um sub-frame para os controles de input e personalização à esquerda
        # E o qr_label à direita, dentro do generation_frame.
        self.generation_frame = tk.LabelFrame(self.main_frame, text="Gerar Novo QR Code", padx=10, pady=10)
        self.generation_frame.pack(pady=10, fill=tk.BOTH, expand=True) # expand=True para preencher o espaço

        # Sub-frame para Inputs e Opções (Coluna Esquerda)
        self.input_options_frame = tk.Frame(self.generation_frame, padx=5, pady=5)
        self.input_options_frame.grid(row=0, column=0, sticky="nsew") # sticky="nsew" para expandir

        tk.Label(self.input_options_frame, text="Texto/URL:").grid(row=0, column=0, sticky="w", pady=5)
        self.text_input = tk.Entry(self.input_options_frame, width=40) # Largura ajustada
        self.text_input.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.input_options_frame, text="Nome do Arquivo:").grid(row=1, column=0, sticky="w", pady=5)
        self.filename_input = tk.Entry(self.input_options_frame, width=40) # Largura ajustada
        self.filename_input.grid(row=1, column=1, padx=5, pady=5)
        self.filename_input.insert(0, "meu_qr_code")

        # --- Opções de Personalização ---
        self.options_frame = tk.LabelFrame(self.input_options_frame, text="Opções de Personalização", padx=10, pady=5)
        self.options_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10) # sticky "ew" para expandir horizontalmente

        tk.Label(self.options_frame, text="Cor do QR Code:").grid(row=0, column=0, sticky="w", pady=2)
        self.front_color_button = tk.Button(self.options_frame, text="Escolher Cor", command=self.choose_front_color)
        self.front_color_button.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.front_color_preview = tk.Label(self.options_frame, textvariable=self.front_color_hex, width=10, relief="solid")
        self.front_color_preview.grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.front_color_preview.config(bg=self.front_color_hex.get())

        tk.Label(self.options_frame, text="Cor de Fundo:").grid(row=1, column=0, sticky="w", pady=2)
        self.back_color_button = tk.Button(self.options_frame, text="Escolher Cor", command=self.choose_back_color)
        self.back_color_button.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.back_color_preview = tk.Label(self.options_frame, textvariable=self.back_color_hex, width=10, relief="solid")
        self.back_color_preview.grid(row=1, column=2, sticky="w", padx=5, pady=2)
        self.back_color_preview.config(bg=self.back_color_hex.get())

        tk.Label(self.options_frame, text="Nível de Erro:").grid(row=2, column=0, sticky="w", pady=2)
        self.error_level_combobox = ttk.Combobox(self.options_frame, textvariable=self.error_level_var,
                                                 values=["L (Baixo)", "M (Médio)", "Q (Quartil)", "H (Alto)"], state="readonly")
        self.error_level_combobox.grid(row=2, column=1, columnspan=2, sticky="ew", padx=5, pady=2)
        self.error_level_combobox.set("L (Baixo)")

        self.generate_button = tk.Button(self.input_options_frame, text="Gerar QR Code", command=self.handle_generate_qr)
        self.generate_button.grid(row=3, column=0, columnspan=2, pady=10) # Posicionado no input_options_frame

        # Área para exibir o QR Code (Coluna Direita)
        self.qr_label = tk.Label(self.generation_frame)
        # Ocupa a coluna 1 e expande (sticky "nsew")
        self.qr_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Configura as colunas do generation_frame para expandir
        self.generation_frame.grid_columnconfigure(0, weight=1) # Coluna da esquerda (inputs)
        self.generation_frame.grid_columnconfigure(1, weight=1) # Coluna da direita (QR Code)
        self.generation_frame.grid_rowconfigure(0, weight=1) # A única linha que contém tudo

        # --- Seção de Histórico ---
        self.history_frame = tk.LabelFrame(self.main_frame, text="Histórico de QR Codes", padx=10, pady=10)
        self.history_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.history_listbox = tk.Listbox(self.history_frame, height=10)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_listbox.bind("<<ListboxSelect>>", self.display_selected_qr)

        self.scrollbar = tk.Scrollbar(self.history_frame, orient="vertical", command=self.history_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=self.scrollbar.set)

        self.history_buttons_frame = tk.Frame(self.history_frame)
        self.history_buttons_frame.pack(pady=5)

        self.refresh_history_button = tk.Button(self.history_buttons_frame, text="Atualizar Histórico", command=self.populate_history)
        self.refresh_history_button.pack(side=tk.LEFT, padx=5)

        self.delete_history_button = tk.Button(self.history_buttons_frame, text="Excluir Selecionado", command=self.handle_delete_qr)
        self.delete_history_button.pack(side=tk.LEFT, padx=5)

        self.populate_history()

    def choose_front_color(self):
        color_code = colorchooser.askcolor(title="Escolha a Cor do QR Code", initialcolor=self.front_color_hex.get())
        if color_code[1]:
            self.front_color_hex.set(color_code[1])
            self.front_color_preview.config(bg=color_code[1])

    def choose_back_color(self):
        color_code = colorchooser.askcolor(title="Escolha a Cor de Fundo", initialcolor=self.back_color_hex.get())
        if color_code[1]:
            self.back_color_hex.set(color_code[1])
            self.back_color_preview.config(bg=color_code[1])

    def handle_generate_qr(self):
        """Lida com a ação de gerar um QR Code, incluindo personalização."""
        texto = self.text_input.get()
        nome_arquivo_base = self.filename_input.get()
        cor_frente = self.front_color_hex.get()
        cor_fundo = self.back_color_hex.get()
        nivel_erro_display = self.error_level_var.get()
        nivel_erro_sigla = nivel_erro_display[0]

        if not texto:
            messagebox.showwarning("Atenção", "Por favor, digite o texto ou URL para gerar o QR Code.")
            return

        if not nome_arquivo_base:
            nome_arquivo_base = "qr_code"

        caminho_qr_gerado = gerar_qr_code_e_salvar(texto, nome_arquivo_base, cor_frente, cor_fundo, nivel_erro_sigla)

        if caminho_qr_gerado:
            nome_arquivo_final = os.path.basename(caminho_qr_gerado)
            registrar_historico(texto, nome_arquivo_final, caminho_qr_gerado, cor_frente, cor_fundo, nivel_erro_sigla)
            self.display_qr_image(caminho_qr_gerado)
            self.populate_history()
            messagebox.showinfo("Sucesso", f"QR Code gerado e salvo como:\n{caminho_qr_gerado}")

    def display_qr_image(self, image_path):
        """Exibe a imagem do QR Code na interface."""
        try:
            img = Image.open(image_path)
            # Redimensiona a imagem para preencher o espaço, mas mantendo proporção.
            # Ajuste o tamanho máximo se necessário.
            img.thumbnail((300, 300), Image.LANCZOS) # Aumentei o tamanho máximo para melhor visualização
            photo = ImageTk.PhotoImage(img)
            self.qr_label.config(image=photo)
            self.qr_label.image = photo
        except FileNotFoundError:
            self.qr_label.config(image='')
            messagebox.showerror("Erro", f"Arquivo não encontrado: {image_path}")
        except Exception as e:
            self.qr_label.config(image='')
            messagebox.showerror("Erro", f"Erro ao carregar imagem: {e}")

    def populate_history(self):
        """Preenche a Listbox com os itens do histórico."""
        self.history_listbox.delete(0, tk.END)
        registros = buscar_historico()
        if not registros:
            self.history_listbox.insert(tk.END, "Nenhum QR Code gerado ainda.")
        else:
            self.history_data = registros
            for registro in registros:
                self.history_listbox.insert(tk.END, f"ID: {registro[0]} | Nome: {registro[2]} | Criado em: {registro[4]} | Cores: {registro[5]}/{registro[6]} | Nível: {registro[7]}")

    def display_selected_qr(self, event):
        """Exibe o QR Code selecionado na Listbox e preenche os campos de entrada e personalização."""
        selected_indices = self.history_listbox.curselection()
        if not selected_indices:
            return

        index = selected_indices[0]
        selected_record = self.history_data[index]
        caminho_completo = selected_record[3]

        self.display_qr_image(caminho_completo)

        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, selected_record[1])

        self.filename_input.delete(0, tk.END)
        full_filename_with_ext = selected_record[2]
        base_name_parts = full_filename_with_ext.replace(".png", "").rsplit('_', 2)
        original_filename_base = base_name_parts[0] if len(base_name_parts) == 3 else full_filename_with_ext.replace(".png", "")
        self.filename_input.insert(0, original_filename_base)

        self.front_color_hex.set(selected_record[5] if selected_record[5] else "black")
        self.front_color_preview.config(bg=self.front_color_hex.get())

        self.back_color_hex.set(selected_record[6] if selected_record[6] else "white")
        self.back_color_preview.config(bg=self.back_color_hex.get())

        nivel_erro_map_display = {
            "L": "L (Baixo)",
            "M": "M (Médio)",
            "Q": "Q (Quartil)",
            "H": "H (Alto)"
        }
        self.error_level_var.set(nivel_erro_map_display.get(selected_record[7], "L (Baixo)"))

    def handle_delete_qr(self):
        """Lida com a exclusão de um QR Code selecionado do histórico."""
        selected_indices = self.history_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Atenção", "Por favor, selecione um QR Code no histórico para excluir.")
            return

        index = selected_indices[0]
        selected_record = self.history_data[index]
        record_id = selected_record[0]
        caminho_arquivo = selected_record[3]

        confirm = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o QR Code '{selected_record[2]}' do histórico e do disco?"
        )

        if confirm:
            try:
                deletar_registro_historico(record_id)

                if os.path.exists(caminho_arquivo):
                    os.remove(caminho_arquivo)
                    print(f"Arquivo '{caminho_arquivo}' removido.")
                else:
                    print(f"Aviso: Arquivo '{caminho_arquivo}' não encontrado no disco.")

                messagebox.showinfo("Sucesso", "QR Code excluído com sucesso.")
                self.populate_history()
                self.qr_label.config(image='')
                self.text_input.delete(0, tk.END)
                self.filename_input.delete(0, tk.END)
                self.filename_input.insert(0, "meu_qr_code")
                self.front_color_hex.set("black")
                self.front_color_preview.config(bg="black")
                self.back_color_hex.set("white")
                self.back_color_preview.config(bg="white")
                self.error_level_var.set("L (Baixo)")

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir QR Code: {e}")

# --- Execução da Aplicação ---
if __name__ == "__main__":
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()