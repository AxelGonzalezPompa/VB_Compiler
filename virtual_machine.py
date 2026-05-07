class VirtualMachine:
    def __init__(self, cuadruplos, tabla_simbolos):
        self.cuadruplos = cuadruplos
        self.tabla = tabla_simbolos
        self.memoria = {}  # Nuestra "Memoria RAM" principal
        self.ip = 0        # Instruction Pointer (Apunta al cuádruplo actual)
        self.pila_saltos_llamadas = []

    def _obtener_valor(self, operando):
        """Convierte literales a su valor real o extrae el valor de la RAM"""
        op_str = str(operando)
        
        # 1. Literales numéricos
        if op_str.replace('.', '', 1).isdigit():
            return float(op_str) if '.' in op_str else int(op_str)
            
        # 2. Literales de texto
        if op_str.startswith('"') and op_str.endswith('"'):
            return op_str[1:-1]
        if op_str.startswith("'") and op_str.endswith("'"):
            return op_str[1:-1]
            
        # 3. Literales booleanos
        if op_str == 'True': return True
        if op_str == 'False': return False

        # 4. Es una variable o temporal, la buscamos en la RAM
        # Si no se ha inicializado en VB, por defecto es 0 (o vacío)
        return self.memoria.get(op_str, 0)

    def ejecutar(self):
        print("\n" + "="*40)
        print(" INICIANDO MÁQUINA VIRTUAL ".center(40, "="))
        print("="*40 + "\n")

        while self.ip < len(self.cuadruplos):
            cuad = self.cuadruplos[self.ip]
            op = cuad[0]
            arg1 = cuad[1]
            arg2 = cuad[2]
            res = cuad[3]

            try:
                # --- OPERACIONES MATEMÁTICAS ---
                if op == '+': self.memoria[res] = self._obtener_valor(arg1) + self._obtener_valor(arg2)
                elif op == '-': self.memoria[res] = self._obtener_valor(arg1) - self._obtener_valor(arg2)
                elif op == '*': self.memoria[res] = self._obtener_valor(arg1) * self._obtener_valor(arg2)
                elif op == '/': 
                    divisor = self._obtener_valor(arg2)
                    if divisor == 0: raise Exception("Error de ejecución: División por cero")
                    self.memoria[res] = self._obtener_valor(arg1) / divisor
                
                # --- ASIGNACIÓN BÁSICA ---
                elif op == '=':
                    self.memoria[res] = self._obtener_valor(arg1)

                # --- OPERACIONES LÓGICAS Y RELACIONALES ---
                elif op == '>': self.memoria[res] = self._obtener_valor(arg1) > self._obtener_valor(arg2)
                elif op == '<': self.memoria[res] = self._obtener_valor(arg1) < self._obtener_valor(arg2)
                elif op == '>=': self.memoria[res] = self._obtener_valor(arg1) >= self._obtener_valor(arg2)
                elif op == '<=': self.memoria[res] = self._obtener_valor(arg1) <= self._obtener_valor(arg2)
                elif op == '==': self.memoria[res] = self._obtener_valor(arg1) == self._obtener_valor(arg2)
                elif op == '<>': self.memoria[res] = self._obtener_valor(arg1) != self._obtener_valor(arg2)
                elif op == 'And': self.memoria[res] = bool(self._obtener_valor(arg1)) and bool(self._obtener_valor(arg2))
                elif op == 'Or': self.memoria[res] = bool(self._obtener_valor(arg1)) or bool(self._obtener_valor(arg2))

                # --- CONTROL DE FLUJO (LOS SALTOS MÁGICOS) ---
                elif op == 'GOTO':
                    destino = int(res[1:]) # Le quitamos la 'L' y lo convertimos a entero
                    self.ip = destino
                    continue # Usamos continue para evitar que el IP sume 1 al final
                    
                elif op == 'GOTOF':
                    condicion = self._obtener_valor(arg1)
                    if not condicion: # Si es Falso, saltamos
                        destino = int(res[1:])
                        self.ip = destino
                        continue

                # --- MANEJO DE ARREGLOS ---
                elif op == 'VERIF':
                    indice = self._obtener_valor(arg1)
                    limite = int(res)
                    if indice < 0 or indice > limite:
                        raise Exception(f"Error de ejecución: Índice de arreglo fuera de rango ({indice}). Límite: {limite}")
                        
                elif op == 'ASIG_ARR':
                    valor_a_guardar = self._obtener_valor(arg1)
                    indice = self._obtener_valor(arg2)
                    direccion_virtual = f"{res}[{indice}]" # Guardamos como "calificaciones[5]"
                    self.memoria[direccion_virtual] = valor_a_guardar
                    
                elif op == 'ACCESO_ARR':
                    indice = self._obtener_valor(arg2)
                    direccion_virtual = f"{arg1}[{indice}]"
                    self.memoria[res] = self.memoria.get(direccion_virtual, 0)
                
                # --- LLAMADAS A FUNCIONES ---
                elif op == 'ERA':
                    # Para un proyecto básico, la memoria plana de Python maneja
                    # el contexto global suficientemente bien.
                    pass 

                elif op == 'PARAM':
                    # arg1 es el valor (ej. 5), res es el nombre real ('a')
                    self.memoria[res] = self._obtener_valor(arg1)

                elif op == 'GOSUB':
                    # 1. Guardamos la instrucción a la que debe regresar (IP actual + 1)
                    self.pila_saltos_llamadas.append(self.ip + 1)
                    # 2. Saltamos a la función
                    destino = int(res[1:])
                    self.ip = destino
                    continue # Importante: evitamos el self.ip += 1 del final

                elif op == 'RETURN':
                    # arg1 es lo que se devuelve, res es el nombre de la función
                    valor_retorno = self._obtener_valor(arg1)
                    self.memoria[res] = valor_retorno

                elif op == 'ENDFUNC':
                    # Sacamos el hilo de Ariadna para regresar a donde estábamos
                    if self.pila_saltos_llamadas:
                        self.ip = self.pila_saltos_llamadas.pop()
                        continue
                
                # --- FUNCIONES DE CONSOLA ---
                elif op == 'PRINT':
                    val1 = self._obtener_valor(arg1)
                    # Usamos print normal, que el IDE redirigirá a la caja de texto
                    print(f">> {val1}")

            except Exception as e:
                print(f"\n[CRASH EN LÍNEA INTERNA {self.ip}]: {e}")
                break

            self.ip += 1 # Avanzamos al siguiente cuádruplo

        print("\n" + "="*40)
        print(" EJECUCIÓN TERMINADA ".center(40, "="))
        print("="*40)
        
        print("\n--- VOLCADO DE MEMORIA FINAL (Solo Variables) ---")
        for var, val in self.memoria.items():
            if not var.startswith('T'): # Ocultamos los temporales (T1, T2...) para limpiar la vista
                print(f"  > {var} = {val}")