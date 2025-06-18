#proyecto3_Daniel_Alejandro_Arrieta_Víquez
import tkinter as tk
from tkinter import messagebox
import time, json

#------------------ CONFIGURACIÓN INICIAL ------------------#
TIEMPO_LIMITE = 2 * 60 * 60
TAMAÑO_TABLERO = 5
ESTRUCTURA_TABLERO = [
    [-1, -1, -1, -1, -1],
    [-1,  0,  0,  0, -1],
    [-1,  0,  0,  0, -1],
    [-1,  0,  0,  0, -1],
    [-1, -1, -1, -1, -1],
]

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

#------------------ FUNCIONES ------------------#
def actualizar_reloj():
    if juego_activo:
        transcurrido = int(time.time() - tiempo_inicio)
        h, m, s = transcurrido // 3600, (transcurrido % 3600) // 60, transcurrido % 60
        tiempo_mostrado.set(f"{h:02}:{m:02}:{s:02}")
        ventana.after(1000, actualizar_reloj)

def iniciar():
    global juego_activo, tiempo_inicio, nombre_jugador
    nombre = entrada_nombre.get().strip()
    if not nombre or len(nombre) > 40:
        messagebox.showerror("Error", "Nombre inválido")
        return
    nombre_jugador = nombre
    juego_activo = True
    tiempo_inicio = time.time()
    boton_iniciar.config(state="disabled")
    actualizar_reloj()

def elegir_numero(n):
    numero_elegido.set(str(n))
    for boton in botones_numeros:
        boton.config(bg="SystemButtonFace")
    botones_numeros[n-1].config(bg="lightblue")

def click_en_casilla(fila, columna):
    if not juego_activo or ESTRUCTURA_TABLERO[fila][columna] != 0 or not numero_elegido.get():
        messagebox.showerror("Error", "Jugada inválida")
        return

    nuevo = numero_elegido.get()
    anterior = valores_tablero[fila][columna]
    if nuevo == anterior:
        return

    if nuevo in [valores_tablero[fila][i] for i in range(TAMAÑO_TABLERO) if ESTRUCTURA_TABLERO[fila][i] == 0] or \
       nuevo in [valores_tablero[i][columna] for i in range(TAMAÑO_TABLERO) if ESTRUCTURA_TABLERO[i][columna] == 0]:
        messagebox.showerror("Error", "Número repetido en fila o columna")
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
    guardar_record(nombre_jugador, tiempo_mostrado.get())
    messagebox.showinfo("¡Éxito!", "Juego finalizado con éxito")
    reiniciar()

def guardar_record(nombre, tiempo):
    try:
        with open("records_kakuro.json", "r") as archivo:
            records = json.load(archivo)
    except:
        records = []
    records.append({"nombre": nombre, "tiempo": tiempo})
    with open("records_kakuro.json", "w") as archivo:
        json.dump(records, archivo, indent=2)

def reiniciar():
    global juego_activo, valores_tablero, pila_jugadas, pila_deshacer
    juego_activo = False
    boton_iniciar.config(state="normal")
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
    if not records:
        messagebox.showinfo("RÉCORDS", "No hay récords guardados.")
        return
    texto = "\n".join(f"{r['nombre']}: {r['tiempo']}" for r in records)
    messagebox.showinfo("RÉCORDS", texto)

#------------------ INTERFAZ ------------------#
tk.Label(ventana, text="KAKURO", font=("Arial", 28, "bold"), bg='white').place(x=30, y=10)
tk.Label(ventana, text="Jugador: (1-40 caracteres)", bg='white').place(x=150, y=20)
tk.Entry(ventana, textvariable=entrada_nombre, width=40).place(x=500, y=20)
tk.Label(ventana, text="Horas", bg='white').place(x=80, y=610)
tk.Label(ventana, text="Minutos", bg='white').place(x=150, y=610)
tk.Label(ventana, text="Segundos", bg='white').place(x=230, y=610)
tk.Label(ventana, textvariable=tiempo_mostrado, font=("Courier", 14), bg='white').place(x=80, y=640)
tk.Label(ventana, text="NIVEL FÁCIL", font=("Arial", 12, "bold"), bg='white').place(x=80, y=670)

botones_numeros = []
for i in range(9):
    boton = tk.Button(ventana, text=str(i+1), width=4, height=2, command=lambda n=i+1: elegir_numero(n))
    boton.place(x=880, y=100 + i*40)
    botones_numeros.append(boton)

tk.Button(ventana, text="Goma", width=4, height=2, command=lambda: [numero_elegido.set(""), [b.config(bg="SystemButtonFace") for b in botones_numeros]]).place(x=880, y=100 + 9*40)

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
        celda = tk.Label(ventana, text="", bg="gray", relief="solid") if ESTRUCTURA_TABLERO[i][j] == -1 else \
                tk.Button(ventana, text="", command=lambda f=i, c=j: click_en_casilla(f, c))
        celda.place(x=x, y=y, width=40, height=40)
        fila.append(celda)
    botones_tablero.append(fila)

ventana.mainloop()

