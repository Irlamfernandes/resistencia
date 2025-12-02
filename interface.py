import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from processador_dados import executar_calculo

class Aplicacao(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Calculadora de Engenharia")
        self.minsize(700, 800) 
        self.configure(bg="#F0F8FF") 

        style = ttk.Style(self)
        style.theme_use('clam') 

        self.primary_bg = "#F0F8FF"
        self.secondary_bg = "#E6F3FF"
        self.accent_blue = "#4682B4"
        self.button_green = "#2E8B57"
        self.button_hover_green = "#3CB371"
        self.button_red = "#B22222" # Firebrick
        self.button_hover_red = "#DC143C" # Crimson
        self.text_dark = "#333333"
        self.result_bg = "#FFFACD"
        self.result_fg = "#8B0000"

        style.configure('TFrame', background=self.primary_bg)
        style.configure('TLabel', background=self.primary_bg, foreground=self.text_dark, font=('Helvetica', 16))
        style.configure('TButton', background=self.button_green, foreground='white', font=('Helvetica', 16, 'bold'), borderwidth=0, padding=10) 
        style.configure('Clear.TButton', background=self.button_red, foreground='white', font=('Helvetica', 16, 'bold'), borderwidth=0, padding=10)
        style.map('TButton', background=[('active', self.button_hover_green), ('!disabled', self.button_green)], foreground=[('active', 'white'), ('!disabled', 'white')]) 
        style.map('Clear.TButton', background=[('active', self.button_hover_red), ('!disabled', self.button_red)], foreground=[('active', 'white'), ('!disabled', 'white')])
        style.configure('TCombobox', fieldbackground='white', background=self.secondary_bg, foreground=self.text_dark, font=('Helvetica', 14)) 
        style.configure('TEntry', fieldbackground='white', foreground=self.text_dark, font=('Helvetica', 14)) 
        style.configure('TLabelframe', background=self.primary_bg, bordercolor=self.accent_blue, relief='solid', borderwidth=1) 
        style.configure('TLabelframe.Label', background=self.primary_bg, foreground=self.accent_blue, font=('Helvetica', 18, 'bold')) 
        style.configure('Result.TLabel', background=self.result_bg, foreground=self.result_fg, font=('Helvetica', 20, 'bold'), anchor='center', padding=10) 

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        top_controls_frame = ttk.Frame(self, style='TFrame')
        top_controls_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        top_controls_frame.grid_columnconfigure(0, weight=1) # Coluna para o botão Adicionar
        top_controls_frame.grid_columnconfigure(1, weight=1) # Coluna para o botão Limpar

        self.btn_adicionar = ttk.Button(top_controls_frame, text="Adicionar Campos de Entrada", command=self.adicionar_conjunto_campos, style='TButton')
        self.btn_adicionar.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self.btn_limpar = ttk.Button(top_controls_frame, text="Limpar Tudo", command=self.limpar_campos, style='Clear.TButton')
        self.btn_limpar.grid(row=0, column=1, sticky="ew", padx=(10, 0))

        canvas_frame = ttk.Frame(self, padding=(20, 0), style='TFrame')
        canvas_frame.grid(row=1, column=0, sticky="nsew") 
        canvas_frame.grid_rowconfigure(0, weight=1) 
        canvas_frame.grid_columnconfigure(0, weight=1) 

        canvas = tk.Canvas(canvas_frame)
        scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        self.scrollable_frame.configure(style='TFrame') 
        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))) 
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw") 
        canvas.configure(yscrollcommand=scrollbar.set) 
        canvas.configure(background=self.secondary_bg, highlightbackground=self.secondary_bg) 
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        main_frame = ttk.Frame(self, padding="20", style='TFrame')
        main_frame.grid(row=2, column=0, sticky="ew")
        main_frame.grid_columnconfigure(0, weight=1)

        controles_frame = ttk.LabelFrame(main_frame, text="Opções de Cálculo", padding="20", style='TLabelframe')
        controles_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20)) 
        ttk.Label(controles_frame, text="Escolha o cálculo a ser realizado:").pack(anchor="w")
        
        opcoes_calculo = [
            "Cálculo da Tensão Admissível",
            "Calcular Força de Projeto",
            "Calcular Força por Apoio",
            "Calcular Área de Projeto",
            "Calcular Área por Apoio",
            "Determinar Dimensão do Apoio",
            "Cálculo da Deformação (Simples)",
            "Cálculo da Deformação (Segmentada)",
            "Propriedades de Perfil L",
            "Propriedades de Perfil T",
            "Propriedades de Perfil I",
            "Propriedades de Retângulo Vazado",
            "Propriedades de Círculo Vazado",
            "Propriedades de Trapézio",
        ]
        self.combo_calculo = ttk.Combobox(controles_frame, values=opcoes_calculo, state="readonly")
        self.combo_calculo.pack(pady=(10, 15), fill="x", expand=True) 
        self.combo_calculo.set("Selecione um cálculo") 
        self.combo_calculo.bind("<<ComboboxSelected>>", self.atualizar_unidades_saida) 
        
        ttk.Label(controles_frame, text="Escolha a unidade de medida da saída:").pack(anchor="w")
        
        self.unidades_saida_map = {
            "Cálculo da Tensão Admissível": ["kgf/cm²", "MPa", "psi"],
            "Calcular Força de Projeto": ["kgf", "N", "lbf"],
            "Calcular Força por Apoio": ["kgf", "N", "lbf"],
            "Calcular Área de Projeto": ["cm²", "mm²", "in²"],
            "Calcular Área por Apoio": ["cm²", "mm²", "in²"],
            "Determinar Dimensão do Apoio": ["cm", "mm", "in"],
            "Cálculo da Deformação (Simples)": ["mm", "cm", "in"],
            "Cálculo da Deformação (Segmentada)": ["mm", "cm", "in"],
            "Propriedades de Perfil L": ["cm", "mm", "in"],
            "Propriedades de Perfil T": ["cm", "mm", "in"],
            "Propriedades de Perfil I": ["cm", "mm", "in"],
            "Propriedades de Retângulo Vazado": ["cm", "mm", "in"],
            "Propriedades de Círculo Vazado": ["cm", "mm", "in"],
            "Propriedades de Trapézio": ["cm", "mm", "in"],
        }

        self.combo_unidade_saida = ttk.Combobox(controles_frame, state="readonly")
        self.combo_unidade_saida.pack(pady=(10, 15), fill="x", expand=True) 

        self.btn_calcular = ttk.Button(main_frame, text="Calcular", command=self.obter_e_processar_dados, style='TButton')
        self.btn_calcular.grid(row=1, column=0, pady=(0, 20), sticky="ew") 
        resultado_frame = ttk.LabelFrame(main_frame, text="Resultado", padding="20", style='TLabelframe')
        resultado_frame.grid(row=2, column=0, sticky="ew")

        self.resultado_var = tk.StringVar()
        self.label_resultado = ttk.Label(resultado_frame, textvariable=self.resultado_var, style='Result.TLabel')
        self.label_resultado.pack(pady=10, fill="x", expand=True) 
        self.conjuntos_de_campos = []

        self.atualizar_unidades_saida(None)

    def atualizar_unidades_saida(self, event):
        calculo_selecionado = self.combo_calculo.get()
        unidades = self.unidades_saida_map.get(calculo_selecionado, [])
        
        self.combo_unidade_saida['values'] = unidades
        if unidades:
            self.combo_unidade_saida.set(unidades[0])
        else:
            self.combo_unidade_saida.set("")

    def limpar_campos(self):
        """Destrói todos os campos de entrada e reseta a interface."""
        # Remove todos os frames de entrada da área rolável
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Limpa a lista que armazena as referências dos campos
        self.conjuntos_de_campos.clear()

        # Limpa a variável do resultado
        self.resultado_var.set("")

        # Reseta os comboboxes de cálculo e unidade de saída
        self.combo_calculo.set("Selecione um cálculo")
        self.atualizar_unidades_saida(None)

    def adicionar_conjunto_campos(self):
        frame_conjunto = ttk.Frame(self.scrollable_frame, style='TFrame')
        frame_conjunto.pack(fill="x", pady=5, padx=10, expand=True)
        frame_conjunto.grid_columnconfigure(0, weight=4) 
        frame_conjunto.grid_columnconfigure(1, weight=1)
        frame_conjunto.grid_columnconfigure(2, weight=1)
        frame_conjunto.grid_columnconfigure(3, weight=0) # Coluna para o botão de remover

        opcoes_principais = [
            "Peso", "Peso Adicional", 
            "Coeficiente de Força", "Coeficiente de Resistência", 
            "Tensão Limite",
            "Quantidade de apoios",
            "Proporção entre dimensões",
            "Comprimento Inicial", "Módulo de Elasticidade",
            "Área de Seção", "Carga Distribuída",
            "Comprimento da Carga", "Diâmetro Externo", "Espessura da Parede",
            "Segmento",
            "Largura Total (B)", # Para Perfil L
            "Altura Total (H)",
            "Espessura da Alma (b)", # Para Perfis L e T
            "Espessura da Mesa (h)", # Para Perfis L e T
            "Largura da Mesa (B)", # Para Perfil T
            "Base do Retângulo (B)",
            "Altura do Retângulo (H)",
            "Espessura do Retângulo (e)",
            "Diâmetro Externo do Círculo (D)",
            "Espessura do Círculo (e)",
            "Base Superior do Trapézio",
            "Base Inferior do Trapézio",
            "Altura do Trapézio",
            "Largura da Mesa Superior (I)",
            "Espessura da Mesa Superior (I)",
            "Largura da Mesa Inferior (i)",
            "Espessura da Mesa Inferior (i)",
        ]

        def ajustar_largura_dropdown(widget):
            """Ajusta a largura do dropdown com base no item mais longo."""
            opcoes = widget['values']
            if not opcoes:
                return
            # Encontra o comprimento da string mais longa nas opções
            largura_maxima = max(len(str(opcao)) for opcao in opcoes)
            widget.config(width=largura_maxima)

        combo_opcao = ttk.Combobox(frame_conjunto, values=opcoes_principais, state="readonly", style='TCombobox', postcommand=lambda: ajustar_largura_dropdown(combo_opcao))
        combo_opcao.grid(row=0, column=0, padx=(0, 10), sticky="ew") 
        combo_opcao.set("Escolha um tipo") 

        entrada_valor = ttk.Entry(frame_conjunto, style='TEntry')
        combo_unidade = ttk.Combobox(frame_conjunto, state="readonly", style='TCombobox')

        unidades = {
            "Peso": ["kgf", "N", "lbf"],
            "Peso Adicional": ["kgf", "N", "lbf"],
            "Tensão Limite": ["kgf/cm²", "MPa", "psi"],
            "Comprimento Inicial": ["m", "cm", "mm"],
            "Módulo de Elasticidade": ["GPa", "MPa", "kgf/cm²"],
            "Área de Seção": ["cm²", "mm²", "in²"],
            "Carga Distribuída": ["kN/m", "N/m", "kgf/m"],
            "Comprimento da Carga": ["m", "cm", "mm"],
            "Diâmetro Externo": ["mm", "cm", "in"],
            "Espessura da Parede": ["mm", "cm", "in"],
            "Largura Total (B)": ["cm", "mm", "in"],
            "Altura Total (H)": ["cm", "mm", "in"],
            "Espessura da Alma (b)": ["cm", "mm", "in"],
            "Espessura da Mesa (h)": ["cm", "mm", "in"],
            "Largura da Mesa (B)": ["cm", "mm", "in"],
            "Base do Retângulo (B)": ["cm", "mm", "in"],
            "Altura do Retângulo (H)": ["cm", "mm", "in"],
            "Espessura do Retângulo (e)": ["cm", "mm", "in"],
            "Diâmetro Externo do Círculo (D)": ["cm", "mm", "in"],
            "Espessura do Círculo (e)": ["cm", "mm", "in"],
            "Base Superior do Trapézio": ["cm", "mm", "in"],
            "Base Inferior do Trapézio": ["cm", "mm", "in"],
            "Altura do Trapézio": ["cm", "mm", "in"],
            "Largura da Mesa Superior (I)": ["cm", "mm", "in"],
            "Espessura da Mesa Superior (I)": ["cm", "mm", "in"],
            "Largura da Mesa Inferior (i)": ["cm", "mm", "in"],
            "Espessura da Mesa Inferior (i)": ["cm", "mm", "in"],
        }

        def ao_selecionar_opcao(event):
            selecionado = combo_opcao.get()

            if selecionado == "Segmento":
                entrada_valor.grid_forget()
                combo_unidade.grid_forget()
                self.abrir_janela_segmento(frame_conjunto)
            elif selecionado in unidades:
                entrada_valor.grid(row=0, column=1, padx=10, sticky="ew")
                combo_unidade['values'] = unidades[selecionado]
                combo_unidade.set(unidades[selecionado][0])
                combo_unidade.grid(row=0, column=2, padx=(0, 10), sticky="ew") 
            else:
                entrada_valor.grid(row=0, column=1, padx=10, sticky="ew")
                combo_unidade.grid_forget()

        combo_opcao.bind("<<ComboboxSelected>>", ao_selecionar_opcao) 
        
        conjunto_widgets = (combo_opcao, entrada_valor, combo_unidade)
        self.conjuntos_de_campos.append(conjunto_widgets)

        btn_remover = ttk.Button(frame_conjunto, text="X", width=2, command=lambda f=frame_conjunto, c=conjunto_widgets: self.remover_conjunto_campos(f, c))
        btn_remover.grid(row=0, column=3, padx=(10, 0), sticky="e")

    def remover_conjunto_campos(self, frame_a_remover, conjunto_a_remover):
        """Remove um conjunto específico de campos de entrada."""
        # Remove o frame da interface
        frame_a_remover.destroy()
        # Remove o conjunto de widgets da lista de dados
        self.conjuntos_de_campos.remove(conjunto_a_remover)

    def abrir_janela_segmento(self, frame_pai):
        janela = tk.Toplevel(self)
        janela.title("Adicionar Segmento")
        janela.configure(bg=self.secondary_bg)
        janela.transient(self)
        janela.grab_set()

        frame_interno = ttk.Frame(janela, padding=20, style='TFrame')
        frame_interno.pack(expand=True, fill="both")

        # Comprimento
        ttk.Label(frame_interno, text="Comprimento:").grid(row=0, column=0, sticky="w", pady=5)
        entry_comp = ttk.Entry(frame_interno)
        entry_comp.grid(row=0, column=1, sticky="ew", pady=5)
        combo_comp = ttk.Combobox(frame_interno, values=["m", "cm", "mm"], state="readonly")
        combo_comp.set("m")
        combo_comp.grid(row=0, column=2, sticky="ew", pady=5, padx=(5,0))

        # Diâmetro Externo
        ttk.Label(frame_interno, text="Diâmetro Externo:").grid(row=1, column=0, sticky="w", pady=5)
        entry_diam = ttk.Entry(frame_interno)
        entry_diam.grid(row=1, column=1, sticky="ew", pady=5)
        combo_diam = ttk.Combobox(frame_interno, values=["mm", "cm", "in"], state="readonly")
        combo_diam.set("mm")
        combo_diam.grid(row=1, column=2, sticky="ew", pady=5, padx=(5,0))

        # Espessura da Parede
        ttk.Label(frame_interno, text="Espessura da Parede:").grid(row=2, column=0, sticky="w", pady=5)
        entry_esp = ttk.Entry(frame_interno)
        entry_esp.grid(row=2, column=1, sticky="ew", pady=5)
        combo_esp = ttk.Combobox(frame_interno, values=["mm", "cm", "in"], state="readonly")
        combo_esp.set("mm")
        combo_esp.grid(row=2, column=2, sticky="ew", pady=5, padx=(5,0))

        def salvar_segmento():
            dados_segmento = {
                "comprimento": entry_comp.get(), "unidade_comprimento": combo_comp.get(),
                "diam_ext": entry_diam.get(), "unidade_diam_ext": combo_diam.get(),
                "espessura": entry_esp.get(), "unidade_espessura": combo_esp.get()
            }
            # Armazena os dados do segmento no frame principal para ser lido depois
            frame_pai.dados_segmento = dados_segmento
            # Atualiza a interface para mostrar que o segmento foi adicionado
            for widget in frame_pai.winfo_children():
                if isinstance(widget, ttk.Combobox): continue
                widget.destroy()
            ttk.Label(frame_pai, text=f"Segmento: L={dados_segmento['comprimento']}{dados_segmento['unidade_comprimento']}, D={dados_segmento['diam_ext']}{dados_segmento['unidade_diam_ext']}, E={dados_segmento['espessura']}{dados_segmento['unidade_espessura']}").grid(row=0, column=1, columnspan=2, sticky="w")
            janela.destroy()

        btn_salvar = ttk.Button(frame_interno, text="Salvar Segmento", command=salvar_segmento)
        btn_salvar.grid(row=3, column=0, columnspan=3, pady=20, sticky="ew")

    def obter_e_processar_dados(self):
        calculo_selecionado = self.combo_calculo.get()
        unidade_saida_selecionada = self.combo_unidade_saida.get()

        if not calculo_selecionado or calculo_selecionado == "Selecione um cálculo":
            messagebox.showwarning("Aviso", "Por favor, selecione um tipo de cálculo.")
            return
        if not unidade_saida_selecionada:
            messagebox.showwarning("Aviso", "Por favor, selecione uma unidade de saída.")
            return

        resultado = executar_calculo(calculo_selecionado, self.conjuntos_de_campos, unidade_saida_selecionada)
        self.resultado_var.set(resultado)