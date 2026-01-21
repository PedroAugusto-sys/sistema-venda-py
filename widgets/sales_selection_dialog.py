import customtkinter as ctk
from datetime import datetime, timedelta
from tkinter import filedialog
import calendar

# Cores do tema escuro
COLORS = {
    "bg_dark": "#242424",
    "bg_panel": "#2b2b2b",
    "green": "#2ed573",
    "red": "#ff4757",
    "text_light": "#ffffff",
    "text_gray": "#a0a0a0"
}

def format_time_ago(date_str, timestamp_str=None):
    """Retorna string formatada de há quanto tempo foi a venda"""
    try:
        # Tentar usar timestamp completo se disponível (mais preciso)
        if timestamp_str:
            try:
                sale_datetime = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                today = datetime.now()
                delta = today - sale_datetime
                
                # Se for do mesmo dia, mostrar horas
                if delta.days == 0:
                    hours = delta.seconds // 3600
                    minutes = (delta.seconds % 3600) // 60
                    if hours > 0:
                        return f"Há {hours} hora{'s' if hours > 1 else ''}"
                    elif minutes > 0:
                        return f"Há {minutes} minuto{'s' if minutes > 1 else ''}"
                    else:
                        return "Agora mesmo"
            except:
                pass
        
        # Converter data string para datetime
        sale_date = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now().date()
        sale_date_only = sale_date.date()
        
        delta = today - sale_date_only
        
        if delta.days == 0:
            return "Hoje"
        elif delta.days == 1:
            return "Ontem"
        elif delta.days < 7:
            return f"Há {delta.days} dias"
        elif delta.days < 30:
            weeks = delta.days // 7
            return f"Há {weeks} semana{'s' if weeks > 1 else ''}"
        elif delta.days < 365:
            months = delta.days // 30
            return f"Há {months} mês{'es' if months > 1 else ''}"
        else:
            years = delta.days // 365
            return f"Há {years} ano{'s' if years > 1 else ''}"
    except:
        return "Data inválida"

