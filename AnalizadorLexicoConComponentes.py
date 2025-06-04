import tkinter as tk
from tkinter import scrolledtext, ttk
import ply.lex as lex

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

# ==== Reglas del lexer ====
t_PUNTO = r'\.'
t_PAREN_IZQ = r'\('
t_PAREN_DER = r'\)'
t_ignore = ' \t' # Ignorar espacios y tabulaciones

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
    pass  # Ignorar comentarios de línea

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    # Los errores léxicos se registran internamente, pero no se muestran en la GUI ni en consola.
    # Esto cumple con la solicitud de no mostrar errores.
    t.lexer.skip(1) # Saltar el carácter ilegal para continuar el análisis

# Construir el lexer
lexer = lex.lex()

# ==== Lista para almacenar los tokens léxicos ====
# Esta lista será la fuente de datos para la tabla en la GUI
tokens_lexicos_encontrados = []

# ==== Función para analizar código ====
def analizar_codigo():
    global tokens_lexicos_encontrados
    tokens_lexicos_encontrados = [] # Limpiar la lista de tokens en cada análisis

    codigo = entrada_texto.get("1.0", tk.END)
    
    lexer.lineno = 1 # Reiniciar el contador de línea del lexer
    lexer.input(codigo) # Pasar todo el código al lexer

    # Iterar sobre todos los tokens encontrados por el lexer
    while True:
        tok = lexer.token()
        if not tok:
            break # No hay más tokens
        tokens_lexicos_encontrados.append((tok.type, tok.value, tok.lineno))
    
    mostrar_resultados()

# ==== Función para mostrar resultados ====
def mostrar_resultados():
    # Limpiar la tabla de tokens
    tree_tokens.delete(*tree_tokens.get_children())
    
    # Insertar los tokens encontrados en la tabla
    for tok_type, tok_value, tok_lineno in tokens_lexicos_encontrados:
        tree_tokens.insert("", tk.END, values=(tok_type, tok_value, tok_lineno))

# Función para actualizar los números de línea en el widget de líneas
def actualizar_lineas(event=None):
    line_numbers.config(state='normal')
    line_numbers.delete('1.0', 'end')
    
    # Obtener el número de líneas en el área de texto principal
    line_count = entrada_texto.index('end-1c').split('.')[0]
    
    # Generar el texto con los números de línea
    line_numbers_txt = "\n".join(str(i) for i in range(1, int(line_count) + 1))
    
    # Insertar los números de línea
    line_numbers.insert('1.0', line_numbers_txt)
    
    line_numbers.config(state='disabled') # Deshabilitar edición de los números de línea

# ==== Configuración de la interfaz de usuario ====
ventana = tk.Tk()
ventana.title("Analizador Léxico de Robot")
ventana.geometry("900x600")
ventana.resizable(False, False)

# Frame para los números de línea y el área de texto del código
frame_codigo = tk.Frame(ventana)
frame_codigo.pack(pady=10, padx=10, fill=tk.BOTH, expand=False)

# Widget para mostrar los números de línea
line_numbers = tk.Text(frame_codigo, width=4, height=10, padx=3, takefocus=0, border=0,
                        background='lightgrey', state='disabled', wrap='none')
line_numbers.pack(side='left', fill='y')

# Área de texto para que el usuario ingrese el código
entrada_texto = scrolledtext.ScrolledText(frame_codigo, width=86, height=10, font=("Consolas", 12))
entrada_texto.pack(side='right', fill='both', expand=True)

# Asociar la función de actualización de líneas a eventos de teclado
entrada_texto.bind('<KeyRelease>', actualizar_lineas)

# Realizar una actualización inicial de los números de línea
actualizar_lineas()

# Botón para iniciar el análisis
boton_analizar = tk.Button(ventana, text="Analizar", command=analizar_codigo, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white")
boton_analizar.pack(pady=10)

# Frame para la tabla de tokens
frame_tokens = tk.Frame(ventana)
frame_tokens.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

label_tokens = tk.Label(frame_tokens, text="Tabla de Tokens", font=("Arial", 12, "bold"))
label_tokens.pack()

# Treeview con scrollbar para la tabla de tokens
tree_scroll = ttk.Scrollbar(frame_tokens)
tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

tree_tokens = ttk.Treeview(frame_tokens, yscrollcommand=tree_scroll.set,
                    columns=("Tipo de Token", "Valor del Token", "Línea"), 
                    show='headings', height=15)
tree_tokens.pack(fill=tk.BOTH, expand=True)
tree_scroll.config(command=tree_tokens.yview)

# Configurar las columnas de la tabla de tokens
for col in ["Tipo de Token", "Valor del Token", "Línea"]:
    tree_tokens.heading(col, text=col)
    tree_tokens.column(col, width=150, anchor='center') # Ancho ajustado para mejor visualización

# Iniciar el bucle principal de la aplicación Tkinter
ventana.mainloop()