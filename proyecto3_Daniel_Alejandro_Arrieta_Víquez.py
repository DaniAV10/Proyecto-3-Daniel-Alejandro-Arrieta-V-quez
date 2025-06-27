#proyecto3_Daniel_Alejandro_Arrieta_Víquez

"""
Fácil: Tableros con menos pistas y claves; sumas más pequeñas; grupos de 2 o 3 casillas; resolución sencilla.

Medio: Aumenta el número de claves; sumas más altas; grupos de hasta 4 casillas; dificultad intermedia.

Difícil: Claves con sumas altas cercanas al máximo; grupos de 4 casillas; tableros más llenos; resolución desafiante.

Experto: Tableros muy densos con muchas claves y grupos grandes (4 casillas); sumas siempre altas y complejas; máxima dificultad.
"""

import tkinter as tk
from tkinter import messagebox
import time, json
import random #Para cargar una partida
import unicodedata #Normalizar texto
from PIL import Image, ImageTk
from tkinter import font


#----------FUNCIÓN MENÚ PRINCIPAL-----------------------#

def mostrar_menu_principal():
    menu = tk.Tk()
    menu.configure (background="#9bbc0f")
    menu.title("Menú Principal Kakuro - Daniel Alejandro Arrieta Víquez")
    menu.geometry("500x500") # Se aumenta el alto para ver las otras opciones
    menu.resizable(False,False)

    #Colores retro Game Boy
    color_fondo = "#9bbc0f" 
    color_oscuro = "#0f380f"  
    color_boton = "#8bac0f"
    color_hover = "#306230"

    fuente_pixel = font.Font(family="Press Start 2P", size=10)


    tk.Label(menu, text="KAKURO", font=fuente_pixel, bg=color_oscuro, fg="white", pady=20).pack(pady=(20, 10), fill='x')

    #Función para estilo de botón retro
    def crear_boton(texto, comando):
        btn = tk.Button(menu, text=texto, font=fuente_pixel,
                        width=30, height=2,
                        bg=color_boton, fg=color_oscuro,
                        activebackground=color_hover, activeforeground="white",
                        relief="ridge", bd=5,
                        command=comando)
        btn.pack(pady=6)
        btn.bind("<Enter>", lambda e: btn.config(bg=color_hover, fg="white"))
        btn.bind("<Leave>", lambda e: btn.config(bg=color_boton, fg=color_oscuro))



    crear_boton("Opción A: Jugar", lambda: [menu.destroy(), iniciar_juego()])
    crear_boton("Opción B: Configurar", mostrar_configuracion)
    crear_boton("Opción C: Ayuda", lambda: messagebox.showinfo("Ayuda", "Aún no implementado"))
    crear_boton("Opción D: Acerca de", lambda: messagebox.showinfo("Acerca de", "Aún no implementado"))
    crear_boton("Opción E: Salir", menu.destroy)

    tk.Label(menu, text="-Daniel Alejandro Arrieta Víquez-", font=fuente_pixel, bg=color_oscuro, fg="white", pady=20).pack(pady=(20, 10), fill='x')



def formatear_tiempo(segundos):
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60
    return f"{horas:02d}:{minutos:02d}:{segs:02d}"

