import tkinter as tk
from tkinter import ttk
import re

# ------------------- Tabla de métodos conocidos --------------------
metodos_validos = {
    "Garra": True,
    "Cuerpo": True,
    "base": True,
    "iniciar": False,
    "finalizar": True,
    "abrirGarra": True,
    "cerrarGarra": True,
    "velocidad": True,
    "repetir": True
}

# ------------------- Analizador Léxico ------------------------
def analizar_lexico(codigo):
    tabla_simbolos = []
    esperando_metodo = False
    patron = r'([a-zA-Z_]\w*|\d+|[=().])'

    lineas = codigo.splitlines()
    for num_linea, linea in enumerate(lineas, start=1):
        for match in re.finditer(patron, linea):
            token = match.group(1)
            columna = match.start() + 1
            if token == "Robot":
                tipo = "Palabra_r"
            elif token in metodos_validos:
                tipo = "Metodo"
                esperando_metodo = False
            elif token.isdigit():
                tipo = "Numero"
                esperando_metodo = False
            elif token == '.':
                tipo = "Operador"
                esperando_metodo = True
            elif token in {'=', '(', ')'}:
                tipo = "Operador"
                esperando_metodo = False
            elif re.match(r'^[a-zA-Z_]\w*$', token):
                if esperando_metodo:
                    tipo = "Metodo_desconocido"
                    esperando_metodo = False
                else:
                    tipo = "Identificador"
            else:
                tipo = "Desconocido"
                esperando_metodo = False

            tabla_simbolos.append((token, tipo, num_linea, columna))
    return tabla_simbolos

# ------------------ Analizador Sintáctico ----------------------
def analizar_sintactico(tabla_lexica, codigo):
    errores = []
    objeto_robot = None
    tokens = tabla_lexica

    # Detectar declaración del objeto Robot
    for i in range(len(tokens) - 1):
        if tokens[i][0] == "Robot" and tokens[i + 1][1] == "Identificador":
            objeto_robot = tokens[i + 1][0]
            break

    i = 0
    while i < len(tokens):
        if i + 2 < len(tokens):
            t0, t1, t2 = tokens[i], tokens[i+1], tokens[i+2]

            # patrón objeto.metodo
            if t0[0] == objeto_robot and t1[0] == '.' and re.match(r'^[a-zA-Z_]\w*$', t2[0]):
                metodo = t2[0]
                requiere_parametro = metodos_validos.get(metodo, None)

                # Verificar paréntesis de apertura
                if i + 3 >= len(tokens) or tokens[i + 3][0] != '(':
                    errores.append(f"Error de Sintaxis: falta '(' en la llamada a '{metodo}'. Línea {t2[2]}, columna {t2[3]+ len(metodo)}")
                    i += 3
                    continue

                if requiere_parametro is None:
                    # Si el método no está definido, pero tiene una llamada, ya se validó la estructura
                    i += 4
                    continue

                if requiere_parametro:
                    if i + 5 >= len(tokens):
                        errores.append(f"Error de Sintaxis: el método '{metodo}' requiere un número como parámetro. Línea {t2[2]}, columna {t2[3]}")
                        i += 4
                        continue

                    t4, t5 = tokens[i+4], tokens[i+5]

                    if t4[1] != "Numero":
                        errores.append(f"Error de Sintaxis: se espera un número como parámetro para '{metodo}'. Línea {t4[2]}, columna {t4[3]}")

                    if t5[0] != ')':
                        errores.append(f"Error de Sintaxis: falta ')' al final de la llamada a '{metodo}'. Línea {t5[2]}, columna {t5[3]}")

                    i += 6
                else:
                    if i + 4 >= len(tokens) or tokens[i + 4][0] != ')':
                        errores.append(f"Error de Sintaxis: el método '{metodo}' no debe llevar parámetros. Línea {t2[2]}, columna {t2[3]}")
                        i += 4
                    else:
                        i += 5
                continue

            # Caso: falta el punto
            elif t0[0] == objeto_robot and t1[1] == "Metodo":
                errores.append(f"Error de Sintaxis: falta '.' entre objeto y método '{t1[0]}'. Línea {t1[2]}, columna {t1[3]}")
                i += 1
                continue

        i += 1

    # Validar identificadores como rbase que deberían tener punto
    for token in tokens:
        token_str, tipo, linea, columna = token
        if tipo == "Identificador" and objeto_robot:
            for metodo in metodos_validos:
                if token_str == f"{objeto_robot}{metodo}":
                    errores.append(
                        f"Error de Sintaxis: falta '.' entre objeto y método '{metodo}'. Línea {linea}, columna {columna}"
                    )

    return errores