def convert_yyyy_mm_dd_to_dd_mm_yyyy(date_str):
    """Converte data de YYYY-MM-DD para DD-MM-YYYY"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%d-%m-%Y")
    except:
        return date_str

def convert_dd_mm_yyyy_to_yyyy_mm_dd(date_str):
    """Converte data de DD-MM-YYYY para YYYY-MM-DD"""
    try:
        date_obj = datetime.strptime(date_str, "%d-%m-%Y")
        return date_obj.strftime("%Y-%m-%d")
    except:
        return date_str

class SalesSelectionDialog(ctk.CTkToplevel):
    """Diálogo para selecionar uma venda e gerar comprovante"""
    
    def __init__(self, parent, client_name, sales_data, company_data, client_data=None):
        super().__init__(parent)
        
        self.client_name = client_name
        self.sales_data = sales_data.copy() if sales_data else []
        self.company_data = company_data
        self.client_data = client_data or {}
        self.selected_sale = None
        
        self.title("Selecionar Venda para Comprovante")
        self.resizable(False, False)
        self.geometry("800x600")
        
        # Centralizar janela na tela
        self.transient(parent)
        self.grab_set()
        
        # Configurar tema
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_panel"], corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Título
        title_label = ctk.CTkLabel(
            main_frame,
            text=f"Vendas de {client_name}",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["text_light"]
        )
        title_label.pack(pady=(20, 15))
        
        # Frame de filtros
        filters_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        filters_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Filtro de data inicial
        date_start_label = ctk.CTkLabel(
            filters_frame,
            text="Data Inicial:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_gray"]
        )
        date_start_label.grid(row=0, column=0, sticky="w", padx=(0, 5), pady=5)
        
        date_start_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        date_start_frame.grid(row=0, column=1, padx=(0, 15), pady=5)
        
        self.date_start_entry = ctk.CTkEntry(
            date_start_frame,
            font=ctk.CTkFont(size=12),
            width=120,
            placeholder_text="DD-MM-YYYY"
        )
        self.date_start_entry.pack(side="left")
        
        date_start_btn = ctk.CTkButton(
            date_start_frame,
            text="📅",
            font=ctk.CTkFont(size=14),
            width=35,
            height=28,
            fg_color=COLORS["bg_dark"],
            hover_color="#333333",
            command=lambda: self.open_date_picker(self.date_start_entry)
        )
        date_start_btn.pack(side="left", padx=(5, 0))
        
        # Filtro de data final
        date_end_label = ctk.CTkLabel(
            filters_frame,
            text="Data Final:",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_gray"]
        )
        date_end_label.grid(row=0, column=2, sticky="w", padx=(0, 5), pady=5)
        
        date_end_frame = ctk.CTkFrame(filters_frame, fg_color="transparent")
        date_end_frame.grid(row=0, column=3, padx=(0, 15), pady=5)
        
        self.date_end_entry = ctk.CTkEntry(
            date_end_frame,
            font=ctk.CTkFont(size=12),
            width=120,
            placeholder_text="DD-MM-YYYY"
        )
        self.date_end_entry.pack(side="left")
        
        date_end_btn = ctk.CTkButton(
            date_end_frame,
            text="📅",
            font=ctk.CTkFont(size=14),
            width=35,
            height=28,
            fg_color=COLORS["bg_dark"],
            hover_color="#333333",
            command=lambda: self.open_date_picker(self.date_end_entry)
        )
        date_end_btn.pack(side="left", padx=(5, 0))
        
        # Botão de filtrar
        filter_btn = ctk.CTkButton(
            filters_frame,
            text="Filtrar",
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10,
            height=30,
            width=80,
            fg_color=COLORS["green"],
            hover_color="#26c463",
            command=self.apply_filters
        )
        filter_btn.grid(row=0, column=4, padx=(0, 10), pady=5)
        
        # Botão de limpar filtros
        clear_btn = ctk.CTkButton(
            filters_frame,
            text="Limpar",
            font=ctk.CTkFont(size=12),
            corner_radius=10,
            height=30,
            width=80,
            fg_color=COLORS["bg_dark"],
            hover_color="#333333",
            command=self.clear_filters
        )
        clear_btn.grid(row=0, column=5, pady=5)
        
        # ScrollableFrame para lista de vendas
        scroll_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color=COLORS["bg_dark"],
            scrollbar_button_color=COLORS["bg_panel"],
            scrollbar_button_hover_color="#3a3a3a"
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        self.sales_list_frame = scroll_frame
        self.sales_widgets = []
        
        # Carregar vendas
        self.filtered_sales = self.sales_data.copy()
        self.display_sales()
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40,
            fg_color=COLORS["bg_dark"],
            hover_color="#333333",
            command=self.cancel_action
        )
        cancel_btn.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.generate_btn = ctk.CTkButton(
            buttons_frame,
            text="Gerar Comprovante",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=10,
            height=40,
            fg_color=COLORS["green"],
            hover_color="#26c463",
            command=self.generate_receipt,
            state="disabled"
        )
        self.generate_btn.grid(row=0, column=1, sticky="ew", padx=(5, 0))
        
        # Centralizar após criar a janela
        self.after(100, self._center_on_screen)
    
    def open_date_picker(self, entry_widget):
        """Abre um diálogo de seleção de data"""
        DatePickerDialog(self, entry_widget)
    
    def _center_on_screen(self):
        """Centraliza a janela no centro da tela"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        try:
            self.attributes('-topmost', True)
            self.after(50, lambda: self.attributes('-topmost', False))
        except:
            pass
    
    def display_sales(self):
        """Exibe a lista de vendas"""
        # Limpar lista anterior
        for widget in self.sales_list_frame.winfo_children():
            widget.destroy()
        self.sales_widgets.clear()
        
        if not self.filtered_sales:
            empty_label = ctk.CTkLabel(
                self.sales_list_frame,
                text="Nenhuma venda encontrada",
                font=ctk.CTkFont(size=14),
                text_color=COLORS["text_gray"]
            )
            empty_label.pack(pady=20)
            return
        
        # Ordenar vendas por data (mais recente primeiro)
        sorted_sales = sorted(
            self.filtered_sales,
            key=lambda x: x.get("date", ""),
            reverse=True
        )
        
        for sale in sorted_sales:
            self.create_sale_item(sale)
    
    def create_sale_item(self, sale):
        """Cria um item de venda na lista"""
        sale_id = sale.get("id", 0)
        date_str = sale.get("date", "")
        timestamp_str = sale.get("timestamp", None)
        total = sale.get("total", 0.0)
        payment_method = sale.get("payment_method", "N/A")
        time_ago = format_time_ago(date_str, timestamp_str)
        
        # Frame do item
        item_frame = ctk.CTkFrame(
            self.sales_list_frame,
            corner_radius=10,
            fg_color=COLORS["bg_panel"],
            border_width=2,
            border_color=COLORS["bg_panel"]
        )
        item_frame.pack(fill="x", padx=5, pady=5)
        item_frame.grid_columnconfigure(1, weight=1)
        
        # Bind para seleção
        def select_sale(s):
            self.selected_sale = s
            # Atualizar visual de todos os itens
            for w in self.sales_widgets:
                w["frame"].configure(border_color=COLORS["bg_panel"])
            item_frame.configure(border_color=COLORS["green"])
            self.generate_btn.configure(state="normal")
        
        item_frame.bind("<Button-1>", lambda e, s=sale: select_sale(s))
        
        # ID da venda
        id_label = ctk.CTkLabel(
            item_frame,
            text=f"#{sale_id}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS["green"],
            width=50
        )
        id_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        id_label.bind("<Button-1>", lambda e, s=sale: select_sale(s))
        
        # Informações da venda
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=10)
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Data e tempo relativo - Converter para DD-MM-YYYY para exibição
        date_display = convert_yyyy_mm_dd_to_dd_mm_yyyy(date_str)
        date_label = ctk.CTkLabel(
            info_frame,
            text=f"{date_display} ({time_ago})",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS["text_light"],
            anchor="w"
        )
        date_label.grid(row=0, column=0, sticky="w", pady=(0, 5))
        date_label.bind("<Button-1>", lambda e, s=sale: select_sale(s))
        
        # Método de pagamento
        method_label = ctk.CTkLabel(
            info_frame,
            text=f"Método: {payment_method}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_gray"],
            anchor="w"
        )
        method_label.grid(row=1, column=0, sticky="w")
        method_label.bind("<Button-1>", lambda e, s=sale: select_sale(s))
        
        # Valor
        value_label = ctk.CTkLabel(
            item_frame,
            text=f"R$ {total:.2f}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["green"],
            width=120
        )
        value_label.grid(row=0, column=2, sticky="e", padx=10, pady=10)
        value_label.bind("<Button-1>", lambda e, s=sale: select_sale(s))
        
        # Armazenar referência
        self.sales_widgets.append({
            "frame": item_frame,
            "sale": sale
        })
    
    def apply_filters(self):
        """Aplica filtros de data"""
        date_start = self.date_start_entry.get().strip()
        date_end = self.date_end_entry.get().strip()
        
        filtered = self.sales_data.copy()
        
        if date_start:
            try:
                # Converter DD-MM-YYYY para YYYY-MM-DD para comparação
                date_start_yyyy = convert_dd_mm_yyyy_to_yyyy_mm_dd(date_start)
                datetime.strptime(date_start_yyyy, "%Y-%m-%d")
                filtered = [s for s in filtered if s.get("date", "") >= date_start_yyyy]
            except ValueError:
                pass
        
        if date_end:
            try:
                # Converter DD-MM-YYYY para YYYY-MM-DD para comparação
                date_end_yyyy = convert_dd_mm_yyyy_to_yyyy_mm_dd(date_end)
                datetime.strptime(date_end_yyyy, "%Y-%m-%d")
                filtered = [s for s in filtered if s.get("date", "") <= date_end_yyyy]
            except ValueError:
                pass
        
        self.filtered_sales = filtered
        self.display_sales()
        self.selected_sale = None
        self.generate_btn.configure(state="disabled")
    
    def clear_filters(self):
        """Limpa os filtros"""
        self.date_start_entry.delete(0, ctk.END)
        self.date_end_entry.delete(0, ctk.END)
        self.filtered_sales = self.sales_data.copy()
        self.display_sales()
        self.selected_sale = None
        self.generate_btn.configure(state="disabled")
    
    def generate_receipt(self):
        """Gera o comprovante da venda selecionada"""
        if not self.selected_sale:
            return
        
        # Solicitar local para salvar
        client_name_safe = self.client_name.replace("/", "-").replace("\\", "-")
        date_safe = self.selected_sale.get("date", "").replace("-", "")
        default_filename = f"comprovante_{client_name_safe}_{date_safe}_{self.selected_sale.get('id', '')}.pdf"
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=default_filename,
            title="Salvar Comprovante"
        )
        
        if not file_path:
            return
        
        try:
            from reports.receipt_generator import generate_receipt_pdf
            
            # Converter venda para formato de order
            order = {
                "timestamp": f"{self.selected_sale.get('date', '')} 00:00:00",
                "items": self.selected_sale.get("items", []),
                "total": self.selected_sale.get("total", 0.0),
                "payment_method": self.selected_sale.get("payment_method", "N/A")
            }
            
            # Usar dados completos do cliente se disponíveis
            generate_receipt_pdf(
                self.client_name,
                self.client_data,
                order,
                file_path,
                company_data=self.company_data
            )
            
            # Mostrar sucesso e abrir PDF
            from widgets.alert_dialog import AlertDialog
            dialog = AlertDialog(
                self,
                "Comprovante Gerado",
                f"Comprovante salvo com sucesso!\n\nLocal: {file_path}",
                "info",
                show_back_button=False,
                on_ok_callback=lambda: self.open_pdf(file_path)
            )
            self.wait_window(dialog)
            
            # Fechar diálogo após gerar
            self.cancel_action()
            
        except Exception as e:
            from widgets.alert_dialog import AlertDialog
            dialog = AlertDialog(
                self,
                "Erro",
                f"Erro ao gerar comprovante:\n{str(e)}",
                "error"
            )
            self.wait_window(dialog)
    
    def open_pdf(self, file_path):
        """Abre o PDF gerado"""
        import subprocess
        import platform
        import os
        
        try:
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
        except Exception as e:
            print(f"Erro ao abrir PDF: {e}")
    
    def cancel_action(self):
        """Cancela a operação"""
        self.selected_sale = None
        self.destroy()


