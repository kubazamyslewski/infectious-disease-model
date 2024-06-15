import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Slider, Button
import tkinter as tk
from tkinter import simpledialog

import math
import numpy as np


class Person:
    def __init__(self, i, posx, posy, objx, objy, v, t_contagiado, fijo):
        self.v = max(v, 1)  # Ustawienie minimalnej wartości prędkości na 1
        self.objx = objx
        self.objy = objy
        self.indice = i
        self.nombre = "Persona " + str(i)
        self.infectado = False
        self.suceptible = True
        self.retirado = False
        self.posx = posx
        self.posy = posy
        self.fijo = fijo
        if self.fijo:
            self.deltax = 0
            self.deltay = 0
        else:
            self.deltax = (self.objx - self.posx) / self.v
            self.deltay = (self.objy - self.posy) / self.v
        self.i_contagio = -1
        self.t_contagiado = t_contagiado

    def __str__(self):
        return self.nombre + " en posicin " + str(self.posx) + ", " + str(self.posy)

    def infectar(self, i):
        self.infectado = True
        self.suceptible = False
        self.retirado = False
        self.i_contagio = i

    def retirar(self):
        self.retirado = True
        self.suceptible = False
        self.infectado = False

    def set_objetivo(self, objx, objy):
        self.objx = objx
        self.objy = objy
        if self.fijo:
            #self.deltax = 0
            #self.deltay = 0
            self.deltax = (self.objx - self.posx) / self.v
            self.deltay = (self.objy - self.posy) / self.v
        else:
            self.deltax = (self.objx - self.posx) / self.v
            self.deltay = (self.objy - self.posy) / self.v
        print("Nuevo OBJ   ", self.objx, self.objy, "  ", self.indice)

    def check_contagio(self, i):
        if self.i_contagio > -1:
            if i - self.i_contagio > self.t_contagiado:
                self.retirar()

    def update_pos(self, n_posx, n_posy):
        if n_posx == 0 and n_posy == 0:
            self.posx = self.posx + self.deltax
            self.posy = self.posy + self.deltay
        else:
            self.posx = n_posx
            self.posy = n_posy

        if abs(self.posx - self.objx) < 3 and abs(self.posy - self.objy) < 3:
            self.set_objetivo(np.random.random() * 100, np.random.random() * 100)
        if self.posx > 100:
            self.posx = 100
        if self.posy > 100:
            self.posy = 100
        if self.posx < 0:
            self.posx = 0
        if self.posy < 0:
            self.posy = 0

    def get_color(self):
        if self.infectado:
            return 'red'
        if self.suceptible:
            return 'blue'
        if self.retirado:
            return 'gray'

    def get_pos(self):
        return (self.posx, self.posy)

    def get_dist(self, x, y):
        return math.sqrt((self.posx - x) ** 2 + (self.posy - y) ** 2)


# SIMULATION PARAMETERS
n = 350  # number of individuals
percentageOfInfected = 1  # percentage of infected people at the beginning of the simulation (0-100%)
radiusOfTransmission = 2  # radius of transmission in pixels (0-100)
probabilityOfTransmission = 4  # probability of transmission in percentage (0-100%)
percentageInQuarantine = 70  # percentage of the people in quarantine (0-100%)
timeToRecover = 100  # time taken to recover in number of frames (0-infinity)
v_speed = 50

contagiados = 0
personas = []


def initialize_personas():
    global contagiados, personas, n, v_speed
    p_infectadas = slider_infectadas.val  # Pobierz wartość z suwaka
    contagiados = 0
    personas.clear()
    for i in range(n):
        p = Person(i, np.random.random() * 100, np.random.random() * 100,
                   np.random.random() * 100, np.random.random() * 100,
                   (np.random.random() + 0.5) * (100 - v_speed), timeToRecover, False)
        if np.random.random() < p_infectadas / 100:
            p.infectar(0)
            contagiados += 1
        if np.random.random() < percentageInQuarantine / 100:
            p.fijo = True
        personas.append(p)


fig = plt.figure(figsize=(14, 7))
ax = fig.add_subplot(1, 2, 1)
cx = fig.add_subplot(1, 2, 2)
ax.axis('off')
cx.axis([0, 1000, 0, n])
scatt = ax.scatter([p.posx for p in personas],
                   [p.posy for p in personas], c='blue', s=8)
caja = plt.Rectangle((0, 0), 100, 100, fill=False)
ax.add_patch(caja)
cvst, = cx.plot([0], color="red", label="Currently infected")
rvst, = cx.plot([0], color="gray", label="Recovered")
hvst, = cx.plot([0], color="blue", label="Healthy")
cx.legend(handles=[rvst, cvst, hvst])
cx.set_xlabel("Time")
cx.set_ylabel("People")

