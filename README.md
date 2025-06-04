
# 🤖 AnalizadoresRobot

¡Hola! 👋 Este proyecto lo hicimos en equipo con mi compañero Heber como parte de la materia de **Lenguajes y Autómatas**.  
En este proyecto se trabajó con analizadores léxicos y sintácticos usando **Python** y la librería **PLY** (Lex & Yacc en Python).  
Todos los analizadores tienen interfaz, así que no es solo consola. 😎

## 📁 Archivos del proyecto

- `AnalizadorLexicoConComponentes.py`: Analizador léxico con interfaz gráfica y componentes extra para ver los tokens.
- `analizadorlexicosinComponentes.py`: La versión básica del analizador léxico, sin interfaz.
- `AnalizadorSintacticoconComponentes.py`: Analizador sintáctico con interfaz incluida. ¡Muy útil para ver el análisis paso a paso!
- `AnalizadorSintacticosinComponentes.py`: Versión sencilla del analizador sintáctico.
- `parsetab.py` y `parser.out`: Archivos generados automáticamente por PLY al compilar la gramática.
- `README.md`: Este archivo que estás leyendo. 😄

## 🧠 ¿Para qué sirve?

Este proyecto es como una mini simulación de cómo funcionan los compiladores.  
Aprendemos a dividir el código en tokens (léxico) y a ver si cumple las reglas del lenguaje (sintáctico).  
Básicamente, todo lo que vemos en la materia ¡pero funcionando de verdad!

## ▶️ Cómo correrlo

1. Asegúrate de tener Python 3 y la librería `ply` instalada:

   ```bash
   pip install ply
   ```

2. Luego solo ejecutas el analizador que quieras, por ejemplo:

   ```bash
   python AnalizadorLexicoConComponentes.py
   ```

3. Y listo, se abre la interfaz. 🚀
