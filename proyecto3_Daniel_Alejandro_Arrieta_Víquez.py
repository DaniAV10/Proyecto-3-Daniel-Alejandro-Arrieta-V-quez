#proyecto3_Daniel_Alejandro_Arrieta_Víquez
import tkinter as tk
from tkinter import messagebox
import time, json


#------------------ CONFIGURACIÓN INICIAL ------------------#
#-1 para casillas negras (pistas o bloqueadas), 0 para casillas blancas que se pueden modificar.
TIEMPO_LIMITE = 2 * 60 * 60
TAMAÑO_TABLERO = 5
ESTRUCTURA_TABLERO = [
    [-1, -1, -1, -1, -1],
    [-1,  0,  0,  0, -1],
    [-1,  0,  0,  0, -1],
    [-1,  0,  0,  0, -1],
    [-1, -1, -1, -1, -1],
]

# Claves

# (fila, columna): {"fila": suma_horizontal, "columna": suma_vertical}
CLAVES = {
    (0, 2): {"columna": 9},        
    (1, 0): {"fila": 6, "columna": 9},
    (2, 0): {"fila": 15},
    (3, 0): {"fila": 9}
}


# Diccionario con claves de suma por grupo de fila
CLAVES_FILA = {
    (1, 1): 6,  # grupo que empieza en fila 1, columna 1
    (2, 1): 15,
    (3, 1): 9
}

# Diccionario con claves de suma por grupo de columna
CLAVES_COLUMNA = {
    (1, 1): 9,   # grupo que empieza en fila 1, columna 1
    (1, 2): 9,
    (1, 3): 12
}


#------------------ VARIABLES DE ESTADO ------------------#
nombre_jugador = ""
juego_activo = False
tiempo_inicio = None
pila_jugadas = []
pila_deshacer = []
valores_tablero = [["" for _ in range(TAMAÑO_TABLERO)] for _ in range(TAMAÑO_TABLERO)]

#------------------ VENTANA PRINCIPAL ------------------#
ventana = tk.Tk()
ventana.title("Kakuro-Daniel Alejandro Arrieta Víquez")
ventana.geometry("1000x700")
ventana.configure(bg='white')

entrada_nombre = tk.StringVar()
tiempo_mostrado = tk.StringVar(value="00:00:00")
numero_elegido = tk.StringVar(value="")
nivel_actual = "facil"  #Variable que lleva el nivel actual, por el momento el fácil


#Tiempo:
modo_tiempo = tk.StringVar(value="sin_reloj")  #Valor por defecto sin reloj
horas_config = tk.IntVar(value=0)
minutos_config = tk.IntVar(value=0)
segundos_config = tk.IntVar(value=0)
tiempo_limite = None  #Se definirá al iniciar si es temporizador

#------------------ FUNCIONES ------------------#

def actualizar_reloj():
    global juego_activo, tiempo_inicio, modo_tiempo, tiempo_limite

    if not juego_activo or modo_tiempo.get() == "sin_reloj": #Si no está en jeugo o el reloj está desactivado, no se ejecutará el resto de la función
        return

    if modo_tiempo.get() == "cronometro":
        transcurrido = int(time.time() - tiempo_inicio)
        h, m, s = transcurrido // 3600, (transcurrido % 3600) // 60, transcurrido % 60
    if modo_tiempo.get() == "cronometro": 
        transcurrido = int(time.time() - tiempo_inicio) #Validaciones de tiempo
        if transcurrido > 2*3600:
            #Si se llega a 2 horas, detener juego o mostrar mensaje
            messagebox.showinfo("Tiempo", "El cronómetro ha alcanzado el límite de 2 horas. Juego terminado.")
            reiniciar()
            return
        h, m, s = transcurrido // 3600, (transcurrido % 3600) // 60, transcurrido % 60

    else:  # temporizador
        tiempo_restante = tiempo_limite - int(time.time() - tiempo_inicio)

        if tiempo_restante <= 0:
            # Temporizador llegó a 0, preguntar si quiere continuar con cronómetro
            respuesta = messagebox.askyesno("Tiempo Expirado", "TIEMPO EXPIRADO.\n¿DESEA CONTINUAR EL MISMO JUEGO (SI/NO)?")
            if respuesta:  # Sí -> Cambiar a cronómetro con tiempo inicial igual al configurado
                modo_tiempo.set("cronometro")  # Cambiar modo
                tiempo_inicio = time.time() - tiempo_limite  # Ajustar tiempo_inicio para que cronómetro empiece desde tiempo_limite
            else:  # No -> Finalizar juego
                messagebox.showinfo("Juego", "Juego finalizado por expiración de tiempo.")
                reiniciar()
            return

        h, m, s = tiempo_restante // 3600, (tiempo_restante % 3600) // 60, tiempo_restante % 60

    tiempo_mostrado.set(f"{h:02}:{m:02}:{s:02}")
    ventana.after(1000, actualizar_reloj)


