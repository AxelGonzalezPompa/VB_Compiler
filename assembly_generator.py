class GeneradorEnsamblador:
    def __init__(self, cuadruplos, tabla_simbolos):
        self.cuadruplos = cuadruplos
        self.tabla = tabla_simbolos
        self.asm = []
        self.label_counter = 0 # Para generar etiquetas únicas en los relacionales

    def generar_x86(self):
        # 1. ESPECTRO DE VARIABLES Y TEXTOS
        vars_set = set()
        strings_dict = {}
        str_counter = 0

        # Recorremos los cuádruplos para extraer TODO lo que necesitamos
        for c in self.cuadruplos:
            op, arg1, arg2, res = c
            
            for arg in [arg1, arg2, res]:
                if not arg or arg == 'PENDIENTE': continue
                s_arg = str(arg)
                
                # A) Es un String ("Hola")
                if s_arg.startswith('"') or s_arg.startswith("'"):
                    if s_arg not in strings_dict:
                        strings_dict[s_arg] = f"msg_{str_counter}"
                        str_counter += 1
                
                # B) Es Número Constante o Booleano
                elif s_arg.replace('.', '', 1).isdigit() or s_arg in ['True', 'False']:
                    continue
                
                # C) Es una Etiqueta (Ej. L1, L5)
                elif s_arg.startswith('L') and s_arg[1:].isdigit():
                    continue
                
                # D) Es Variable, Temporal o Arreglo
                else:
                    vars_set.add(s_arg)

        # 2. CABECERA EMU8086
        self.asm.append("; --- CÓDIGO GENERADO PARA EMU8086 ---")
        self.asm.append(".MODEL SMALL")
        self.asm.append(".STACK 100h")
        self.asm.append(".DATA")

        # 3. DECLARAR VARIABLES
        for v in vars_set:
            es_arr = False
            limite = 100 # Default por seguridad
            
            # Unimos los scopes activos y el historial para buscar la variable
            todos_los_scopes = self.tabla.scopes + self.tabla.historial_scopes
            
            for scope in todos_los_scopes:
                if v in scope and scope[v].get("es_arreglo"):
                    es_arr = True
                    limite = scope[v].get("limite") + 1
                    break
            
            if es_arr:
                self.asm.append(f"    {v} dw {limite} dup(0) ; Arreglo reservado")
            else:
                self.asm.append(f"    {v} dw 0")

        # 4. DECLARAR TEXTOS CONSTANTES
        for text, label in strings_dict.items():
            clean_text = text[1:-1] # Quitamos las comillas
            # El '$' al final es obligatorio en DOS para saber dónde acaba el texto
            self.asm.append(f"    {label} db '{clean_text}', 13, 10, '$'")

        # 5. INICIO DE CÓDIGO EJECUTABLE
        self.asm.append("\n.CODE")
        self.asm.append("MAIN PROC")
        self.asm.append("    ; Iniciar Segmento de Datos (Obligatorio en 8086)")
        self.asm.append("    MOV AX, @DATA")
        self.asm.append("    MOV DS, AX\n")

        # 6. TRADUCCIÓN DE CUÁDRUPLOS
        for i, cuad in enumerate(self.cuadruplos):
            op, arg1, arg2, res = cuad
            self.asm.append(f"    ; --- Cuadruplo {i}: {cuad} ---")
            self.asm.append(f"L{i}:") 
            self._traducir_instruccion(op, arg1, arg2, res, strings_dict)
        # Etiqueta de escape para saltos que van más allá del último cuádruplo
        self.asm.append(f"L{len(self.cuadruplos)}:")

        # 7. FIN DE PROGRAMA Y SUBRUTINAS
        self.asm.append("\n    ; --- FIN DEL PROGRAMA (Syscall Exit DOS) ---")
        self.asm.append("    MOV AH, 4Ch")
        self.asm.append("    INT 21h")
        self.asm.append("MAIN ENDP")

        self.asm.append("\n; --- LIBRERÍA ESTÁNDAR (SUBRUTINAS) ---")
        self.asm.append(self._obtener_rutinas_8086())
        self.asm.append("END MAIN")

        return "\n".join(self.asm)

    # Helper para obtener el valor literal numérico o nombre de variable
    def _arg_val(self, arg):
        s = str(arg)
        if s == 'True': return '1'
        if s == 'False': return '0'
        return s

    def _traducir_instruccion(self, op, arg1, arg2, res, strings_dict):
        # Asignación Normal
        if op == '=':
            self.asm.append(f"    MOV AX, {self._arg_val(arg1)}")
            self.asm.append(f"    MOV {res}, AX")

        # Matemáticas Básicas
        elif op == '+':
            self.asm.append(f"    MOV AX, {self._arg_val(arg1)}")
            self.asm.append(f"    ADD AX, {self._arg_val(arg2)}")
            self.asm.append(f"    MOV {res}, AX")

        elif op == '-':
            self.asm.append(f"    MOV AX, {self._arg_val(arg1)}")
            self.asm.append(f"    SUB AX, {self._arg_val(arg2)}")
            self.asm.append(f"    MOV {res}, AX")

        elif op == '*':
            self.asm.append(f"    MOV AX, {self._arg_val(arg1)}")
            self.asm.append(f"    MOV BX, {self._arg_val(arg2)}")
            self.asm.append(f"    IMUL BX    ; AX = AX * BX")
            self.asm.append(f"    MOV {res}, AX")

        elif op == '/':
            self.asm.append(f"    MOV AX, {self._arg_val(arg1)}")
            self.asm.append(f"    CWD        ; Extiende signo de AX a DX")
            self.asm.append(f"    MOV BX, {self._arg_val(arg2)}")
            self.asm.append(f"    IDIV BX    ; Divide DX:AX entre BX")
            self.asm.append(f"    MOV {res}, AX") # Guardamos cociente

        # Lógicas Relacionales
        # En 8086 no hay instrucción 'SET', debemos simularla con saltos nativos
        elif op in ['<', '>', '<=', '>=', '==', '<>']:
            self.asm.append(f"    MOV AX, {self._arg_val(arg1)}")
            self.asm.append(f"    CMP AX, {self._arg_val(arg2)}")
            
            l_true = f"TRUE_{self.label_counter}"
            l_end = f"END_REL_{self.label_counter}"
            self.label_counter += 1

            if op == '<': jmp_inst = 'JL'
            elif op == '>': jmp_inst = 'JG'
            elif op == '<=': jmp_inst = 'JLE'
            elif op == '>=': jmp_inst = 'JGE'
            elif op == '==': jmp_inst = 'JE'
            elif op == '<>': jmp_inst = 'JNE'

            self.asm.append(f"    {jmp_inst} {l_true}")
            self.asm.append(f"    MOV {res}, 0     ; Falso")
            self.asm.append(f"    JMP {l_end}")
            self.asm.append(f"{l_true}:")
            self.asm.append(f"    MOV {res}, 1     ; Verdadero")
            self.asm.append(f"{l_end}:")

        # Operaciones de Arreglos (con aritmética de Punteros Básica 8086)
        elif op == 'VERIF':
            self.asm.append(f"    ; Verificando límite: {arg1} hasta {res}")

        elif op == 'ASIG_ARR':
            # res[arg2] = arg1
            self.asm.append(f"    MOV BX, {self._arg_val(arg2)}")
            self.asm.append(f"    SHL BX, 1        ; Multiplicar índice x2 (Palabras 16-bits)")
            self.asm.append(f"    MOV AX, {self._arg_val(arg1)}")
            self.asm.append(f"    MOV {res}[BX], AX")

        elif op == 'ACCESO_ARR':
            # res = arg1[arg2]
            self.asm.append(f"    MOV BX, {self._arg_val(arg2)}")
            self.asm.append(f"    SHL BX, 1        ; Índice x2")
            self.asm.append(f"    MOV AX, {arg1}[BX]")
            self.asm.append(f"    MOV {res}, AX")

        # Saltos (GOTO)
        elif op == 'GOTO':
            self.asm.append(f"    JMP {res}")

        elif op == 'GOTOF':
            self.asm.append(f"    CMP {arg1}, 0")
            self.asm.append(f"    JE {res}         ; Salta si es 0 (Falso)")

        # IMPRESIÓN (Manejo Mágico I/O)
        elif op == 'PRINT':
            s_arg = str(arg1)
            # ¿Es una cadena de texto?
            if s_arg in strings_dict:
                label = strings_dict[s_arg]
                self.asm.append(f"    LEA DX, {label}")
                self.asm.append(f"    MOV AH, 09h")
                self.asm.append(f"    INT 21h          ; Imprimir String")
            else:
                # Es un número (variable o literal)
                self.asm.append(f"    MOV AX, {self._arg_val(arg1)}")
                self.asm.append(f"    CALL PRINT_NUM   ; Imprimir Entero")
                self.asm.append(f"    CALL PRINT_NL    ; Salto de línea")


    def _obtener_rutinas_8086(self):
        return """
; =============================================
; Rutina para imprimir números enteros en AX
; =============================================
PRINT_NUM PROC
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX

    ; ¿Es negativo?
    CMP AX, 0
    JGE INICIAR_CONV
    PUSH AX
    MOV AH, 02h
    MOV DL, '-'    ; Imprimir signo
    INT 21h
    POP AX
    NEG AX         ; Hacer positivo para dividir

INICIAR_CONV:
    XOR CX, CX     ; Contador a 0
    MOV BX, 10     ; Base 10
DIVIDIR:
    XOR DX, DX     ; Limpiar residuo
    DIV BX
    PUSH DX        ; Guardar residuo en pila
    INC CX
    CMP AX, 0
    JNE DIVIDIR

IMPRIMIR_DIGITOS:
    POP DX         ; Recuperar dígitos invertidos
    ADD DL, '0'    ; Convertir a ASCII
    MOV AH, 02h
    INT 21h        ; Imprimir caracter
    LOOP IMPRIMIR_DIGITOS

    POP DX
    POP CX
    POP BX
    POP AX
    RET
PRINT_NUM ENDP

; =============================================
; Rutina para salto de línea
; =============================================
PRINT_NL PROC
    PUSH AX
    PUSH DX
    MOV AH, 02h
    MOV DL, 13     ; Retorno de carro (CR)
    INT 21h
    MOV DL, 10     ; Salto de línea (LF)
    INT 21h
    POP DX
    POP AX
    RET
PRINT_NL ENDP
"""