#--------------FUNCIÓN INICIAR JUEGO------------------#
def iniciar_juego():
    global ventana, modo_tiempo, label_tiempo, tiempo_mostrado
    global entrada_horas_juego, entrada_minutos_juego, entrada_segundos_juego
    global TIEMPO_LIMITE, id_reloj, nivel_actual, entrada_nombre
    global botones_numeros, botones_tablero, modo_borrador, boton_iniciar
    global pila_jugadas, pila_deshacer, valores_tablero, juego_activo, tiempo_inicio
    global numero_elegido

    ventana = tk.Tk()
    ventana.title("Kakuro-Daniel Alejandro Arrieta Víquez")
    ventana.geometry("800x730")
    ventana.resizable(False, False)

    tiempo_mostrado = tk.StringVar(value="00:00:00")
    entrada_nombre = tk.StringVar()

    nivel_actual = "facil"
    try:
        with open("kakuro2025_configuración.json") as f:
            config = json.load(f)
            modo_tiempo_valor = config.get("reloj", "sin_reloj")
            h = config.get("horas", 0)
            m = config.get("minutos", 0)
            s = config.get("segundos", 0)
            nivel_actual = normalizar_texto(config.get("nivel", "fácil"))
    except:
        modo_tiempo_valor = "sin_reloj"
        h = m = s = 0

    modo_tiempo = tk.StringVar(value=modo_tiempo_valor)
    modo_tiempo.trace_add("write", actualizar_visibilidad_reloj)

    label_tiempo = tk.Label(ventana, textvariable=tiempo_mostrado, font=("Courier", 14), bg='white')
    label_tiempo.place(x=350, y=660)

    entrada_horas_juego = tk.Entry(ventana, width=3)
    entrada_minutos_juego = tk.Entry(ventana, width=3)
    entrada_segundos_juego = tk.Entry(ventana, width=3)

    if modo_tiempo.get() == "temporizador":
        tk.Label(ventana, text="Horas:").place(x=50, y=645)
        entrada_horas_juego.place(x=50, y=680)
        entrada_horas_juego.insert(0, str(h))

        tk.Label(ventana, text="Minutos:").place(x=100, y=645)
        entrada_minutos_juego.place(x=100, y=680)
        entrada_minutos_juego.insert(0, str(m))

        tk.Label(ventana, text="Segundos:").place(x=160, y=645)
        entrada_segundos_juego.place(x=160, y=680)
        entrada_segundos_juego.insert(0, str(s))
    else:
        entrada_horas_juego.place_forget()
        entrada_minutos_juego.place_forget()
        entrada_segundos_juego.place_forget()

    if modo_tiempo.get() == "temporizador":
        TIEMPO_LIMITE = h * 3600 + m * 60 + s
    elif modo_tiempo.get() == "cronometro":
        TIEMPO_LIMITE = 0
    else:
        TIEMPO_LIMITE = 0

    tiempo_mostrado.set(formatear_tiempo(TIEMPO_LIMITE))

    partida = obtener_partida_aleatoria(nivel_actual)
    if partida is None:
        messagebox.showerror("Error", "No hay partidas disponibles para este nivel")
        ventana.destroy()
        mostrar_menu_principal()
        return

    TAMAÑO_TABLERO = 9
    estructura_desde_partida(partida)
    numero_elegido = tk.StringVar()
    nombre_jugador = ""
    juego_activo = False
    tiempo_inicio = None
    pila_jugadas = []
    pila_deshacer = []
    valores_tablero = [["" for _ in range(TAMAÑO_TABLERO)] for _ in range(TAMAÑO_TABLERO)]

    color_fondo = "#9bbc0f"
    color_oscuro = "#0f380f"
    color_boton = "#8bac0f"
    color_hover = "#306230"
    fuente_pixel = font.Font(family="Press Start 2P", size=9)

    ventana.configure(bg=color_fondo)

    tk.Label(ventana, text="KAKURO", font=fuente_pixel, bg=color_oscuro, fg="white", pady=10).place(x=30, y=10)
    tk.Label(ventana, text="Jugador:", font=fuente_pixel, bg=color_fondo, fg=color_oscuro).place(x=390, y=20)
    tk.Entry(ventana, textvariable=entrada_nombre, width=40).place(x=500, y=20)
    """
    tk.Label(ventana, text="Horas", bg='black', fg="white").place(x=330, y=630)
    tk.Label(ventana, text="Minutos", bg='black', fg="white").place(x=370, y=630)
    tk.Label(ventana, text="Segundos", bg='black', fg="white").place(x=422, y=630)
    """

    #Crear etiquetas como variables globales para poder mostrarlas/ocultarlas
    global etiqueta_horas_label, etiqueta_minutos_label, etiqueta_segundos_label

    etiqueta_horas_label = tk.Label(ventana, text="Horas", bg='black', fg="white")
    etiqueta_minutos_label = tk.Label(ventana, text="Minutos", bg='black', fg="white")
    etiqueta_segundos_label = tk.Label(ventana, text="Segundos", bg='black', fg="white")

    #Se posicionarán solo si modo_tiempo no es "sin_reloj"
    if modo_tiempo.get() != "sin_reloj":
        etiqueta_horas_label.place(x=330, y=630)
        etiqueta_minutos_label.place(x=370, y=630)
        etiqueta_segundos_label.place(x=422, y=630)
    tk.Label(ventana, text="NIVEL:" + nivel_actual.capitalize(), font=fuente_pixel, bg=color_fondo, fg=color_oscuro).place(x=330, y=700)

    botones_numeros = []
    for i in range(9):
        boton = tk.Button(ventana, text=str(i+1), font=fuente_pixel, width=2, height=2,
                          bg=color_boton, fg=color_oscuro,
                          activebackground=color_hover, activeforeground="white",
                          command=lambda n=i+1: elegir_numero(n))
        boton.place(x=730, y=60 + i*40)
        botones_numeros.append(boton)

    modo_borrador = False
    boton_goma = tk.Button(ventana, text="Goma", font=fuente_pixel, width=5, height=2,
                       bg="red", fg="white",
                       activebackground="#aa0000", activeforeground="white",
                       command=activar_borrador)
    boton_goma.place(x=710, y=60 + 9*40)

    boton_iniciar = tk.Button(ventana, text="INICIAR\nJUEGO", font=fuente_pixel,
                              bg=color_hover, fg="white", width=12, height=2, command=iniciar)
    boton_iniciar.place(x=30, y=500)

    botones_control = [
        ("DESHACER", "lightgreen", deshacer, 180, 500),
        ("BORRAR", "lightsteelblue", borrar, 330, 500),
        ("GUARDAR", "orange", guardar_juego, 480, 500),
        ("RÉCORDS", "yellow", mostrar_records, 630, 500),
        ("REHACER", "cyan", rehacer, 180, 570),
        ("TERMINAR", "mediumseagreen", terminar_juego, 330, 570),
        ("CARGAR", "chocolate", cargar_juego, 480, 570),
    ]

    for texto, color, comando, x, y in botones_control:
        tk.Button(ventana, text=texto, font=fuente_pixel, bg=color, width=12, height=2, command=comando).place(x=x, y=y)

    botones_tablero = []
    for i in range(TAMAÑO_TABLERO):
        fila = []
        for j in range(TAMAÑO_TABLERO):
            x, y = 30 + j*40, 70 + i*40
            if ESTRUCTURA_TABLERO[i][j] == -1:
                texto = ""
                if (i, j) in CLAVES:
                    clave = CLAVES[(i, j)]
                    fila_clave = f"{clave['fila']}\u2192" if "fila" in clave else ""
                    columna_clave = f"\u2193{clave['columna']}" if "columna" in clave else ""
                    texto = f"{fila_clave}\n{columna_clave}".strip()
                celda = tk.Label(ventana, text=texto, bg="black", fg="white",
                                 relief="solid", font=("Arial", 8), justify="center")
            else:
                celda = tk.Button(ventana, text="", command=lambda f=i, c=j: click_en_casilla(f, c))
            celda.place(x=x, y=y, width=40, height=40)
            fila.append(celda)
        botones_tablero.append(fila)

    actualizar_visibilidad_reloj()


#------------------ FUNCIONES ------------------#
    