def iniciar():
    #Validar nombre:
    global juego_activo, tiempo_inicio, tiempo_limite, nombre_jugador
    nombre = entrada_nombre.get().strip()
    if len(nombre) == 0:
        messagebox.showerror("ERROR", "Debe ingresar un nombre para iniciar el juego.")
        return
    if len(nombre) > 40:
        messagebox.showerror("ERROR", "El nombre debe tener máximo 40 caracteres.")
        return

    #Tiempo:
    if modo_tiempo.get() == "temporizador":
        h = horas_config.get()
        m = minutos_config.get()
        s = segundos_config.get()
        tiempo_limite = h*3600 + m*60 + s
        if tiempo_limite == 0:
            messagebox.showerror("ERROR", "Debe configurar un tiempo mayor a cero para el temporizador.")
            return
    elif modo_tiempo.get() == "cronometro":
        tiempo_limite = None

    else:  #Sin reloj
        tiempo_limite = None

    nombre_jugador = nombre
    juego_activo = True
    tiempo_inicio = time.time()
    boton_iniciar.config(state="disabled") #Deshabilitar botón
    actualizar_reloj()
    

def elegir_numero(n):
    numero_elegido.set(str(n))
    for boton in botones_numeros:
        boton.config(bg="SystemButtonFace")
    botones_numeros[n-1].config(bg="lightblue")

def click_en_casilla(fila, columna):
    #Validar que la casilla sea modificable
    if ESTRUCTURA_TABLERO[fila][columna] != 0:
        messagebox.showerror("Error", "Esta casilla no puede ser modificada.")
        return
    
    #Borrador:
    global modo_borrador
    if modo_borrador:
        anterior = valores_tablero[fila][columna]
        #Si la casilla no se puede modificar
        if ESTRUCTURA_TABLERO[fila][columna] != 0:
            messagebox.showerror("Error", "Esta casilla no puede ser modificada.")
        return
        if anterior == "":
            messagebox.showinfo("Info", "La casilla ya está vacía.")
            return
        valores_tablero[fila][columna] = ""
        botones_tablero[fila][columna].config(text="")
        pila_jugadas.append({"fila": fila, "col": columna, "anterior": anterior, "nuevo": ""})
        pila_deshacer.clear()
        modo_borrador = False  # Desactiva modo borrador
        messagebox.showinfo("Borrado", "Contenido eliminado.")
        return

    
    if not juego_activo or ESTRUCTURA_TABLERO[fila][columna] != 0:
        messagebox.showerror("ERROR", "Jugada inválida")
        return

    #Dividir validación si no se ha seleccionado un número
    if not numero_elegido.get():
        messagebox.showerror("ERROR", "FALTA QUE SELECCIONE EL NÚMERO")
        return

    nuevo = numero_elegido.get()
    anterior = valores_tablero[fila][columna]
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
    for i in range(TAMAÑO_TABLERO):
        for j in range(TAMAÑO_TABLERO):
            if ESTRUCTURA_TABLERO[i][j] == 0 and valores_tablero[i][j] == "":
                return
    guardar_record(nombre_jugador, tiempo_mostrado.get(), "Fácil") 
    messagebox.showinfo("¡EXCELENTE JUGADOR!", "TERMINÓ EL JUEGO CON ÉXITO.")
    reiniciar()


