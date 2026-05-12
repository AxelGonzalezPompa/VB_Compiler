import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import re
from compiler_engine import CompiladorProyecto
import sys
from virtual_machine import VirtualMachine
import ast
from assembly_generator import GeneradorEnsamblador

class ConsolaRedirigida:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        
    def write(self, mensaje):
        self.text_widget.config(state='normal')
        # Si el mensaje tiene ">>", es un Print de la VM (Naranja)
        if ">>" in mensaje:
            self.text_widget.insert(tk.END, mensaje, "VM_Out")
        # Si el mensaje dice "CRASH", es un error de la VM (Rojo)
        elif "CRASH" in mensaje or "Excepción" in mensaje:
            self.text_widget.insert(tk.END, mensaje, "ConsoleError")
        else:
            self.text_widget.insert(tk.END, mensaje, "ConsoleNormal")
            
        self.text_widget.see(tk.END)
        self.text_widget.config(state='disabled')
        
    def flush(self):
        pass

class IDEVisualBasic:
    def __init__(self, root):
        self.root = root
        self.root.title("IDE Visual Basic")
        self.root.geometry("900x650")

        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "icons", "icon.png")
        try:
            self.root.iconbitmap(icon_path)
        except tk.TclError:
            try:
                self.root.iconphoto(True, tk.PhotoImage(file=icon_path))
            except Exception as e:
                print(e)
        except Exception as e:
            print(e)

        self.root.configure(bg="#00332a")
        self.ruta_archivo_actual = None
        self.timer_sintaxis = None

        # Colores
        self.bg_color = "#004d40"
        self.text_fg = "white"
        self.line_num_bg = "#00332a"
        self.line_num_fg = "#80cbc4"

        # --- NUEVO: Contenedor redimensionable (PanedWindow) ---
        # sashwidth y sashrelief crean la barra separadora visible que puedes arrastrar
        self.paned_window = tk.PanedWindow(self.root, orient=tk.VERTICAL, sashwidth=8, sashrelief=tk.RAISED, bg="#00332a")
        self.paned_window.pack(expand=True, fill='both', padx=5, pady=5)

        # 1. Panel Superior: Frame Principal (Editor)
        self.editor_frame = tk.Frame(self.paned_window, bg="#00332a")
        self.paned_window.add(self.editor_frame, stretch="always")

        # Scrollbar del editor
        style = ttk.Style()
        style.theme_use('clam') # 'clam' permite modificar los colores nativos de Windows
        style.configure("Dark.Vertical.TScrollbar", 
                        background="#004d40",      # Color de la barra movible
                        troughcolor="#00211b",     # Color del fondo del carril
                        bordercolor="#00211b",     # Sin bordes blancos
                        arrowcolor="white",        # Flechas blancas
                        lightcolor="#004d40", 
                        darkcolor="#00332a")

        # Cambiamos tk.Scrollbar por ttk.Scrollbar y le aplicamos el estilo
        self.scrollbar = ttk.Scrollbar(self.editor_frame, style="Dark.Vertical.TScrollbar")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Widget de números de línea
        self.line_numbers = tk.Text(self.editor_frame, width=4, padx=5, takefocus=0, border=0,
                                    background=self.line_num_bg, foreground=self.line_num_fg,
                                    state='disabled', font=("Consolas", 12))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Area de texto principal
        self.text_area = tk.Text(self.editor_frame, bg=self.bg_color, fg=self.text_fg,
                                 insertbackground='white', font=("Consolas", 12), border=0,
                                 yscrollcommand=self.scrollbar.set, undo=True)
        self.text_area.pack(side=tk.LEFT, expand=True, fill='both')

        # Configurar scrollbar
        self.scrollbar.config(command=self.sync_scroll)

        # Configuración de colores (Tags) para Sintaxis
        self.text_area.tag_configure("Keyword", foreground="#81d4fa", font=("Consolas", 12, "bold"))  # Azul claro
        self.text_area.tag_configure("Type", foreground="#ce93d8", font=("Consolas", 12, "bold"))     # Morado claro
        self.text_area.tag_configure("Number", foreground="#ffb74d")                                  # Naranja
        self.text_area.tag_configure("String", foreground="#a5d6a7")                                  # Verde claro
        self.text_area.tag_configure("Boolean", foreground="#ffcc80", font=("Consolas", 12, "italic"))# Naranja claro (Cursiva)
        self.text_area.tag_configure("ErrorLine", background="#7f0000")
        self.text_area.tag_configure("Comment", foreground="#9e9e9e", font=("Consolas", 12, "italic")) # Color Gris

        # Bindings para actualizar números
        self.text_area.bind('<KeyRelease>', self.actualizar_numeros_linea)
        self.text_area.bind('<MouseWheel>', self.sync_scroll_wheel)
        self.text_area.bind('<Button-1>', self.actualizar_numeros_linea)
        
        # Binding para Tabulador, Auto-Indentación y Borrado Inteligent
        self.text_area.bind('<Tab>', self.insertar_tab)
        self.text_area.bind('<Return>', self.auto_indent)
        self.text_area.bind('<BackSpace>', self.borrar_indentacion)
        
        # 2. Panel Inferior: Output/Consola
        # Cambiamos el fondo a un verde mucho más oscuro (#00211b), agregamos padding (padx, pady) y quitamos el borde
        self.output_area = tk.Text(self.paned_window, height=8, bg="#00211b", fg="#e0e0e0",
                                   insertbackground='white', font=("Consolas", 11), 
                                   padx=15, pady=10, borderwidth=0)
        self.paned_window.add(self.output_area, stretch="never") 

        # Etiquetas de color para la Consola
        self.output_area.tag_configure("ConsoleHeader", foreground="#81d4fa", font=("Consolas", 11, "bold")) # Azul Claro
        self.output_area.tag_configure("ConsoleNormal", foreground="#e0e0e0")                                # Blanco opaco
        self.output_area.tag_configure("ConsoleSuccess", foreground="#a5d6a7")                               # Verde
        self.output_area.tag_configure("ConsoleError", foreground="#ef9a9a", font=("Consolas", 11, "bold"))  # Rojo
        self.output_area.tag_configure("ConsoleInfo", foreground="#ce93d8")                                  # Morado
        self.output_area.tag_configure("VM_Out", foreground="#ffcc80", font=("Consolas", 12, "bold"))        # Naranja resaltado
        
        self.output_area.insert('1.0', "⚡ Terminal lista. Esperando ejecución...\n", "ConsoleInfo")
        self.output_area.config(state='disabled')

        # Etiquetas avanzadas para Lexer
        self.output_area.tag_configure("LexPunct", foreground="#546e7a") # Gris oscuro para los < >
        self.output_area.tag_configure("LexType", foreground="#ce93d8", font=("Consolas", 11, "bold")) # Morado para el tipo
        self.output_area.tag_configure("LexValue", foreground="#a5d6a7") # Verde para el valor del token

        # Etiquetas avanzadas para Cuádruplos
        self.output_area.tag_configure("QuadIndex", foreground="#78909c") # Gris azulado
        self.output_area.tag_configure("QuadPunct", foreground="#546e7a") # Gris oscuro
        self.output_area.tag_configure("QuadOp", foreground="#f48fb1", font=("Consolas", 11, "bold")) # Rosa
        self.output_area.tag_configure("QuadArg", foreground="#c5e1a5") # Verde claro
        self.output_area.tag_configure("QuadRes", foreground="#81d4fa", font=("Consolas", 11, "bold")) # Azul claro
        
        # Equites avanzadas para Tabla de Simbolos
        self.output_area.tag_configure("SymLabel", foreground="#78909c") # Gris
        self.output_area.tag_configure("SymName", foreground="#ffcc80", font=("Consolas", 11, "bold")) # Naranja
        self.output_area.tag_configure("SymScope", foreground="#b39ddb", font=("Consolas", 11, "italic")) # Morado
        self.output_area.tag_configure("SymDict", foreground="#e0e0e0") # Blanco

        # Colores para el diccionario
        self.output_area.tag_configure("SymPunct", foreground="#546e7a")       # Gris oscuro para { } : ,
        self.output_area.tag_configure("SymKey", foreground="#81d4fa")         # Azul claro para las llaves ('tipo')
        self.output_area.tag_configure("SymValueStr", foreground="#a5d6a7")    # Verde para texto ('Integer')
        self.output_area.tag_configure("SymValueNum", foreground="#ffb74d")    # Naranja para números (1000)
        self.output_area.tag_configure("SymValueBool", foreground="#f48fb1", font=("Consolas", 11, "italic")) # Rosa cursiva para True/False

        # Etiquetas avanzadas para Ensamblador
        self.output_area.tag_configure("AsmComment", foreground="#9e9e9e", font=("Consolas", 11, "italic")) # Gris
        self.output_area.tag_configure("AsmLabel", foreground="#ffd54f", font=("Consolas", 11, "bold"))     # Amarillo
        self.output_area.tag_configure("AsmDirective", foreground="#ce93d8", font=("Consolas", 11, "bold")) # Morado
        self.output_area.tag_configure("AsmInstruction", foreground="#81d4fa", font=("Consolas", 11, "bold")) # Azul Claro
        self.output_area.tag_configure("AsmRegister", foreground="#ef9a9a")                                 # Rojo pastel
        self.output_area.tag_configure("AsmNumber", foreground="#ffb74d")                                   # Naranja
        self.output_area.tag_configure("AsmString", foreground="#a5d6a7")

        # Menus
        self.crear_menus()
        
        # Inicializar números
        self.actualizar_numeros_linea()

        # Bindings (atajos de teclado)
        self.root.bind('<Control-a>', lambda event: self.abrir_archivo())
        self.root.bind('<Control-g>', lambda event: self.guardar_archivo())
        self.root.bind('<Control-G>', lambda event: self.guardar_como())
        self.root.bind('<Control-q>', lambda event: self.cerrar_app())
        self.root.bind('<F5>', lambda event: self.ejecutar_compilador()) # Atajo para compilar

    # --- Lógica de números de línea ---
    def actualizar_numeros_linea(self, event=None):
        lines = self.text_area.get('1.0', tk.END).split('\n')
        line_count = len(lines)
        if lines[-1] == '': line_count -= 1 
        
        line_numbers_string = "\n".join(str(i) for i in range(1, line_count + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_numbers_string)
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.text_area.yview()[0])
        # Cancelamos el coloreado anterior si el usuario sigue escribiendo
        if self.timer_sintaxis is not None:
            self.root.after_cancel(self.timer_sintaxis)
        # Programamos el coloreado para que ocurra 300ms después de que deje de escribir
        self.timer_sintaxis = self.root.after(300, self.resaltar_sintaxis)
    
    def resaltar_sintaxis(self):
        # 1. Limpiamos los colores actuales
        for tag in ["Keyword", "Type", "Number", "String", "Boolean", "ErrorLine", "Comment"]:
            self.text_area.tag_remove(tag, "1.0", tk.END)

        # 2. STRINGS Y CHARS
        # Regex estricto para Chars: solo admite exactamente 1 carácter entre comillas simples
        self.aplicar_tag_color(r"'[^']'", "String") 
        self.aplicar_tag_color(r"\"[^\"]*\"", "String")

        # 3. COMENTARIOS
        self.aplicar_tag_color(r"'.*", "Comment", ignorar_tags=["String"])

        # 4. Palabras Clave
        keywords = ["Imports", "Module", "Sub", "Main", "End", 
                    "Dim", "As", "Print", "If", "Then", "Select", 
                    "Case", "Is", "To", "Else", "For", "Next",
                    "Step", "While", "Function", "Return"]
        
        # ¡ESTE ES EL BUCLE QUE FALTABA!
        for word in keywords:
            self.aplicar_tag_color(f"\\m{word}\\M", "Keyword", ignorar_tags=["String", "Comment"])

        # 5. Tipos de Datos
        tipos = ["Integer", "Double", "String", "Boolean", "Char"]
        for tipo in tipos:
            self.aplicar_tag_color(f"\\m{tipo}\\M", "Type", ignorar_tags=["String", "Comment"])

        # 6. Valores Booleanos
        for booleano in ["True", "False"]:
            self.aplicar_tag_color(f"\\m{booleano}\\M", "Boolean", ignorar_tags=["String", "Comment"])

        # 7. Números
        self.aplicar_tag_color(r"\m\d+\M", "Number", ignorar_tags=["String", "Comment"])

    def aplicar_tag_color(self, patron, tag, ignorar_tags=None):
        """Busca un patrón Regex en el texto y le aplica el Tag correspondiente"""
        pos = "1.0"
        count_var = tk.StringVar()
        
        while True:
            # nocase=True permite que Visual Basic sea case-insensitive (Dim se colorea igual que dim o DIM)
            pos = self.text_area.search(patron, pos, stopindex=tk.END, count=count_var, regexp=True, nocase=True)
            if not pos:
                break
            
            longitud = count_var.get()
            if not longitud or int(longitud) == 0:
                break
                
            fin_pos = f"{pos}+{longitud}c"
            
            if ignorar_tags:
                # Obtenemos los tags que ya tiene el primer carácter encontrado
                tags_actuales = self.text_area.tag_names(pos)
                # Si coincide con alguno de los que queremos ignorar, lo saltamos
                if any(t in tags_actuales for t in ignorar_tags):
                    pos = fin_pos
                    continue

            self.text_area.tag_add(tag, pos, fin_pos)
            pos = fin_pos
    
    def resaltar_errores(self, lista_errores):
        # 1. Limpiamos cualquier error resaltado previamente
        self.text_area.tag_remove("ErrorLine", "1.0", tk.END)
        
        # 2. Iteramos sobre cada mensaje de error
        for error in lista_errores:
            # Buscamos el patrón "Linea X:"
            match = re.search(r"Linea (\d+):", error)
            if match:
                linea = match.group(1)
                # Pintamos desde el inicio de esa línea (.0) hasta el final (.end)
                self.text_area.tag_add("ErrorLine", f"{linea}.0", f"{linea}.end")

    def insertar_tab(self, event):
        # Inserta exactamente 4 espacios en lugar de una tabulación (\t)
        self.text_area.insert(tk.INSERT, "    ")
        # El 'break' le dice a Tkinter que anule su comportamiento por defecto
        return 'break'

    def auto_indent(self, event):
        # 1. Obtener la posición actual del cursor (línea y columna)
        posicion_cursor = self.text_area.index(tk.INSERT)
        linea_actual = posicion_cursor.split(".")[0]
        
        # 2. Obtener todo el texto de la línea actual
        texto_linea = self.text_area.get(f"{linea_actual}.0", f"{linea_actual}.end")
        
        # 3. Extraer los espacios o tabulaciones al inicio de la línea
        indentacion = ""
        for char in texto_linea:
            if char in [' ', '\t']:
                indentacion += char
            else:
                break # Nos detenemos al encontrar el primer carácter que no sea espacio
                
        # 4. Insertar un salto de línea seguido de la indentación capturada
        self.text_area.insert(tk.INSERT, "\n" + indentacion)
        
        # 5. Actualizar la barra lateral de números y mantener el cursor a la vista
        self.actualizar_numeros_linea()
        self.text_area.see(tk.INSERT)
        
        # 6. MUY IMPORTANTE: Retornar 'break' anula el Enter por defecto de Tkinter
        # Esto evita que Tkinter inserte un segundo salto de línea no deseado.
        return 'break'
    
    def borrar_indentacion(self, event):
        # 1. Obtener la posición actual
        posicion_cursor = self.text_area.index(tk.INSERT)
        linea, columna = posicion_cursor.split(".")
        columna = int(columna)

        # Si estamos al principio de la línea, dejamos que Tkinter haga su trabajo normal (unir líneas)
        if columna == 0:
            return 

        # 2. Extraer todo el texto a la izquierda del cursor en esa línea
        texto_previo = self.text_area.get(f"{linea}.0", posicion_cursor)

        # 3. Detectar si TODO a la izquierda son solo espacios
        if texto_previo.strip() == "":
            # Matemática para encajar en el múltiplo de 4 más cercano
            espacios_a_borrar = columna % 4
            
            # Si ya estamos en un múltiplo exacto (ej. 4, 8, 12), borramos el bloque completo de 4
            if espacios_a_borrar == 0:
                espacios_a_borrar = 4

            # Borrar exactamente esa cantidad de espacios hacia atrás
            inicio_borrado = f"{linea}.{columna - espacios_a_borrar}"
            self.text_area.delete(inicio_borrado, posicion_cursor)
            
            # Refrescar UI y anular el Backspace normal de Tkinter
            self.actualizar_numeros_linea()
            return 'break'
            
        # Si hay texto normal, no hacemos nada y dejamos que borre letra por letra
        return

    def sync_scroll(self, *args):
        self.text_area.yview(*args)
        self.line_numbers.yview(*args)

    def sync_scroll_wheel(self, event):
        self.text_area.yview_scroll(int(-1*(event.delta/120)), "units")
        self.line_numbers.yview_scroll(int(-1*(event.delta/120)), "units")
        return "break"

    # --- Lógica de menús ---
    def crear_menus(self):
        # 1. Crear el Frame que simulará la barra de menús
        self.barra_menu = tk.Frame(self.root, bg="#00211b")
        # Lo empaquetamos ANTES del paned_window para que quede hasta arriba
        self.barra_menu.pack(side=tk.TOP, fill=tk.X, before=self.paned_window)

        # 2. Estilos para los botones de la barra y los submenús
        estilo_btn = {
            "bg": "#00211b", "fg": "#e0e0e0",
            "activebackground": "#004d40", "activeforeground": "white",
            "bd": 0, "padx": 10, "pady": 4, "font": ("Segoe UI", 10)
        }
        estilo_submenu = {
            "bg": "#00211b", "fg": "#e0e0e0",
            "activebackground": "#004d40", "activeforeground": "white",
            "bd": 0, "relief": "flat", "font": ("Segoe UI", 10)
        }

        # --- Menú Archivo ---
        btn_archivo = tk.Menubutton(self.barra_menu, text="Archivo", **estilo_btn)
        btn_archivo.pack(side=tk.LEFT)
        archivo_menu = tk.Menu(btn_archivo, tearoff=0, **estilo_submenu)
        btn_archivo.config(menu=archivo_menu)
        
        archivo_menu.add_command(label="Abrir (Ctrl+A)", command=self.abrir_archivo)
        archivo_menu.add_command(label="Guardar (Ctrl+G)", command=self.guardar_archivo)
        archivo_menu.add_command(label="Guardar Como (Ctrl+Shift+G)", command=self.guardar_como)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Limpiar Pantalla", command=lambda: self.text_area.delete('1.0', tk.END))
        archivo_menu.add_command(label="Cerrar (Ctrl+Q)", command=self.cerrar_app)

        # --- Menú Editar ---
        btn_editar = tk.Menubutton(self.barra_menu, text="Editar", **estilo_btn)
        btn_editar.pack(side=tk.LEFT)
        editar_menu = tk.Menu(btn_editar, tearoff=0, **estilo_submenu)
        btn_editar.config(menu=editar_menu)

        editar_menu.add_command(label="Deshacer (Ctrl+Z)", command=self.text_area.edit_undo)
        editar_menu.add_command(label="Rehacer (Ctrl+Y)", command=self.text_area.edit_redo)
        editar_menu.add_separator()
        editar_menu.add_command(label="Cortar (Ctrl+X)", command=lambda: self.text_area.event_generate("<<Cut>>"))
        editar_menu.add_command(label="Copiar (Ctrl+C)", command=lambda: self.text_area.event_generate("<<Copy>>"))
        editar_menu.add_command(label="Pegar (Ctrl+V)", command=lambda: self.text_area.event_generate("<<Paste>>"))
        editar_menu.add_separator()
        editar_menu.add_command(label="Seleccionar todo", command=self.seleccionar_todo)

        # --- Menú Ejecutar ---
        btn_ejecutar = tk.Menubutton(self.barra_menu, text="Ejecutar", **estilo_btn)
        btn_ejecutar.pack(side=tk.LEFT)
        ejecutar_menu = tk.Menu(btn_ejecutar, tearoff=0, **estilo_submenu)
        btn_ejecutar.config(menu=ejecutar_menu)

        ejecutar_menu.add_command(label="Iniciar Depuración", command=lambda: self.log_salida("Iniciando depuración..."))
        ejecutar_menu.add_command(label="Ejecutar sin Depuración (Ctrl+F5)", command=self.ejecutar_programa)
        ejecutar_menu.add_separator()
        ejecutar_menu.add_command(label="Detener Ejecución", command=lambda: self.log_salida("Ejecución detenida."))

        # --- Menú Compiladores ---
        btn_compiladores = tk.Menubutton(self.barra_menu, text="Compiladores", **estilo_btn)
        btn_compiladores.pack(side=tk.LEFT)
        compiladores_menu = tk.Menu(btn_compiladores, tearoff=0, **estilo_submenu)
        btn_compiladores.config(menu=compiladores_menu)
        
        compiladores_menu.add_command(label="Análisis Léxico", command=self.ejecutar_lexico)
        compiladores_menu.add_command(label="Análisis Sintáctico", command=self.ejecutar_sintactico)
        compiladores_menu.add_command(label="Análisis Semántico", command=self.ejecutar_semantico)
        compiladores_menu.add_command(label="Generar Cuádruplos", command=self.mostrar_cuadruplos)
        compiladores_menu.add_command(label="Generar Tabla de Símbolos", command=self.mostrar_tabla_simbolos)
        compiladores_menu.add_command(label="Generar Ensamblador (.asm)", command=self.generar_ensamblador)
        compiladores_menu.add_separator()
        compiladores_menu.add_command(label="Compilación Completa (F5)", command=self.ejecutar_compilador)

        # --- Menú Ayuda ---
        btn_ayuda = tk.Menubutton(self.barra_menu, text="Ayuda", **estilo_btn)
        btn_ayuda.pack(side=tk.LEFT)
        ayuda_menu = tk.Menu(btn_ayuda, tearoff=0, **estilo_submenu)
        btn_ayuda.config(menu=ayuda_menu)

        imports_menu = tk.Menu(ayuda_menu, tearoff=0, **estilo_submenu)
        ayuda_menu.add_cascade(label="Imports", menu=imports_menu)
        
        vb_libs = ["System", "System.IO", "System.Math", "System.Windows.Forms", "Microsoft.VisualBasic"]
        for lib in vb_libs:
            imports_menu.add_command(label=lib, command=lambda l=lib: self.insertar_imports(l))

        ayuda_menu.add_command(label="Estructura Main", command=self.insertar_main_vb)
        ayuda_menu.add_command(label="Acerca de...", command=self.mostrar_info_acerca_de)

        # --- Menú Variables ---
        btn_variables = tk.Menubutton(self.barra_menu, text="Variables", **estilo_btn)
        btn_variables.pack(side=tk.LEFT)
        variables_menu = tk.Menu(btn_variables, tearoff=0, **estilo_submenu)
        btn_variables.config(menu=variables_menu)
        
        tipos_menu = tk.Menu(variables_menu, tearoff=0, **estilo_submenu)
        variables_menu.add_cascade(label="Tipos", menu=tipos_menu)
        
        tipos_menu.add_command(label="Integer", command=lambda: self.insertar_tipo_vb("Integer", "System"))
        tipos_menu.add_command(label="Double", command=lambda: self.insertar_tipo_vb("Double", "System"))
        tipos_menu.add_command(label="String", command=lambda: self.insertar_tipo_vb("String", "System"))
        tipos_menu.add_command(label="Boolean", command=lambda: self.insertar_tipo_vb("Boolean", "System"))

    # --- Funciones de utilidad (Editor, Imports, etc.) ---
    def abrir_archivo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos Visual Basic", "*.vb"), ("Todos", "*.*")])
        if file_path:
            with open(file_path, 'r') as file:
                self.text_area.delete('1.0', tk.END)
                self.text_area.insert('1.0', file.read())
            
            self.ruta_archivo_actual = file_path
            self.root.title(f"IDE Visual Basic - {file_path}")
            self.log_salida(f"Archivo abierto: {file_path}")
            self.actualizar_numeros_linea()

    def guardar_archivo(self):
        # Si ya hay una ruta guardada en memoria, sobrescribe directamente
        if self.ruta_archivo_actual:
            with open(self.ruta_archivo_actual, 'w') as file:
                file.write(self.text_area.get('1.0', tk.END))
            self.log_salida(f"Archivo guardado: {self.ruta_archivo_actual}")
        # Si es un archivo nuevo y no tiene ruta, llama a Guardar Como
        else:
            self.guardar_como()

    def guardar_como(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".vb", filetypes=[("Archivos Visual Basic", "*.vb")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.text_area.get('1.0', tk.END))
            
            self.ruta_archivo_actual = file_path # Actualizamos la ruta en memoria
            self.root.title(f"IDE Visual Basic - {file_path}") # Opcional: Mostrar ruta en el título
            self.log_salida(f"Archivo guardado como: {file_path}")
    
    def seleccionar_todo(self):
        self.text_area.tag_add(tk.SEL, "1.0", tk.END)
        self.text_area.mark_set(tk.INSERT, "1.0")
        self.text_area.see(tk.INSERT)
        return 'break'
    
    def cerrar_app(self):
        if messagebox.askokcancel("Salir", "¿Desea cerrar la aplicación?"):
            self.root.quit()

    def insertar_imports(self, imports):
        self.text_area.insert('1.0', f"Imports {imports}\n")
        self.actualizar_numeros_linea()

    def insertar_main_vb(self):
        codigo = "\nModule Module1\n    Sub Main()\n        Console.WriteLine(\"Hola Mundo\")\n    End Sub\nEnd Module"
        self.text_area.insert(tk.INSERT, codigo)
        self.actualizar_numeros_linea()

    def insertar_tipo_vb(self, tipo, import_requerido):
        self.text_area.insert(tk.INSERT, f"Dim variable As {tipo} ")
        contenido = self.text_area.get('1.0', tk.END)
        if f"Imports {import_requerido}" not in contenido:
            self.text_area.insert('1.0', f"Imports {import_requerido}\n")
            self.log_salida(f"Agregado 'Imports {import_requerido}' para {tipo}.")
        self.text_area.focus()
        self.actualizar_numeros_linea()

    def log_salida(self, mensaje):
        self.output_area.config(state='normal')
        self.output_area.insert(tk.END, f">> {mensaje}\n", "ConsoleInfo")
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def preparar_consola(self, titulo):
        self.output_area.config(state='normal')
        self.output_area.delete('1.0', tk.END)
        self.output_area.insert(tk.END, f"❖ {titulo} ❖\n", "ConsoleHeader")
        self.output_area.insert(tk.END, "═" * 60 + "\n\n", "ConsoleHeader")

    def finalizar_consola(self):
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def ejecutar_lexico(self):
        self.preparar_consola("ANÁLISIS LÉXICO")
        compilador = CompiladorProyecto(self.text_area.get('1.0', tk.END))
        tokens = compilador.obtener_tokens_vertical()
        
        if tokens:
            for t in tokens:
                # Quitamos los símbolos < > de los extremos y separamos por la coma
                if t.startswith("<") and t.endswith(">"):
                    contenido = t[1:-1]
                    if ", " in contenido:
                        tipo_token, valor_token = contenido.split(", ", 1)
                        
                        self.output_area.insert(tk.END, "<", "LexPunct")
                        self.output_area.insert(tk.END, f"{tipo_token}", "LexType")
                        self.output_area.insert(tk.END, ", ", "LexPunct")
                        self.output_area.insert(tk.END, f"{valor_token}", "LexValue")
                        self.output_area.insert(tk.END, ">\n", "LexPunct")
                    else:
                        self.output_area.insert(tk.END, f"{t}\n", "ConsoleNormal")
                else:
                    self.output_area.insert(tk.END, f"{t}\n", "ConsoleNormal")
        else:
            self.output_area.insert(tk.END, "No se encontraron tokens.\n", "ConsoleError")
            
        self.finalizar_consola()

    def ejecutar_sintactico(self):
        self.preparar_consola("ANÁLISIS SINTÁCTICO")
        compilador = CompiladorProyecto(self.text_area.get('1.0', tk.END))
        errores = compilador.filtrar_warnings(["missing", "unexpected", "instruction", "scope", "parenthesis", "unclosed", "incomplete"])
        
        if errores:
            for error in errores:
                self.output_area.insert(tk.END, f">> {error}\n", "ConsoleError")
        else:
            self.output_area.insert(tk.END, "✓ Sintaxis correcta.\n", "ConsoleSuccess")
            
        self.resaltar_errores(errores)
        self.finalizar_consola()

    def ejecutar_semantico(self):
        self.preparar_consola("ANÁLISIS SEMÁNTICO")
        compilador = CompiladorProyecto(self.text_area.get('1.0', tk.END))
        errores = compilador.filtrar_warnings(["type", "undefine", "ambiguity", "variable", "invalid", "mismatch"])
        
        if errores:
            for error in errores:
                self.output_area.insert(tk.END, f">> {error}\n", "ConsoleError")
        else:
            self.output_area.insert(tk.END, "✓ Semántica correcta.\n", "ConsoleSuccess")
            
        self.resaltar_errores(errores)
        self.finalizar_consola()

    def mostrar_tabla_simbolos(self):
        self.preparar_consola("TABLA DE SÍMBOLOS")
        compilador = CompiladorProyecto(self.text_area.get('1.0', tk.END))
        compilador.analizar_todo()
        tabla = compilador.obtener_formato_tabla()
        
        if tabla:
            for linea in tabla:
                if linea.strip():
                    if " -> " in linea:
                        izq, der = linea.split(" -> ", 1)
                        texto_izq = izq.replace("ID: ", "")
                        nombre = texto_izq
                        scope = ""
                        if " (" in texto_izq:
                            nombre, scope = texto_izq.split(" (", 1)
                            scope = " (" + scope
                        
                        self.output_area.insert(tk.END, "ID: ", "SymLabel")
                        self.output_area.insert(tk.END, f"{nombre}", "SymName")
                        if scope:
                            self.output_area.insert(tk.END, f"{scope}", "SymScope")
                        self.output_area.insert(tk.END, " -> ", "SymLabel")
                        # Coloreado de diccionario
                        try:
                            # Convertimos el string de texto a un diccionario de verdad
                            diccionario = ast.literal_eval(der)
                            self.output_area.insert(tk.END, "{", "SymPunct")
                            
                            items = list(diccionario.items())
                            for idx, (k, v) in enumerate(items):
                                # Pintar la Llave
                                self.output_area.insert(tk.END, f"'{k}'", "SymKey")
                                self.output_area.insert(tk.END, ": ", "SymPunct")
                                
                                # Pintar el Valor dependiendo de su tipo
                                if isinstance(v, str):
                                    self.output_area.insert(tk.END, f"'{v}'", "SymValueStr")
                                elif isinstance(v, bool): # Es importante poner bool antes que int en Python
                                    self.output_area.insert(tk.END, str(v), "SymValueBool")
                                elif isinstance(v, (int, float)):
                                    self.output_area.insert(tk.END, str(v), "SymValueNum")
                                else:
                                    # Para listas y otras estructuras complejas
                                    self.output_area.insert(tk.END, repr(v), "SymDict")
                                
                                # Coma separadora (excepto en el último elemento)
                                if idx < len(items) - 1:
                                    self.output_area.insert(tk.END, ", ", "SymPunct")
                                    
                            self.output_area.insert(tk.END, "}\n", "SymPunct")
                        except Exception:
                            # Si por alguna razón falla el parseo, se imprime blanco como antes
                            self.output_area.insert(tk.END, f"{der}\n", "SymDict")
                    else:
                        self.output_area.insert(tk.END, f"{linea}\n", "ConsoleInfo")
        else:
            self.output_area.insert(tk.END, "Tabla vacía.\n", "ConsoleNormal")
            
        self.finalizar_consola()

    def mostrar_cuadruplos(self):
        self.preparar_consola("CÓDIGO INTERMEDIO (CUÁDRUPLOS)")
        codigo_fuente = self.text_area.get('1.0', tk.END)
        compilador = CompiladorProyecto(codigo_fuente)
        compilador.analizar_todo() 
        
        cuadruplos = compilador.cuadruplos
        
        if cuadruplos:
            for i, cuad in enumerate(cuadruplos):
                self.output_area.insert(tk.END, f"{i}: ", "QuadIndex")
                self.output_area.insert(tk.END, "(", "QuadPunct")
                self.output_area.insert(tk.END, f"'{cuad[0]}'", "QuadOp")
                self.output_area.insert(tk.END, ", ", "QuadPunct")
                self.output_area.insert(tk.END, f"'{cuad[1]}'", "QuadArg")
                self.output_area.insert(tk.END, ", ", "QuadPunct")
                self.output_area.insert(tk.END, f"'{cuad[2]}'", "QuadArg")
                self.output_area.insert(tk.END, ", ", "QuadPunct")
                self.output_area.insert(tk.END, f"'{cuad[3]}'", "QuadRes")
                self.output_area.insert(tk.END, ")\n", "QuadPunct")
        else:
            self.output_area.insert(tk.END, "No se generaron cuádruplos (revisa errores sintácticos).\n", "ConsoleError")
            
        self.finalizar_consola()

    def ejecutar_compilador(self):
        codigo_fuente = self.text_area.get('1.0', tk.END)
        compilador = CompiladorProyecto(codigo_fuente)
        resultados = compilador.compilar()
        
        self.output_area.config(state='normal')
        self.output_area.delete('1.0', tk.END)
        
        # Función auxiliar para imprimir encabezados con el diamante
        def imprimir_encabezado(titulo):
            self.output_area.insert(tk.END, f"\n◆ {titulo} ◆\n", "ConsoleHeader")
            self.output_area.insert(tk.END, "═" * 40 + "\n", "ConsoleHeader")

        # --- APARTADO LÉXICO ---
        imprimir_encabezado("ANÁLISIS LÉXICO")
        if resultados["lexico"]:
            for t in resultados["lexico"]:
                if t.startswith("<") and t.endswith(">"):
                    contenido = t[1:-1]
                    if ", " in contenido:
                        tipo_token, valor_token = contenido.split(", ", 1)
                        
                        self.output_area.insert(tk.END, "<", "LexPunct")
                        self.output_area.insert(tk.END, f"{tipo_token}", "LexType")
                        self.output_area.insert(tk.END, ", ", "LexPunct")
                        self.output_area.insert(tk.END, f"{valor_token}", "LexValue")
                        self.output_area.insert(tk.END, ">\n", "LexPunct")
                    else:
                        self.output_area.insert(tk.END, f"{t}\n", "ConsoleNormal")
                else:
                    self.output_area.insert(tk.END, f"{t}\n", "ConsoleNormal")

        # --- APARTADO SINTÁCTICO ---
        imprimir_encabezado("ANÁLISIS SINTÁCTICO")
        if resultados["sintactico"]:
            for res in resultados["sintactico"]: self.output_area.insert(tk.END, f">> {res}\n", "ConsoleError")
        else: 
            self.output_area.insert(tk.END, "✓ Sin errores sintácticos.\n", "ConsoleSuccess")

        # --- APARTADO SEMÁNTICO ---
        imprimir_encabezado("ANÁLISIS SEMÁNTICO")
        if resultados["semantico"]:
            for res in resultados["semantico"]: self.output_area.insert(tk.END, f">> {res}\n", "ConsoleError")
        else: 
            self.output_area.insert(tk.END, "✓ Sin errores semánticos.\n", "ConsoleSuccess")
        
        # --- APARTADO DE CUÁDRUPLOS (MULTICOLOR) ---
        imprimir_encabezado("CÓDIGO INTERMEDIO (CUÁDRUPLOS)")
        if "cuadruplos" in resultados and resultados["cuadruplos"]:
            for i, cuad in enumerate(resultados["cuadruplos"]):
                self.output_area.insert(tk.END, f"{i}: ", "QuadIndex")
                self.output_area.insert(tk.END, "(", "QuadPunct")
                self.output_area.insert(tk.END, f"'{cuad[0]}'", "QuadOp")
                self.output_area.insert(tk.END, ", ", "QuadPunct")
                self.output_area.insert(tk.END, f"'{cuad[1]}'", "QuadArg")
                self.output_area.insert(tk.END, ", ", "QuadPunct")
                self.output_area.insert(tk.END, f"'{cuad[2]}'", "QuadArg")
                self.output_area.insert(tk.END, ", ", "QuadPunct")
                self.output_area.insert(tk.END, f"'{cuad[3]}'", "QuadRes")
                self.output_area.insert(tk.END, ")\n", "QuadPunct")
        else:
            self.output_area.insert(tk.END, "Sin cuádruplos generados.\n", "ConsoleNormal")

        # --- TABLA DE SÍMBOLOS (MULTICOLOR) ---
        imprimir_encabezado("TABLA DE SÍMBOLOS")
        if resultados["tabla"]:
            for linea in resultados["tabla"]:
                if linea.strip():
                    if " -> " in linea:
                        izq, der = linea.split(" -> ", 1)
                        texto_izq = izq.replace("ID: ", "")
                        nombre = texto_izq
                        scope = ""
                        if " (" in texto_izq:
                            nombre, scope = texto_izq.split(" (", 1)
                            scope = " (" + scope
                        
                        self.output_area.insert(tk.END, "ID: ", "SymLabel")
                        self.output_area.insert(tk.END, f"{nombre}", "SymName")
                        if scope:
                            self.output_area.insert(tk.END, f"{scope}", "SymScope")
                        self.output_area.insert(tk.END, " -> ", "SymLabel")
                        # Coloreado de diccionario
                        try:
                            # Convertimos el string de texto a un diccionario de verdad
                            diccionario = ast.literal_eval(der)
                            self.output_area.insert(tk.END, "{", "SymPunct")
                            
                            items = list(diccionario.items())
                            for idx, (k, v) in enumerate(items):
                                # Pintar la Llave
                                self.output_area.insert(tk.END, f"'{k}'", "SymKey")
                                self.output_area.insert(tk.END, ": ", "SymPunct")
                                
                                # Pintar el Valor dependiendo de su tipo
                                if isinstance(v, str):
                                    self.output_area.insert(tk.END, f"'{v}'", "SymValueStr")
                                elif isinstance(v, bool): # Es importante poner bool antes que int en Python
                                    self.output_area.insert(tk.END, str(v), "SymValueBool")
                                elif isinstance(v, (int, float)):
                                    self.output_area.insert(tk.END, str(v), "SymValueNum")
                                else:
                                    # Para listas y otras estructuras complejas
                                    self.output_area.insert(tk.END, repr(v), "SymDict")
                                
                                # Coma separadora (excepto en el último elemento)
                                if idx < len(items) - 1:
                                    self.output_area.insert(tk.END, ", ", "SymPunct")
                                    
                            self.output_area.insert(tk.END, "}\n", "SymPunct")
                        except Exception:
                            # Si por alguna razón falla el parseo, se imprime blanco como antes
                            self.output_area.insert(tk.END, f"{der}\n", "SymDict")
                    else:
                        self.output_area.insert(tk.END, f"{linea}\n", "ConsoleInfo")

        errores_totales = resultados["sintactico"] + resultados["semantico"]
        self.resaltar_errores(errores_totales)

        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def ejecutar_programa(self):
        self.preparar_consola("EJECUCIÓN DEL PROGRAMA (MÁQUINA VIRTUAL)")
        
        # 1. Compilamos el código
        codigo_fuente = self.text_area.get('1.0', tk.END)
        compilador = CompiladorProyecto(codigo_fuente)
        compilador.analizar_todo()
        
        # 2. Verificamos que no haya errores semánticos o de sintaxis
        errores = compilador.filtrar_warnings(["missing", "unexpected", "type", "undefine", "mismatch"], auto_analizar=False)
        if errores:
            self.output_area.insert(tk.END, "\n[ERROR] No se puede ejecutar el programa. Corrige los errores de compilación primero.\n")
            self.finalizar_consola()
            return

        # 3. Redirigimos la salida de consola (prints) hacia nuestra caja de texto
        stdout_original = sys.stdout
        sys.stdout = ConsolaRedirigida(self.output_area)
        
        try:
            # 4. ¡Instanciamos y encendemos el procesador virtual!
            vm = VirtualMachine(compilador.cuadruplos, compilador.tabla)
            vm.ejecutar()
        except Exception as e:
            print(f"\nExcepción crítica del sistema: {e}")
        finally:
            # 5. Restauramos la consola original para no romper Python
            sys.stdout = stdout_original
            self.finalizar_consola()

    def imprimir_ensamblador_coloreado(self, codigo_asm):
        self.output_area.insert(tk.END, "\n--- CÓDIGO ENSAMBLADOR GENERADO ---\n", "ConsoleInfo")
        
        # Guardar la posición exacta donde empieza el código ensamblador
        start_pos = self.output_area.index(tk.INSERT)
        self.output_area.insert(tk.END, f"{codigo_asm}\n", "ConsoleNormal")
        
        # Función interna para pintar usando RegEx
        def aplicar_tag(patron, tag, ignorar=None):
            pos = start_pos
            count_var = tk.StringVar()
            while True:
                # Búsqueda Case-Insensitive usando el motor de Tkinter
                pos = self.output_area.search(patron, pos, stopindex=tk.END, count=count_var, regexp=True, nocase=True)
                if not pos: break
                
                longitud = count_var.get()
                if not longitud or int(longitud) == 0: break
                fin_pos = f"{pos}+{longitud}c"
                
                # Respetar si la palabra ya está dentro de un comentario o un string
                if ignorar:
                    tags_actuales = self.output_area.tag_names(pos)
                    if any(t in tags_actuales for t in ignorar):
                        pos = fin_pos
                        continue
                        
                self.output_area.tag_add(tag, pos, fin_pos)
                pos = fin_pos

        # 1. Comentarios y Strings (Se pintan primero para que sirvan de escudo)
        aplicar_tag(r"'.*?'", "AsmString")
        aplicar_tag(r'".*?"', "AsmString")
        aplicar_tag(r";.*", "AsmComment")
        
        # 2. Etiquetas (Ej: L1: o MAIN PROC)
        aplicar_tag(r"^[ \t]*[a-z0-9_]+:", "AsmLabel", ignorar=["AsmComment", "AsmString"])
        
        # 3. Directivas de Memoria y Secciones (\m y \M delimitan palabras enteras)
        directivas_con_punto = [r"\.model", r"\.stack", r"\.data", r"\.code"]
        for d in directivas_con_punto:
            aplicar_tag(rf"{d}\M", "AsmDirective", ignorar=["AsmComment", "AsmString"])
            
        directivas_normales = ["proc", "endp", "end", "db", "dw", "dup"]
        for d in directivas_normales:
            aplicar_tag(rf"\m{d}\M", "AsmDirective", ignorar=["AsmComment", "AsmString"])
            
        # 4. Instrucciones del CPU
        instrucciones = ["mov", "add", "sub", "cmp", "jmp", "je", "jne", "jg", "jl", "jle", "jge", 
                         "call", "ret", "int", "push", "pop", "lea", "shl", "xor", "div", "idiv", 
                         "imul", "cwd", "neg", "inc", "dec", "loop"]
        for i in instrucciones:
            aplicar_tag(rf"\m{i}\M", "AsmInstruction", ignorar=["AsmComment", "AsmString"])
            
        # 5. Registros de CPU
        registros = ["ax", "bx", "cx", "dx", "ah", "al", "bh", "bl", "ch", "cl", "dh", "dl", 
                     "ds", "cs", "ss", "es", "si", "di", "sp", "bp"]
        for r in registros:
            aplicar_tag(rf"\m{r}\M", "AsmRegister", ignorar=["AsmComment", "AsmString"])
            
        # 6. Números (Hexadecimales y Decimales, Ej: 10, 09h, 4Ch)
        aplicar_tag(r"\m\d+[a-f0-9]*h?\M", "AsmNumber", ignorar=["AsmComment", "AsmString", "AsmLabel"])

        self.output_area.insert(tk.END, "\n-----------------------------------\n", "ConsoleInfo")

    def generar_ensamblador(self):
        self.preparar_consola("GENERADOR DE ENSAMBLADOR x86")
        codigo_fuente = self.text_area.get('1.0', tk.END)
        compilador = CompiladorProyecto(codigo_fuente)
        compilador.analizar_todo()
        
        errores = compilador.filtrar_warnings(["missing", "unexpected", "type", "undefine"], auto_analizar=False)
        if errores:
            self.output_area.insert(tk.END, "Corrige los errores antes de generar ensamblador.\n", "ConsoleError")
            self.finalizar_consola()
            return

        # Instanciar el nuevo generador
        generador = GeneradorEnsamblador(compilador.cuadruplos, compilador.tabla)
        codigo_asm = generador.generar_x86()

        self.imprimir_ensamblador_coloreado(codigo_asm)
        
        # Pedirle al usuario dónde guardar el .asm
        file_path = filedialog.asksaveasfilename(defaultextension=".asm", filetypes=[("Archivos Ensamblador", "*.asm")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(codigo_asm)
            self.output_area.insert(tk.END, f"✓ Ensamblador guardado exitosamente en:\n{file_path}\n", "ConsoleSuccess")
        else:
            # Si el usuario cancela la ventana de guardado, le avisamos que de todos modos lo puede ver en consola
            self.output_area.insert(tk.END, "⚠ Archivo no guardado (visible solo en consola).\n", "ConsoleInfo")
        
        self.finalizar_consola()

    def mostrar_info_acerca_de(self):
        info = (
            "IDE Visual Basic\n"
            "Versión: v2.0 (Edición Completa)\n\n"
            
            "--- MOTOR DE COMPILACIÓN (FRONTEND) ---\n"
            "• Análisis modular completo: Léxico, Sintáctico y Semántico.\n"
            "• Tabla de Símbolos con direccionamiento y gestión dinámica de ámbitos.\n"
            "• Generador de Código Intermedio optimizado (Cuádruplos).\n"
            "• Recuperación de errores en Modo Pánico para evitar fallos en cascada.\n\n"

            "--- GENERACIÓN DE CÓDIGO (BACKEND) ---\n"
            "• Traducción a Lenguaje Ensamblador nativo (Arquitectura x86 16-bits).\n"
            "• Código objeto 100% compatible con el entorno MS-DOS (EMU8086).\n"
            "• Asignación automática de memoria estática (.DATA) para arreglos.\n"
            "• Inyección de librería estándar (Subrutinas I/O para consola).\n\n"
            
            "--- EXPERIENCIA DE USUARIO (UI/UX) ---\n"
            "• Resaltado de Sintaxis dinámico (Editor Visual Basic y Salida ASM).\n"
            "• Auto-indentación inteligente y borrado alineado a 4 espacios.\n"
            "• Máquina Virtual integrada para depuración y pruebas rápidas.\n\n"
            
            "Desarrollado para la materia de Compiladores (CUCEI)\n"
            "Por: Axel González Pompa."
        )
        messagebox.showinfo("Acerca de IDE Visual Basic", info)

if __name__ == "__main__":
    root = tk.Tk()
    app = IDEVisualBasic(root)
    root.mainloop()
