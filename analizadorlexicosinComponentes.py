import tkinter as tk
from tkinter import ttk
import re

# ---------------- Lógica del Analizador ----------------

instrucciones = {
    "iniciar", "finalizar", "velocidad", "base", "cuerpo",
    "garra", "abrirGarra", "cerrarGarra", "repetir", "Robot"
}

def analizar_lexico(codigo):
    tabla_simbolos = []
    esperando_metodo = False
    patron = r'([a-zA-Z_]\w*|\d+|[=().]|.)'

    for linea in codigo.splitlines():
        tokens = re.findall(patron, linea)
        for token in tokens:
            if token == "Robot":
                tipo = "Palabra_r"
            elif token in instrucciones:
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

            tabla_simbolos.append((token, tipo))
    return tabla_simbolos

# ---------------- Interfaz Gráfica ----------------

def ejecutar_analisis():
    codigo = entrada_texto.get("1.0", tk.END)
    resultado = analizar_lexico(codigo)
    tabla.delete(*tabla.get_children())
    for token, tipo in resultado:
        tabla.insert("", tk.END, values=(token, tipo))

def limpiar():
    entrada_texto.delete("1.0", tk.END)
    tabla.delete(*tabla.get_children())

# Crear ventana
ventana = tk.Tk()
ventana.title("Analizador Léxico")
ventana.configure(bg="#d0e6f6")  # Fondo azul pastel

# Estilo de tabla
style = ttk.Style()
style.theme_use("default")
style.configure("Treeview", 
                background="#e6f2fb", 
                fieldbackground="#e6f2fb", 
                foreground="black",
                rowheight=25)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

# Área de entrada
tk.Label(ventana, text="Código fuente:", bg="#d0e6f6", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=10, pady=(10, 0))
entrada_texto = tk.Text(ventana, height=10, width=60, bg="#f0f8ff", fg="black", font=("Consolas", 10))
entrada_texto.pack(padx=10, pady=5)

# Botones
frame_botones = tk.Frame(ventana, bg="#d0e6f6")
frame_botones.pack(pady=5)

btn_analizar = tk.Button(frame_botones, text="Analizar", command=ejecutar_analisis,
                         bg="#add8e6", fg="black", font=("Segoe UI", 10, "bold"), width=15)
btn_analizar.pack(side="left", padx=10)

btn_limpiar = tk.Button(frame_botones, text="Limpiar", command=limpiar,
                        bg="#add8e6", fg="black", font=("Segoe UI", 10, "bold"), width=15)
btn_limpiar.pack(side="left", padx=10)

# Tabla de símbolos
tk.Label(ventana, text="📘 Tabla de Símbolos:", bg="#d0e6f6", font=("Segoe UI", 10, "bold")).pack(anchor='w', padx=10)
tabla = ttk.Treeview(ventana, columns=("TOKEN", "TIPO"), show='headings')
tabla.heading("TOKEN", text="TOKEN")
tabla.heading("TIPO", text="TIPO")
tabla.pack(padx=10, pady=(0, 10), fill="both")

ventana.mainloop()