import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Adiciona o diretório do script ao path para garantir que os módulos sejam encontrados
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa as classes das interfaces gráficas de cada exportador
try:
    from bpa_exporter import BPAExporterGUI
    from apac_exporter import APACExporterGUI
    from ciha_exporter import CIHAExporterGUI
except ImportError as e:
    messagebox.showerror("Erro de Importação", f"Não foi possível encontrar os arquivos dos exportadores.\nVerifique se 'bpa_exporter.py', 'apac_exporter.py' e 'ciha_exporter.py' estão na mesma pasta que o loader.\n\nDetalhe: {e}")
    sys.exit(1)
except Exception as e:
    messagebox.showerror("Erro Inesperado", f"Ocorreu um erro ao carregar os módulos:\n\n{e}")
    sys.exit(1)


class LoaderApp:
    """
    A janela principal que serve como um menu para as ferramentas de exportação.
    """
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Hub de Ferramentas de Exportação SIGH")
        self.root.geometry("500x350")
        
        # Estilo
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TButton", padding=10, font=('Helvetica', 12, 'bold'))
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        title_label = ttk.Label(
            main_frame,
            text="Selecione a Ferramenta",
            font=("Helvetica", 18, "bold"),
            anchor="center"
        )
        title_label.pack(pady=(0, 20))

        # Botões para cada exportador
        btn_bpa = ttk.Button(
            main_frame,
            text="Exportador BPA-I",
            command=self.launch_bpa
        )
        btn_bpa.pack(fill=tk.X, pady=5, ipady=5)

        btn_apac = ttk.Button(
            main_frame,
            text="Exportador APAC",
            command=self.launch_apac
        )
        btn_apac.pack(fill=tk.X, pady=5, ipady=5)

        btn_ciha = ttk.Button(
            main_frame,
            text="Exportador CIHA",
            command=self.launch_ciha
        )
        btn_ciha.pack(fill=tk.X, pady=5, ipady=5)
    
    def launch_tool(self, gui_class):
        """
        Função genérica para abrir uma nova janela com a ferramenta selecionada.
        """
        try:
            # Cria uma nova janela (Toplevel) que é filha da janela principal
            tool_window = tk.Toplevel(self.root)
            # Instancia a classe da GUI da ferramenta dentro da nova janela
            gui_class(tool_window)
        except Exception as e:
            messagebox.showerror("Erro ao Abrir Ferramenta", f"Ocorreu um erro ao tentar iniciar a ferramenta:\n\n{e}")

    def launch_bpa(self):
        self.launch_tool(BPAExporterGUI)

    def launch_apac(self):
        self.launch_tool(APACExporterGUI)
        
    def launch_ciha(self):
        self.launch_tool(CIHAExporterGUI)


def main():
    """Função principal para iniciar o Loader."""
    root = tk.Tk()
    app = LoaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