# ------------------ Funciones de Interfaz ---------------------
def mostrar_errores_sintacticos(errores):
    cuadro_errores.config(state="normal")
    cuadro_errores.delete("1.0", tk.END)
    entrada_texto.tag_remove("error", "1.0", tk.END)  # Limpiar marcas anteriores

    if errores:
        mensaje = "\n".join(errores)
        cuadro_errores.insert(tk.END, mensaje)

        # Aplicar marca en rojo en el código fuente
        for error in errores:
            match = re.search(r"Línea (\d+), columna (\d+)", error)
            if match:
                linea = int(match.group(1))
                columna = int(match.group(2))
                start = f"{linea}.{columna-1}"
                end = f"{linea}.{columna-1+1}"
                entrada_texto.tag_add("error", start, end)

    entrada_texto.tag_config("error", foreground="red", underline=1)
    cuadro_errores.config(state="disabled")

def ejecutar_analisis():
    codigo = entrada_texto.get("1.0", tk.END)
    resultado = analizar_lexico(codigo)
    tabla.delete(*tabla.get_children())
    for token, tipo, _, _ in resultado:
        tabla.insert("", tk.END, values=(token, tipo))
    errores = analizar_sintactico(resultado, codigo)
    mostrar_errores_sintacticos(errores)
    actualizar_numeros_linea()

def limpiar():
    entrada_texto.delete("1.0", tk.END)
    tabla.delete(*tabla.get_children())
    cuadro_errores.config(state="normal")
    cuadro_errores.delete("1.0", tk.END)
    cuadro_errores.config(state="disabled")
    actualizar_numeros_linea()

def actualizar_numeros_linea(event=None):
    contenido = entrada_texto.get("1.0", "end-1c")
    lineas = contenido.split("\n")
    numeros_linea.config(state="normal")
    numeros_linea.delete("1.0", "end")
    for i in range(1, len(lineas) + 1):
        numeros_linea.insert("end", f"{i}\n")
    numeros_linea.config(state="disabled")

def sincronizar_scroll(*args):
    entrada_texto.yview(*args)
    numeros_linea.yview(*args)

# ------------------ Interfaz Gráfica --------------------------
ventana = tk.Tk()
ventana.title("Analizador Léxico y Sintáctico")
ventana.configure(bg="#d0e6f6")

style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", background="#e6f2fb", fieldbackground="#e6f2fb", foreground="black", rowheight=25)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

tk.Label(ventana, text="Código fuente:", bg="#d0e6f6", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=10, pady=(10, 0))

frame_texto = tk.Frame(ventana, bg="#d0e6f6")
frame_texto.pack(padx=10, fill="both", expand=True)

numeros_linea = tk.Text(frame_texto, width=4, height=10, bg="#d0e6f6", fg="gray30", font=("Consolas", 10), state="disabled", bd=0)
numeros_linea.pack(side="left", fill="y")

entrada_texto = tk.Text(frame_texto, height=10, bg="#f0f8ff", fg="black", font=("Consolas", 10), wrap="none")
entrada_texto.pack(side="left", fill="both", expand=True)

scroll = tk.Scrollbar(frame_texto, command=sincronizar_scroll)
scroll.pack(side="right", fill="y")
entrada_texto.config(yscrollcommand=scroll.set)
numeros_linea.config(yscrollcommand=scroll.set)

entrada_texto.bind("<KeyRelease>", actualizar_numeros_linea)
entrada_texto.bind("<MouseWheel>", lambda e: actualizar_numeros_linea())

frame_botones = tk.Frame(ventana, bg="#d0e6f6")
frame_botones.pack(pady=5)

btn_analizar = tk.Button(frame_botones, text="Analizar", command=ejecutar_analisis, bg="#add8e6", fg="black", font=("Segoe UI", 10, "bold"), width=15)
btn_analizar.pack(side="left", padx=10)

btn_limpiar = tk.Button(frame_botones, text="Limpiar", command=limpiar, bg="#add8e6", fg="black", font=("Segoe UI", 10, "bold"), width=15)
btn_limpiar.pack(side="left", padx=10)

tk.Label(ventana, text="📘 Tabla de Símbolos:", bg="#d0e6f6", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=10)
tabla = ttk.Treeview(ventana, columns=("TOKEN", "TIPO"), show='headings')
tabla.heading("TOKEN", text="TOKEN")
tabla.heading("TIPO", text="TIPO")
tabla.pack(padx=10, pady=(0, 10), fill="both")

tk.Label(ventana, text="⚠️ Errores de Sintaxis:", bg="#d0e6f6", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=10, pady=(10, 0))
cuadro_errores = tk.Text(ventana, height=6, bg="#fff5f5", fg="black", font=("Consolas", 10))
cuadro_errores.pack(padx=10, pady=(0, 10), fill="both")
cuadro_errores.config(state="disabled")

actualizar_numeros_linea()
ventana.mainloop()