def actualizar_reloj():
    global juego_activo, tiempo_inicio, modo_tiempo, TIEMPO_LIMITE, id_reloj

    if not juego_activo or modo_tiempo.get() == "sin_reloj":
        return

    if modo_tiempo.get() == "cronometro":
        transcurrido = int(time.time() - tiempo_inicio)
        if transcurrido > 2 * 3600:
            if id_reloj is not None:
                ventana.after_cancel(id_reloj)
                id_reloj = None
            juego_activo = False
            messagebox.showinfo("Tiempo", "El cronómetro ha alcanzado el límite de 2 horas. Juego terminado.")
            return
        h, m, s = transcurrido // 3600, (transcurrido % 3600) // 60, transcurrido % 60

    elif modo_tiempo.get() == "temporizador":
        tiempo_restante = TIEMPO_LIMITE - int(time.time() - tiempo_inicio)

        if tiempo_restante <= 0:
            if id_reloj is not None:
                ventana.after_cancel(id_reloj)
                id_reloj = None
            respuesta = messagebox.askyesno("Tiempo Expirado", "TIEMPO EXPIRADO.\n¿DESEA CONTINUAR EL MISMO JUEGO (SI/NO)?")
            if respuesta:
                modo_tiempo.set("cronometro")
                tiempo_inicio = time.time() - TIEMPO_LIMITE
                actualizar_reloj()
            else:
                juego_activo = False
                messagebox.showinfo("Juego", "Juego finalizado por expiración de tiempo.")
                ventana.destroy()
                mostrar_menu_principal()
            return

        h, m, s = tiempo_restante // 3600, (tiempo_restante % 3600) // 60, tiempo_restante % 60

    tiempo_mostrado.set(f"{h:02}:{m:02}:{s:02}")

    #Solo programar de nuevo si el juego sigue activo
    if juego_activo:
        id_reloj = ventana.after(1000, actualizar_reloj)



def iniciar():
    global juego_activo, TIEMPO_LIMITE, nombre_jugador, tiempo_inicio
    

    nombre = entrada_nombre.get().strip()
    if len(nombre) == 0:
        messagebox.showerror("ERROR", "Debe ingresar un nombre para iniciar el juego.")
        return
    if len(nombre) > 40:
        messagebox.showerror("ERROR", "El nombre debe tener máximo 40 caracteres.")
        return

    try:
        with open("kakuro2025_configuración.json", "r") as archivo:
            config = json.load(archivo)
    except:
        config = {"reloj": "sin_reloj"}

    modo = config.get("reloj", "sin_reloj")

    if modo == "temporizador":
        try:
            horas = int(entrada_horas_juego.get())
            minutos = int(entrada_minutos_juego.get())
            segundos = int(entrada_segundos_juego.get())
        except:
            messagebox.showerror("ERROR", "Por favor ingrese números válidos para el tiempo.")
            return

        TIEMPO_LIMITE = horas * 3600 + minutos * 60 + segundos

        if TIEMPO_LIMITE <= 0:
            messagebox.showerror("ERROR", "El tiempo debe ser mayor a cero.")
            return
    else:
        TIEMPO_LIMITE = None

    nombre_jugador = nombre
    juego_activo = True
    tiempo_inicio = time.time()
    boton_iniciar.config(state="disabled")

    for i in range(TAMAÑO_TABLERO):
        for j in range(TAMAÑO_TABLERO):
            if ESTRUCTURA_TABLERO[i][j] == 0:
                valores_tablero[i][j] = ""
                botones_tablero[i][j].config(text="")

    #Restaurar claves
    for i in range(TAMAÑO_TABLERO):
        for j in range(TAMAÑO_TABLERO):
            if ESTRUCTURA_TABLERO[i][j] == -1 and (i, j) in CLAVES:
                clave = CLAVES[(i, j)]
                texto_fila = f"{clave.get('fila', '')}\u2192" if 'fila' in clave else ""
                texto_columna = f"\u2193{clave.get('columna', '')}" if 'columna' in clave else ""
                texto = f"{texto_fila}\n{texto_columna}".strip()
                botones_tablero[i][j].config(text=texto)

    actualizar_reloj()


    
def elegir_numero(n):
    numero_elegido.set(str(n))
    for boton in botones_numeros:
        boton.config(bg="SystemButtonFace")
    botones_numeros[n-1].config(bg="lightblue")


