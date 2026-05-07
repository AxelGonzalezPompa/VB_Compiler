import enum

# --- LÉXICO ---
class TokenType(enum.Enum):
    IMPORTS = "Imports"
    MODULE = "Module"
    SUB = "Sub"
    MAIN = "Main"
    END = "End"
    DIM = "Dim"
    AS = "As"
    PRINT = "Print"
    IF = "If"
    THEN = "Then"
    SELECT = "Select"
    CASE = "Case"
    IS = "Is"
    TO = "To"
    ELSE = "Else"
    FOR = "For"
    NEXT = "Next"
    STEP = "Step"
    WHILE = "While"
    AND = "And"
    OR = "Or"
    FUNCTION = "Function"
    RETURN = "Return"
    
    TIPO_ENTERO = "Integer"
    TIPO_DOUBLE = "Double"
    TIPO_CADENA = "String"
    TIPO_BOOLEANO = "Boolean"
    TIPO_CHAR = "Char"
    
    IDENTIFICADOR = "Identificador"
    NUMERO = "Numero"
    CADENA_LITERAL = "Cadena"
    BOOLEANO_LITERAL = "Booleano"
    CHAR_LITERAL = "Caracter"
    UNCLOSED_STRING = "UnclosedString"
    UNCLOSED_CHAR = "UnclosedChar"  
    
    IGUAL = "="
    SUMA = "+"
    RESTA = "-"
    MULT = "*"
    DIV = "/"
    PAREN_A = "("
    PAREN_C = ")"
    PUNTO_COMA = ";"
    PUNTO = "."
    COMA = ","
    MAYOR = ">"
    MENOR = "<"
    MAYOR_IGUAL = ">="
    MENOR_IGUAL = "<="
    IGUAL_LOGICO = "=="
    DIFERENTE = "<>"
    FIN = "EOF"
    NUEVA_LINEA = "NewLine"
    INVALID_ID = "Invalid_ID"
    SIMBOLO_DESCONOCIDO = "Simbolo_Desconocido"

class Token:
    def __init__(self, type, value, linea):
        self.type = type
        self.value = value
        self.linea = linea

class Lexico:
    def __init__(self, fuente):
        self.fuente = fuente
        self.pos = 0
        self.linea = 1
        self.keywords = {
            "imports": TokenType.IMPORTS,
            "module": TokenType.MODULE,
            "sub": TokenType.SUB,
            "main": TokenType.MAIN,
            "end": TokenType.END,
            "dim": TokenType.DIM,
            "as": TokenType.AS,
            "integer": TokenType.TIPO_ENTERO,
            "double": TokenType.TIPO_DOUBLE,
            "string": TokenType.TIPO_CADENA,
            "boolean": TokenType.TIPO_BOOLEANO,
            "char": TokenType.TIPO_CHAR,
            "print": TokenType.PRINT,
            "true": TokenType.BOOLEANO_LITERAL,
            "false": TokenType.BOOLEANO_LITERAL,
            "if": TokenType.IF,
            "then": TokenType.THEN,
            "select": TokenType.SELECT,
            "case": TokenType.CASE,
            "is": TokenType.IS,
            "to": TokenType.TO,
            "else": TokenType.ELSE,
            "for": TokenType.FOR,
            "next": TokenType.NEXT,
            "step": TokenType.STEP,
            "while": TokenType.WHILE,
            "and": TokenType.AND,
            "or": TokenType.OR,
            "function": TokenType.FUNCTION,
            "return": TokenType.RETURN
        }

        self.op_dobles = {
                "==": TokenType.IGUAL_LOGICO, ">=": TokenType.MAYOR_IGUAL,
                "<=": TokenType.MENOR_IGUAL, "<>": TokenType.DIFERENTE
            }
        
        self.mapa_simbolos = {
            '+': TokenType.SUMA, '-': TokenType.RESTA, '*': TokenType.MULT, 
            '/': TokenType.DIV, '(': TokenType.PAREN_A, ')': TokenType.PAREN_C, 
            '=': TokenType.IGUAL, '>': TokenType.MAYOR, '<': TokenType.MENOR,
            '.': TokenType.PUNTO, ',': TokenType.COMA
        }

    def siguiente_token(self):
        # 1. Saltar espacios
        while self.pos < len(self.fuente) and self.fuente[self.pos] in [' ', '\t', '\r']:
            self.pos += 1

        # 2. Verificación de FIN (EOF)
        if self.pos >= len(self.fuente):
            return Token(TokenType.FIN, "", self.linea)

        # 3. Operadores de dos caracteres
        if self.pos + 1 < len(self.fuente):
            two_char = self.fuente[self.pos:self.pos+2]
            
            # --- MODIFICADO: Usamos el diccionario pre-cargado en memoria ---
            if two_char in self.op_dobles:
                self.pos += 2
                return Token(self.op_dobles[two_char], two_char, self.linea)

        # 4. Capturar el carácter actual una sola vez    
        char = self.fuente[self.pos]

        # 5. Caracteres especiales y saltos
        if char == '\n':
            self.linea += 1
            self.pos += 1
            return Token(TokenType.NUEVA_LINEA, "\\n", self.linea - 1)

        if char == ';':
            self.pos += 1
            return Token(TokenType.PUNTO_COMA, ";", self.linea)

        # Manejo de Strings
        if char == '"':
            self.pos += 1
            cadena = ""
            while self.pos < len(self.fuente) and self.fuente[self.pos] not in ['"', '\n']:
                cadena += self.fuente[self.pos]
                self.pos += 1
            
            if self.pos < len(self.fuente) and self.fuente[self.pos] == '"':
                self.pos += 1
                return Token(TokenType.CADENA_LITERAL, cadena, self.linea)
            else:
                return Token(TokenType.UNCLOSED_STRING, cadena, self.linea)

        # Manejo de Chars
        if char == "'":
            self.pos += 1
            caracter = ""
            while self.pos < len(self.fuente) and self.fuente[self.pos] not in ["'", '\n']:
                caracter += self.fuente[self.pos]
                self.pos += 1
            
            if self.pos < len(self.fuente) and self.fuente[self.pos] == "'":
                self.pos += 1
                return Token(TokenType.CHAR_LITERAL, caracter, self.linea)
            else:
                return Token(TokenType.UNCLOSED_CHAR, caracter, self.linea)

        # Manejo de identificadores
        if char.isalpha():
            word = ""
            while self.pos < len(self.fuente) and (self.fuente[self.pos].isalnum() or self.fuente[self.pos] == '_'):
                word += self.fuente[self.pos]
                self.pos += 1
            token_type = self.keywords.get(word.lower(), TokenType.IDENTIFICADOR)
            return Token(token_type, word, self.linea)

        # Manejo de números
        if char.isdigit():
            num = ""
            while self.pos < len(self.fuente) and self.fuente[self.pos].isdigit():
                num += self.fuente[self.pos]
                self.pos += 1
            
            if self.pos < len(self.fuente) and self.fuente[self.pos].isalpha():
                invalid_id = num
                while self.pos < len(self.fuente) and self.fuente[self.pos].isalnum():
                    invalid_id += self.fuente[self.pos]
                    self.pos += 1
                return Token(TokenType.INVALID_ID, invalid_id, self.linea)
                
            return Token(TokenType.NUMERO, num, self.linea)

        # 6. Operadores de un solo carácter
        self.pos += 1
        
        # --- MODIFICADO: Usamos el diccionario pre-cargado en memoria ---
        if char in self.mapa_simbolos:
            return Token(self.mapa_simbolos[char], char, self.linea)
            
        return Token(TokenType.SIMBOLO_DESCONOCIDO, char, self.linea)