class DatePickerDialog(ctk.CTkToplevel):
    """Diálogo para seleção de data"""
    
    def __init__(self, parent, entry_widget):
        super().__init__(parent)
        
        self.entry_widget = entry_widget
        self.selected_date = None
        
        self.title("Selecionar Data")
        self.resizable(False, False)
        self.geometry("350x400")
        
        # Configurar como modal
        self.transient(parent)
        self.grab_set()
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Obter data atual
        today = datetime.now()
        self.current_year = today.year
        self.current_month = today.month
        self.current_day = today.day
        
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_panel"], corner_radius=15)
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Controles de navegação (mês/ano)
        nav_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        prev_btn = ctk.CTkButton(
            nav_frame,
            text="◀",
            width=40,
            height=30,
            fg_color=COLORS["bg_dark"],
            hover_color="#333333",
            command=self.prev_month
        )
        prev_btn.pack(side="left")
        
        self.month_year_label = ctk.CTkLabel(
            nav_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_light"]
        )
        self.month_year_label.pack(side="left", expand=True)
        
        next_btn = ctk.CTkButton(
            nav_frame,
            text="▶",
            width=40,
            height=30,
            fg_color=COLORS["bg_dark"],
            hover_color="#333333",
            command=self.next_month
        )
        next_btn.pack(side="right")
        
        # Dias da semana
        weekdays_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        weekdays_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        weekdays = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]
        for day in weekdays:
            label = ctk.CTkLabel(
                weekdays_frame,
                text=day,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_gray"],
                width=40
            )
            label.pack(side="left", padx=2)
        
        # Frame do calendário
        self.calendar_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.calendar_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Botões de ação
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        cancel_btn = ctk.CTkButton(
            buttons_frame,
            text="Cancelar",
            width=100,
            height=35,
            fg_color=COLORS["bg_dark"],
            hover_color="#333333",
            command=self.destroy
        )
        cancel_btn.pack(side="left", padx=(0, 10), expand=True)
        
        today_btn = ctk.CTkButton(
            buttons_frame,
            text="Hoje",
            width=100,
            height=35,
            fg_color=COLORS["green"],
            hover_color="#26c463",
            command=self.select_today
        )
        today_btn.pack(side="right", expand=True)
        
        # Criar calendário
        self.update_calendar()
        
        # Centralizar
        self.after(100, self._center_on_screen)
    
    def _center_on_screen(self):
        """Centraliza a janela"""
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        dialog_width = self.winfo_width()
        dialog_height = self.winfo_height()
        
        x = (screen_width // 2) - (dialog_width // 2)
        y = (screen_height // 2) - (dialog_height // 2)
        
        self.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def update_calendar(self):
        """Atualiza o calendário"""
        # Limpar calendário anterior
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        # Atualizar label de mês/ano
        month_names = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                      "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.month_year_label.configure(
            text=f"{month_names[self.current_month - 1]} {self.current_year}"
        )
        
        # Obter primeiro dia do mês e número de dias
        first_day, num_days = calendar.monthrange(self.current_year, self.current_month)
        
        # Criar grid de dias (6 linhas x 7 colunas)
        today = datetime.now()
        
        # Preencher dias vazios do início
        row = 0
        col = first_day
        for _ in range(first_day):
            # Espaço vazio
            empty_label = ctk.CTkLabel(
                self.calendar_frame,
                text="",
                width=40,
                height=40
            )
            empty_label.grid(row=row, column=col, padx=2, pady=2)
            col += 1
        
        # Preencher dias do mês
        for day in range(1, num_days + 1):
            date_obj = datetime(self.current_year, self.current_month, day)
            is_today = (date_obj.date() == today.date())
            
            day_btn = ctk.CTkButton(
                self.calendar_frame,
                text=str(day),
                width=40,
                height=40,
                font=ctk.CTkFont(size=12, weight="bold" if is_today else "normal"),
                fg_color=COLORS["green"] if is_today else COLORS["bg_dark"],
                hover_color="#26c463" if is_today else "#333333",
                text_color=COLORS["bg_dark"] if is_today else COLORS["text_light"],
                command=lambda d=day: self.select_date(d)
            )
            day_btn.grid(row=row, column=col, padx=2, pady=2)
            
            col += 1
            if col >= 7:
                col = 0
                row += 1
    
    def prev_month(self):
        """Mês anterior"""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()
    
    def next_month(self):
        """Próximo mês"""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar()
    
    def select_date(self, day):
        """Seleciona uma data - Retorna no formato DD-MM-YYYY"""
        date_str = f"{day:02d}-{self.current_month:02d}-{self.current_year}"
        self.entry_widget.delete(0, ctk.END)
        self.entry_widget.insert(0, date_str)
        self.destroy()
    
    def select_today(self):
        """Seleciona a data de hoje - Retorna no formato DD-MM-YYYY"""
        today = datetime.now()
        date_str = today.strftime("%d-%m-%Y")
        self.entry_widget.delete(0, ctk.END)
        self.entry_widget.insert(0, date_str)
        self.destroy()