def click_en_casilla(fila, columna):
    global modo_borrador

    #Validar que la casilla sea modificable
    if ESTRUCTURA_TABLERO[fila][columna] != 0:
        messagebox.showerror("Error", "Esta casilla no puede ser modificada.")
        return

    if modo_borrador:
        anterior = valores_tablero[fila][columna]
        if anterior == "":
            messagebox.showinfo("Info", "La casilla ya está vacía.")
        else:
            valores_tablero[fila][columna] = ""
            botones_tablero[fila][columna].config(text="")
            pila_jugadas.append({"fila": fila, "col": columna, "anterior": anterior, "nuevo": ""})
            pila_deshacer.clear()
            messagebox.showinfo("Borrado", "Contenido eliminado.")
        modo_borrador = False  #Desactiva modo borrador
        return

    #Validar si el juego está activo
    if not juego_activo:
        messagebox.showerror("ERROR", "El juego no está activo.")
        return

    #Validar si se seleccionó un número
    if not numero_elegido.get():
        messagebox.showerror("ERROR", "FALTA QUE SELECCIONE EL NÚMERO")
        return

    #Aplicar número
    anterior = valores_tablero[fila][columna]
    nuevo = numero_elegido.get()

    if nuevo == anterior:
        return

    #Validar si el número ya está en el grupo de fila
    grupo_fila = []
    i = columna
    while i >= 0 and ESTRUCTURA_TABLERO[fila][i] == 0:
        grupo_fila.insert(0, i)
        i -= 1
    i = columna + 1
    while i < TAMAÑO_TABLERO and ESTRUCTURA_TABLERO[fila][i] == 0:
        grupo_fila.append(i)
        i += 1

    for i in grupo_fila:
        if valores_tablero[fila][i] == nuevo:
            messagebox.showerror("ERROR", "JUGADA NO ES VÁLIDA PORQUE EL NÚMERO YA ESTÁ EN SU GRUPO DE FILA")
            return

    #Validar si el número ya está en el grupo de columna
    grupo_columna = []
    i = fila
    while i >= 0 and ESTRUCTURA_TABLERO[i][columna] == 0:
        grupo_columna.insert(0, i)
        i -= 1
    i = fila + 1
    while i < TAMAÑO_TABLERO and ESTRUCTURA_TABLERO[i][columna] == 0:
        grupo_columna.append(i)
        i += 1

    for i in grupo_columna:
        if valores_tablero[i][columna] == nuevo:
            messagebox.showerror("ERROR", "JUGADA NO ES VÁLIDA PORQUE EL NÚMERO YA ESTÁ EN SU GRUPO DE COLUMNA")
            return

    #Validar suma del grupo de fila
    suma_fila = 0
    inicio = columna
    while inicio > 0 and ESTRUCTURA_TABLERO[fila][inicio - 1] == 0:
        inicio -= 1
    clave = None
    for c in range(inicio - 1, -1, -1):
        if ESTRUCTURA_TABLERO[fila][c] == -1 and (fila, c) in CLAVES and "fila" in CLAVES[(fila, c)]:
            clave = CLAVES[(fila, c)]["fila"]
            break
    if clave:
        for i in range(inicio, TAMAÑO_TABLERO):
            if ESTRUCTURA_TABLERO[fila][i] != 0:
                break
            valor = nuevo if i == columna else valores_tablero[fila][i]
            if valor != "":
                suma_fila += int(valor)
        if suma_fila > clave:
            messagebox.showerror("Error", f"JUGADA NO ES VÁLIDA PORQUE LA SUMA DE LA FILA ES {suma_fila} Y LA CLAVE NUMÉRICA ES {clave}")
            return

    #Validar suma del grupo de columna
    suma_columna = 0
    inicio = fila
    while inicio > 0 and ESTRUCTURA_TABLERO[inicio - 1][columna] == 0:
        inicio -= 1
    clave = None
    for f in range(inicio - 1, -1, -1):
        if ESTRUCTURA_TABLERO[f][columna] == -1 and (f, columna) in CLAVES and "columna" in CLAVES[(f, columna)]:
            clave = CLAVES[(f, columna)]["columna"]
            break
    if clave:
        for i in range(inicio, TAMAÑO_TABLERO):
            if ESTRUCTURA_TABLERO[i][columna] != 0:
                break
            valor = nuevo if i == fila else valores_tablero[i][columna]
            if valor != "":
                suma_columna += int(valor)
        if suma_columna > clave:
            messagebox.showerror("Error", f"JUGADA NO ES VÁLIDA PORQUE LA SUMA DE LA COLUMNA ES {suma_columna} Y LA CLAVE NUMÉRICA ES {clave}")
            return

    valores_tablero[fila][columna] = nuevo
    botones_tablero[fila][columna].config(text=nuevo)
    pila_jugadas.append({"fila": fila, "col": columna, "anterior": anterior, "nuevo": nuevo})
    pila_deshacer.clear()
    numero_elegido.set("")
    for b in botones_numeros:
        b.config(bg="SystemButtonFace")
    verificar_fin()

def verificar_fin():
    #Reiniciar juego con nueva partida aleatoria del mismo nivel
    global juego_activo, valores_tablero, pila_jugadas, pila_deshacer, tiempo_inicio

    for i in range(TAMAÑO_TABLERO):
        for j in range(TAMAÑO_TABLERO):
            if ESTRUCTURA_TABLERO[i][j] == 0 and valores_tablero[i][j] == "":
                return  #Todavía hay casillas vacías

    #Si no hay vacías, entonces GANÓ
    messagebox.showinfo("¡FELICIDADES!", "¡Has completado el Kakuro correctamente!")

   

    partida = obtener_partida_aleatoria(nivel_actual)
    if partida is None:
        messagebox.showerror("Error", "No hay más partidas disponibles.")
        return

    estructura_desde_partida(partida)

    valores_tablero = [["" for _ in range(TAMAÑO_TABLERO)] for _ in range(TAMAÑO_TABLERO)]
    pila_jugadas.clear()
    pila_deshacer.clear()
    juego_activo = False
    tiempo_inicio = None

    for i in range(TAMAÑO_TABLERO):
        for j in range(TAMAÑO_TABLERO):
            if ESTRUCTURA_TABLERO[i][j] == 0:
                botones_tablero[i][j].config(text="", command=lambda f=i, c=j: click_en_casilla(f, c))
            else:
                clave = CLAVES.get((i, j), {})
                texto_fila = f"{clave.get('fila', '')}\u2192" if 'fila' in clave else ""
                texto_columna = f"\u2193{clave.get('columna', '')}" if 'columna' in clave else ""
                texto = f"{texto_fila}\n{texto_columna}".strip()
                botones_tablero[i][j].config(text=texto)

    boton_iniciar.config(state="normal")


def guardar_record(nombre, tiempo, nivel_actual):
    try:
        with open("kakuro2025_récords.json", "r") as archivo:
            records = json.load(archivo)
    except:
        records = {"fácil": [], "medio": [], "difícil": [], "experto": []}

    records.setdefault(nivel_actual, [])
    records[nivel_actual].append({"nombre": nombre, "tiempo": tiempo})
    
    #Ordenar por tiempo
    def convertir_a_segundos(tiempo_str):
        h, m, s = map(int, tiempo_str.split(":"))
        return h * 3600 + m * 60 + s
    
    records[nivel_actual].sort(key=lambda x: convertir_a_segundos(x["tiempo"]))
    
    with open("kakuro2025_récords.json", "w") as archivo:
        json.dump(records, archivo, indent=2)


def reiniciar():
    global juego_activo, valores_tablero, pila_jugadas, pila_deshacer, id_reloj
    juego_activo = False
    boton_iniciar.config(state="normal")
    valores_tablero = [["" for _ in range(TAMAÑO_TABLERO)] for _ in range(TAMAÑO_TABLERO)]
    pila_jugadas.clear()
    pila_deshacer.clear()
    for i in range(TAMAÑO_TABLERO):
        for j in range(TAMAÑO_TABLERO):
            if ESTRUCTURA_TABLERO[i][j] == 0:
                botones_tablero[i][j].config(text="")
    tiempo_mostrado.set("00:00:00")
    numero_elegido.set("")
    for b in botones_numeros:
        b.config(bg="SystemButtonFace")

    if id_reloj is not None:
        ventana.after_cancel(id_reloj)
        id_reloj = None