# --- TABLA DE SÍMBOLOS (CON PILA DE ÁMBITOS) ---
class TablaSimbolos:
    def __init__(self):
        # self.scopes es una lista de diccionarios. 
        # El índice 0 siempre será el ámbito global (Module).
        self.scopes = [{}]
        self.historial_scopes = []
        self.direccion_actual = 1000 
        self.tamanos = {
            "Integer": 4,
            "Double": 8,
            "String": 10,
            "Boolean": 2,
            "Char": 2
        }

    def entrar_ambito(self):
        # Crea un nuevo diccionario temporal para el Sub/Función
        self.scopes.append({})

    def salir_ambito(self):
        if len(self.scopes) > 1:
            # Antes de borrarlo de la pila, lo guardamos en el historial
            scope_cerrado = self.scopes.pop()
            self.historial_scopes.append(scope_cerrado)

    def declarar(self, nombre, tipo, tamano_arreglo=None):
        ambito_actual = self.scopes[-1]
        
        if nombre in ambito_actual:
            return False, ambito_actual[nombre]["tipo"]
        
        direccion = self.direccion_actual
        tamano_base = self.tamanos.get(tipo, 4) # 4 por defecto si no lo encuentra
        
        # --- Cálculo dinámico de memoria para arreglos ---
        if tamano_arreglo is not None:
            # Reservamos memoria para N elementos
            espacio_total = tamano_base * tamano_arreglo
            ambito_actual[nombre] = {
                "tipo": tipo, 
                "dir": direccion, 
                "es_arreglo": True, 
                "limite": tamano_arreglo
            }
            self.direccion_actual += espacio_total
        else:
            # Variable normal
            ambito_actual[nombre] = {
                "tipo": tipo, 
                "dir": direccion, 
                "es_arreglo": False
            }
            self.direccion_actual += tamano_base

        return True, tipo

    def existe(self, nombre):
        # Busca la variable desde el ámbito más local (tope) hasta el global (base)
        for ambito in reversed(self.scopes):
            if nombre in ambito:
                return True
        return False
    
    def obtener_tipo(self, nombre):
        # Busca la variable desde lo local a lo global y devuelve su tipo
        for ambito in reversed(self.scopes):
            if nombre in ambito:
                return ambito[nombre]["tipo"]
        return None

    def declarar_funcion(self, nombre, tipo_retorno, parametros, cuad_inicio):
        # Las funciones siempre se guardan en el scope global (índice 0)
        if nombre in self.scopes[0]:
            return False
            
        self.scopes[0][nombre] = {
            "tipo": tipo_retorno,
            "es_funcion": True,
            "parametros": parametros, # Lista de tipos. Ej: ['Integer', 'Integer']
            "cuad_inicio": cuad_inicio
        }
        return True

