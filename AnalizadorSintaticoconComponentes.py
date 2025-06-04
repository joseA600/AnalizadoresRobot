import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk
import ply.lex as lex
import ply.yacc as yacc

# ==== Lista de tokens ====
tokens = (
    'ROBOT',
    'ID',
    'PUNTO',
    'METODO',
    'NUMERO',
    'PAREN_IZQ',
    'PAREN_DER'
)

# ==== Instrucciones válidas ====
instrucciones = {
    "iniciar": {"tipo": "accion", "parametros": False},
    "finalizar": {"tipo": "accion", "parametros": False},
    "velocidad": {"tipo": "metodo", "parametros": True},
    "base": {"tipo": "metodo", "parametros": True},
    "cuerpo": {"tipo": "metodo", "parametros": True},
    "garra": {"tipo": "metodo", "parametros": True},
    "abrirGarra": {"tipo": "metodo", "parametros": False},
    "cerrarGarra": {"tipo": "metodo", "parametros": False},
    "repetir": {"tipo": "metodo", "parametros": True}
}

# ==== Tabla de símbolos ====
tabla_simbolos = []
errores = []
linea_actual= 1
tokens_lexicos=[]
# ==== Reglas del lexer ====
t_PUNTO = r'\.'
t_PAREN_IZQ = r'\('
t_PAREN_DER = r'\)'
t_ignore = ' \t'

def t_ROBOT(t):
    r'Robot'
    return t