ct = [contagiados]
rt = [0]
ht = [n - contagiados]
t = [0]

# Top sliders
ax_infectadas = plt.axes([0.25, 0.95, 0.50, 0.02])
slider_infectadas = Slider(ax_infectadas, 'Initial Infected %', 0, 100, valinit=percentageOfInfected, valstep=1)

ax_individuals = plt.axes([0.25, 0.92, 0.50, 0.02])
slider_individuals = Slider(ax_individuals, 'Number of Individuals', 100, 500, valinit=n, valstep=1)

ax_speed = plt.axes([0.25, 0.89, 0.50, 0.02])
slider_speed = Slider(ax_speed, 'Speed of Individuals', 10, 100, valinit=v_speed)

initialize_personas()
# Separate window for reset and add infected options
root = tk.Tk()
root.withdraw()


def update(frame, rt, ct, ht, t):
    contciclo = 0
    recuciclo = 0
    for p in personas:
        p.check_contagio(frame)
        p.update_pos(0, 0)
        if p.retirado:
            recuciclo += 1
        if p.infectado:
            contciclo += 1
            for per in personas:
                if per.indice == p.indice or per.infectado or per.retirado:
                    continue
                d = p.get_dist(per.posx, per.posy)
                if d < radiusOfTransmission and np.random.random() < probabilityOfTransmission / 100:
                    per.infectar(frame)

    ct.append(contciclo)
    rt.append(recuciclo)
    ht.append(n - contciclo - recuciclo)
    t.append(frame)

    offsets = np.array([[p.posx for p in personas],
                        [p.posy for p in personas]])
    scatt.set_offsets(np.ndarray.transpose(offsets))
    scatt.set_color([p.get_color() for p in personas])
    scatt.set_sizes([8 for p in personas])
    cvst.set_data(t, ct)
    rvst.set_data(t, rt)
    hvst.set_data(t, ht)
    cx.set_xlim(0, max(t) + 10)
    cx.set_ylim(0, n)
    return scatt, cvst, rvst, hvst


def on_slider_update(val):
    global percentageOfInfected
    percentageOfInfected = slider_infectadas.val


def on_individuals_update(val):
    global n
    n = int(slider_individuals.val)


def on_speed_update(val):
    global v_speed
    v_speed = slider_speed.val


def on_reset(event=None):
    global ct, rt, ht, t, contagiados, animation

    # Zatrzymaj animację
    animation.event_source.stop()

    # Inicjalizuj osoby
    initialize_personas()

    # Wyczyść listy
    ct.clear()
    rt.clear()
    ht.clear()
    t.clear()

    # Ustaw wartości początkowe
    ct.append(contagiados)
    rt.append(0)
    ht.append(n - contagiados)
    t.append(0)

    # Uruchom animację od nowa
    animation = FuncAnimation(fig, update, interval=25, fargs=(rt, ct, ht, t), blit=True)
    animation.event_source.start()


def on_start(event):
    global ct, rt, ht, t, contagiados, animation

    # Zatrzymaj animację, jeśli jest uruchomiona
    animation.event_source.stop()

    # Inicjalizuj osoby
    initialize_personas()

    # Wyczyść listy
    ct.clear()
    rt.clear()
    ht.clear()
    t.clear()

    # Ustaw wartości początkowe
    ct.append(contagiados)
    rt.append(0)
    ht.append(n - contagiados)
    t.append(0)

    # Uruchom animację od nowa
    animation = FuncAnimation(fig, update, interval=25, fargs=(rt, ct, ht, t), blit=True)
    animation.event_source.start()


def on_stop(event):
    animation.event_source.stop()


# Add buttons and their callbacks
ax_reset = plt.axes([0.05, 0.05, 0.20, 0.05])
button_reset = Button(ax_reset, 'Restart')
button_reset.on_clicked(on_reset)

ax_start = plt.axes([0.30, 0.05, 0.20, 0.05])
button_start = Button(ax_start, 'Start')
button_start.on_clicked(on_start)

ax_stop = plt.axes([0.75, 0.05, 0.20, 0.05])
button_stop = Button(ax_stop, 'Stop')
button_stop.on_clicked(on_stop)

# Connect sliders to their callbacks
slider_infectadas.on_changed(on_slider_update)
slider_individuals.on_changed(on_individuals_update)
slider_speed.on_changed(on_speed_update)

# Start the animation
animation = FuncAnimation(fig, update, interval=25, fargs=(rt, ct, ht, t), blit=True)
plt.show()