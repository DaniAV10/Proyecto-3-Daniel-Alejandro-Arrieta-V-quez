#proyecto3_Daniel_Alejandro_Arrieta_Víquez
import tkinter as tk
from tkinter import messagebox
import time, json

#----------FUNCIÓN MENÚ PRINCIPAL-----------------------#
def mostrar_menu_principal():
    menu = tk.Tk()
    menu.title("Menú Principal Kakuro - Daniel Alejandro Arrieta Víquez")
    menu.geometry("500x300")
    menu.configure(bg="white")

    tk.Label(menu, text="KAKURO", font=("Arial", 32, "bold"), bg="white", fg="black").pack(pady=30)

    tk.Button(menu, text="Opción A: Jugar", font=("Arial", 14), width=20, height=2,
              command=lambda: [menu.destroy(), iniciar_juego()]).pack(pady=10)

    tk.Button(menu, text="Opción B: Configurar", font=("Arial", 14), width=20, height=2,
              command=lambda: messagebox.showinfo("Configurar", "Aún no implementado.")).pack()

    menu.mainloop()


#--------------FUNCIÓN INICIAR JUEGO------------------#
def iniciar_juego():
    global ventana
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
    
    #------------------ CONFIGURACIÓN INICIAL ------------------#
    TIEMPO_LIMITE = 2 * 60 * 60
    TAMAÑO_TABLERO = 9
    ESTRUCTURA_TABLERO = [
        [-1, -1, -1, -1, -1, -1, -1, -1, -1],
        [-1, -1, {"columna": 16}, {"columna": 24}, -1, {"columna": 17}, {"columna": 29}, {"columna": 35}, -1],
        [-1, {"fila": 17}, 0, 0, -1, 0, 0, 0, {"columna": 7}],
        [-1, {"fila": 16}, 0, 0, {"fila": 17}, 0, 0, 0, {"columna": 8}],
        [-1, -1, -1, {"fila": 35}, 0, 0, 0, 0, 0],
        [-1, {"columna": 7}, {"fila": 7}, 0, 0, {"fila": 8}, 0, 0, -1],
        [-1, {"columna": 8}, 0, 0, {"columna": 9}, 0, 0, -1, -1],
        [-1, -1, -1, -1, {"fila": 7}, 0, 0, -1, -1],
        [-1, -1, -1, -1, -1, -1, -1, -1, -1],
    ]

    #Claves
    CLAVES = {}
    for i in range(TAMAÑO_TABLERO):
        for j in range(TAMAÑO_TABLERO):
            celda = ESTRUCTURA_TABLERO[i][j]
            if isinstance(celda, dict):
                CLAVES[(i, j)] = celda
                ESTRUCTURA_TABLERO[i][j] = -1  


    #Diccionario con claves de suma por grupo de fila
    CLAVES_FILA = {
        (1, 1): 6,  
        (2, 1): 15,
        (3, 1): 9
    }

    #Diccionario con claves de suma por grupo de columna
    CLAVES_COLUMNA = {
        (1, 1): 9,   
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

    boton_goma = tk.Button(ventana, text="Goma", width=4, height=2, command=activar_borrador) #Puse goma porque borrador no cabe
    boton_goma.place(x=880, y=100 + 9*40)



    boton_iniciar = tk.Button(ventana, text="INICIAR\nJUEGO", bg="deeppink", fg="white", width=10, height=2, command=iniciar)
    boton_iniciar.place(x=30, y=500)

    botones_control = [
        ("DESHACER\nJUGADA", "lightgreen", deshacer, 150, 500),
        ("BORRAR\nJUEGO", "lightsteelblue", borrar, 300, 500),
        ("GUARDAR\nJUEGO", "orange", guardar_juego, 430, 500), #Se conecta, ya se implemento el botón.
        ("RÉCORDS", "yellow", mostrar_records, 560, 500),
        ("REHACER\nJUGADA", "cyan", rehacer, 150, 570),
        ("TERMINAR\nJUEGO", "mediumseagreen", terminar_juego, 300, 570),
        ("CARGAR\nJUEGO", "chocolate", cargar_juego, 430, 570), #Se conecta, ya se implemento el botón.

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

    modo_tiempo.trace_add("write", actualizar_visibilidad_reloj) #Cambiar cada vez que se modifique el modo de tiempo


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

    else:  #temporizador
        tiempo_restante = tiempo_limite - int(time.time() - tiempo_inicio)

        if tiempo_restante <= 0:
            #Temporizador llegó a 0, preguntar si quiere continuar con cronómetro
            respuesta = messagebox.askyesno("Tiempo Expirado", "TIEMPO EXPIRADO.\n¿DESEA CONTINUAR EL MISMO JUEGO (SI/NO)?")
            if respuesta:  #Sí -> Cambiar a cronómetro con tiempo inicial igual al configurado
                modo_tiempo.set("cronometro")  # Cambiar modo
                tiempo_inicio = time.time() - tiempo_limite  #Ajustar tiempo_inicio para que cronómetro empiece desde tiempo_limite
            else:  #No -> Finalizar juego
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
    global juego_activo, valores_tablero, pila_jugadas, pila_deshacer
    juego_activo = False
    boton_iniciar.config(state="normal") #Habilitar nuevamente el botón
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
        messagebox.showwarning("Advertencia", "NO SE HA INICIADO EL JUEGO")
        return

    respuesta = messagebox.askyesno("Confirmar", "¿ESTÁ SEGURO DE BORRAR EL JUEGO?")
    if respuesta:
        reiniciar()
    else:
        messagebox.showinfo("Continuar", "Puede continuar con el mismo juego.")
        
def mostrar_records():
    global juego_activo
    if juego_activo:
        detener_temporizador = True
    else:
        detener_temporizador = False

    if detener_temporizador:
        juego_activo_backup = True
        juego_activo = False

    try:
        with open("kakuro2025_récords.json", "r") as archivo:
            records = json.load(archivo)
    except:
        messagebox.showinfo("RÉCORDS", "No hay récords guardados.")
        return

    ventana_records = tk.Toplevel(ventana)
    ventana_records.title("RÉCORDS")
    ventana_records.geometry("600x500")
    ventana_records.configure(bg='white')

    tk.Label(ventana_records, text="RECORDS", font=("Arial", 20, "bold"), bg='white').pack(pady=10)

    frame_opciones = tk.Frame(ventana_records, bg='white')
    frame_opciones.pack()

    nivel_var = tk.StringVar(value=nivel_actual)
    jugador_var = tk.StringVar(value="Todos")

    niveles = ["Todos", "fácil", "medio", "difícil", "experto"]
    jugadores = ["Todos", "Yo"]

    tk.Label(frame_opciones, text="Nivel:", bg='white').grid(row=0, column=0)
    tk.OptionMenu(frame_opciones, nivel_var, *niveles).grid(row=0, column=1)

    tk.Label(frame_opciones, text="Jugador:", bg='white').grid(row=0, column=2)
    tk.OptionMenu(frame_opciones, jugador_var, *jugadores).grid(row=0, column=3)

    area_texto = tk.Text(ventana_records, width=60, height=20, font=("Courier", 10))
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
                if jv == "Yo" and entry["nombre"] != nombre_jugador:
                    continue
                area_texto.insert(tk.END, f"{idx}- {entry['nombre']} {entry['tiempo']}\n")
            area_texto.insert(tk.END, "\n")

    tk.Button(ventana_records, text="MOSTRAR", command=actualizar_resultado, bg="lightblue").pack(pady=5)

    def cerrar():
        ventana_records.destroy()
        if detener_temporizador:
            juego_activo = True
            actualizar_reloj()

    ventana_records.protocol("WM_DELETE_WINDOW", cerrar)

def regresar_menu_principal():
    reiniciar()
    messagebox.showinfo("Menú", "Regresando al menú principal")


#Nueva función: Terminar juego:
def terminar_juego():
    global juego_activo
    if not juego_activo:
        messagebox.showwarning("Advertencia", "NO SE HA INICIADO EL JUEGO")
        return

    respuesta = messagebox.askyesno("Confirmar", "¿ESTÁ SEGURO DE TERMINAR EL JUEGO?")
    if respuesta:
        reiniciar()
        messagebox.showinfo("Juego terminado", "El juego ha finalizado. Puede iniciar uno nuevo.")
    else:
        messagebox.showinfo("Continuar", "Puede continuar con el mismo juego.")

#Nueva función: Guardar juego:

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
        label_tiempo.place_forget()  #Ocultar el reloj
    else:
        label_tiempo.place(x=80, y=640)  #Mostrar el reloj

#----------------------------------------------
mostrar_menu_principal() #Al ejecutar el código, se llama a la función del menú principal