def t_METODO(t):
    r'iniciar|finalizar|velocidad|base|cuerpo|garra|abrirGarra|cerrarGarra|repetir'
    return t

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_COMMENT(t):
    r'\#.*'
    pass  # ignorar comentarios

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    errores.append(f"❌ Carácter ilegal '{t.value[0]}' en línea {t.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# Reglas de el parser sintatico
def p_inicio(p):
    '''inicio : instruccion
              | instruccion inicio'''
    pass

def p_instruccion(p):
    '''instruccion : declaracion_robot
                  | metodo_sin_parametro
                  | metodo_con_parametro'''
    pass

def p_declaracion_robot (p):
    'declaracion_robot : ROBOT ID'
    try:
        linea = p.lineno(1)  # Línea donde aparece "Robot"
        tabla_simbolos.extend([
            ("Robot", "Palabra_r", "", "", linea),
            (p[2], "identificador", "", "", linea)
        ])
    except Exception as e:
        errores.append(f"Error declarando robot: {str(e)}")

def p_metodo_sin_parametro(p):
    '''metodo_sin_parametro : ID PUNTO METODO
                             | ID PUNTO METODO PAREN_IZQ PAREN_DER'''
    
    metodo = p[3]
    linea = p.lineno(1)
    
    if metodo not in instrucciones:
        errores.append(f"Método desconocido '{metodo}' (línea {linea})")
    elif instrucciones[metodo]["parametros"]:
        errores.append(f"El método '{metodo}' requiere parámetros (línea {linea})")
    else:
        tabla_simbolos.append((p[1], "identificador", "", "No", linea))
        
        if metodo in ["iniciar", "finalizar"]:
            if len(p) == 4:  # Sin paréntesis
                tabla_simbolos.append((metodo, "Método", "", "No", linea))
            else:  # Con paréntesis vacíos
                tabla_simbolos.append((metodo, "Método", "()", "No", linea))
        else:
            tabla_simbolos.append((metodo, "Método", "()", "No", linea))
            
def p_metodo_con_parametro(p):
    'metodo_con_parametro : ID PUNTO METODO PAREN_IZQ NUMERO PAREN_DER'
    try:
        linea = p.lineno(1)
        metodo = p[3]
        valor = p[5]
        
        if metodo not in instrucciones:
            errores.append(f"Error léxico: método '{metodo}' no existe (línea {linea})")
        elif not instrucciones[metodo]["parametros"]:
            errores.append(f"Error sintáctico: '{metodo}' no acepta parámetros (línea {linea})")
        else:
            tabla_simbolos.extend([
                (p[1], "identificador", "", "Sí", linea),
                (metodo, "Método", str(valor), "Sí", linea)
            ])
    except Exception as e:
        errores.append(f"Error interno procesando instrucción: {str(e)}")

def p_error(p):
    if p:
        errores.append(f"❌ Error de sintaxis con el token '{p.value}' en línea {p.lineno}")
    else:
        errores.append("❌ Error de sintaxis: entrada incompleta o inesperada")

parser = yacc.yacc()
 

# ==== Función para analizar código ====
def analizar_codigo():
    global tabla_simbolos, errores, tokens_lexicos, linea_actual
    tabla_simbolos = []
    errores = []
    tokens_lexicos = []

    codigo = entrada_texto.get("1.0", tk.END)
    lineas = codigo.splitlines()
    
    for i, linea in enumerate(lineas, start=1):
        if linea.strip() == "":
            continue  # Saltar líneas vacías
        
        lexer.lineno = i  # Asignar correctamente la línea actual
        lexer.input(linea)
        
        while True:
            tok = lexer.token()
            if not tok:
                break
            tokens_lexicos.append((tok.type, tok.value, tok.lineno))
        
        try:
            parser.parse(linea)
        except Exception as e:
            errores.append(f"❌ Error procesando la línea {i}: {str(e)}")

    mostrar_resultados()

# ==== Función para mostrar resultados ====
def mostrar_resultados():
    # Limpiar tablas
    tree.delete(*tree.get_children())
    tree_errores.delete(*tree_errores.get_children())
    
    # Insertar tokens y símbolos
    for simbolo in tabla_simbolos:
        tree.insert("", tk.END, values=simbolo)
    
    # Insertar errores
    for err in errores:
        if "línea" in err:
            try:
                # Extraer el token y la línea del mensaje
                token = err.split("token")[-1].split("en")[0].strip().strip("'")
                linea = err.split("línea")[-1].strip()
                mensaje = f"❌ Error de sintaxis en '{token}' en la línea {linea}"
                tree_errores.insert("", tk.END, values=(mensaje,))
            except:
                tree_errores.insert("", tk.END, values=(err,))
        else:
            tree_errores.insert("", tk.END, values=(err,))


# Función para actualizar los números de línea
def actualizar_lineas(event=None):
    line_numbers.config(state='normal')  # Habilitar edición de los números de línea
    line_numbers.delete('1.0', 'end')  # Limpiar los números de línea actuales
    
    # Obtener la cantidad de líneas en el área de texto
    line_count = entrada_texto.index('end-1c').split('.')[0]
    
    # Generar los números de línea
    line_numbers_txt = "\n".join(str(i) for i in range(1, int(line_count)+1))
    
    # Insertar los números de línea en el widget
    line_numbers.insert('1.0', line_numbers_txt)
    
    line_numbers.config(state='disabled')  # Deshabilitar la edición de los números de línea

# ==== Configuración de la interfaz ====
ventana = tk.Tk()
ventana.title("Analizador de Código de Robot")
ventana.geometry("900x600")
ventana.resizable(False, False)


# Antes del frame_entrada, creamos frame para líneas + texto
frame_codigo = tk.Frame(ventana)
frame_codigo.pack(pady=10, padx=10, fill=tk.BOTH, expand=False)

# Widget para números de línea
line_numbers = tk.Text(frame_codigo, width=4, height=10, padx=3, takefocus=0, border=0,
                       background='lightgrey', state='disabled', wrap='none')
line_numbers.pack(side='left', fill='y')

# Área de texto para código
entrada_texto = scrolledtext.ScrolledText(frame_codigo, width=86, height=10, font=("Consolas", 12))
entrada_texto.pack(side='right', fill='both', expand=True)

# Asociar la función de actualización de los números de línea al evento de presionar Enter
entrada_texto.bind('<KeyRelease-Return>', actualizar_lineas)

# Iniciar la actualización de los números de línea cuando se cargue la ventana
actualizar_lineas()

# Función para actualizar números de línea
def actualizar_lineas(event=None):
    line_numbers.config(state='normal')
    line_numbers.delete('1.0', 'end')
    line_count = entrada_texto.index('end-1c').split('.')[0]
    line_numbers_txt = "\n".join(str(i) for i in range(1, int(line_count)+1))
    line_numbers.insert('1.0', line_numbers_txt)
    line_numbers.config(state='disabled')
entrada_texto.bind('<KeyRelease>', actualizar_lineas)

actualizar_lineas()

# Botón analizar
boton_analizar = tk.Button(ventana, text="Analizar", command=analizar_codigo, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white")
boton_analizar.pack(pady=10)

# Frame para tablas
frame_tablas = tk.Frame(ventana)
frame_tablas.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)



# Tabla de símbolos (izquierda)
frame_simbolos = tk.Frame(frame_tablas)
frame_simbolos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

label_simbolos = tk.Label(frame_simbolos, text="Tabla de Tokens y Símbolos", font=("Arial", 12, "bold"))
label_simbolos.pack()

# Treeview con scrollbar para símbolos
tree_scroll = ttk.Scrollbar(frame_simbolos)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
tree = ttk.Treeview(frame_simbolos, yscrollcommand=tree_scroll.set,
                   columns=("Nombre", "Tipo", "Valor", "Parámetro"), 
                   show='headings', height=15)
tree.pack(fill=tk.BOTH, expand=True)
tree_scroll.config(command=tree.yview)

# Configurar columnas
for col in ["Nombre", "Tipo", "Valor", "Parámetro"]:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor='center')


# Tabla de errores (derecha)
frame_errores = tk.Frame(frame_tablas)
frame_errores.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

label_errores = tk.Label(frame_errores, text="Tabla de Errores", 
                        font=("Arial", 12, "bold"), fg="red")
label_errores.pack()



# Treeview con scrollbar para errores
error_scroll = ttk.Scrollbar(frame_errores)
error_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree_errores = ttk.Treeview(frame_errores, yscrollcommand=error_scroll.set,
                          columns=("Error",), show='headings', height=15)
tree_errores.pack(fill=tk.BOTH, expand=True)

error_scroll.config(command=tree_errores.yview)

tree_errores.heading("Error", text="Error")
tree_errores.column("Error", width=400, anchor='w')

ventana.mainloop()

# Fin del código