def deshacer():
    if not pila_jugadas:
        return
    jugada = pila_jugadas.pop()
    f, c = jugada["fila"], jugada["col"]
    valores_tablero[f][c] = jugada["anterior"]
    botones_tablero[f][c].config(text=jugada["anterior"])
    pila_deshacer.append(jugada)

def rehacer():
    if not pila_deshacer:
        messagebox.showwarning("Sin jugadas", "No hay jugadas para rehacer")
        return
    jugada = pila_deshacer.pop()
    f, c = jugada["fila"], jugada["col"]
    valores_tablero[f][c] = jugada["nuevo"]
    botones_tablero[f][c].config(text=jugada["nuevo"])
    pila_jugadas.append(jugada)

def borrar():
    global juego_activo
    if not juego_activo:
        messagebox.showwarning("ADVERTENCIA", "NO SE HA INICIADO EL JUEGO")
        return

    respuesta = messagebox.askyesno("CONFIRMAR", "¿ESTÁ SEGURO DE BORRAR EL JUEGO?")
    if respuesta:
        reiniciar()
    else:
        messagebox.showinfo("CONTINUAR", "Puede continuar con el mismo juego.")


def mostrar_records():
    global juego_activo, reloj_pausado, pausa_inicio, id_reloj

    if juego_activo:
        reloj_pausado = True
        pausa_inicio = time.time()
        if id_reloj is not None:
            ventana.after_cancel(id_reloj)
            id_reloj = None
        juego_activo = False
    else:
        reloj_pausado = False

    try:
        with open("kakuro2025_récords.json", "r") as archivo:
            records = json.load(archivo)
    except:
        messagebox.showinfo("RÉCORDS", "No hay récords guardados.")
        return

    ventana_records = tk.Toplevel(ventana)
    ventana_records.title("RÉCORDS")
    ventana_records.geometry("600x500")

    #Estilo Game Boy
    color_fondo = "#9bbc0f"
    color_oscuro = "#0f380f"
    color_boton = "#8bac0f"
    color_hover = "#306230"
    fuente_pixel = font.Font(family="Press Start 2P", size=10)

    ventana_records.configure(bg=color_fondo)
    tk.Label(ventana_records, text="RECORDS", font=fuente_pixel, bg=color_oscuro, fg="white", pady=10).pack(fill="x")

    frame_opciones = tk.Frame(ventana_records, bg=color_fondo)
    frame_opciones.pack(pady=10)

    nivel_var = tk.StringVar(value=nivel_actual)
    jugador_var = tk.StringVar(value="Todos")

    niveles = ["Todos", "FACIL", "MEDIO", "DIFICIL", "EXPERTO"]
    jugadores = ["Todos", "Yo"] if "nombre_jugador" in globals() and nombre_jugador else ["Todos"]

    tk.Label(frame_opciones, text="Nivel:", bg=color_fondo, fg=color_oscuro, font=fuente_pixel).grid(row=0, column=0, padx=5)
    nivel_menu = tk.OptionMenu(frame_opciones, nivel_var, *niveles)
    nivel_menu.config(font=fuente_pixel, bg=color_boton, fg=color_oscuro, activebackground=color_hover, activeforeground="white", relief="ridge", bd=3)
    nivel_menu.grid(row=0, column=1, padx=5)

    tk.Label(frame_opciones, text="Jugador:", bg=color_fondo, fg=color_oscuro, font=fuente_pixel).grid(row=0, column=2, padx=5)
    jugador_menu = tk.OptionMenu(frame_opciones, jugador_var, *jugadores)
    jugador_menu.config(font=fuente_pixel, bg=color_boton, fg=color_oscuro, activebackground=color_hover, activeforeground="white", relief="ridge", bd=3)
    jugador_menu.grid(row=0, column=3, padx=5)

    area_texto = tk.Text(ventana_records, width=60, height=20, font=("Courier", 10), bg=color_oscuro, fg="white", bd=5, relief="ridge")
    area_texto.pack(pady=10)

    def actualizar_resultado():
        area_texto.delete("1.0", tk.END)
        nv = nivel_var.get()
        jv = jugador_var.get()
        niveles_a_mostrar = records.keys() if nv == "Todos" else [nv]
        for nivel in niveles_a_mostrar:
            if nivel not in records or not records[nivel]:
                continue
            area_texto.insert(tk.END, f"NIVEL {nivel.upper()}\n")
            for idx, entry in enumerate(records[nivel], 1):
                if jv == "Yo":
                    if "nombre_jugador" not in globals() or entry["nombre"] != nombre_jugador:
                        continue
                area_texto.insert(tk.END, f"{idx}- {entry['nombre']} {entry['tiempo']}\n")
            area_texto.insert(tk.END, "\n")

    btn_mostrar = tk.Button(ventana_records, text="MOSTRAR", font=fuente_pixel,
                            bg=color_boton, fg=color_oscuro,
                            activebackground=color_hover, activeforeground="white",
                            relief="ridge", bd=5,
                            command=actualizar_resultado)
    btn_mostrar.pack(pady=5)

    def cerrar():
        global juego_activo, tiempo_inicio, reloj_pausado, pausa_inicio
        ventana_records.destroy()
        if reloj_pausado:
            tiempo_pausa = time.time() - pausa_inicio
            tiempo_inicio += tiempo_pausa
            juego_activo = True
            reloj_pausado = False
            actualizar_reloj()

    ventana_records.protocol("WM_DELETE_WINDOW", cerrar)



def regresar_menu_principal():
    reiniciar()
    messagebox.showinfo("MENÚ", "Regresando al menú principal")


