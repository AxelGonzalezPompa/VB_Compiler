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
            "while": TokenType.WHILE
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

    def declarar(self, nombre, tipo):
        ambito_actual = self.scopes[-1]
        
        if nombre in ambito_actual:
            return False, ambito_actual[nombre]["tipo"]
        
        # Cálculo de dirección de memoria como en semantica.py
        direccion = self.direccion_actual
        ambito_actual[nombre] = {"tipo": tipo, "dir": direccion}
        
        # Incremento de la dirección según el tamaño del tipo
        tamano = self.tamanos.get(tipo, 4) # 4 por defecto si no lo encuentra
        self.direccion_actual += tamano
        
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
            TokenType.WHILE: self._analizar_while
        }

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
            "tabla": self.obtener_formato_tabla()
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
        
        self.analizar_condicion()
        
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
                else:
                    self.registrar_warning("Warning unexpected 'End While'")
        
        elif self.token_actual.type == TokenType.SUB:
            self.consumir()
            if not self.en_sub:
                self.registrar_warning("Warning unexpected 'End Sub'")
            self.en_sub = False
            self.tabla.salir_ambito()
        
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
                
                exito, tipo_previo = self.tabla.declarar(nombre_var, tipo_var_str)
                if not exito:
                    self.registrar_warning(f"Warning ambiguity '{tipo_var_str[:3].lower()}' to '{tipo_previo[:3].lower()}'")
                
                if self.token_actual.type == TokenType.IGUAL:
                    self.consumir()
                    self.saltar_expresion() 
        else:
            self.saltar_expresion()

    def _analizar_identificador(self):
        nombre_var = self.token_actual.value
        self.consumir()
        tipo_esperado = self.tabla.obtener_tipo(nombre_var)
        if not self.tabla.existe(nombre_var):
            self.registrar_warning(f"Warning undefine type '{nombre_var}'")
        if self.token_actual.type == TokenType.IGUAL:
            self.consumir()
            self.saltar_expresion(tipo_esperado=tipo_esperado)

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

            if self.token_actual.type == TokenType.IGUAL:
                self.consumir()
                self.saltar_expresion(tokens_parada=[TokenType.TO, TokenType.NUEVA_LINEA, TokenType.FIN])
            else:
                self.registrar_warning("Warning expected '=' after loop variable")

            if self.token_actual.type == TokenType.TO:
                self.consumir()
                self.saltar_expresion(tokens_parada=[TokenType.STEP, TokenType.NUEVA_LINEA, TokenType.FIN])
            else:
                self.registrar_warning("Warning expected 'To' in 'For' statement")

            if self.token_actual.type == TokenType.STEP:
                self.consumir()
                self.saltar_expresion()

            self.pila_fors.append(linea_inicio_for)
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

        # Validación de anidamiento cruzado
        if estructura_top and estructura_top != "For":
            self.registrar_warning(f"Warning scope error: Cannot use 'Next', currently inside an unclosed '{estructura_top}' block")
        else:
            if len(self.pila_fors) > 0:
                self.pila_fors.pop()
                self.pila_estructuras_abiertas.pop() # Quitamos el For de la pila universal
                self.tabla.salir_ambito()
            else:
                self.registrar_warning("Warning unexpected 'Next'")

    def _analizar_while(self):
        linea_inicio_while = self.token_actual.linea
        self.consumir() # Consumimos la palabra 'While'

        # Opcional: Permitir paréntesis estilo While (x < 10) o While x < 10
        uso_parentesis = False
        if self.token_actual.type == TokenType.PAREN_A:
            uso_parentesis = True
            self.consumir()
        
        # Reciclamos tu evaluador de condiciones
        self.analizar_condicion()
        
        if uso_parentesis:
            if self.token_actual.type == TokenType.PAREN_C:
                self.consumir()
            else:
                self.registrar_warning("Warning missing ')' in condition")
            
        # Registramos que abrimos un bloque While y entramos a un nuevo ámbito local
        self.pila_whiles.append(linea_inicio_while)
        self.pila_estructuras_abiertas.append("While")
        self.tabla.entrar_ambito()

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

    def analizar_condicion(self):
        operandos_validos = [TokenType.IDENTIFICADOR, TokenType.NUMERO, TokenType.CADENA_LITERAL, TokenType.BOOLEANO_LITERAL]
        operadores_relacionales = [TokenType.IGUAL_LOGICO, TokenType.IGUAL, TokenType.MAYOR, TokenType.MENOR, 
                                   TokenType.MAYOR_IGUAL, TokenType.MENOR_IGUAL, TokenType.DIFERENTE]
        
        # --- NUEVA DETECCIÓN PARA EL CASO 2: Operador al inicio ---
        if self.token_actual.type in operadores_relacionales:
            self.registrar_warning(f"Warning invalid condition order: unexpected operator '{self.token_actual.value}' at the start")
            
            # MODO PÁNICO: Consumimos la "basura" hasta encontrar el 'Then' o el final de línea
            # para que el compilador pueda seguir analizando el resto del código sin tropezarse.
            while self.token_actual.type not in [TokenType.THEN, TokenType.PAREN_C, TokenType.NUEVA_LINEA, TokenType.FIN]:
                self.consumir()
            return
            
        # Validar primer operando (Flujo normal)
        if self.token_actual.type not in operandos_validos:
            self.registrar_warning("Warning missing variable or constant in condition")
            # Modo pánico por si escriben basura en lugar de una variable
            while self.token_actual.type not in [TokenType.THEN, TokenType.PAREN_C, TokenType.NUEVA_LINEA, TokenType.FIN]:
                self.consumir()
            return
            
        if self.token_actual.type == TokenType.IDENTIFICADOR:
            if not self.tabla.existe(self.token_actual.value):
                self.registrar_warning(f"Warning undefine type '{self.token_actual.value}'")
        self.consumir() # Consumimos la variable
        
        # Validar operador relacional
        if self.token_actual.type in operadores_relacionales:
            self.consumir() # Consumimos el operador (ej. ==)
            
            # Validar segundo operando
            if self.token_actual.type not in operandos_validos:
                self.registrar_warning("Warning invalid or missing operand in condition")
                # Modo pánico si falta el operando final
                while self.token_actual.type not in [TokenType.THEN, TokenType.PAREN_C, TokenType.NUEVA_LINEA, TokenType.FIN]:
                    self.consumir()
            else:
                if self.token_actual.type == TokenType.IDENTIFICADOR:
                    if not self.tabla.existe(self.token_actual.value):
                        self.registrar_warning(f"Warning undefine type '{self.token_actual.value}'")
                self.consumir() # Consumimos el segundo operando
        else:
            self.registrar_warning("Warning missing relational operator in condition")
            # Modo pánico
            while self.token_actual.type not in [TokenType.THEN, TokenType.PAREN_C, TokenType.NUEVA_LINEA, TokenType.FIN]:
                self.consumir()