import tkinter as tk
from tkinter import messagebox, filedialog
import re
from compiler_engine import CompiladorProyecto

class IDEVisualBasic:
    def __init__(self, root):
        self.root = root
        self.root.title("IDE Visual Basic")
        self.root.geometry("900x650")
        self.root.iconbitmap("icons/icon.ico")
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
        self.editor_frame = tk.Frame(self.paned_window)
        # Añadimos el editor al panel. stretch="always" hace que el editor ocupe el espacio principal
        self.paned_window.add(self.editor_frame, stretch="always") 

        # Scrollbar del editor
        self.scrollbar = tk.Scrollbar(self.editor_frame)
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

        # Bindings para actualizar números
        self.text_area.bind('<KeyRelease>', self.actualizar_numeros_linea)
        self.text_area.bind('<MouseWheel>', self.sync_scroll_wheel)
        self.text_area.bind('<Button-1>', self.actualizar_numeros_linea)
        
        # Binding para Tabulador, Auto-Indentación y Borrado Inteligent
        self.text_area.bind('<Tab>', self.insertar_tab)
        self.text_area.bind('<Return>', self.auto_indent)
        self.text_area.bind('<BackSpace>', self.borrar_indentacion)
        
        # 2. Panel Inferior: Output/Consola
        self.output_area = tk.Text(self.paned_window, height=8, bg=self.bg_color, fg=self.text_fg,
                                   insertbackground='white', font=("Consolas", 10))
        # Añadimos la consola al panel. stretch="never" mantiene su tamaño inicial hasta que tú lo arrastres
        self.paned_window.add(self.output_area, stretch="never") 
        
        self.output_area.insert('1.0', "Listo. Esperando código VB...\n")
        self.output_area.config(state='disabled')

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
        for tag in ["Keyword", "Type", "Number", "String", "Boolean", "ErrorLine"]:
            self.text_area.tag_remove(tag, "1.0", tk.END)

        # 2. STRINGS PRIMERO (Fundamental para que las excepciones funcionen)
        self.aplicar_tag_color(r"\"[^\"]*\"", "String")
        self.aplicar_tag_color(r"'[^']*'", "String") 

        # 3. Palabras Clave
        keywords = ["Imports", "Module", "Sub", "Main", "End", 
                    "Dim", "As", "Print", "If", "Then", "Select", 
                    "Case", "Is", "To", "Else", "For", "Next",
                    "Step", "While"]
        
        for word in keywords:
            self.aplicar_tag_color(f"\\m{word}\\M", "Keyword", ignorar_tags=["String"])

        # 4. Tipos de Datos
        tipos = ["Integer", "Double", "String", "Boolean", "Char"]
        for tipo in tipos:
            self.aplicar_tag_color(f"\\m{tipo}\\M", "Type", ignorar_tags=["String"])

        # 5. Valores Booleanos
        for booleano in ["True", "False"]:
            self.aplicar_tag_color(f"\\m{booleano}\\M", "Boolean", ignorar_tags=["String"])

        # 6. Números
        self.aplicar_tag_color(r"\m\d+\M", "Number", ignorar_tags=["String"])

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
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú Archivo
        archivo_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=archivo_menu)
        archivo_menu.add_command(label="Abrir (Ctrl+A)", command=self.abrir_archivo)
        archivo_menu.add_command(label="Guardar (Ctrl+G)", command=self.guardar_archivo)
        archivo_menu.add_command(label="Guardar Como (Ctrl+Shift+G)", command=self.guardar_como)
        archivo_menu.add_separator()
        archivo_menu.add_command(label="Limpiar Pantalla", command=lambda: self.text_area.delete('1.0', tk.END))
        archivo_menu.add_command(label="Cerrar (Ctrl+Q)", command=self.cerrar_app)

        # Menú Editar
        editar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Editar", menu=editar_menu)
        editar_menu.add_command(label="Deshacer (Ctrl+Z)", command=self.text_area.edit_undo)
        editar_menu.add_command(label="Rehacer (Ctrl+Y)", command=self.text_area.edit_redo)
        editar_menu.add_separator()
        editar_menu.add_command(label="Cortar (Ctrl+X)", command=lambda: self.text_area.event_generate("<<Cut>>"))
        editar_menu.add_command(label="Copiar (Ctrl+C)", command=lambda: self.text_area.event_generate("<<Copy>>"))
        editar_menu.add_command(label="Pegar (Ctrl+V)", command=lambda: self.text_area.event_generate("<<Paste>>"))
        editar_menu.add_separator()
        editar_menu.add_command(label="Seleccionar todo", command=self.seleccionar_todo)

        # Menú Ejecutar
        ejecutar_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ejecutar", menu=ejecutar_menu)
        ejecutar_menu.add_command(label="Iniciar Depuración", command=lambda: self.log_salida("Iniciando depuración..."))
        ejecutar_menu.add_command(label="Ejecutar sin Depuración (Ctrl+F5)", command=lambda: self.log_salida("Ejecutando programa..."))
        ejecutar_menu.add_separator()
        ejecutar_menu.add_command(label="Detener Ejecución", command=lambda: self.log_salida("Ejecución detenida."))

        # Menú Compiladores
        compiladores_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Compiladores", menu=compiladores_menu)
        
        compiladores_menu.add_command(label="Análisis Léxico", command=self.ejecutar_lexico)
        compiladores_menu.add_command(label="Análisis Sintáctico", command=self.ejecutar_sintactico)
        compiladores_menu.add_command(label="Análisis Semántico", command=self.ejecutar_semantico)
        compiladores_menu.add_command(label="Generar Tabla de Símbolos", command=self.mostrar_tabla_simbolos)
        compiladores_menu.add_separator()
        compiladores_menu.add_command(label="Compilación Completa (F5)", command=self.ejecutar_compilador)

        # Menú Ayuda
        ayuda_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=ayuda_menu)

        imports_menu = tk.Menu(ayuda_menu, tearoff=0)
        ayuda_menu.add_cascade(label="Imports", menu=imports_menu)
        
        vb_libs = ["System", "System.IO", "System.Math", "System.Windows.Forms", "Microsoft.VisualBasic"]
        for lib in vb_libs:
            imports_menu.add_command(label=lib, command=lambda l=lib: self.insertar_imports(l))

        ayuda_menu.add_command(label="Estructura Main", command=self.insertar_main_vb)
        ayuda_menu.add_command(label="Acerca de...", command=self.mostrar_info_acerca_de)

        # Menú Variables
        variables_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Variables", menu=variables_menu)
        
        tipos_menu = tk.Menu(variables_menu, tearoff=0)
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
        self.output_area.insert(tk.END, f">> {mensaje}\n")
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def preparar_consola(self, titulo):
        self.output_area.config(state='normal')
        self.output_area.delete('1.0', tk.END)
        self.output_area.insert(tk.END, f"--- {titulo} ---\n")

    def finalizar_consola(self):
        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def ejecutar_lexico(self):
        self.preparar_consola("ANÁLISIS LÉXICO")
        compilador = CompiladorProyecto(self.text_area.get('1.0', tk.END))
        tokens = compilador.obtener_tokens_vertical()
        self.output_area.insert(tk.END, "\n".join(tokens) if tokens else "No se encontraron tokens.")
        self.finalizar_consola()

    def ejecutar_sintactico(self):
        self.preparar_consola("ANÁLISIS SINTÁCTICO")
        compilador = CompiladorProyecto(self.text_area.get('1.0', tk.END))
        errores = compilador.filtrar_warnings(["missing", "unexpected", "instruction", "scope", "parenthesis", "unclosed"])
        self.output_area.insert(tk.END, "\n".join(errores) + "\n" if errores else "Sintaxis correcta.\n")
        self.resaltar_errores(errores)
        self.finalizar_consola()

    def ejecutar_semantico(self):
        self.preparar_consola("ANÁLISIS SEMÁNTICO")
        compilador = CompiladorProyecto(self.text_area.get('1.0', tk.END))
        errores = compilador.filtrar_warnings(["type", "undefine", "ambiguity", "variable", "invalid"])
        
        self.output_area.insert(tk.END, "\n".join(errores) + "\n" if errores else "Semántica correcta.\n")
        self.resaltar_errores(errores)
        self.finalizar_consola()

    def mostrar_tabla_simbolos(self):
        self.preparar_consola("TABLA DE SÍMBOLOS")
        compilador = CompiladorProyecto(self.text_area.get('1.0', tk.END))
        compilador.analizar_todo()
        tabla = compilador.obtener_formato_tabla()
        self.output_area.insert(tk.END, "\n".join(tabla) if tabla else "Tabla vacía.")
        self.finalizar_consola()

    def ejecutar_compilador(self):
        codigo_fuente = self.text_area.get('1.0', tk.END)
        compilador = CompiladorProyecto(codigo_fuente)
        resultados = compilador.compilar()
        
        self.output_area.config(state='normal')
        self.output_area.delete('1.0', tk.END)
        
        # --- APARTADO LÉXICO ---
        self.output_area.insert(tk.END, "--- ANÁLISIS LÉXICO ---\n")
        self.output_area.insert(tk.END, "\n".join(resultados["lexico"]) + "\n\n")

        # --- APARTADO SINTÁCTICO Y SEMÁNTICO ---
        self.output_area.insert(tk.END, "--- ANÁLISIS SINTÁCTICO ---\n")
        if resultados["sintactico"]:
            for res in resultados["sintactico"]: self.output_area.insert(tk.END, f">> {res}\n")
        else: self.output_area.insert(tk.END, "Sin errores sintácticos.\n")

        self.output_area.insert(tk.END, "\n--- ANÁLISIS SEMÁNTICO ---\n")
        if resultados["semantico"]:
            for res in resultados["semantico"]: self.output_area.insert(tk.END, f">> {res}\n")
        else: self.output_area.insert(tk.END, "Sin errores semánticos.\n")
            
        # --- TABLA DE SÍMBOLOS ---
        self.output_area.insert(tk.END, "\n--- TABLA DE SÍMBOLOS ---\n")
        self.output_area.insert(tk.END, "\n".join(resultados["tabla"]))

        errores_totales = resultados["sintactico"] + resultados["semantico"]
        self.resaltar_errores(errores_totales)

        self.output_area.config(state='disabled')
        self.output_area.see(tk.END)

    def mostrar_info_acerca_de(self):
        info = (
            "IDE Visual Basic\n"
            "Versión: v1.5\n\n"
            
            "--- MOTOR DE COMPILACIÓN ---\n"
            "• Análisis modular completo: Léxico, Sintáctico y Semántico.\n"
            "• Tabla de Símbolos con direccionamiento de memoria (Base 1000).\n"
            "• Soporte para estructura condicional nativa (If ... Then ... End If).\n"
            "• Gestión avanzada de ámbitos (Scopes) mediante pilas.\n"
            "• Recuperación de errores en Modo Pánico para evitar fallos en cascada.\n\n"
            
            "--- EXPERIENCIA DE USUARIO (UI/UX) ---\n"
            "• Resaltado de Sintaxis en tiempo real (Keywords, Tipos, Strings, etc.).\n"
            "• Resaltado visual de errores (fondo rojo) guiado por el compilador.\n"
            "• Auto-indentación inteligente al presionar Enter.\n"
            "• Borrado inteligente de tabulaciones (Backspace alineado a 4 espacios).\n"
            "• Interfaz de paneles redimensionables (PanedWindow) para la consola.\n"
            "• Flujo nativo de archivos: Abrir, Guardar y Guardar Como.\n\n"
            
            "Desarrollado para la materia de Compiladores (CUCEI)\n"
            "Por: Axel González Pompa."
        )
        messagebox.showinfo("Acerca de IDE Visual Basic", info)

if __name__ == "__main__":
    root = tk.Tk()
    app = IDEVisualBasic(root)
    root.mainloop()