def terminar_juego():
    global juego_activo, id_reloj, tiempo_inicio

    if not juego_activo:
        messagebox.showwarning("ADVERTENCIA", "NO SE HA INICIADO EL JUEGO")
        return

    respuesta = messagebox.askyesno("CONFIRMAR", "¿ESTÁ SEGURO DE TERMINAR EL JUEGO?")
    if respuesta:
        juego_activo = False

        if id_reloj is not None:
            ventana.after_cancel(id_reloj)
            id_reloj = None

        reiniciar()

        #Obtener una nueva partida aleatoria del mismo nivel
        partida = obtener_partida_aleatoria(nivel_actual)
        if partida:
            estructura_desde_partida(partida)

            for i in range(TAMAÑO_TABLERO):
                for j in range(TAMAÑO_TABLERO):
                    if ESTRUCTURA_TABLERO[i][j] == 0:
                        valores_tablero[i][j] = ""
                        botones_tablero[i][j].config(text="", state="normal")
                    elif ESTRUCTURA_TABLERO[i][j] == -1 and (i, j) in CLAVES:
                        clave = CLAVES[(i, j)]
                        texto_fila = f"{clave.get('fila', '')}\u2192" if 'fila' in clave else ""
                        texto_columna = f"\u2193{clave.get('columna', '')}" if 'columna' in clave else ""
                        texto = f"{texto_fila}\n{texto_columna}".strip()
                        botones_tablero[i][j].config(text=texto, state="disabled")

        #Restablecer reloj
        if modo_tiempo.get() == "temporizador":
            try:
                horas = int(entrada_horas_juego.get())
                minutos = int(entrada_minutos_juego.get())
                segundos = int(entrada_segundos_juego.get())
                TIEMPO_LIMITE = horas * 3600 + minutos * 60 + segundos
            except:
                TIEMPO_LIMITE = 0
        else:
            TIEMPO_LIMITE = 0

        tiempo_mostrado.set(formatear_tiempo(TIEMPO_LIMITE))
        boton_iniciar.config(state="normal")
        messagebox.showinfo("JUEGO TERMINADO", "Se ha reiniciado el juego con un tablero nuevo.")
    else:
        messagebox.showinfo("CONTINUAR", "Puede continuar con el mismo juego.")
        
def reiniciar_tablero():
    global botones_tablero, valores_tablero, juego_activo

    juego_activo = False  #Detener el juego al reiniciar

    valores_tablero = [["" for _ in range(TAMAÑO_TABLERO)] for _ in range(TAMAÑO_TABLERO)]

    for i in range(TAMAÑO_TABLERO):
        for j in range(TAMAÑO_TABLERO):
            if ESTRUCTURA_TABLERO[i][j] == -1:  #Casilla negra con posible clave
                texto = ""
                if (i, j) in CLAVES:
                    fila_clave = f"{CLAVES[(i, j)].get('fila', '')}\u2192" if "fila" in CLAVES[(i, j)] else ""
                    columna_clave = f"\u2193{CLAVES[(i, j)].get('columna', '')}" if "columna" in CLAVES[(i, j)] else ""
                    texto = f"{fila_clave}\n{columna_clave}".strip()

                #Convertir botón en etiqueta negra con clave
                botones_tablero[i][j].destroy()  # Destruye el botón viejo
                etiqueta = tk.Label(ventana, text=texto, bg="black", fg="white",
                                    relief="solid", font=("Arial", 8), justify="center")
                etiqueta.place(x=30 + j*40, y=70 + i*40, width=40, height=40)
                botones_tablero[i][j] = etiqueta

            else:  #Casilla blanca (editable)
                #Si antes había una etiqueta, destruirla y crear botón
                if isinstance(botones_tablero[i][j], tk.Label):
                    botones_tablero[i][j].destroy()
                    boton = tk.Button(ventana, text="", bg="SystemButtonFace", fg="black",
                                      relief="raised", command=lambda f=i, c=j: click_en_casilla(f, c))
                    boton.place(x=30 + j*40, y=70 + i*40, width=40, height=40)
                    botones_tablero[i][j] = boton
                else:
                    #Reiniciar su estado y texto
                    botones_tablero[i][j].config(text="", bg="SystemButtonFace", fg="black", relief="raised", state="normal")

    #Reiniciar pila y otras variables
    pila_jugadas.clear()
    pila_deshacer.clear()
    numero_elegido.set("")
    for b in botones_numeros:
        b.config(bg="SystemButtonFace")


#Guardar juego:

def guardar_juego():
    global juego_activo

    if not juego_activo:
        messagebox.showwarning("Advertencia", "NO SE HA INICIADO EL JUEGO")
        return

    #Detener el reloj
    juego_activo = False

    #Crear estructura de datos
    datos = {
        "jugador": nombre_jugador,
        "nivel": nivel_actual,
        "tiempo": tiempo_mostrado.get(),
        "valores_tablero": valores_tablero,
        "pila_jugadas": pila_jugadas,
        "pila_deshacer": pila_deshacer
    }

    try:
        with open("kakuro2025_juego_actual.json", "r") as archivo:
            juegos_guardados = json.load(archivo)
    except:
        juegos_guardados = {}

    #Reemplazar partida del mismo jugador
    juegos_guardados[nombre_jugador] = datos

    with open("kakuro2025_juego_actual.json", "w") as archivo:
        json.dump(juegos_guardados, archivo, indent=2)

    #Preguntar si desea seguir
    respuesta = messagebox.askyesno("Juego guardado", "¿VA A CONTINUAR JUGANDO?")
    if respuesta:
        juego_activo = True
        actualizar_reloj()
    else:
        reiniciar()

#Cargar juego:

def cargar_juego():
    global valores_tablero, pila_jugadas, pila_deshacer, tiempo_mostrado, nombre_jugador, nivel_actual, juego_activo

    if juego_activo:
        messagebox.showwarning("Advertencia", "NO SE PUEDE CARGAR UN JUEGO YA INICIADO")
        return

    nombre = entrada_nombre.get().strip()
    if not nombre:
        messagebox.showerror("Error", "Debe ingresar su nombre antes de cargar el juego.")
        return

    try:
        with open("kakuro2025_juego_actual.json", "r") as archivo:
            juegos_guardados = json.load(archivo)
    except:
        messagebox.showinfo("Info", "NO HAY PARTIDAS GUARDADAS.")
        return

    if nombre not in juegos_guardados:
        messagebox.showinfo("Info", "NO HAY UNA PARTIDA GUARDADA PARA ESTE JUGADOR.")
        return

    datos = juegos_guardados[nombre]
    nombre_jugador = nombre
    nivel_actual = datos.get("nivel", "fácil")
    tiempo_mostrado.set(datos.get("tiempo", "00:00:00"))
    valores_tablero = datos.get("valores_tablero", [["" for _ in range(TAMAÑO_TABLERO)] for _ in range(TAMAÑO_TABLERO)])
    pila_jugadas = datos.get("pila_jugadas", [])
    pila_deshacer = datos.get("pila_deshacer", [])

    #Refrescar la interfaz del tablero
    for i in range(TAMAÑO_TABLERO):
        for j in range(TAMAÑO_TABLERO):
            if ESTRUCTURA_TABLERO[i][j] == 0:
                valor = valores_tablero[i][j]
                botones_tablero[i][j].config(text=valor)

    messagebox.showinfo("Partida cargada", "Juego cargado correctamente. Pulse INICIAR JUEGO para continuar.")


def activar_borrador():
    global modo_borrador
    modo_borrador = True
    numero_elegido.set("")  #Deseleccionar número
    for b in botones_numeros:
        b.config(bg="SystemButtonFace")
    messagebox.showinfo("Borrador", "Seleccione una casilla para borrar su contenido.")


  
def actualizar_visibilidad_reloj(*args):
    if modo_tiempo.get() == "sin_reloj":
        label_tiempo.place_forget()
        try:
            etiqueta_horas_label.place_forget()
            etiqueta_minutos_label.place_forget()
            etiqueta_segundos_label.place_forget()
        except:
            pass
    else:
        label_tiempo.place(x=350, y=660)
        try:
            etiqueta_horas_label.place(x=330, y=630)
            etiqueta_minutos_label.place(x=370, y=630)
            etiqueta_segundos_label.place(x=422, y=630)
        except:
            pass

#--------------------CONFIGURACIÓN
def mostrar_configuracion():
    ventana_config = tk.Toplevel()
    ventana_config.title("Configurar Juego - Kakuro")
    ventana_config.geometry("500x500")
    ventana_config.configure(bg="#9bbc0f")
    ventana_config.resizable(False, False)

    #Colores y fuente Game Boy
    color_fondo = "#9bbc0f"
    color_oscuro = "#0f380f"
    color_boton = "#8bac0f"
    color_hover = "#306230"
    fuente_pixel = font.Font(family="Press Start 2P", size=8)

    #Leer configuración previa
    config_actual = {
        "nivel": "fácil",
        "reloj": "sin_reloj",
        "horas": 0,
        "minutos": 0,
        "segundos": 0
    }

    try:
        with open("kakuro2025_configuración.json", "r") as archivo:
            config_actual.update(json.load(archivo))
    except:
        pass  #Si no existe o hay error, usamos valores por defecto

    #Función para botón estilo Game Boy
    def crear_boton(texto, comando):
        btn = tk.Button(ventana_config, text=texto, font=fuente_pixel,
                        width=35, height=2,
                        bg=color_boton, fg=color_oscuro,
                        activebackground=color_hover, activeforeground="white",
                        relief="ridge", bd=5,
                        command=comando)
        btn.pack(pady=15)
        btn.bind("<Enter>", lambda e: btn.config(bg=color_hover, fg="white"))
        btn.bind("<Leave>", lambda e: btn.config(bg=color_boton, fg=color_oscuro))

    # ----------------- NIVEL DE DIFICULTAD -----------------
    tk.Label(ventana_config, text="Nivel de Dificultad", bg=color_oscuro, fg="white",
             font=fuente_pixel).pack(pady=10, fill="x")

    nivel_var = tk.StringVar(value=config_actual["nivel"])
    niveles = ["fácil", "medio", "difícil", "experto"]
    radios_nivel = []

    def actualizar_estilo_nivel(*_):
        for rb in radios_nivel:
            if rb.cget("value") == nivel_var.get():
                rb.config(fg="white", font=font.Font(family="Press Start 2P", size=8, underline=1))
            else:
                rb.config(fg=color_oscuro, font=font.Font(family="Press Start 2P", size=8, underline=0))

    for nivel in niveles:
        rb = tk.Radiobutton(ventana_config, text=nivel.capitalize(), variable=nivel_var, value=nivel,
                            bg=color_fondo, font=fuente_pixel, fg=color_oscuro,
                            selectcolor=color_hover,
                            activebackground=color_hover, activeforeground="white",
                            command=actualizar_estilo_nivel)
        rb.pack(anchor="w", padx=40)
        radios_nivel.append(rb)
    actualizar_estilo_nivel()

    # ----------------- MODO DE RELOJ -----------------
    tk.Label(ventana_config, text="Modo de Reloj", bg=color_oscuro, fg="white",
             font=fuente_pixel).pack(pady=10, fill="x")

    reloj_var = tk.StringVar(value=config_actual["reloj"])
    modos = [("Sin reloj", "sin_reloj"), ("Cronómetro", "cronometro"), ("Temporizador", "temporizador")]
    radios_reloj = []

    def actualizar_estilo_reloj(*_):
        for rb in radios_reloj:
            if rb.cget("value") == reloj_var.get():
                rb.config(fg="white", font=font.Font(family="Press Start 2P", size=8, underline=1))
            else:
                rb.config(fg=color_oscuro, font=font.Font(family="Press Start 2P", size=8, underline=0))

    for texto, valor in modos:
        rb = tk.Radiobutton(ventana_config, text=texto, variable=reloj_var, value=valor,
                            bg=color_fondo, font=fuente_pixel, fg=color_oscuro,
                            selectcolor=color_hover,
                            activebackground=color_hover, activeforeground="white",
                            command=actualizar_estilo_reloj)
        rb.pack(anchor="w", padx=40)
        radios_reloj.append(rb)
    actualizar_estilo_reloj()

    # ----------------- TIEMPO -----------------
    tk.Label(ventana_config, text="Tiempo para Temporizador", bg=color_oscuro, fg="white",
             font=fuente_pixel).pack(pady=10, fill="x")

    frame_tiempo = tk.Frame(ventana_config, bg=color_fondo)
    frame_tiempo.pack(pady=5)

    def entrada_retro(etiqueta, valor):
        tk.Label(frame_tiempo, text=etiqueta, bg=color_fondo, fg=color_oscuro,
                 font=fuente_pixel).pack(side="left", padx=5)
        entry = tk.Entry(frame_tiempo, width=3, font=fuente_pixel,
                         bg="white", fg=color_oscuro, justify="center")
        entry.insert(0, str(valor))
        entry.pack(side="left", padx=5)
        return entry

    entrada_horas = entrada_retro("Horas:", config_actual["horas"])
    entrada_minutos = entrada_retro("Minutos:", config_actual["minutos"])
    entrada_segundos = entrada_retro("Segs:", config_actual["segundos"])

    # ----------------- GUARDAR CONFIGURACIÓN -----------------
    def guardar_configuracion():
        reloj = reloj_var.get()
        nivel = nivel_var.get()

        def leer_entero(campo):
            texto = campo.get().strip()
            return int(texto) if texto.isdigit() else 0

        horas = leer_entero(entrada_horas)
        minutos = leer_entero(entrada_minutos)
        segundos = leer_entero(entrada_segundos)

        if reloj == "temporizador":
            if not (0 <= horas <= 2):
                messagebox.showerror("ERROR", "Las horas deben estar entre 0 y 2.")
                return
            if not (0 <= minutos <= 59):
                messagebox.showerror("ERROR", "Los minutos deben estar entre 0 y 59.")
                return
            if not (0 <= segundos <= 59):
                messagebox.showerror("ERROR", "Los segundos deben estar entre 0 y 59.")
                return
            if horas == 0 and minutos == 0 and segundos == 0:
                messagebox.showerror("ERROR", "El tiempo debe ser mayor a 0.")
                return

        configuracion = {
            "nivel": nivel,
            "reloj": reloj,
            "horas": horas,
            "minutos": minutos,
            "segundos": segundos
        }

        with open("kakuro2025_configuración.json", "w") as archivo:
            json.dump(configuracion, archivo, indent=2)

        messagebox.showinfo("Éxito", "Configuración guardada correctamente.")
        ventana_config.destroy()

    crear_boton("Guardar Configuración", guardar_configuracion)



