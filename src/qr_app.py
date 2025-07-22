# src/qr_app.py

import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser, ttk
from PIL import Image, ImageTk 
import os
import re
import io

# Tenta importar win32clipboard, mas o fallback ainda está dentro de copy_qr_to_clipboard
try:
    import win32clipboard
except ImportError:
    win32clipboard = None

# Importações corrigidas para o novo layout de pacote e config
from src import db_manager
from src import qr_logic
from src.config import DB_NAME, IMAGES_DIR, TEMP_CLIPBOARD_DIR # Importa diretórios de config

class QRGeneratorApp:
    def __init__(self, master):
        self.master = master
        master.title("Gerador de QR Code")
        master.geometry("800x750")

        # Garante que os diretórios necessários existam (já feito em config.py, mas pode repetir para segurança)
        os.makedirs(IMAGES_DIR, exist_ok=True)
        os.makedirs(TEMP_CLIPBOARD_DIR, exist_ok=True)
        
        # Inicializa o banco de dados
        db_manager.criar_tabela()
        db_manager.migrar_tabela()

        self.front_color_hex = tk.StringVar(value="black")
        self.back_color_hex = tk.StringVar(value="white")
        self.error_level_var = tk.StringVar(value="L")

        self.logo_path_var = tk.StringVar(value="")

        self.current_selected_qr_id = None
        self.current_selected_qr_old_path = None
        self.current_displayed_qr_image_path = None


        self.main_frame = tk.Frame(master, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Seção de Geração de QR Code ---
        self.generation_frame = tk.LabelFrame(self.main_frame, text="Gerar/Editar QR Code", padx=10, pady=10)
        self.generation_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.input_options_frame = tk.Frame(self.generation_frame, padx=5, pady=5)
        self.input_options_frame.grid(row=0, column=0, sticky="nsew")

        tk.Label(self.input_options_frame, text="Texto/URL:").grid(row=0, column=0, sticky="w", pady=5)
        self.text_input = tk.Entry(self.input_options_frame, width=40)
        self.text_input.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.input_options_frame, text="Nome do Arquivo:").grid(row=1, column=0, sticky="w", pady=5)
        self.filename_input = tk.Entry(self.input_options_frame, width=40)
        self.filename_input.grid(row=1, column=1, padx=5, pady=5)
        self.filename_input.insert(0, "meu_qr_code")

        # --- Opções de Personalização ---
        self.options_frame = tk.LabelFrame(self.input_options_frame, text="Opções de Personalização", padx=10, pady=5)
        self.options_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)

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

        # --- Adicionar Logo ---
        tk.Label(self.options_frame, text="Caminho do Logo:").grid(row=3, column=0, sticky="w", pady=2)
        self.logo_entry = tk.Entry(self.options_frame, textvariable=self.logo_path_var, width=25)
        self.logo_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=2)
        self.logo_button = tk.Button(self.options_frame, text="Buscar", command=self.choose_logo_file)
        self.logo_button.grid(row=3, column=2, sticky="w", padx=5, pady=2)


        # Botões de Ação (Gerar, Salvar Como, Atualizar e Copiar)
        self.action_buttons_frame = tk.Frame(self.input_options_frame)
        self.action_buttons_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.generate_button = tk.Button(self.action_buttons_frame, text="Gerar Novo QR Code", command=self.handle_generate_qr)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.update_button = tk.Button(self.action_buttons_frame, text="Atualizar QR Code", command=self.handle_update_qr, state=tk.DISABLED)
        self.update_button.pack(side=tk.LEFT, padx=5)

        self.save_as_button = tk.Button(self.action_buttons_frame, text="Salvar Como...", command=self.handle_save_as)
        self.save_as_button.pack(side=tk.LEFT, padx=5)

        self.copy_to_clipboard_button = tk.Button(self.action_buttons_frame, text="Copiar Imagem", command=self.copy_qr_to_clipboard, state=tk.DISABLED)
        self.copy_to_clipboard_button.pack(side=tk.LEFT, padx=5)

        # Área para exibir o QR Code (Coluna Direita)
        self.qr_label = tk.Label(self.generation_frame)
        self.qr_label.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.generation_frame.grid_columnconfigure(0, weight=1)
        self.generation_frame.grid_columnconfigure(1, weight=1)
        self.generation_frame.grid_rowconfigure(0, weight=1)

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

        self.clear_fields_button = tk.Button(self.history_buttons_frame, text="Limpar Campos", command=self.clear_input_fields)
        self.clear_fields_button.pack(side=tk.LEFT, padx=5)

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

    def choose_logo_file(self):
        file_path = filedialog.askopenfilename(
            title="Selecione um arquivo de logo",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if file_path:
            self.logo_path_var.set(file_path)

    def validate_inputs(self):
        """Valida os campos de entrada antes de gerar ou salvar."""
        texto = self.text_input.get().strip()
        nome_arquivo_base = self.filename_input.get().strip()

        if not texto:
            messagebox.showwarning("Atenção", "O campo 'Texto/URL' não pode estar vazio.")
            return False, None, None

        if not nome_arquivo_base:
            messagebox.showwarning("Atenção", "O campo 'Nome do Arquivo' não pode estar vazio.")
            return False, None, None

        sanitized_filename = qr_logic.sanitize_filename(nome_arquivo_base)
        if sanitized_filename != nome_arquivo_base:
            messagebox.showinfo("Aviso", f"O nome do arquivo '{nome_arquivo_base}' foi ajustado para '{sanitized_filename}' para remover caracteres inválidos.")
            self.filename_input.delete(0, tk.END)
            self.filename_input.insert(0, sanitized_filename)
        if not sanitized_filename:
            messagebox.showwarning("Atenção", "O nome do arquivo resultante da limpeza está vazio. Por favor, insira um nome válido.")
            return False, None, None

        return True, texto, sanitized_filename

    def clear_input_fields(self):
        """Limpa todos os campos de entrada e redefine as opções para o padrão."""
        self.text_input.delete(0, tk.END)
        self.filename_input.delete(0, tk.END)
        self.filename_input.insert(0, "meu_qr_code")
        self.front_color_hex.set("black")
        self.front_color_preview.config(bg="black")
        self.back_color_hex.set("white")
        self.back_color_preview.config(bg="white")
        self.error_level_var.set("L (Baixo)")
        self.logo_path_var.set("")
        self.qr_label.config(image='')
        self.current_selected_qr_id = None
        self.current_selected_qr_old_path = None
        self.current_displayed_qr_image_path = None
        self.update_button.config(state=tk.DISABLED)
        self.copy_to_clipboard_button.config(state=tk.DISABLED)
        self.history_listbox.selection_clear(0, tk.END)


    def handle_generate_qr(self):
        """Lida com a ação de gerar um NOVO QR Code."""
        is_valid, texto, nome_arquivo_base = self.validate_inputs()
        if not is_valid:
            return

        cor_frente = self.front_color_hex.get()
        cor_fundo = self.back_color_hex.get()
        nivel_erro_display = self.error_level_var.get()
        nivel_erro_sigla = nivel_erro_display[0]
        caminho_logo = self.logo_path_var.get() if self.logo_path_var.get() else None

        try:
            caminho_qr_gerado = qr_logic.gerar_qr_code_e_salvar(
                texto, nome_arquivo_base, cor_frente, cor_fundo, nivel_erro_sigla, caminho_logo=caminho_logo
            )

            if caminho_qr_gerado:
                nome_arquivo_final = os.path.basename(caminho_qr_gerado)
                db_manager.registrar_historico(texto, nome_arquivo_final, caminho_qr_gerado, cor_frente, cor_fundo, nivel_erro_sigla)
                self.display_qr_image(caminho_qr_gerado)
                self.populate_history()
                messagebox.showinfo("Sucesso", f"QR Code gerado e salvo em histórico:\n{caminho_qr_gerado}")
                self.clear_input_fields()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar QR Code: {e}")


    def handle_update_qr(self):
        """Lida com a atualização de um QR Code existente no histórico."""
        if not self.current_selected_qr_id:
            messagebox.showwarning("Atenção", "Nenhum QR Code selecionado para atualizar.")
            return

        is_valid, texto, nome_arquivo_base = self.validate_inputs()
        if not is_valid:
            return

        cor_frente = self.front_color_hex.get()
        cor_fundo = self.back_color_hex.get()
        nivel_erro_display = self.error_level_var.get()
        nivel_erro_sigla = nivel_erro_display[0]
        caminho_logo = self.logo_path_var.get() if self.logo_path_var.get() else None

        confirm = messagebox.askyesno(
            "Confirmar Atualização",
            f"Tem certeza que deseja atualizar o QR Code selecionado (ID: {self.current_selected_qr_id})?\n"
            "Isso irá gerar um novo arquivo de imagem e substituir o antigo."
        )
        if not confirm:
            return

        try:
            novo_caminho_qr_gerado = qr_logic.gerar_qr_code_e_salvar(
                texto, nome_arquivo_base, cor_frente, cor_fundo, nivel_erro_sigla, caminho_logo=caminho_logo
            )

            if novo_caminho_qr_gerado:
                novo_nome_arquivo_final = os.path.basename(novo_caminho_qr_gerado)

                db_manager.atualizar_registro_historico(self.current_selected_qr_id, texto, novo_nome_arquivo_final,
                                             novo_caminho_qr_gerado, cor_frente, cor_fundo, nivel_erro_sigla)

                if os.path.exists(self.current_selected_qr_old_path):
                    try:
                        os.remove(self.current_selected_qr_old_path)
                        print(f"Arquivo antigo '{self.current_selected_qr_old_path}' removido.")
                    except Exception as e:
                        print(f"Erro ao remover arquivo antigo '{self.current_selected_qr_old_path}': {e}")

                messagebox.showinfo("Sucesso", f"QR Code atualizado com sucesso e salvo como:\n{novo_caminho_qr_gerado}")
                self.display_qr_image(novo_caminho_qr_gerado)
                self.populate_history()
                self.clear_input_fields()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar QR Code: {e}")


    def handle_save_as(self):
        """Lida com a ação de salvar o QR Code em um local específico escolhido pelo usuário."""
        is_valid, texto, nome_arquivo_base = self.validate_inputs()
        if not is_valid:
            return

        cor_frente = self.front_color_hex.get()
        cor_fundo = self.back_color_hex.get()
        nivel_erro_display = self.error_level_var.get()
        nivel_erro_sigla = nivel_erro_display[0]
        caminho_logo = self.logo_path_var.get() if self.logo_path_var.get() else None

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            initialfile=qr_logic.sanitize_filename(nome_arquivo_base)
        )

        if file_path:
            try:
                caminho_qr_gerado = qr_logic.gerar_qr_code_e_salvar(
                    texto,
                    nome_arquivo_base,
                    cor_frente,
                    cor_fundo,
                    nivel_erro_sigla,
                    caminho_personalizado=file_path,
                    caminho_logo=caminho_logo
                )
                if caminho_qr_gerado:
                    messagebox.showinfo("Sucesso", f"QR Code salvo com sucesso em:\n{caminho_qr_gerado}")
                    self.current_displayed_qr_image_path = caminho_qr_gerado
                    self.copy_to_clipboard_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar QR Code: {e}")
        else:
            messagebox.showinfo("Informação", "Operação 'Salvar Como' cancelada.")


    def copy_qr_to_clipboard(self):
        """Copia a imagem do QR Code exibida atualmente para a área de transferência."""
        if not self.current_displayed_qr_image_path:
            messagebox.showwarning("Atenção", "Nenhum QR Code para copiar. Por favor, gere ou selecione um QR Code primeiro.")
            return

        try:
            img_to_copy = Image.open(self.current_displayed_qr_image_path)
            
            img_to_copy.thumbnail((500, 500), Image.LANCZOS)

            if win32clipboard:
                try:
                    output = io.BytesIO()
                    img_to_copy.convert("RGB").save(output, "BMP")
                    data = output.getvalue()[14:] 

                    win32clipboard.OpenClipboard()
                    win32clipboard.EmptyClipboard()
                    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                    win32clipboard.CloseClipboard()
                    messagebox.showinfo("Sucesso", "Imagem copiada para a área de transferência!")

                except Exception as ex:
                    messagebox.showerror("Erro de Cópia (pywin32)", f"Não foi possível copiar a imagem: {ex}")
                    self.save_temp_and_notify_clipboard(img_to_copy)
            else:
                self.save_temp_and_notify_clipboard(img_to_copy)

        except FileNotFoundError:
            messagebox.showerror("Erro", "O arquivo da imagem exibida não foi encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao acessar a imagem para cópia: {e}")

    def save_temp_and_notify_clipboard(self, img_pil_obj):
        """Função auxiliar para salvar em um arquivo temporário e notificar o usuário para cópia manual."""
        # TEMP_CLIPBOARD_DIR já é importado de config.py e garantido que exista
        temp_file = os.path.join(TEMP_CLIPBOARD_DIR, "temp_qr_clipboard.png")
        try:
            img_pil_obj.save(temp_file)
            messagebox.showinfo("Sucesso (Manual)", f"Imagem salva temporariamente em:\n{temp_file}\n"
                                                   "Por favor, copie de lá manualmente (Ctrl+C).")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar a imagem temporária: {e}")


    def display_qr_image(self, image_path):
        """Exibe a imagem do QR Code na interface e armazena o caminho para cópia."""
        try:
            img = Image.open(image_path)
            img.thumbnail((300, 300), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.qr_label.config(image=photo)
            self.qr_label.image = photo
            self.current_displayed_qr_image_path = image_path
            self.copy_to_clipboard_button.config(state=tk.NORMAL)
        except FileNotFoundError:
            self.qr_label.config(image='')
            messagebox.showerror("Erro", f"Arquivo não encontrado: {image_path}")
            self.current_displayed_qr_image_path = None
            self.copy_to_clipboard_button.config(state=tk.DISABLED)
        except Exception as e:
            self.qr_label.config(image='')
            messagebox.showerror("Erro", f"Erro ao carregar imagem: {e}")
            self.current_displayed_qr_image_path = None
            self.copy_to_clipboard_button.config(state=tk.DISABLED)

    def populate_history(self):
        """Preenche a Listbox com os itens do histórico."""
        self.history_listbox.delete(0, tk.END)
        registros = db_manager.buscar_historico()
        if not registros:
            self.history_listbox.insert(tk.END, "Nenhum QR Code gerado ainda.")
        else:
            self.history_data = registros
            for registro in registros:
                self.history_listbox.insert(tk.END, f"ID: {registro[0]} | Nome: {registro[2]} | Criado em: {registro[4]} | Cores: {registro[5]}/{registro[6]} | Nível: {registro[7]}")

    def display_selected_qr(self, event):
        """
        Exibe o QR Code selecionado na Listbox e preenche os campos de entrada e personalização.
        """
        selected_indices = self.history_listbox.curselection()

        if not selected_indices:
            if self.current_selected_qr_id is not None:
                self.clear_input_fields()
            return

        index = selected_indices[0]
        selected_record = self.history_data[index]
        record_id = selected_record[0]
        caminho_completo = selected_record[3]

        self.current_selected_qr_id = record_id
        self.current_selected_qr_old_path = caminho_completo

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

        self.logo_path_var.set("")

        self.update_button.config(state=tk.NORMAL)


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
                db_manager.deletar_registro_historico(record_id)

                if os.path.exists(caminho_arquivo):
                    os.remove(caminho_arquivo)
                    print(f"Arquivo '{caminho_arquivo}' removido.")
                else:
                    print(f"Aviso: Arquivo '{caminho_arquivo}' não encontrado no disco.")

                messagebox.showinfo("Sucesso", "QR Code excluído com sucesso.")
                self.populate_history()
                self.clear_input_fields()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir QR Code: {e}")

# --- Execução da Aplicação ---
if __name__ == "__main__":
    root = tk.Tk()
    app = QRGeneratorApp(root)
    root.mainloop()