def guardar_record(nombre, tiempo):
    try:
        with open("records_kakuro.json", "r") as archivo:
            records = json.load(archivo)
    except:
        records = []
    records.append({"nombre": nombre, "tiempo": tiempo, "nivel": nivel_actual})
    with open("records_kakuro.json", "w") as archivo:
        json.dump(records, archivo, indent=2)

def reiniciar():
    global juego_activo, valores_tablero, pila_jugadas, pila_deshacer
    juego_activo = False
    boton_iniciar.config(state="normal") #Habilitar nuevamente el botón
    valores_tablero = [["" for _ in range(TAMAÑO_TABLERO)] for _ in range(TAMAÑO_TABLERO)]
    pila_jugadas.clear()
    pila_deshacer.clear()
    for i in range(TAMAÑO_TABLERO):
        for j in range(TAMAÑO_TABLERO):
            botones_tablero[i][j].config(text="")
    tiempo_mostrado.set("00:00:00")
    numero_elegido.set("")
    for b in botones_numeros:
        b.config(bg="SystemButtonFace")

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
        return
    jugada = pila_deshacer.pop()
    f, c = jugada["fila"], jugada["col"]
    valores_tablero[f][c] = jugada["nuevo"]
    botones_tablero[f][c].config(text=jugada["nuevo"])
    pila_jugadas.append(jugada)

def borrar():
    if juego_activo and messagebox.askyesno("Confirmar", "¿Desea borrar el juego?"):
        reiniciar()
        
def mostrar_records():
    try:
        with open("records_kakuro.json", "r") as archivo:
            records = json.load(archivo)
    except:
        records = []

    # Filtrar solo récords para nivel actual
    records_nivel = [r for r in records if r.get("nivel") == nivel_actual]

    if not records_nivel:
        messagebox.showinfo("Récords", "NO HAY PARTIDAS PARA ESTE NIVEL.")
        regresar_menu_principal()
        return

    texto = "\n".join(f"{r['nombre']}: {r['tiempo']}" for r in records_nivel)
    messagebox.showinfo("Récords", texto)

def regresar_menu_principal():
    reiniciar()
    messagebox.showinfo("Menú", "Regresando al menú principal")    
#------------------ INTERFAZ ------------------#
tk.Label(ventana, text="KAKURO", font=("Arial", 28, "bold"), bg='white').place(x=30, y=10)
tk.Label(ventana, text="Jugador: (1-40 caracteres)", bg='white').place(x=150, y=20)
tk.Entry(ventana, textvariable=entrada_nombre, width=40).place(x=500, y=20)
tk.Label(ventana, text="Horas", bg='white').place(x=80, y=610)
tk.Label(ventana, text="Minutos", bg='white').place(x=150, y=610)
tk.Label(ventana, text="Segundos", bg='white').place(x=230, y=610)
tk.Label(ventana, text="NIVEL FÁCIL", font=("Arial", 12, "bold"), bg='white').place(x=80, y=670)

#Tiempo:
#Etiqueta para modo de tiempo
label_tiempo = tk.Label(ventana, textvariable=tiempo_mostrado, font=("Courier", 14), bg='white')
label_tiempo.place(x=80, y=640)
tk.Label(ventana, text="Modo de Tiempo:", bg='white').place(x=700, y=10)

#Radio buttons para elegir modo
tk.Radiobutton(ventana, text="Sin Reloj", variable=modo_tiempo, value="sin_reloj", bg='white').place(x=700, y=10)
tk.Radiobutton(ventana, text="Cronómetro", variable=modo_tiempo, value="cronometro", bg='white').place(x=700, y=40)
tk.Radiobutton(ventana, text="Temporizador", variable=modo_tiempo, value="temporizador", bg='white').place(x=800, y=40)