#--------Cargar partidas json

def cargar_partidas_desde_archivo():
    global partidas_usadas , partidas_por_nivel,partidas_disponibles
    partidas_usadas = {}
    partidas_por_nivel = {}
    partidas_disponibles = {}
    try:
        with open("kakuro2025_partidas.json", encoding="utf-8-sig") as archivo:
            todas = json.load(archivo)
            for partida in todas:
                nivel = normalizar_texto(partida["nivel_de_dificultad"])
                if nivel not in partidas_disponibles:
                    partidas_disponibles[nivel] = []
                partidas_disponibles[nivel].append(partida)
    except Exception as e:
        print("Error al cargar partidas:", e)
        
def obtener_partida_aleatoria(nivel):
    global partidas_usadas

    if nivel not in partidas_disponibles:
        return None

    if nivel not in partidas_usadas:
        partidas_usadas[nivel] = []

    disponibles = [p for p in partidas_disponibles[nivel] if p["partida"] not in partidas_usadas[nivel]]

    if not disponibles:
        partidas_usadas[nivel] = []
        disponibles = partidas_disponibles[nivel][:]

    partida = random.choice(disponibles)
    partidas_usadas[nivel].append(partida["partida"])
    return partida

def normalizar_texto(texto):
    texto = texto.upper()
    texto = unicodedata.normalize('NFD', texto)
    texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')  #Quita tildes
    return texto

#---Generar tablero

def estructura_desde_partida(partida):
    global ESTRUCTURA_TABLERO, CLAVES, TAMAÑO_TABLERO
    TAMAÑO_TABLERO = 9
    #Inicializa matriz 9x9 con -1 (casillas negras)
    ESTRUCTURA_TABLERO = [[-1 for _ in range(TAMAÑO_TABLERO)] for _ in range(TAMAÑO_TABLERO)]
    CLAVES = {}

    #Recorre cada clave para colocarla en el tablero y marcar casillas blancas
    for clave in partida["claves"]:
        tipo = clave["tipo_de_clave"]   # "F" o "C"
        fila = clave["fila"]
        columna = clave["columna"]
        valor = clave["clave"]
        casillas = clave["casillas"]

        #Coloca la casilla negra que tiene la clave con valor (no puede usarse)
        #Aquí la casilla es negra y contiene clave, se pone -1 en tablero
        ESTRUCTURA_TABLERO[fila][columna] = -1

        #Guarda la clave en CLAVES: 
        #Si ya existe para esa posición, actualiza (puede haber clave fila y columna juntas)
        if (fila, columna) not in CLAVES:
            CLAVES[(fila, columna)] = {}

        if tipo == "F":
            CLAVES[(fila, columna)]["fila"] = valor
            #Marca casillas blancas a la derecha de la clave
            for i in range(1, casillas + 1):
                # Solo si está dentro de límites
                if columna + i < TAMAÑO_TABLERO:
                    ESTRUCTURA_TABLERO[fila][columna + i] = 0  # Casilla blanca vacía

        elif tipo == "C":
            CLAVES[(fila, columna)]["columna"] = valor
            #Marca casillas blancas hacia abajo de la clave
            for i in range(1, casillas + 1):
                if fila + i < TAMAÑO_TABLERO:
                    ESTRUCTURA_TABLERO[fila + i][columna] = 0  #Casilla blanca vacía

#----------------------------------------------
cargar_partidas_desde_archivo()
mostrar_menu_principal() #Al ejecutar el código, se llama a la función del menú principal