# --- PARSER ---
class CompiladorProyecto:
    def __init__(self, codigo_fuente):
        self.codigo_fuente = codigo_fuente
        self.lexer = Lexico(self.codigo_fuente)
        self.tabla = TablaSimbolos()
        self.warnings = []
        self.token_actual = self.lexer.siguiente_token()
        self.tokens_identificados = []

        self.en_modulo = False
        self.en_sub = False
        
        self.pila_ifs = []
        self.pila_selects = []
        self.pila_fors = []
        self.pila_whiles = []
        self.pila_estructuras_abiertas = []

        self.cuadruplos = []
        self.contador_temporales = 1
        self.pila_saltos = []
        self.pila_inicios_while = []
        self.tipos_temporales = {}

        self.rutas_analisis = {
            TokenType.IMPORTS: self._analizar_imports,
            TokenType.MODULE: self._analizar_module,
            TokenType.SUB: self._analizar_sub,
            TokenType.IF: self._analizar_if,
            TokenType.SELECT: self._analizar_select,
            TokenType.CASE: self._analizar_case,
            TokenType.END: self._analizar_end,
            TokenType.DIM: self._analizar_dim,
            TokenType.IDENTIFICADOR: self._analizar_identificador,
            TokenType.INVALID_ID: self._analizar_invalid_id,
            TokenType.PRINT: self._analizar_print,
            TokenType.FOR: self._analizar_for,
            TokenType.NEXT: self._analizar_next,
            TokenType.WHILE: self._analizar_while,
            TokenType.ELSE: self._analizar_else,
            TokenType.FUNCTION: self._analizar_function,
            TokenType.RETURN: self._analizar_return
        }

    def generar_temporal(self):
        nombre_temp = f"T{self.contador_temporales}"
        self.contador_temporales += 1
        return nombre_temp

    def emitir_cuadruplo(self, operador, arg1, arg2, resultado):
        self.cuadruplos.append((operador, arg1, arg2, resultado))

    def rellenar_salto(self, indice_cuadruplo):
        # El destino es el índice del próximo cuádruplo que se va a generar
        destino = len(self.cuadruplos) 
        
        # Extraemos la tupla pendiente
        cuad_antiguo = self.cuadruplos[indice_cuadruplo]
        
        # En Python las tuplas son inmutables, así que creamos una nueva
        # reemplazando el último valor (el destino)
        self.cuadruplos[indice_cuadruplo] = (cuad_antiguo[0], cuad_antiguo[1], cuad_antiguo[2], f"L{destino}")

    def consumir(self):
        token_consumido = self.token_actual
        self.token_actual = self.lexer.siguiente_token()
        return token_consumido

    def registrar_warning(self, mensaje, linea=None):
        # Si le pasamos una línea específica la usa, si no, usa la del token actual
        lin = linea if linea is not None else self.token_actual.linea
        formato = f"Linea {lin}: {mensaje}"
        self.warnings.append(formato)

    def compilar(self):
        #Ejecuta todas las fases y devuelve un reporte completo.
        self.warnings = []
        self.analizar_todo()
        return {
            "lexico": self.obtener_tokens_vertical(),
            "sintactico": self.filtrar_warnings(["missing", "unexpected", "expected", "instruction", "scope", "parenthesis", "unclosed", "incomplete"], auto_analizar=False),
            "semantico": self.filtrar_warnings(["type", "undefine", "ambiguity", "variable", "invalid", "mismatch"], auto_analizar=False),
            "tabla": self.obtener_formato_tabla(),
            "cuadruplos": self.cuadruplos
        }

    def analizar_todo(self):
        """Realiza el análisis completo sin devolver nada aún."""
        while self.token_actual.type != TokenType.FIN:
            self.analizar_instruccion()
        
        if self.en_sub: self.registrar_warning("Warning missing 'End Sub'")
        if self.en_modulo: self.registrar_warning("Warning missing 'End Module'")
        
        for linea_abierta in self.pila_ifs:
            self.registrar_warning("Warning missing 'End If'", linea=linea_abierta)
        
        for select_abierto in self.pila_selects:
            self.registrar_warning("Warning missing 'End Select'", linea=select_abierto["linea"])

        for for_abierto in self.pila_fors:
            self.registrar_warning("Warning missing 'Next'", linea=for_abierto)

        for while_abierto in self.pila_whiles:
            self.registrar_warning("Warning missing 'End While'", linea=while_abierto)

    def obtener_tokens_vertical(self):
        # Fase Léxica: Retorna la lista de tokens identificados.
        tokens = []
        temp_lexer = Lexico(self.codigo_fuente)
        t = temp_lexer.siguiente_token()
        while t.type != TokenType.FIN:
            if t.type != TokenType.NUEVA_LINEA:
                tokens.append(f"<{t.type.name}, {t.value}>")
            t = temp_lexer.siguiente_token()
        return tokens

    def filtrar_warnings(self, palabras_clave, auto_analizar=True):
        """Filtra los warnings registrados."""
        if auto_analizar and not self.warnings: 
            self.analizar_todo()
        return [w for w in self.warnings if any(p in w.lower() for p in palabras_clave)]

    def obtener_formato_tabla(self):
        """Retorna el estado de la tabla de símbolos en el formato de semantica.py."""
        lineas = []
        # Ámbito Global
        for var, info in self.tabla.scopes[0].items():
            lineas.append(f"ID: {var} -> {info}")
        # Ámbitos Locales (Historial)
        for i, scope in enumerate(self.tabla.historial_scopes):
            for var, info in scope.items():
                lineas.append(f"ID: {var} (Local {i+1}) -> {info}")
        lineas.append("\n")
        return lineas

    def analizar_instruccion(self):
        t = self.token_actual
        
        # 1. Casos triviales o errores léxicos sueltos
        if t.type in [TokenType.NUEVA_LINEA, TokenType.UNCLOSED_STRING, TokenType.UNCLOSED_CHAR]:
            if t.type != TokenType.NUEVA_LINEA:
                self.registrar_warning(f"Warning unclosed {t.type.value} literal")
            self.consumir()
            return

        # 2. Buscar la función específica para el token actual
        funcion_analisis = self.rutas_analisis.get(t.type)

        # 3. Ejecutar la función, o consumir si es algo desconocido (modo pánico básico)
        if funcion_analisis:
            funcion_analisis() 
        else:
            self.consumir()

    def _analizar_imports(self):
        self.consumir()
        if self.token_actual.type == TokenType.IDENTIFICADOR:
            self.consumir()
            while self.token_actual.type == TokenType.PUNTO:
                self.consumir()
                if self.token_actual.type == TokenType.IDENTIFICADOR:
                    self.consumir()
                else:
                    self.registrar_warning("Warning expected identifier after '.' in Imports")
                    break
        else:
            self.registrar_warning("Warning expected namespace after 'Imports'")

    def _analizar_module(self):
        self.consumir()
        if self.token_actual.type == TokenType.IDENTIFICADOR:
            self.consumir()
            self.en_modulo = True 

    def _analizar_sub(self):
        self.consumir()
        if self.token_actual.type in [TokenType.MAIN, TokenType.IDENTIFICADOR]:
            self.consumir()
            if self.token_actual.type == TokenType.PAREN_A:
                self.consumir()
                if self.token_actual.type == TokenType.PAREN_C:
                    self.consumir()
            self.en_sub = True
            self.tabla.entrar_ambito() 

    def _analizar_if(self):
        linea_inicio_if = self.token_actual.linea
        self.consumir()
        
        uso_parentesis = False
        if self.token_actual.type == TokenType.PAREN_A:
            uso_parentesis = True
            self.consumir()
        
        # 1. Evaluamos la condición completa y obtenemos el temporal (ej. T4)
        resultado_condicion = self.analizar_expresion_logica()
        
        # 2. Emitimos el GOTOF con destino pendiente y guardamos su índice
        self.emitir_cuadruplo('GOTOF', resultado_condicion, '', 'PENDIENTE')
        self.pila_saltos.append(len(self.cuadruplos) - 1)
        
        if uso_parentesis:
            if self.token_actual.type == TokenType.PAREN_C:
                self.consumir()
            else:
                self.registrar_warning("Warning missing ')' in condition")
            
        if self.token_actual.type == TokenType.THEN:
            self.consumir()
        else:
            self.registrar_warning("Warning instruction missing 'Then'")
            
        self.pila_ifs.append(linea_inicio_if)
        self.pila_estructuras_abiertas.append("If")
        self.tabla.entrar_ambito()

    def _analizar_select(self):
        linea_inicio_select = self.token_actual.linea
        self.consumir()
        tipo_select = None

        if self.token_actual.type == TokenType.CASE:
            self.consumir()
            if self.token_actual.type in [TokenType.IDENTIFICADOR, TokenType.NUMERO, TokenType.CADENA_LITERAL, TokenType.BOOLEANO_LITERAL]:
                if self.token_actual.type == TokenType.IDENTIFICADOR:
                    if not self.tabla.existe(self.token_actual.value):
                        self.registrar_warning(f"Warning undefine type '{self.token_actual.value}'")
                    tipo_select = self.tabla.obtener_tipo(self.token_actual.value)
                elif self.token_actual.type == TokenType.NUMERO: tipo_select = "Integer"
                elif self.token_actual.type == TokenType.CADENA_LITERAL: tipo_select = "String"
                elif self.token_actual.type == TokenType.BOOLEANO_LITERAL: tipo_select = "Boolean"
                self.consumir()
            else:
                self.registrar_warning("Warning expected expression after 'Select Case'")
                
            # --- MODIFICACIÓN: Agregamos el arreglo para rastrear duplicados ---
            self.pila_selects.append({
                "linea": linea_inicio_select, 
                "tipo": tipo_select, 
                "tiene_else": False,
                "casos_vistos": [] 
            })
        else:
            self.registrar_warning("Warning expected 'Case' after 'Select'")

    def _analizar_case(self):
        if not self.pila_selects:
            self.registrar_warning("Warning 'Case' outside of a 'Select Case' block")
            self.consumir()
            return
            
        info_select = self.pila_selects[-1]
        
        if info_select["tiene_else"]:
            self.registrar_warning("Warning unexpected 'Case' after 'Case Else'")

        self.consumir()
        
        if self.token_actual.type == TokenType.ELSE:
            info_select["tiene_else"] = True
            self.consumir()
            
        elif self.token_actual.type == TokenType.IS:
            self.consumir()
            operadores_relacionales = [TokenType.MAYOR, TokenType.MENOR, TokenType.IGUAL, 
                                       TokenType.MAYOR_IGUAL, TokenType.MENOR_IGUAL, TokenType.DIFERENTE]
            
            if self.token_actual.type in operadores_relacionales:
                operador_val = self.token_actual.value # Guardamos el string del operador ("<", ">", etc.)
                self.consumir()
                
                if self.token_actual.type in [TokenType.NUMERO, TokenType.CADENA_LITERAL, TokenType.BOOLEANO_LITERAL, TokenType.IDENTIFICADOR]:
                    tipo_caso = None
                    valor_token = self.token_actual.value # Guardamos el valor
                    
                    if self.token_actual.type == TokenType.IDENTIFICADOR:
                        if not self.tabla.existe(valor_token):
                            self.registrar_warning(f"Warning undefine type '{valor_token}'")
                        tipo_caso = self.tabla.obtener_tipo(valor_token)
                    elif self.token_actual.type == TokenType.NUMERO: tipo_caso = "Integer"
                    elif self.token_actual.type == TokenType.CADENA_LITERAL: tipo_caso = "String"
                    elif self.token_actual.type == TokenType.BOOLEANO_LITERAL: tipo_caso = "Boolean"

                    if info_select["tipo"] and tipo_caso and info_select["tipo"] != tipo_caso:
                        self.registrar_warning(f"Warning type mismatch: Cannot compare '{info_select['tipo']}' with '{tipo_caso}'")
                    
                    # --- NUEVO: Validar si la condición "Is" ya se evaluó antes ---
                    condicion_completa = f"Is {operador_val} {valor_token}"
                    if condicion_completa in info_select["casos_vistos"]:
                        self.registrar_warning(f"Warning ambiguity: duplicate case '{condicion_completa}'")
                    else:
                        info_select["casos_vistos"].append(condicion_completa)

                    self.consumir()
                else:
                    self.registrar_warning("Warning expected value after relational operator in 'Case Is'")
            else:
                self.registrar_warning("Warning expected relational operator after 'Is'")
                while self.token_actual.type not in [TokenType.NUEVA_LINEA, TokenType.FIN]:
                    self.consumir()
        else:
            esperando_valor = True
            while self.token_actual.type not in [TokenType.NUEVA_LINEA, TokenType.FIN]:
                t_eval = self.token_actual
                if esperando_valor:
                    if t_eval.type in [TokenType.NUMERO, TokenType.CADENA_LITERAL, TokenType.BOOLEANO_LITERAL, TokenType.IDENTIFICADOR]:
                        tipo_caso = None
                        valor_token = t_eval.value

                        if t_eval.type == TokenType.IDENTIFICADOR:
                            if not self.tabla.existe(valor_token):
                                self.registrar_warning(f"Warning undefine type '{valor_token}'")
                            tipo_caso = self.tabla.obtener_tipo(valor_token)
                        elif t_eval.type == TokenType.NUMERO: tipo_caso = "Integer"
                        elif t_eval.type == TokenType.CADENA_LITERAL: tipo_caso = "String"
                        elif t_eval.type == TokenType.BOOLEANO_LITERAL: tipo_caso = "Boolean"

                        if info_select["tipo"] and tipo_caso and info_select["tipo"] != tipo_caso:
                            self.registrar_warning(f"Warning type mismatch: Cannot compare '{info_select['tipo']}' with '{tipo_caso}'")
                        
                        # --- NUEVO: Validar si este valor exacto ya se usó en otro Case ---
                        if valor_token in info_select["casos_vistos"]:
                            self.registrar_warning(f"Warning ambiguity: duplicate case '{valor_token}'")
                        else:
                            info_select["casos_vistos"].append(valor_token)

                        self.consumir()
                        esperando_valor = False 
                    else:
                        self.registrar_warning("Warning expected expression in 'Case'")
                        while self.token_actual.type not in [TokenType.NUEVA_LINEA, TokenType.FIN]:
                            self.consumir()
                        break 
                else:
                    if t_eval.type == TokenType.COMA:
                        self.consumir()
                        esperando_valor = True 
                    elif t_eval.type == TokenType.TO:
                        self.consumir()
                        esperando_valor = True 
                    else:
                        self.registrar_warning(f"Warning unexpected token '{t_eval.value}' in 'Case' list")
                        break
                        
            if esperando_valor and self.token_actual.type in [TokenType.NUEVA_LINEA, TokenType.FIN]:
                self.registrar_warning("Warning incomplete 'Case' expression")

    def _analizar_end(self):
        self.consumir()
        # Obtenemos la última estructura que se abrió para validar el anidamiento
        estructura_top = self.pila_estructuras_abiertas[-1] if self.pila_estructuras_abiertas else None
        
        if self.token_actual.type == TokenType.IF:
            self.consumir()
            if estructura_top and estructura_top != "If":
                self.registrar_warning(f"Warning scope error: Cannot close 'If', currently inside an unclosed '{estructura_top}' block")
            else:
                if len(self.pila_ifs) > 0:
                    self.pila_ifs.pop()
                    self.pila_estructuras_abiertas.pop() # Quitamos el If de la pila universal
                    self.tabla.salir_ambito()
                
                    # Rellenar el GOTOF
                    if self.pila_saltos:
                        indice_salto = self.pila_saltos.pop()
                        self.rellenar_salto(indice_salto)

                else:
                    self.registrar_warning("Warning unexpected 'End If'")
        
        elif self.token_actual.type == TokenType.SELECT:
            self.consumir()
            if len(self.pila_selects) > 0:
                self.pila_selects.pop()
            else:
                self.registrar_warning("Warning unexpected 'End Select'")
        
        elif self.token_actual.type == TokenType.MODULE:
            self.consumir()
            if not self.en_modulo:
                self.registrar_warning("Warning unexpected 'End Module'")
            if self.en_sub:
                self.registrar_warning("Warning missing 'End Sub' before 'End Module'")
                self.en_sub = False
                self.tabla.salir_ambito()
            self.en_modulo = False
        
        elif self.token_actual.type == TokenType.WHILE:
            self.consumir()
            if estructura_top and estructura_top != "While":
                self.registrar_warning(f"Warning scope error: Cannot close 'While', currently inside an unclosed '{estructura_top}' block")
            else:
                if len(self.pila_whiles) > 0:
                    self.pila_whiles.pop()
                    self.pila_estructuras_abiertas.pop() # Quitamos el While de la pila universal
                    self.tabla.salir_ambito()

                    # --- Lógica de Saltos del While ---
                    # 1. Emitir el GOTO incondicional para regresar al inicio
                    if self.pila_inicios_while:
                        indice_regreso = self.pila_inicios_while.pop()
                        self.emitir_cuadruplo('GOTO', '', '', f"L{indice_regreso}")
                        
                    # 2. Rellenar el GOTOF pendiente que sacaba del ciclo
                    if self.pila_saltos:
                        indice_salto_falso = self.pila_saltos.pop()
                        self.rellenar_salto(indice_salto_falso)
                
                else:
                    self.registrar_warning("Warning unexpected 'End While'")
        
        elif self.token_actual.type == TokenType.SUB:
            self.consumir()
            if not self.en_sub:
                self.registrar_warning("Warning unexpected 'End Sub'")
            self.en_sub = False
            self.tabla.salir_ambito()
        
        elif self.token_actual.type == TokenType.FUNCTION:
            self.consumir()
            if estructura_top and estructura_top != "Function":
                self.registrar_warning(f"Warning scope error: Cannot close 'Function', inside '{estructura_top}'")
            else:
                if self.pila_estructuras_abiertas:
                    self.pila_estructuras_abiertas.pop()
                self.en_sub = False
                self.tabla.salir_ambito()
                # Emitimos el marcador de fin de función
                self.emitir_cuadruplo('ENDFUNC', '', '', '')

        else:
            self.registrar_warning("Warning incomplete 'End' statement")

    def _analizar_dim(self):
        if not self.en_modulo and not self.en_sub:
            self.registrar_warning("Warning invalid scope: Variable outside Module/Sub")
            self.saltar_expresion()
            return
        self.consumir()
        if self.token_actual.type == TokenType.IDENTIFICADOR:
            nombre_var = self.token_actual.value
            self.consumir()

            # --- Detectar si es un arreglo Dim arr(10) ---
            tamano_arreglo = None
            if self.token_actual.type == TokenType.PAREN_A:
                self.consumir()
                if self.token_actual.type == TokenType.NUMERO:
                    tamano_arreglo = int(self.token_actual.value)
                    self.consumir()
                else:
                    self.registrar_warning("Warning expected array size (number)")

                if self.token_actual.type == TokenType.PAREN_C:
                    self.consumir()
                else:
                    self.registrar_warning("Warning missing ')' in array declaration")

            if self.token_actual.type == TokenType.AS:
                self.consumir()
                tipos_validos = [TokenType.TIPO_ENTERO, TokenType.TIPO_DOUBLE, TokenType.TIPO_CADENA, TokenType.TIPO_BOOLEANO, TokenType.TIPO_CHAR]
                if self.token_actual.type not in tipos_validos:
                    self.registrar_warning(f"Warning invalid type '{self.token_actual.value}'")
                    tipo_var_str = "Unknown"
                    self.consumir()
                else:
                    tipo_var_str = self.token_actual.value 
                    self.consumir() 
                
                # Le pasamos el tamaño del arreglo a la tabla
                exito, tipo_previo = self.tabla.declarar(nombre_var, tipo_var_str, tamano_arreglo)
                if not exito:
                    self.registrar_warning(f"Warning ambiguity '{tipo_var_str[:3].lower()}' to '{tipo_previo[:3].lower()}'")
                
                if self.token_actual.type == TokenType.IGUAL:
                    # Validar semánticamente que no se asigne valor directo a un arreglo entero en su Dim
                    if tamano_arreglo is not None:
                        self.registrar_warning("Warning cannot assign direct value to array during declaration")
                    self.consumir()
                    self.saltar_expresion()
        else:
            self.saltar_expresion()

    def _analizar_identificador(self):
        nombre_var = self.token_actual.value
        self.consumir()
        
        # 1. Obtenemos información de la variable
        tipo_esperado = self.tabla.obtener_tipo(nombre_var)
        info_var = None
        for ambito in reversed(self.tabla.scopes):
            if nombre_var in ambito:
                info_var = ambito[nombre_var]
                break
                
        es_arreglo = info_var and info_var.get("es_arreglo")
        indice_arreglo = None
        
        if not self.tabla.existe(nombre_var):
            self.registrar_warning(f"Warning undefine type '{nombre_var}'")

        # --- Parsear el índice si la variable es un arreglo ---
        if es_arreglo:
            if self.token_actual.type == TokenType.PAREN_A:
                self.consumir()
                indice_arreglo = self.analizar_expresion_logica()
                
                if self.token_actual.type == TokenType.PAREN_C:
                    self.consumir()
                else:
                    self.registrar_warning(f"Warning missing ')' in array assignment '{nombre_var}'")
                
                # Generamos el cuádruplo de protección de límites
                self.emitir_cuadruplo('VERIF', indice_arreglo, '0', info_var['limite'])
            else:
                self.registrar_warning(f"Warning expected index for array '{nombre_var}'")

        if self.token_actual.type == TokenType.IGUAL:
            self.consumir() # Consumir el '='
            
            # 2. Procesamos toda la expresión a la derecha del igual
            resultado_expresion = self.analizar_expresion_logica()
            
            # Validación semántica estándar
            if tipo_esperado: 
                tipo_resultado = self._inferir_tipo(resultado_expresion)
                if tipo_resultado and tipo_resultado != "Unknown" and tipo_esperado != tipo_resultado:
                    if not (tipo_esperado == 'Double' and tipo_resultado == 'Integer'):
                        self.registrar_warning(f"Warning type mismatch: Cannot assign '{tipo_resultado}' to '{tipo_esperado}' variable '{nombre_var}'")
            
            # --- Generar el cuádruplo de asignación correcto ---
            if es_arreglo and indice_arreglo:
                # Escribimos en una posición de memoria (Puntero indirecto)
                self.emitir_cuadruplo('ASIG_ARR', resultado_expresion, indice_arreglo, nombre_var)
            else:
                # Asignación normal
                self.emitir_cuadruplo('=', resultado_expresion, '', nombre_var)

    def _analizar_invalid_id(self):
        self.registrar_warning(f"Warning undefined varible '{self.token_actual.value}'")
        self.consumir()
        if self.token_actual.type == TokenType.IGUAL:
            self.consumir()
            self.saltar_expresion(tipo_esperado=None)

    def _analizar_print(self):
        self.consumir()
        if self.token_actual.type == TokenType.PAREN_A:
            self.consumir()
            if self.token_actual.type == TokenType.IDENTIFICADOR:
                if not self.tabla.existe(self.token_actual.value):
                    self.registrar_warning(f"Warning undefine type '{self.token_actual.value}'")
            self.consumir() 
            if self.token_actual.type == TokenType.PAREN_C:
                self.consumir() 
            else:
                self.registrar_warning("Warning missing ')'")
            
            if self.token_actual.type != TokenType.PUNTO_COMA:
                self.registrar_warning("Warning end intruction 'print' ';'")
            else:
                self.consumir()
        else:
            self.registrar_warning("Warning missing '('")
            self.saltar_expresion()

    def _analizar_for(self):
        linea_inicio_for = self.token_actual.linea
        self.consumir()

        if self.token_actual.type == TokenType.IDENTIFICADOR:
            nombre_var = self.token_actual.value
            self.consumir()

            if self.token_actual.type == TokenType.AS:
                self.consumir()
                if self.token_actual.type in [TokenType.TIPO_ENTERO, TokenType.TIPO_DOUBLE]:
                    self.tabla.declarar(nombre_var, self.token_actual.value)
                    self.consumir()
                else:
                    self.registrar_warning(f"Warning invalid type '{self.token_actual.value}' for loop counter")
                    self.consumir()
            else:
                if not self.tabla.existe(nombre_var):
                    self.registrar_warning(f"Warning undefine type '{nombre_var}'")

            # --- INYECCIÓN 1: La Asignación Inicial ---
            if self.token_actual.type == TokenType.IGUAL:
                self.consumir()
                # Parseamos lo que va antes del 'To'
                valor_inicio = self.analizar_expresion_logica()
                self.emitir_cuadruplo('=', valor_inicio, '', nombre_var)
            else:
                self.registrar_warning("Warning expected '=' after loop variable")

            # Marcamos a qué cuádruplo debe regresar el Next
            indice_inicio_condicion = len(self.cuadruplos)

            # --- INYECCIÓN 2: La Condición Límite ---
            if self.token_actual.type == TokenType.TO:
                self.consumir()
                valor_fin = self.analizar_expresion_logica()
                
                # Creamos la condición: x <= limite
                temp_cond = self.generar_temporal()
                self.emitir_cuadruplo('<=', nombre_var, valor_fin, temp_cond)

                # Emitimos el GOTOF para salir del ciclo
                self.emitir_cuadruplo('GOTOF', temp_cond, '', 'PENDIENTE')
                indice_gotof = len(self.cuadruplos) - 1
            else:
                self.registrar_warning("Warning expected 'To' in 'For' statement")
                indice_gotof = None

            # Detectar el Step (Si no hay, por defecto es 1)
            valor_step = '1'
            if self.token_actual.type == TokenType.STEP:
                self.consumir()
                valor_step = self.analizar_expresion_logica()

            self.pila_fors.append({
                "linea": linea_inicio_for,
                "var": nombre_var,
                "step": valor_step,
                "inicio_cond": indice_inicio_condicion,
                "salto_falso": indice_gotof
            })

            self.pila_estructuras_abiertas.append("For")
            self.tabla.entrar_ambito()
        else:
            self.registrar_warning("Warning expected identifier after 'For'")
            self.saltar_expresion()

    def _analizar_next(self):
        self.consumir()
        
        estructura_top = self.pila_estructuras_abiertas[-1] if self.pila_estructuras_abiertas else None
        
        if self.token_actual.type == TokenType.IDENTIFICADOR:
            if not self.tabla.existe(self.token_actual.value):
                self.registrar_warning(f"Warning undefine type '{self.token_actual.value}'")
            self.consumir()

        if estructura_top and estructura_top != "For":
                self.registrar_warning(f"Warning scope error: Cannot use 'Next', currently inside an unclosed '{estructura_top}' block")
        else:
            if len(self.pila_fors) > 0:
                info_for = self.pila_fors.pop()
                self.pila_estructuras_abiertas.pop()
                self.tabla.salir_ambito()
                
                # --- INYECCIÓN 3: El Incremento y el Salto ---
                nombre_var = info_for["var"]
                valor_step = info_for["step"]
                
                # 1. Sumamos el step a la variable: x = x + step
                temp_suma = self.generar_temporal()
                self.emitir_cuadruplo('+', nombre_var, valor_step, temp_suma)
                self.emitir_cuadruplo('=', temp_suma, '', nombre_var)
                
                # 2. Regresamos al inicio (donde se evalúa la condición <=)
                self.emitir_cuadruplo('GOTO', '', '', f"L{info_for['inicio_cond']}")
                
                # 3. Rellenamos el GOTOF que se generó en el 'For'
                if info_for["salto_falso"] is not None:
                    self.rellenar_salto(info_for["salto_falso"])

            else:
                self.registrar_warning("Warning unexpected 'Next'")

    def _analizar_while(self):
        linea_inicio_while = self.token_actual.linea
        self.consumir() # Consumimos la palabra 'While'

        # 1: Guardamos en qué cuádruplo empieza la condición
        # Así sabremos a dónde debe regresar el GOTO incondicional
        indice_inicio_condicion = len(self.cuadruplos)
        self.pila_inicios_while.append(indice_inicio_condicion)

        uso_parentesis = False
        if self.token_actual.type == TokenType.PAREN_A:
            uso_parentesis = True
            self.consumir()
        
        # 2: Usamos el Descenso Recursivo igual que en el If
        resultado_condicion = self.analizar_expresion_logica()
        
        # Emitimos el GOTOF para salir del ciclo si la condición es falsa
        self.emitir_cuadruplo('GOTOF', resultado_condicion, '', 'PENDIENTE')
        self.pila_saltos.append(len(self.cuadruplos) - 1)
        
        if uso_parentesis:
            if self.token_actual.type == TokenType.PAREN_C:
                self.consumir()
            else:
                self.registrar_warning("Warning missing ')' in condition")
            
        # Registramos que abrimos un bloque While y entramos a un nuevo ámbito local
        self.pila_whiles.append(linea_inicio_while)
        self.pila_estructuras_abiertas.append("While")
        self.tabla.entrar_ambito()

    def _analizar_else(self):
        self.consumir() # Consumimos la palabra 'Else'
        
        # Validamos que realmente estemos dentro de un 'If'
        estructura_top = self.pila_estructuras_abiertas[-1] if self.pila_estructuras_abiertas else None
        if estructura_top != "If":
            self.registrar_warning("Warning unexpected 'Else' outside of an 'If' block")
            return
            
        # 1. Emitimos un GOTO para que el código 'True' brinque el bloque 'False'
        self.emitir_cuadruplo('GOTO', '', '', 'PENDIENTE')
        indice_goto = len(self.cuadruplos) - 1
        
        # 2. Sacamos de la pila el GOTOF que dejó el 'If' y lo rellenamos 
        #    para que aterrice exactamente aquí (inicio del Else).
        if self.pila_saltos:
            indice_gotof = self.pila_saltos.pop()
            self.rellenar_salto(indice_gotof)
            
        # 3. Metemos nuestro nuevo GOTO a la pila para que 'End If' lo rellene al final
        self.pila_saltos.append(indice_goto)

    def _inferir_tipo(self, operando):
        op_str = str(operando)
        
        # 1. ¿Es un temporal que ya calculamos?
        if op_str in self.tipos_temporales:
            return self.tipos_temporales[op_str]
            
        # 2. ¿Es una variable declarada?
        tipo_var = self.tabla.obtener_tipo(op_str)
        if tipo_var:
            return tipo_var
            
        # 3. Es un literal (constante)
        if op_str in ['True', 'False']: return 'Boolean'
        if op_str.startswith('"'): return 'String'
        if op_str.startswith("'"): return 'Char'
        if op_str.replace('.', '', 1).isdigit(): 
            return 'Double' if '.' in op_str else 'Integer'
            
        return None

    def _consultar_cubo_semantico(self, tipo_izq, operador, tipo_der):
        if not tipo_izq or not tipo_der: return "ERROR"

        # Aritmética (+, -, *, /)
        if operador in ['+', '-', '*', '/']:
            if tipo_izq == 'Integer' and tipo_der == 'Integer': return 'Integer'
            # Si hay un Double, el resultado se promueve a Double
            if tipo_izq in ['Integer', 'Double'] and tipo_der in ['Integer', 'Double']: return 'Double'
            # Concatenación de strings
            if operador == '+' and tipo_izq == 'String' and tipo_der == 'String': return 'String'
            return "ERROR"

        # Relacionales (>, <, >=, <=, =, <>)
        if operador in ['>', '<', '>=', '<=', '=', '<>']:
            if tipo_izq in ['Integer', 'Double'] and tipo_der in ['Integer', 'Double']: return 'Boolean'
            if tipo_izq == tipo_der: return 'Boolean' # String=String, Char=Char, etc.
            return "ERROR"

        # Lógicos (And, Or)
        if operador in ['And', 'Or']:
            if tipo_izq == 'Boolean' and tipo_der == 'Boolean': return 'Boolean'
            return "ERROR"

        return "ERROR"

    def _analizar_function(self):
        linea_inicio = self.token_actual.linea
        self.consumir() # Consumimos 'Function'
        
        if self.token_actual.type == TokenType.IDENTIFICADOR:
            nombre_funcion = self.token_actual.value
            self.consumir()
            
            parametros = []
            
            # 1. Parsear los parámetros
            if self.token_actual.type == TokenType.PAREN_A:
                self.consumir()
                
                # Entramos al ámbito de la función ANTES de declarar los parámetros
                # para que los parámetros se guarden como variables locales de esta función
                self.tabla.entrar_ambito()
                self.en_sub = True # Reutilizamos esta bandera para saber que estamos dentro de un bloque
                
                while self.token_actual.type == TokenType.IDENTIFICADOR:
                    nom_param = self.token_actual.value
                    self.consumir()
                    
                    if self.token_actual.type == TokenType.AS:
                        self.consumir()
                        tipo_param = self.token_actual.value
                        
                        # Guardamos el parámetro en la tabla local de la función
                        self.tabla.declarar(nom_param, tipo_param)
                        # Añadimos el tipo a la "firma" de la función
                        parametros.append(tipo_param)
                        
                        self.consumir() # Consumimos el tipo
                    else:
                        self.registrar_warning(f"Warning expected 'As' for parameter '{nom_param}'")
                        
                    if self.token_actual.type == TokenType.COMA:
                        self.consumir()
                    else:
                        break # Terminaron los parámetros
                        
                if self.token_actual.type == TokenType.PAREN_C:
                    self.consumir()
                else:
                    self.registrar_warning("Warning missing ')' in function parameters")
            else:
                self.registrar_warning("Warning expected '(' after function name")
                self.tabla.entrar_ambito()
                self.en_sub = True

            # 2. Parsear el tipo de retorno
            tipo_retorno = "Void"
            if self.token_actual.type == TokenType.AS:
                self.consumir()
                tipo_retorno = self.token_actual.value
                self.consumir()
                
            # 3. Registrar la función en la tabla global
            cuad_inicio = len(self.cuadruplos)
            exito = self.tabla.declarar_funcion(nombre_funcion, tipo_retorno, parametros, cuad_inicio)
            if not exito:
                self.registrar_warning(f"Warning duplicate function definition '{nombre_funcion}'")
                
            self.pila_estructuras_abiertas.append("Function")
            
        else:
            self.registrar_warning("Warning expected function name")

    def _analizar_return(self):
        self.consumir()
        
        estructura_top = self.pila_estructuras_abiertas[-1] if self.pila_estructuras_abiertas else None
        if estructura_top != "Function":
            self.registrar_warning("Warning 'Return' statement outside of a Function")
            
        # Parseamos lo que sea que vayamos a devolver
        valor_retorno = self.analizar_expresion_logica()
        
        # Opcional: Aquí podrías validar semánticamente que el 'tipo' de valor_retorno 
        # coincida con el 'tipo_retorno' de la función actual.
        
        self.emitir_cuadruplo('RETURN', valor_retorno, '', '')

    def saltar_expresion(self, tipo_esperado=None, tokens_parada=None):
        
        if tokens_parada is None:
            tokens_parada = [TokenType.NUEVA_LINEA, TokenType.FIN, TokenType.PUNTO_COMA]
        
        # --- Expresión vacía ---
        if self.token_actual.type in [TokenType.NUEVA_LINEA, TokenType.FIN, TokenType.PUNTO_COMA]:
            self.registrar_warning("Warning missing expression after '='")
            return
        
        parentesis_abiertos = 0 
        
        # --- Verificación básica de Tipos ---
        t_eval = self.token_actual
        if tipo_esperado and t_eval.type not in [TokenType.NUEVA_LINEA, TokenType.FIN, TokenType.PUNTO_COMA]:
            tipo_asignado = None
            
            # Determinamos el tipo del valor que se está intentando asignar
            if t_eval.type == TokenType.BOOLEANO_LITERAL:
                tipo_asignado = TokenType.TIPO_BOOLEANO.value # "Boolean"
            elif t_eval.type == TokenType.NUMERO:
                tipo_asignado = TokenType.TIPO_ENTERO.value # Asumimos Integer para números
            elif t_eval.type == TokenType.CADENA_LITERAL:
                tipo_asignado = TokenType.TIPO_CADENA.value # "String"
            elif t_eval.type == TokenType.CHAR_LITERAL:
                tipo_asignado = TokenType.TIPO_CHAR.value # "Char"
            elif t_eval.type == TokenType.IDENTIFICADOR:
                tipo_asignado = self.tabla.obtener_tipo(t_eval.value)
            
            # Si hay una discordancia estricta con Booleanos, arrojamos error
            if tipo_asignado and tipo_esperado:
                if tipo_esperado == "Boolean" and tipo_asignado != "Boolean":
                    self.registrar_warning(f"Warning type mismatch: Cannot assign '{tipo_asignado}' to 'Boolean'")
                elif tipo_esperado != "Boolean" and tipo_asignado == "Boolean":
                    self.registrar_warning(f"Warning type mismatch: Cannot assign 'Boolean' to '{tipo_esperado}'")

        # --- BUCLE ORIGINAL DE VALIDACIÓN ---
        while self.token_actual.type not in tokens_parada:
            t_eval = self.token_actual
            
            if t_eval.type == TokenType.PAREN_A:
                parentesis_abiertos += 1
            elif t_eval.type == TokenType.PAREN_C:
                parentesis_abiertos -= 1
                if parentesis_abiertos < 0:
                    self.registrar_warning("Warning unexpected ')'")
                    parentesis_abiertos = 0 
            
            elif t_eval.type in [TokenType.IF, TokenType.THEN, TokenType.MODULE, TokenType.SUB, TokenType.END]:
                self.registrar_warning(f"Warning unexpected keyword '{t_eval.value}' in expression")

            elif t_eval.type == TokenType.UNCLOSED_STRING:
                self.registrar_warning("Warning unclosed string literal")
                
            elif t_eval.type == TokenType.UNCLOSED_CHAR:
                self.registrar_warning("Warning unclosed char literal")
            
            elif t_eval.type == TokenType.INVALID_ID:
                self.registrar_warning(f"Warning undefined varible '{t_eval.value}'")
                
            elif t_eval.type == TokenType.IDENTIFICADOR:
                if not self.tabla.existe(t_eval.value):
                    self.registrar_warning(f"Warning undefine type '{t_eval.value}'")
                    
            self.consumir()
            
        if parentesis_abiertos > 0:
            self.registrar_warning("Warning missing ')'")
        pass

    def analizar_expresion(self):
        # 1. Parseamos el primer bloque (que podría ser una multiplicación/división o solo un número)
        resultado_izquierdo = self.analizar_termino()

        # 2. Si encontramos + o -, iteramos
        while self.token_actual.type in [TokenType.SUMA, TokenType.RESTA]:
            operador = self.token_actual.value
            self.consumir() # Consumimos el símbolo (+ o -)
            
            # Parseamos el bloque de la derecha
            resultado_derecho = self.analizar_termino()
            
            tipo_izq = self._inferir_tipo(resultado_izquierdo)
            tipo_der = self._inferir_tipo(resultado_derecho)
            tipo_resultado = self._consultar_cubo_semantico(tipo_izq, operador, tipo_der)
            
            if tipo_resultado == "ERROR":
                self.registrar_warning(f"Warning type mismatch: Cannot perform '{operador}' between '{tipo_izq}' and '{tipo_der}'")
                tipo_resultado = "Unknown" # Modo pánico para no crashear

            # Creamos un temporal para guardar el resultado de esta suma/resta
            temp = self.generar_temporal()
            self.emitir_cuadruplo(operador, resultado_izquierdo, resultado_derecho, temp)
            
            # El lado izquierdo ahora se convierte en el temporal que acabamos de crear
            # (Para encadenar operaciones como A + B + C)
            resultado_izquierdo = temp

        # Devolvemos la variable o temporal que tiene el resultado final
        return resultado_izquierdo

    def analizar_termino(self):
        # Pedimos un factor (número, variable o paréntesis)
        resultado_izquierdo = self.analizar_factor()

        # Si encontramos * o /, iteramos
        while self.token_actual.type in [TokenType.MULT, TokenType.DIV]:
            operador = self.token_actual.value
            self.consumir()
            
            resultado_derecho = self.analizar_factor()
            
            tipo_izq = self._inferir_tipo(resultado_izquierdo)
            tipo_der = self._inferir_tipo(resultado_derecho)
            tipo_resultado = self._consultar_cubo_semantico(tipo_izq, operador, tipo_der)
            
            if tipo_resultado == "ERROR":
                self.registrar_warning(f"Warning type mismatch: Cannot perform '{operador}' between '{tipo_izq}' and '{tipo_der}'")
                tipo_resultado = "Unknown" # Modo pánico para no crashear

            temp = self.generar_temporal()
            self.emitir_cuadruplo(operador, resultado_izquierdo, resultado_derecho, temp)
            resultado_izquierdo = temp

        return resultado_izquierdo

    def analizar_factor(self):
        t = self.token_actual
        
        # Caso 1: Es un número o una variable
        if t.type in [TokenType.NUMERO, TokenType.IDENTIFICADOR]:
            valor_operando = t.value 
            self.consumir()
            
            if t.type == TokenType.IDENTIFICADOR:
                
                # --- 1. Detectar si es una llamada a función ---
                # Revisamos si existe en el ámbito global (0) y si tiene la bandera 'es_funcion'
                if valor_operando in self.tabla.scopes[0] and self.tabla.scopes[0][valor_operando].get("es_funcion"):
                    info_func = self.tabla.scopes[0][valor_operando]
                    
                    if self.token_actual.type == TokenType.PAREN_A:
                        self.consumir()
                        
                        # A. Preparamos la memoria
                        self.emitir_cuadruplo('ERA', valor_operando, '', '')
                        
                        # B. Procesamos los argumentos
                        k = 0
                        if self.token_actual.type != TokenType.PAREN_C:
                            while True:
                                arg_exp = self.analizar_expresion_logica()
                                tipo_arg = self._inferir_tipo(arg_exp)
                                
                                # Validación semántica de los parámetros
                                if k < len(info_func["parametros"]):
                                    tipo_esperado = info_func["parametros"][k]
                                    if tipo_arg and tipo_arg != "Unknown" and tipo_esperado != tipo_arg:
                                        self.registrar_warning(f"Warning type mismatch: Argument {k+1} of '{valor_operando}' expects '{tipo_esperado}', got '{tipo_arg}'")
                                else:
                                    self.registrar_warning(f"Warning too many arguments for function '{valor_operando}'")
                                
                                # Emitimos el cuádruplo del parámetro
                                self.emitir_cuadruplo('PARAM', arg_exp, '', f'Param{k}')
                                k += 1
                                
                                if self.token_actual.type == TokenType.COMA:
                                    self.consumir()
                                else:
                                    break
                                    
                        if k < len(info_func["parametros"]):
                            self.registrar_warning(f"Warning too few arguments for function '{valor_operando}'")
                            
                        if self.token_actual.type == TokenType.PAREN_C:
                            self.consumir()
                        else:
                            self.registrar_warning(f"Warning missing ')' in call to '{valor_operando}'")
                            
                        # C. Hacemos el salto GOSUB a la línea donde inicia la función
                        self.emitir_cuadruplo('GOSUB', valor_operando, '', f"L{info_func['cuad_inicio']}")
                        
                        # D. Extraemos el valor de retorno a un temporal
                        temp_retorno = self.generar_temporal()
                        self.tipos_temporales[temp_retorno] = info_func["tipo"]
                        
                        # se asigna el "nombre" de la función al temporal
                        self.emitir_cuadruplo('=', valor_operando, '', temp_retorno)
                        
                        return temp_retorno
            
            # --- 2. Detectar si es lectura de un arreglo ---
                info_var = None
                for ambito in reversed(self.tabla.scopes):
                    if valor_operando in ambito:
                        info_var = ambito[valor_operando]
                        break
                        
                if info_var and info_var.get("es_arreglo"):
                    if self.token_actual.type == TokenType.PAREN_A:
                        self.consumir()
                        indice_exp = self.analizar_expresion_logica()
                        
                        if self.token_actual.type == TokenType.PAREN_C:
                            self.consumir()
                        else:
                            self.registrar_warning(f"Warning missing ')' in array access '{valor_operando}'")
                        
                        self.emitir_cuadruplo('VERIF', indice_exp, '0', info_var['limite'])
                        
                        temp_valor = self.generar_temporal()
                        self.tipos_temporales[temp_valor] = info_var['tipo'] 
                        
                        self.emitir_cuadruplo('ACCESO_ARR', valor_operando, indice_exp, temp_valor)
                        
                        return temp_valor
                    else:
                        self.registrar_warning(f"Warning expected index for array '{valor_operando}'")
            # Si no es función ni arreglo, es una variable normal
            return valor_operando
            
        # Caso 2: Es una cadena o booleano (Ajustar según necesites)
        elif t.type in [TokenType.CADENA_LITERAL, TokenType.BOOLEANO_LITERAL, TokenType.CHAR_LITERAL]:
            valor_operando = t.value
            self.consumir()
            return valor_operando

        # Caso 3: Es un paréntesis abierto '('
        elif t.type == TokenType.PAREN_A:
            self.consumir()
            # Llamamos de vuelta a la expresión completa
            valor = self.analizar_expresion_logica()
            
            if self.token_actual.type == TokenType.PAREN_C:
                self.consumir()
            else:
                self.registrar_warning("Warning missing ')' in expression")
            return valor
            
        else:
            self.registrar_warning(f"Warning unexpected token '{t.value}' in expression")
            self.consumir() # Evitar bucles infinitos en modo pánico
            return "ERROR"
    
    def analizar_expresion_logica(self):
        # Primero bajamos al nivel relacional
        resultado_izquierdo = self.analizar_expresion_relacional()

        # Si encontramos un And o un Or, lo procesamos
        while self.token_actual.type in [TokenType.AND, TokenType.OR]:
            operador = self.token_actual.value
            self.consumir()
            
            # Buscamos el lado derecho de la comparación
            resultado_derecho = self.analizar_expresion_relacional()

            tipo_izq = self._inferir_tipo(resultado_izquierdo)
            tipo_der = self._inferir_tipo(resultado_derecho)
            tipo_resultado = self._consultar_cubo_semantico(tipo_izq, operador, tipo_der)
            
            if tipo_resultado == "ERROR":
                self.registrar_warning(f"Warning type mismatch: Cannot perform '{operador}' between '{tipo_izq}' and '{tipo_der}'")
                tipo_resultado = "Unknown" # Modo pánico para no crashear

            # Generamos el temporal booleano
            temp = self.generar_temporal()
            self.emitir_cuadruplo(operador, resultado_izquierdo, resultado_derecho, temp)
            resultado_izquierdo = temp

        return resultado_izquierdo

    def analizar_expresion_relacional(self):
        # Bajamos a las matemáticas normales (+, -)
        resultado_izquierdo = self.analizar_expresion()

        operadores_relacionales = [
            TokenType.MAYOR, TokenType.MENOR, TokenType.MAYOR_IGUAL, 
            TokenType.MENOR_IGUAL, TokenType.IGUAL, TokenType.DIFERENTE, 
            TokenType.IGUAL_LOGICO
        ]

        # A diferencia de la suma, en VB rara vez haces "A > B > C" seguidos,
        # así que usamos un 'if' en lugar de un 'while'
        if self.token_actual.type in operadores_relacionales:
            operador = self.token_actual.value
            self.consumir()
            
            # Buscamos la otra matemática a comparar
            resultado_derecho = self.analizar_expresion()

            tipo_izq = self._inferir_tipo(resultado_izquierdo)
            tipo_der = self._inferir_tipo(resultado_derecho)
            tipo_resultado = self._consultar_cubo_semantico(tipo_izq, operador, tipo_der)
            
            if tipo_resultado == "ERROR":
                self.registrar_warning(f"Warning type mismatch: Cannot perform '{operador}' between '{tipo_izq}' and '{tipo_der}'")
                tipo_resultado = "Unknown" # Modo pánico para no crashear

            # Generamos el temporal booleano
            temp = self.generar_temporal()
            self.emitir_cuadruplo(operador, resultado_izquierdo, resultado_derecho, temp)
            resultado_izquierdo = temp

        return resultado_izquierdo

    def analizar_condicion(self):
        resultado_condicion = self.analizar_expresion_logica()