#Entradas para configurar horas, minutos y segundos (sólo se usan si el modo es temporizador)
tk.Label(ventana, text="Horas:", bg='white').place(x=700, y=70)
tk.Spinbox(ventana, from_=0, to=23, textvariable=horas_config, width=3).place(x=750, y=70)

tk.Label(ventana, text="Minutos:", bg='white').place(x=700, y=100)
tk.Spinbox(ventana, from_=0, to=59, textvariable=minutos_config, width=3).place(x=750, y=100)

tk.Label(ventana, text="Segundos:", bg='white').place(x=700, y=130)
tk.Spinbox(ventana, from_=0, to=59, textvariable=segundos_config, width=3).place(x=750, y=130)



botones_numeros = []
for i in range(9):
    boton = tk.Button(ventana, text=str(i+1), width=4, height=2, command=lambda n=i+1: elegir_numero(n))
    boton.place(x=880, y=100 + i*40)
    botones_numeros.append(boton)
#Borrador:
modo_borrador = False
def activar_borrador():
    global modo_borrador
    modo_borrador = True
    numero_elegido.set("")  # Deseleccionar número
    for b in botones_numeros:
        b.config(bg="SystemButtonFace")
    messagebox.showinfo("Borrador", "Seleccione una casilla para borrar su contenido.")

boton_goma = tk.Button(ventana, text="Goma", width=4, height=2, command=activar_borrador) #Puse goma porque borrador no cabe
boton_goma.place(x=880, y=100 + 9*40)



boton_iniciar = tk.Button(ventana, text="INICIAR\nJUEGO", bg="deeppink", fg="white", width=10, height=2, command=iniciar)
boton_iniciar.place(x=30, y=500)

botones_control = [
    ("DESHACER\nJUGADA", "lightgreen", deshacer, 150, 500),
    ("BORRAR\nJUEGO", "lightsteelblue", borrar, 300, 500),
    ("GUARDAR\nJUEGO", "orange", lambda: messagebox.showinfo("Info", "No implementado"), 430, 500),
    ("RÉCORDS", "yellow", mostrar_records, 560, 500),
    ("REHACER\nJUGADA", "cyan", rehacer, 150, 570),
    ("TERMINAR\nJUEGO", "mediumseagreen", verificar_fin, 300, 570),
    ("CARGAR\nJUEGO", "chocolate", lambda: messagebox.showinfo("Info", "No implementado"), 430, 570),
]
for texto, color, comando, x, y in botones_control:
    tk.Button(ventana, text=texto, bg=color, width=12, height=2, command=comando).place(x=x, y=y)

botones_tablero = []
for i in range(TAMAÑO_TABLERO):
    fila = []
    for j in range(TAMAÑO_TABLERO):
        x, y = 30 + j*40, 70 + i*40
        if ESTRUCTURA_TABLERO[i][j] == -1:
            texto = ""
            if (i, j) in CLAVES:
                clave = CLAVES[(i, j)]
                fila_clave = f"{clave['fila']}→" if "fila" in clave else ""
                columna_clave = f"↓{clave['columna']}" if "columna" in clave else ""
                texto = f"{fila_clave}\n{columna_clave}".strip()
            celda = tk.Label(ventana, text=texto, bg="black", fg="white", relief="solid", font=("Arial", 8), justify="center")
        else:
            celda = tk.Button(ventana, text="", command=lambda f=i, c=j: click_en_casilla(f, c))
        celda.place(x=x, y=y, width=40, height=40)
        fila.append(celda)
    botones_tablero.append(fila)
    
def actualizar_visibilidad_reloj(*args):
    if modo_tiempo.get() == "sin_reloj":
        label_tiempo.place_forget()  #Ocultar el reloj
    else:
        label_tiempo.place(x=80, y=640)  #Mostrar el reloj

modo_tiempo.trace_add("write", actualizar_visibilidad_reloj) #Cambiar cada vez que se modifique el modo de tiempo


ventana.mainloop()



