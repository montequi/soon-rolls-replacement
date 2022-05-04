import tkinter
from tkinter import ttk
from tkinter import *
import os
import json
import time

import psutil
from PIL import ImageTk, Image
import matplotlib.pyplot as plt
import numpy as np
import threading


def imshow(filename):
    threading.Thread(target=window, args=(filename,)).start()

def imclose():
    global running
    running = False

#rolling job, it is defined by the tons, the quality of the material rolled, the constraints among stands and the
#features of the stands geometry and shape separated by #
class Batch:
    def __init__(self,tons,quality,restrictions,cosascajas):
        self.tons = tons
        self.quality = quality
        self.restrictions = restrictions
        self.cosascajas = cosascajas



#a constraint is defined by the type, the quantity and the factor provided the constraints formula
class Restriction:
    def __init__(self,type,quantity,factor):
        self.type = str(type)
        self.quantity = str(quantity)
        self.factor = str(factor)

#Product to be rolled
class Product:
    def __init__(self,window):
        #initializations
        self.restrictions = []
        #jobs that are gonna be rolled
        self.batches = []
        #main window of the application
        self.wind = window
        #Title of the window
        self.wind.title('Batches')

        # a frame is created to create a rolling job inside the main window
        # title of the frame
        frame = LabelFrame(self.wind, text = 'Register new Batch')
        #position of the frame inside the application window
        frame.grid(row = 0, column = 0, columnspan = 6, pady = 20)

        # Tons input
        # text and place of the label of the text input
        Label(frame, text ='Tons:    ',anchor="e", justify=LEFT).grid(row = 1,column = 0)
        #text input
        self.tons= Entry(frame)
        #focus to the text input
        self.tons.focus()
        #place of the text input
        self.tons.grid(row = 1, column = 1)

        # Quality input
        # text and place of the label of the combobox
        Label(frame, text = ' Quality: ').grid(row=1,column = 2)
        self.combo = ttk.Combobox(frame, state="readonly")
        #possible values
        self.combo["values"] = ["1", "2", "3", "4","5"]
        #initial value
        self.combo.set("1")
        #place of the combobox
        self.combo.grid(row = 1, column = 3)
        # value selected of the combobox
        self.quality = self.combo.get()

        # geometry
        # text and place of the label of the combobox
        Label(frame, text='                  Geometries -> 16: ').grid(row=2, column=0)
        self.geometry = ttk.Combobox(frame, state="readonly")
        # possible values
        self.geometry["values"] = ["Rodillos  de 8 x 72"]
        #initial value
        self.geometry.set("Rodillos  de 8 x 72")
        #place of the combobox
        self.geometry.grid(row=2, column=1)

        # text and place of the label of the combobox
        Label(frame, text='17: ').grid(row=2, column=2)
        self.geometry2 = ttk.Combobox(frame, state="readonly")
        #possible values
        self.geometry2["values"] = ["Rodillos  de 8 x 72"]
        #initial value
        self.geometry2.set("Rodillos  de 8 x 72")
        #place of the combobox
        self.geometry2.grid(row=2, column=3)

        #text and place of the label of the combobox
        Label(frame, text='18: ').grid(row=2, column=4)
        self.geometry3= ttk.Combobox(frame, state="readonly")
        #possible values
        self.geometry3["values"] = ["Rodillos  de 8 x 72"]
        #initial value
        self.geometry3.set("Rodillos  de 8 x 72")
        #place of the combobox
        self.geometry3.grid(row=2, column=5)

        #text and place of the label of the combobox
        Label(frame, text='19: ').grid(row=2, column=6)
        self.geometry4= ttk.Combobox(frame, state="readonly")
        #possible values
        self.geometry4["values"] = ["Rodillos  de 6 x 62"]
        #initial value
        self.geometry4.set("Rodillos  de 6 x 62")
        #place of the combobox
        self.geometry4.grid(row=2, column=7)

        # shape
        # text and place of the label of the combobox
        Label(frame, text='                  Shapes ->         16: ').grid(row=3, column=0)
        self.shape = ttk.Combobox(frame, state="readonly")
        #possible values
        self.shape["values"] = ["419"]
        #initial value
        self.shape.set("419")
        #place of the combobox
        self.shape.grid(row=3, column=1)

        #text and place of the label of the combobox
        Label(frame, text='17: ').grid(row=3, column=2)
        self.shape2 = ttk.Combobox(frame, state="readonly")
        #possible values
        self.shape2["values"] = ["420"]
        #initial value
        self.shape2.set("420")
        #place of the combobox
        self.shape2.grid(row=3, column=3)

        #text and place of the label of the combobox
        Label(frame, text='18: ').grid(row=3, column=4)
        self.shape3 = ttk.Combobox(frame, state="readonly")
        #possible values
        self.shape3["values"] = ["357"]
        # initial value
        self.shape3.set("357")
        #place of the combobox
        self.shape3.grid(row=3, column=5)

        #text and place of the label of the combobox
        Label(frame, text='19: ').grid(row=3, column=6)
        self.shape4 = ttk.Combobox(frame, state="readonly")
        #possible values
        self.shape4["values"] = ["394"]
        # initial value
        self.shape4.set("394")
        # place of the combobox
        self.shape4.grid(row=3, column=7)

        # Constraints
        # text and place of the label
        Label(frame, text='         Restrictions : ').grid(row=4, column=0)
        Label(frame, text='16-17 : ').grid(row=5, column=1)
        Label(frame, text='Type : ').grid(row=5, column=2)
        self.combo2 = ttk.Combobox(frame, state="readonly")
        #possible values
        self.combo2["values"] = ["+-", "="]
        #initial value
        self.combo2.set("+-")
        #place of the combobox
        self.combo2.grid(row=5, column=3)

        # text and place of the label
        Label(frame, text='Quantity: ').grid(row=5, column=4)
        #text input
        self.quantity2 = Entry(frame)
        #place of the text input
        self.quantity2.grid(row=5, column=5)

        #text and place of the label
        Label(frame, text='Factor: ').grid(row=5, column=6)
        #text input
        self.factor2 = Entry(frame)
        #place of the text input
        self.factor2.grid(row=5, column=7)


        #####################17-18
        # text and place of the labels
        Label(frame, text='17-18 : ').grid(row=6, column=1)
        Label(frame, text='Type : ').grid(row=6, column=2)
        self.combo3 = ttk.Combobox(frame, state="readonly")
        #possible values
        self.combo3["values"] = ["+-", "="]
        #initial value
        self.combo3.set("+-")
        #place of the combobox
        self.combo3.grid(row=6, column=3)

        # text and place of the label
        Label(frame, text='Quantity: ').grid(row=6, column=4)
        # text input
        self.quantity3 = Entry(frame)
        # place of the text input
        self.quantity3.grid(row=6, column=5)

        #text and place of the label
        Label(frame, text='Factor: ').grid(row=6, column=6)
        #text input
        self.factor3 = Entry(frame)
        #place of the text input
        self.factor3.grid(row=6, column=7)

        #####################18-19
        # text and place of the labels
        Label(frame, text='18-19 : ').grid(row=7, column=1)
        Label(frame, text='Type : ').grid(row=7, column=2)
        self.combo4 = ttk.Combobox(frame, state="readonly")
        # possible values
        self.combo4["values"] = ["+-", "="]
        # initial value
        self.combo4.set("+-")
        #place of the combobox
        self.combo4.grid(row=7, column=3)


        #text and place of the label
        Label(frame, text='Quantity: ').grid(row=7, column=4)
        # text input
        self.quantity4 = Entry(frame)
        # place of the text input
        self.quantity4.grid(row=7, column=5)

        #text and place of the label
        Label(frame, text='Factor: ').grid(row=7, column=6)
        # text input
        self.factor4 = Entry(frame)
        # place of the text input
        self.factor4.grid(row=7, column=7)

        # Button Add Batch
        ttk.Button(frame, text='Save Batch', command=self.add_product).grid(row=8, columnspan=8, sticky=W + E)

        # Output Messages
        self.message = Label(text='', fg='red')
        self.message.grid(row=9, column=0, columnspan=3, sticky=W + E)
        # Table for displaying the jobs saved
        columns = ('#1', '#2', '#3', '#4', '#5', '#6', '#7','#8', '#9')

        self.tree = ttk.Treeview(self.wind, columns=columns, show='headings')
        self.tree.column('#1', width=50, stretch=NO)
        self.tree.column('#2', width=50, stretch=NO)
        self.tree.column('#3', width=100, stretch=NO)
        self.tree.column('#4', width=100, stretch=NO)
        self.tree.column('#5', width=100, stretch=NO)
        self.yscrollbar = ttk.Scrollbar(self.wind, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.yscrollbar.set)
        self.tree.grid(row=10, column=0, sticky="nsew")
        self.yscrollbar.grid(row=10, column=1, sticky='nse')
        self.yscrollbar.configure(command=self.tree.yview)

        self.tree.heading('#1', text='Tons', anchor=CENTER)
        self.tree.heading('#2', text='Quality', anchor=CENTER)
        self.tree.heading('#3', text='Restriction 16-17', anchor=CENTER)
        self.tree.heading('#4', text='Restriction 17-18', anchor=CENTER)
        self.tree.heading('#5', text='Restriction 18-19', anchor=CENTER)
        self.tree.heading('#6', text='Characteristics 16', anchor=CENTER)
        self.tree.heading('#7', text='Characteristics 17', anchor=CENTER)
        self.tree.heading('#8', text='Characteristics 18', anchor=CENTER)
        self.tree.heading('#9', text='Characteristics 19', anchor=CENTER)

        # Buttons
        ttk.Button(text='Delete', command=self.delete_product).grid(row=25,column=0, columnspan=2,  sticky=W + E)
        ttk.Button(text='Edit', command=self.edit_product).grid(row=26,column=0, columnspan=2,  sticky=W + E)
        PPP = Label(text='', fg='red')
        PPP.grid(row=27, column=0, columnspan=3, sticky=W + E)
        # Creating a Frame Container
        framennn = LabelFrame(self.wind, text='Run batches: ')
        framennn.grid(row=28, column=0, columnspan=10, pady=20)

        ttk.Button(framennn, text='RUN BATCHES', command=self.runbatches).grid(row=0, column=0, columnspan=10,sticky=W + E)
        Label(framennn, text='Number of repetitions:    ', anchor="e", justify=LEFT).grid(row=1, column=0)
        #text input
        self.repetitions = Entry(framennn)
        #place of the text input
        self.repetitions.grid(row=1, column=1)
        ttk.Button(framennn, text='RUN BATCHES REPEATEDLY', command=self.runbatchesrepeatedly).grid(row=1, column=5)
        PPP2 = Label(text='', fg='red')
        PPP2.grid(row=30, column=0, columnspan=3, sticky=W + E)
        # Filling the Rows
        self.get_products()

    # repeated rolling of the jobs saved
    def runbatchesrepeatedly(self):
        # check number of repeated times the jobs are executed
        if len(self.repetitions.get()) != 0 and self.repetitions.get().isnumeric():
            # number of times the jobs are repeated
            numerorepeticiones = self.repetitions.get()
            # check if the entry and the output of the job exist, if they exist, remove them
            if os.path.isfile('salidaparagraficasnueva0.json'):
                os.remove('salidaparagraficasnueva0.json')
            if os.path.isfile('pruebatrabajos.json'):
                os.remove('pruebatrabajos.json')
            #trabajos = []
            diametros1 = []
            diametros2 = []
            diametros3 = []
            diametros4 = []
            toneladas = []
            acumuladoarray = []
            valoracu = 0
            valorescostes = []
            imgarray = []
            repeticionestrabajos = int(numerorepeticiones)
            processName = 'Microsoft.Photos.exe'
            for proc in psutil.process_iter():
                if processName.lower() in proc.name().lower():
                    os.system('taskkill /IM Microsoft.Photos.exe /F')
            if (len(self.batches) > 0):
                for elementillo in range(repeticionestrabajos):
                    cadena = "{\"numerorepeticiones\":"+str(1)+",\"TrabajosLaminacion\":["
                    cadena2 = "\"restricciones\": ["
                    for element in self.batches:
                        cadena = cadena + "{\"toneladaslaminadas\": ["+str(element.tons)+"],\"calidadmaterial\": ["+str(element.quality)+"],"
                        cadena = cadena + "\"cajas\":["
                        cadena = cadena +"{\"caja\":16, \"geometria\":\""+element.cosascajas[0].split("#")[0]+"\",\"tallado\":"+str(element.cosascajas[0].split("#")[1])+"},"
                        cadena = cadena + "{\"caja\":17, \"geometria\":\"" + element.cosascajas[1].split("#")[
                            0] + "\",\"tallado\":" + str(element.cosascajas[1].split("#")[1]) + "},"
                        cadena = cadena + "{\"caja\":18, \"geometria\":\"" + element.cosascajas[2].split("#")[
                            0] + "\",\"tallado\":" + str(element.cosascajas[2].split("#")[1]) + "},"
                        cadena = cadena + "{\"caja\":19, \"geometria\":\"" + element.cosascajas[3].split("#")[
                            0] + "\",\"tallado\":" + str(element.cosascajas[3].split("#")[1]) + "}]},"


                        cadena2 = cadena2+ "[{\"caja2\":17,"+"\"caja1\":16,\"tipo\":\""+element.restrictions[0].type+"\", \"cantidad\":"+element.restrictions[0].quantity+", \"factor\":"+element.restrictions[0].factor+"},"
                        cadena2 = cadena2 + "{\"caja2\":18," + "\"caja1\":17,\"tipo\":\"" + element.restrictions[
                            1].type + "\", \"cantidad\":" + element.restrictions[1].quantity + ", \"factor\":" + element.restrictions[
                                      1].factor + "},"
                        cadena2 = cadena2 + "{\"caja2\":19," + "\"caja1\":18,\"tipo\":\"" + element.restrictions[
                            2].type + "\", \"cantidad\":" + element.restrictions[2].quantity + ", \"factor\":" + element.restrictions[
                                      2].factor + "}],"
                    cadena = cadena[:len(cadena) - 1]
                    cadena = cadena + "],"

                    cadena2 = cadena2[:len(cadena2) - 1]
                    cadena2 = cadena2 +"]}"
                    cadena = cadena + cadena2
                    # create the entry for the execution of the algorithm
                    fhand = open('pruebatrabajos.json', 'w')
                    fhand.write(cadena)
                    fhand.close()

                    while not os.path.isfile('pruebatrabajos.json'):
                        time.sleep(10)
                    # launch the script
                    os.system('python auctionsinterfaznuevaversion3.py')
                    # wait for the script to end
                    while not os.path.isfile('salidaparagraficasnueva0.json'):
                        time.sleep(10)
                    # load the output
                    with open('salidaparagraficasnueva0.json') as json_file:
                        data = json.load(json_file)
                    processName = 'Microsoft.Photos.exe'
                    #kill any open photos
                    for proc in psutil.process_iter():
                        if processName.lower() in proc.name().lower():
                            os.system('taskkill /IM Microsoft.Photos.exe /F')
                    p = data['Trabajos']
                    vueltastrabajos = p[len(p) - 1]['vueltas']
                    ultimavuelta = vueltastrabajos[len(vueltastrabajos)-1]
                    costes = []
                    if ultimavuelta['ganadorvuelta'] == -1:
                        costes = p[len(p) - 2]['diametrosmediosporcajas']
                    else:
                        costes = p[len(p) - 1]['diametrosmediosporcajas']
                    for elemento in costes:
                        diametros1.append(elemento[0])
                        diametros2.append(elemento[1])
                        diametros3.append(elemento[2])
                        diametros4.append(elemento[3])
                    costes = diametros1
                    a = range(0, len(costes))
                    x1 = [number for number in a]
                    fig, ax = plt.subplots()
                    l3 = ax.plot(x1, diametros1, label="")
                    l4 = ax.plot(x1, diametros2, label="")
                    l5 = ax.plot(x1, diametros3, label="")
                    l6 = ax.plot(x1, diametros4, label="")

                    ax.legend(["Diameter rolls 16", "Diameter rolls 17", "Diameter rolls 18", "Diameter rolls 19"])
                    plt.xticks(np.arange(min(x1), max(x1) + 1, 1.0))
                    ax.set(xlabel='Order', ylabel='Tons',
                           title=' ')
                    ax.ticklabel_format(useOffset=False, style='plain')
                    plt.grid(which='major', axis='y', linestyle='-', linewidth='0.5', color='gray')
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    fig.savefig("agente.png")
                    time.sleep(3)
                    #show the evolution of the average diameters
                    img = Image.open('agente.png')
                    img.show()
                    imgarray = []

                    tonsini = []
                    p = data['Trabajos']
                    ultimavuelta = p[len(p) - 1]['vueltas']
                    longitudbatches = len(self.batches)
                    if ultimavuelta[0]['ganadorvuelta'] == -1:
                        longitudbatches = len(p)-2
                    trabajitosencontradosolucion = self.batches[0:longitudbatches]
                    for elementot in trabajitosencontradosolucion:
                        tonsini.append(float(elementot.tons))
                    toneladas += tonsini

                    for elementot in trabajitosencontradosolucion:
                        valoracu += float(elementot.tons)
                        acumuladoarray.append(valoracu)
                    costes = toneladas


                    a = range(0, len(costes))
                    x1 = [number for number in a]
                    fig, ax = plt.subplots()
                    l3 = ax.plot(x1, costes, label="")
                    l4 = ax.plot(x1, acumuladoarray, label="")

                    ax.legend(["Tons", "Accumulated tons"])
                    plt.xticks(np.arange(min(x1), max(x1) + 1, 1.0))
                    ax.set(xlabel='Order', ylabel='Tons',
                           title=' ')
                    ax.ticklabel_format(useOffset=False, style='plain')
                    plt.grid(which='major', axis='y', linestyle='-', linewidth='0.5', color='gray')
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    fig.savefig("agente2.png")
                    time.sleep(3)
                    #show the evolution of the tons rolled
                    img2 = Image.open("agente2.png")
                    img2.show()

                    for elementot in p:
                        vueltaganadora = elementot['vueltas'][len(elementot['vueltas']) - 1]
                        if (float(vueltaganadora['costeganador']) > -1):
                            valorescostes.append(vueltaganadora['costeganador'])
                    ultimavuelta = p[len(p) - 1]['vueltas']
                    if ultimavuelta[0]['ganadorvuelta'] == -1:
                        valorescostes = costes[0:len(p) - 2]
                    a = range(0, len(costes))
                    x1 = [number for number in a]
                    fig, ax = plt.subplots()
                    l3 = ax.plot(x1, valorescostes, label="")
                    plt.xticks(np.arange(min(x1), max(x1) + 1, 1.0))
                    ax.set(xlabel='Order', ylabel='Cost of winner agent',
                           title=' ')
                    ax.ticklabel_format(useOffset=False, style='plain')
                    plt.grid(which='major', axis='y', linestyle='-', linewidth='0.5', color='gray')
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    fig.savefig("agentecostes.png")
                    time.sleep(3)
                    #show the evolution of the cost of the winner agent
                    img3 = Image.open("agentecostes.png")
                    img3.show()


                print("acabaron todos")
            else:
                #error there are no saved jobs
                self.message['text'] = 'No batches to run'
        else:
            #if the user indicates a non numeric number of repetitions it is informed that it must be numeric
            self.message['text'] = 'The number of times batches are executed must be numeric'

    #function to show the average diameters by stands
    def showdiameters(self):
        with open('salidaparagraficasnueva0.json') as json_file:
            data = json.load(json_file)
        p = data['Trabajos']
        ultimavuelta = p[len(p) - 1]['vueltas']
        costes = []
        if ultimavuelta[0]['ganadorvuelta'] == -1:
            costes = p[len(p)-2]['diametrosmediosporcajas']
        else:
            costes = p[len(p)-1]['diametrosmediosporcajas']
        diametros1=[]
        diametros2=[]
        diametros3=[]
        diametros4=[]
        for elemento in costes:
            diametros1.append(elemento[0])
            diametros2.append(elemento[1])
            diametros3.append(elemento[2])
            diametros4.append(elemento[3])
        costes = diametros1
        a = range(0, len(costes))
        x1 = [number for number in a]
        fig, ax = plt.subplots()
        l3 = ax.plot(x1, diametros1, label="")
        l4 = ax.plot(x1, diametros2, label="")
        l5 = ax.plot(x1, diametros3, label="")
        l6 = ax.plot(x1, diametros4, label="")

        ax.legend(["Diameter rolls 16", "Diameter rolls 17", "Diameter rolls 18", "Diameter rolls 19"])
        plt.xticks(np.arange(min(x1), max(x1) + 1, 1.0))
        ax.set(xlabel='Order', ylabel='Tons',
               title=' ')
        ax.ticklabel_format(useOffset=False, style='plain')
        plt.grid(which='major', axis='y', linestyle='-', linewidth='0.5', color='gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig("agente.png")
        time.sleep(3)
        img = Image.open('agente.png')
        img.show()




    #function to show the tons rolled
    def showtons(self):
        toneladas = []
        tonsini = []
        for element in self.batches:
            tonsini.append(float(element.tons))
        for element in range(int(self.repetitions.get())):
            toneladas += tonsini
        acumuladoarray = []
        valoracu = 0
        for element in toneladas:
            valoracu += element
            acumuladoarray.append(valoracu)
        with open('salidaparagraficasnueva0.json') as json_file:
            data = json.load(json_file)
        p = data['Trabajos']
        ultimavuelta = p[len(p) - 1]['vueltas']
        costes = []
        if ultimavuelta[0]['ganadorvuelta'] == -1:
            costes = toneladas[0:len(p)-2]
            acumuladoarray = acumuladoarray[0:len(p)-2]
        else:
            costes = toneladas
        a = range(0, len(costes))
        x1 = [number for number in a]
        fig, ax = plt.subplots()
        l3 = ax.plot(x1, costes, label="")
        l4 = ax.plot(x1, acumuladoarray, label="")

        ax.legend(["Tons", "Accumulated tons"])
        plt.xticks(np.arange(min(x1), max(x1) + 1, 1.0))
        ax.set(xlabel='Order', ylabel='Tons',
               title=' ')
        ax.ticklabel_format(useOffset=False, style='plain')
        plt.grid(which='major', axis='y', linestyle='-', linewidth='0.5', color='gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig("agente.png")
        time.sleep(3)
        img = Image.open('agente.png')
        img.show()

    #show the evolution of the cost
    def showcost(self):
        with open('salidaparagraficasnueva0.json') as json_file:
            data = json.load(json_file)
        p = data['Trabajos']
        costes = []
        for element in p:
            vueltaganadora= element['vueltas'][len(element['vueltas'])-1]
            costes.append(vueltaganadora['costeganador'])
        ultimavuelta = p[len(p) - 1]['vueltas']
        if ultimavuelta[0]['ganadorvuelta'] == -1:
            costes = costes[0:len(p)-2]
        a = range(0, len(costes))
        x1 = [number for number in a]
        fig, ax = plt.subplots()
        l3 = ax.plot(x1, costes, label="")
        plt.xticks(np.arange(min(x1), max(x1) + 1, 1.0))
        ax.set(xlabel='Order', ylabel='Cost of winner agent',
               title=' ')
        ax.ticklabel_format(useOffset=False, style='plain')
        plt.grid(which='major', axis='y', linestyle='-', linewidth='0.5', color='gray')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig("agente.png")
        time.sleep(3)
        img = Image.open('agente.png')
        img.show()


    #execute the jobs once
    def runbatches(self):
        #check if the output file exists if it exists remove it
        if os.path.isfile('salidaparagraficasnueva0.json'):
            os.remove('salidaparagraficasnueva0.json')
        if (len(self.batches)>0):
            cadena = "{\"TrabajosLaminacion\":["
            cadena2 = "\"restricciones\": ["
            for element in self.batches:
                cadena = cadena + "{\"toneladaslaminadas\": ["+str(element.tons)+"],\"calidadmaterial\": ["+str(element.quality)+"],"
                cadena = cadena + "\"cajas\":["
                cadena = cadena +"{\"caja\":16, \"geometria\":\""+element.cosascajas[0].split("#")[0]+"\",\"tallado\":"+str(element.cosascajas[0].split("#")[1])+"},"
                cadena = cadena + "{\"caja\":17, \"geometria\":\"" + element.cosascajas[1].split("#")[
                    0] + "\",\"tallado\":" + str(element.cosascajas[1].split("#")[1]) + "},"
                cadena = cadena + "{\"caja\":18, \"geometria\":\"" + element.cosascajas[2].split("#")[
                    0] + "\",\"tallado\":" + str(element.cosascajas[2].split("#")[1]) + "},"
                cadena = cadena + "{\"caja\":19, \"geometria\":\"" + element.cosascajas[3].split("#")[
                    0] + "\",\"tallado\":" + str(element.cosascajas[3].split("#")[1]) + "}]},"


                cadena2 = cadena2+ "[{\"caja2\":17,"+"\"caja1\":16,\"tipo\":\""+element.restrictions[0].type+"\", \"cantidad\":"+element.restrictions[0].quantity+", \"factor\":"+element.restrictions[0].factor+"},"
                cadena2 = cadena2 + "{\"caja2\":18," + "\"caja1\":17,\"tipo\":\"" + element.restrictions[
                    1].type + "\", \"cantidad\":" + element.restrictions[1].quantity + ", \"factor\":" + element.restrictions[
                              1].factor + "},"
                cadena2 = cadena2 + "{\"caja2\":19," + "\"caja1\":18,\"tipo\":\"" + element.restrictions[
                    2].type + "\", \"cantidad\":" + element.restrictions[2].quantity + ", \"factor\":" + element.restrictions[
                              2].factor + "}],"
            cadena = cadena[:len(cadena) - 1]
            cadena = cadena + "],"

            cadena2 = cadena2[:len(cadena2) - 1]
            cadena2 = cadena2 +"]}"
            cadena = cadena + cadena2
            #create the entry file
            fhand = open('pruebatrabajos.json', 'w')
            fhand.write(cadena)
            fhand.close()
            while not os.path.isfile('pruebatrabajos.json'):
                time.sleep(10)
            #run the algorithm
            os.system('python auctionsinterfaznuevaversion.py')
            #wait for the output
            while not os.path.isfile('salidaparagraficasnueva0.json'):
                time.sleep(10)
            with open('salidaparagraficasnueva0.json') as json_file:
                data = json.load(json_file)
            p = data['Trabajos']

            codigostotales = []
            for p2 in p:
                vueltas = p2['vueltas']
                ganador = vueltas[len(vueltas) - 1]['ganadorvuelta']
                valoresvuelta = vueltas[len(vueltas) - 1]['valores']
                datosrodillos = valoresvuelta[int(ganador)]['datosrodillos']
                datosrodillos = datosrodillos[len(datosrodillos) - 1]
                codigos = []
                for element in datosrodillos:
                    datos = element.split()
                    codigos.append(datos[1])
                codigostotales.append(codigos)
            print(str(codigostotales))
            #show results to the user
            self.showresults(codigostotales)
        else:
            #if there are no jobs to run, then indicate it to the user
            self.message['text'] = 'No batches to run'

    #edit a job created window
    def edit_product(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'Please, select Record'
            return
        valores = self.tree.item(self.tree.selection())['values']
        tons2 = valores[0]
        quality2 = valores[1]
        restriction16 = valores[2]
        restriction17 = valores[3]
        restriction18 = valores[4]
        cosas16 = valores[5].split("#")
        cosas17 = valores[6].split("#")
        cosas18 = valores[7].split("#")
        cosas19 = valores[8].split("#")
        geometria16 = cosas16[0]
        geometria17 = cosas17[0]
        geometria18 = cosas18[0]
        geometria19 = cosas19[0]
        shape16 = cosas16[1]
        shape17 = cosas17[1]
        shape18 = cosas18[1]
        shape19 = cosas19[1]
        resedit = []
        datos = restriction16.split()
        res = Restriction(datos[0],datos[1],datos[2])
        resedit.append(res)
        datos = restriction17.split()
        res = Restriction(datos[0], datos[1], datos[2])
        resedit.append(res)
        datos = restriction18.split()
        res = Restriction(datos[0], datos[1], datos[2])
        resedit.append(res)
        #aqui falta pasar los datos a la pantalla y editar el registro
        self.edit_wind = Toplevel()
        self.edit_wind.resizable(False, False)
        self.edit_wind.title('Edit batch')
        # Creating a Frame Container
        framen = LabelFrame(self.edit_wind, text='Edit batch: ')
        framen.grid(row=0, column=0, columnspan=6, pady=20)
        # Tons input
        Label(framen, text='Tons:    ', anchor="e", justify=LEFT).grid(row=1, column=0)
        name = StringVar(framen, value=str(tons2))
        tons = Entry(framen, textvariable=name)
        tons.focus()
        tons.grid(row=1, column=1)

        # Quality input
        Label(framen, text=' Quality: ').grid(row=1, column=2)
        combo = ttk.Combobox(framen, state="readonly")
        combo["values"] = ["1", "2", "3", "4", "5"]
        combo.set(str(quality2))
        combo.grid(row=1, column=3)
        # To know the selected value
        quality = self.combo.get()

        # geometry
        Label(framen, text='                  Geometries -> 16: ').grid(row=2, column=0)
        geometry = ttk.Combobox(framen, state="readonly")
        geometry["values"] = ["Rodillos  de 8 x 72"]
        geometry.set("Rodillos  de 8 x 72")
        geometry.grid(row=2, column=1)

        Label(framen, text='17: ').grid(row=2, column=2)
        geometry2 = ttk.Combobox(framen, state="readonly")
        geometry2["values"] = ["Rodillos  de 8 x 72"]
        geometry2.set("Rodillos  de 8 x 72")
        geometry2.grid(row=2, column=3)

        Label(framen, text='18: ').grid(row=2, column=4)
        geometry3 = ttk.Combobox(framen, state="readonly")
        geometry3["values"] = ["Rodillos  de 8 x 72"]
        geometry3.set("Rodillos  de 8 x 72")
        geometry3.grid(row=2, column=5)

        Label(framen, text='19: ').grid(row=2, column=6)
        geometry4 = ttk.Combobox(framen, state="readonly")
        geometry4["values"] = ["Rodillos  de 6 x 62"]
        geometry4.set("Rodillos  de 6 x 62")
        geometry4.grid(row=2, column=7)

        # shape
        Label(framen, text='                  Shapes ->         16: ').grid(row=3, column=0)
        shape = ttk.Combobox(framen, state="readonly")
        shape["values"] = ["419"]
        shape.set("419")
        shape.grid(row=3, column=1)

        Label(framen, text='17: ').grid(row=3, column=2)
        shape2 = ttk.Combobox(framen, state="readonly")
        shape2["values"] = ["420"]
        shape2.set("420")
        shape2.grid(row=3, column=3)

        Label(framen, text='18: ').grid(row=3, column=4)
        shape3 = ttk.Combobox(framen, state="readonly")
        shape3["values"] = ["357"]
        shape3.set("357")
        shape3.grid(row=3, column=5)

        Label(framen, text='19: ').grid(row=3, column=6)
        shape4 = ttk.Combobox(framen, state="readonly")
        shape4["values"] = ["394"]
        shape4.set("394")
        shape4.grid(row=3, column=7)



        # Constraints
        Label(framen, text='         Restrictions : ').grid(row=4, column=0)
        #####################16-17
        Label(framen, text='16-17 : ').grid(row=5, column=0)
        Label(framen, text='Type : ').grid(row=5, column=1)
        combo2 = ttk.Combobox(framen, state="readonly")
        combo2["values"] = ["+-", "="]
        combo2.set(str(resedit[0].type))
        combo2.grid(row=5, column=2)

        Label(framen, text='Quantity: ').grid(row=5, column=3)
        name2 = StringVar(framen, value=str(resedit[0].quantity))
        quantity2 = Entry(framen, textvariable=name2)
        quantity2.grid(row=5, column=4)

        Label(framen, text='Factor: ').grid(row=5, column=5)
        name3= StringVar(framen, value=str(resedit[0].factor))
        factor2 = Entry(framen, textvariable=name3)
        factor2.grid(row=5, column=6)

        #####################17-18
        Label(framen, text='17-18 : ').grid(row=6, column=0)
        Label(framen, text='Type : ').grid(row=6, column=1)
        combo3 = ttk.Combobox(framen, state="readonly")
        combo3["values"] = ["+-", "="]
        combo3.set(str(resedit[1].type))
        combo3.grid(row=6, column=2)

        Label(framen, text='Quantity: ').grid(row=6, column=3)
        name4 = StringVar(framen, value=str(resedit[1].quantity))
        quantity3 = Entry(framen, textvariable=name4)
        quantity3.grid(row=6, column=4)

        Label(framen, text='Factor: ').grid(row=6, column=5)
        name5 = StringVar(framen, value=str(resedit[1].factor))
        factor3 = Entry(framen, textvariable=name5)
        factor3.grid(row=6, column=6)

        #####################18-19
        Label(framen, text='18-19 : ').grid(row=7, column=0)
        Label(framen, text='Type : ').grid(row=7, column=1)
        combo4 = ttk.Combobox(framen, state="readonly")
        combo4["values"] = ["+-", "="]
        combo4.set(str(resedit[2].type))
        combo4.grid(row=7, column=2)
        # Para saber el valor seleccionado
        # value = self.combo2.get()

        Label(framen, text='Quantity: ').grid(row=7, column=3)
        quantity4 = Entry(framen)
        name6 = StringVar(framen, value=str(resedit[2].quantity))
        quantity4 = Entry(framen, textvariable=name6)
        quantity4.grid(row=7, column=4)

        Label(framen, text='Factor: ').grid(row=7, column=5)
        name7 = StringVar(framen, value=str(resedit[2].factor))
        factor4 = Entry(framen, textvariable=name7)
        factor4.grid(row=7, column=6)
        # Output Messages
        self.message2 = Label(self.edit_wind, text='', fg='red')
        self.message2.grid(row=9, column=0, columnspan=7, sticky=W + E)
        # Button Edit Batch
        Button(framen, text='Edit Batch', command = lambda: self.edit_records(tons2,quality2,resedit,tons.get(),combo.get(),combo2.get(),combo3.get(),combo4.get(),quantity2.get(),quantity3.get(),quantity4.get(),factor2.get(),factor3.get(),factor4.get(),self.message2,geometry.get(),geometry2.get(),geometry3.get(),geometry4.get(),shape.get(),shape2.get(),shape3.get(),shape4.get())).grid(row=8, columnspan=8, sticky=W + E)

    #increase the job and show the information of the next one
    def next(self,codigostotales):
        if self.contador < len(self.batches) - 1:
            self.contador = self.contador+1
            # cleaning Table
            records = self.trees.get_children()
            for element in records:
                self.trees.delete(element)
            row = self.batches[self.contador]

            self.trees.insert('', 'end', text="1", values=(str(row.tons), str(row.quality),
                                                           str(row.restrictions[0].type) + " " + str(
                                                               row.restrictions[0].quantity) + " " + str(
                                                               row.restrictions[0].factor),
                                                           str(row.restrictions[1].type) + " " + str(
                                                               row.restrictions[1].quantity) + " " + str(
                                                               row.restrictions[1].factor),
                                                           str(row.restrictions[2].type) + " " + str(
                                                               row.restrictions[2].quantity) + " " + str(
                                                               row.restrictions[2].factor), str(row.cosascajas[0]),
                                                           str(row.cosascajas[1]), str(row.cosascajas[2]),
                                                           str(row.cosascajas[3]), str(codigostotales[self.contador])))

    #decrease the job and show the information of the previous one
    def previous(self,codigostotales):
        if self.contador > 0:
            self.contador = self.contador - 1
            # cleaning Table
            records = self.trees.get_children()
            for element in records:
                self.trees.delete(element)
            row = self.batches[self.contador]

            self.trees.insert('', 'end', text="1", values=(str(row.tons), str(row.quality),
                                                           str(row.restrictions[0].type) + " " + str(
                                                               row.restrictions[0].quantity) + " " + str(
                                                               row.restrictions[0].factor),
                                                           str(row.restrictions[1].type) + " " + str(
                                                               row.restrictions[1].quantity) + " " + str(
                                                               row.restrictions[1].factor),
                                                           str(row.restrictions[2].type) + " " + str(
                                                               row.restrictions[2].quantity) + " " + str(
                                                               row.restrictions[2].factor), str(row.cosascajas[0]),
                                                           str(row.cosascajas[1]), str(row.cosascajas[2]),
                                                           str(row.cosascajas[3]), str(codigostotales[self.contador])))

    #show results of the execution of the algorithm
    def showresults(self,codigostotales):
        self.results_wind = Toplevel()
        self.results_wind.resizable(False, False)
        self.results_wind.title('Results')
        self.contador = 0
        # Creating a Frame Container
        framen = LabelFrame(self.results_wind, text='Select batch:')
        framen.grid(row=0, column=0, columnspan=10, pady=20)
        # Button previous
        ttk.Button(framen, text='<', command= lambda: self.previous(codigostotales)).grid(row=0, column=4)
        # Button next
        ttk.Button(framen, text='>', command= lambda: self.next(codigostotales)).grid(row=0, column=6)
        # Table with the data from the results of the execution for the job considered
        columns = ('#1', '#2', '#3', '#4', '#5', '#6', '#7', '#8', '#9', '#10')

        self.trees = ttk.Treeview(self.results_wind, columns=columns, show='headings',height=1)
        self.trees.column('#1', width=50, stretch=NO)
        self.trees.column('#2', width=50, stretch=NO)
        self.trees.column('#3', width=100, stretch=NO)
        self.trees.column('#4', width=100, stretch=NO)
        self.trees.column('#5', width=100, stretch=NO)
        self.trees.grid(row=2, column=0, sticky="nsew")

        self.trees.heading('#1', text='Tons', anchor=CENTER)
        self.trees.heading('#2', text='Quality', anchor=CENTER)
        self.trees.heading('#3', text='Restriction 16-17', anchor=CENTER)
        self.trees.heading('#4', text='Restriction 17-18', anchor=CENTER)
        self.trees.heading('#5', text='Restriction 18-19', anchor=CENTER)
        self.trees.heading('#6', text='Characteristics 16', anchor=CENTER)
        self.trees.heading('#7', text='Characteristics 17', anchor=CENTER)
        self.trees.heading('#8', text='Characteristics 18', anchor=CENTER)
        self.trees.heading('#9', text='Characteristics 19', anchor=CENTER)
        self.trees.heading('#10', text='Codes', anchor=CENTER)
        # cleaning Table
        records = self.trees.get_children()
        for element in records:
            self.trees.delete(element)
        row = self.batches[0]
        #initialize the table with the data of the first job
        self.trees.insert('', 'end', text="1", values=(str(row.tons), str(row.quality),
                                                      str(row.restrictions[0].type) + " " + str(
                                                          row.restrictions[0].quantity) + " " + str(
                                                          row.restrictions[0].factor),
                                                      str(row.restrictions[1].type) + " " + str(
                                                          row.restrictions[1].quantity) + " " + str(
                                                          row.restrictions[1].factor),
                                                      str(row.restrictions[2].type) + " " + str(
                                                          row.restrictions[2].quantity) + " " + str(
                                                          row.restrictions[2].factor), str(row.cosascajas[0]),
                                                      str(row.cosascajas[1]), str(row.cosascajas[2]),
                                                      str(row.cosascajas[3]),str(codigostotales[0])))
        #results of the execution of the algoritm
        with open('salidaparagraficasnueva0.json') as json_file:
            data = json.load(json_file)
        p = data['Trabajos']
        p2 = p[0]
        self.vueltas = len(p2['vueltas'])
        self.costesvueltas = []
        for elem in p2['vueltas']:
            self.costesvueltas.append(elem['costeganador'])
        lasvueltas = p2['vueltas']
        self.costesagentestotales = []
        for elemento in lasvueltas:
            costesagentes = []
            valores = elemento['valores']
            self.numagentes = len(valores)
            for elem in valores:
                costesagentes.append(elem['costes'])
            self.costesagentestotales.append(costesagentes)
        #Buttons to display information about the result of the execution of the algorithm
        ttk.Button(self.results_wind, text='Show winner evolution', command=self.showimage).grid(row=3, column=0, sticky = "nsew")
        ttk.Button(self.results_wind, text='Cost evolution among rounds', command=self.showimage2).grid(row=4, column=0,sticky="nsew")
        ttk.Button(self.results_wind, text='Show agents evolution', command=self.showimage3).grid(row=5, column=0,sticky="nsew")

    #show agents evolution
    def showimage3(self):
        self.agents_wind = Toplevel()
        self.agents_wind.resizable(False, False)
        self.agents_wind.title('Agents evolution')
        self.vueltaactual = 0
        # Output Messages
        self.messageagents = Label(self.agents_wind, text='Round 1 of '+str(self.vueltas))
        self.messageagents.grid(row=0, column=0, columnspan=10, sticky=W + E)
        self.messageagents2 = Label(self.agents_wind, text="Cost: " + str(self.costesvueltas[self.vueltaactual]))
        self.messageagents2.grid(row=1, column=0, columnspan=10, sticky=W + E)
        # Creating a Frame Container
        framen = LabelFrame(self.agents_wind, text='Select round:')
        framen.grid(row=2, column=0, columnspan=10, pady=20)
        # Button previous round
        ttk.Button(framen, text='<', command = self.previousround).grid(row=0, column=4)
        # Button next round
        ttk.Button(framen, text='>', command = self.nextround).grid(row=0, column=6)

        Label(self.agents_wind, text=' Agent: ').grid(row=3, column=0)
        self.comboagentes = ttk.Combobox(self.agents_wind, state="readonly")
        listagentes = list(range(self.numagentes))
        listagentes = [str(x) for x in listagentes]
        self.comboagentes["values"] = listagentes
        self.comboagentes.set("0")
        self.comboagentes.grid(row=3, column=1)
        self.numeroagente = self.comboagentes.get()
        #show the selected agent evolution
        ttk.Button(self.agents_wind, text='Show agent evolution', command=self.showimage4).grid(row=4, column=0, columnspan=2, sticky=W + E)

    #move to the previous round of the algorithm
    def previousround(self):
        if self.vueltaactual > 0:
            self.vueltaactual = self.vueltaactual - 1
        self.messageagents['text']='Round ' + str(self.vueltaactual + 1) + ' of ' + str(self.vueltas)
        self.messageagents2['text'] = 'Cost: ' + str(self.costesvueltas[self.vueltaactual])

    #move to the next round of the algorithm
    def nextround(self):
        if self.vueltaactual < self.vueltas - 1:
            self.vueltaactual = self.vueltaactual + 1
        self.messageagents['text'] = 'Round ' + str(self.vueltaactual + 1) + ' of ' + str(self.vueltas)
        self.messageagents2['text'] = 'Cost: ' + str(self.costesvueltas[self.vueltaactual])


    #show the selected agent evolution within the round
    def showimage4(self):
        with open('salidaparagraficasnueva0.json') as json_file:
            data = json.load(json_file)
        p = data['Trabajos']
        p2 = p[int(self.contador)]
        vueltas = p2['vueltas']
        self.numeroagente = self.comboagentes.get()
        vuelta = vueltas[self.vueltaactual]
        valores = vuelta['valores']
        costes= valores[int(self.numeroagente)]
        costes = costes['costes']
        a = range(0, len(costes))
        x1 = [number for number in a]
        fig, ax = plt.subplots()
        l3 = ax.plot(x1, costes, label="")
        plt.xticks(np.arange(min(x1), max(x1) + 1, 1.0))
        ax.set(xlabel='Number of winned auction', ylabel='Cost of agent',
               title=' ')
        ax.ticklabel_format(useOffset=False, style='plain')
        plt.grid(which='major', axis='y', linestyle='-', linewidth='0.5', color='gray')
        # plt.grid(b='None')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig("agente.png")
        time.sleep(3)
        img = Image.open('agente.png')
        img.show()





    #show cost evolution among rounds
    def showimage2(self):
        with open('salidaparagraficasnueva0.json') as json_file:
            data = json.load(json_file)
        p = data['Trabajos']
        p2 = p[int(self.contador)]
        vueltas = p2['vueltas']
        costes = []
        for elem in vueltas:
            costes.append(elem['costeganador'])
        a = range(0, len(costes))
        x1 = [number for number in a]
        fig, ax = plt.subplots()
        l3 = ax.plot(x1, costes, label="")
        plt.xticks(np.arange(min(x1), max(x1) + 1, 1.0))
        ax.set(xlabel='Number of round', ylabel='Cost of winner agent',
               title=' ')
        ax.ticklabel_format(style='plain')
        plt.grid(which='major', axis='y', linestyle='-', linewidth='0.5', color='gray')
        # plt.grid(b='None')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        fig.savefig("ganadorprimera1.png")
        time.sleep(3)
        img = Image.open('ganadorprimera1.png')
        img.show()
    #show winner evolution
    def showimage(self):
        with open('salidaparagraficasnueva0.json') as json_file:
            data = json.load(json_file)
        p = data['Trabajos']
        p2 = p[int(self.contador)]
        vueltas = p2['vueltas']
        ganador = vueltas[len(vueltas) - 1]['ganadorvuelta']
        valoresvuelta = vueltas[len(vueltas) - 1]['valores']
        costes = valoresvuelta[int(ganador)]['costes']
        a = range(0, len(costes))
        x1 = [number for number in a]
        fig, ax = plt.subplots()
        l3 = ax.plot(x1, costes, label="")
        plt.xticks(np.arange(min(x1), max(x1) + 1, 1.0))
        ax.set(xlabel='Number of winned auctions', ylabel='Cost of winner agent',
               title=' ')
        ax.ticklabel_format(style='plain')
        plt.grid(which='major', axis='y', linestyle='-', linewidth='0.5', color='gray')
        # plt.grid(b='None')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        fig.savefig("ganadorprimera1.png")
        time.sleep(3)
        img = Image.open('ganadorprimera1.png')
        img.show()



    #edit a batch and check values
    def edit_records(self,tons2,quality2,resedit,tons,combo,combo2,combo3,combo4,quantity2,quantity3,quantity4,factor2,factor3,factor4,mensaje,geometry16,geometry17,geometry18,geometry19,shape16,shape17,shape18,shape19):
        self.message2 ['text'] = ''
        cuenta = 0
        for element in self.batches:
            es = True
            if str(element.tons) == str(tons2) and str(element.quality)==str(quality2):
                contador = 0
                for element2 in element.restrictions:
                    if not(str(resedit[contador].type)==str(element2.type) and str(resedit[contador].quantity)==str(element2.quantity) and str(resedit[contador].factor)==str(element2.factor)):
                        es = False
                    contador = contador + 1
            else:
                es = False
            if es:
                if len(tons) != 0 and len(quantity2) != 0 and len(quantity3) != 0 and len(
            quantity4) != 0 and len(factor2) != 0 and len(factor3) != 0 and len(
            factor4) != 0 and tons.isnumeric() and quantity2.isnumeric() and quantity3.isnumeric()\
            and quantity4.isnumeric() and factor2.isnumeric() and factor3.isnumeric() \
            and factor4.isnumeric():

                    restrictions = []
                    quality = combo
                    restriction = Restriction(combo2, quantity2, factor2)
                    restrictions.append(restriction)
                    restriction = Restriction(combo3, quantity3, factor3)
                    restrictions.append(restriction)
                    restriction = Restriction(combo4, quantity4, factor4)
                    restrictions.append(restriction)
                    cosascajas = [str(geometry16)+"#"+str(shape16),str(geometry17)+"#"+str(shape17),str(geometry18)+"#"+str(shape18),str(geometry19)+"#"+str(shape19)]
                    batch = Batch(tons, quality, restrictions, cosascajas)
                    self.batches[cuenta] = batch
                    self.edit_wind.destroy()
                    self.message['text'] = 'Batch edited'
                    self.get_products()
                else:
                    mensaje['text'] = 'All values are required and must be numeric'
            cuenta = cuenta + 1


    #delete a job
    def delete_product(self):
        self.message['text'] = ''
        b=''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'Please select a Record'
            return
        self.message['text'] = ''
        valores = self.tree.item(self.tree.selection())['values']
        tons = valores[0]
        quality = valores[1]
        restriction16 = valores[2]
        restriction17 = valores[3]
        restriction18 = valores[4]
        cosascaja16 = valores[5]
        cosascaja17 = valores[6]
        cosascaja18 = valores[7]
        cosascaja19 = valores[8]
        resedit = []
        datos = restriction16.split()
        res = Restriction(datos[0], datos[1], datos[2])
        resedit.append(res)
        datos = restriction17.split()
        res = Restriction(datos[0], datos[1], datos[2])
        resedit.append(res)
        datos = restriction18.split()
        res = Restriction(datos[0], datos[1], datos[2])
        resedit.append(res)
        borrado = False
        for element in self.batches:
            es = True
            if str(element.tons) == str(tons) and str(element.quality) == str(quality) and str(cosascaja16) == \
                    element.cosascajas[0] and str(cosascaja17) == element.cosascajas[1] and str(cosascaja18) == element.cosascajas[2] and str(cosascaja19) == element.cosascajas[3]:
                contador = 0
                for element2 in element.restrictions:
                    if not(str(resedit[contador].type) == str(element2.type) and str(resedit[contador].quantity)==str(element2.quantity) and str(resedit[contador].factor)==str(element2.factor)):
                        es = False
                    contador = contador + 1
            else:
                es = False
            if es and not borrado:
                self.batches.remove(element)
                borrado = True
        self.get_products()


    #add a job
    def add_product(self):
        self.message['text'] = ''
        if self.validation():
            self.restrictions = []
            self.quality = self.combo.get()
            self.geometria16=self.geometry.get()
            self.geometria17 = self.geometry2.get()
            self.geometria18 = self.geometry3.get()
            self.geometria19 = self.geometry4.get()
            self.shape16 = self.shape.get()
            self.shape17 = self.shape2.get()
            self.shape18 = self.shape3.get()
            self.shape19 = self.shape4.get()
            cosascajas = [str(self.geometria16)+"#"+str(self.shape16),str(self.geometria17)+"#"+str(self.shape17),str(self.geometria18)+"#"+str(self.shape18),str(self.geometria19)+"#"+str(self.shape19)]
            restriction = Restriction(self.combo2.get(),self.quantity2.get(),self.factor2.get())
            self.restrictions.append(restriction)
            restriction = Restriction(self.combo3.get(), self.quantity3.get(), self.factor3.get())
            self.restrictions.append(restriction)
            restriction = Restriction(self.combo4.get(), self.quantity4.get(), self.factor4.get())
            self.restrictions.append(restriction)
            batch = Batch(self.tons.get(),self.quality,self.restrictions,cosascajas)
            self.batches.append(batch)
            self.tons.delete(0, END)
            self.combo.set("1")
            self.combo2.set("+-")
            self.combo3.set("+-")
            self.combo4.set("+-")
            self.quantity2.delete(0, END)
            self.factor2.delete(0, END)
            self.quantity3.delete(0, END)
            self.factor3.delete(0, END)
            self.quantity4.delete(0, END)
            self.factor4.delete(0, END)
        else:
            self.message['text'] = 'All values are required and must be numeric'
        self.get_products()

    #get the saved jobs
    def get_products(self):
        # cleaning Table
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
        db_rows = self.batches
        # filling data
        for row in db_rows:
            self.tree.insert('', 'end', text="1", values=(str(row.tons), str(row.quality), str(row.restrictions[0].type)+" "+str(row.restrictions[0].quantity)+" "+str(row.restrictions[0].factor),str(row.restrictions[1].type)+" "+str(row.restrictions[1].quantity)+" "+str(row.restrictions[1].factor),
                                                          str(row.restrictions[2].type)+" "+str(row.restrictions[2].quantity)+" "+str(row.restrictions[2].factor),str(row.cosascajas[0]),str(row.cosascajas[1]),str(row.cosascajas[2]),str(row.cosascajas[3])))

    #User Input Validation
    def validation(self):
        return len(self.tons.get()) != 0 and len(self.quantity2.get()) != 0 and len(self.quantity3.get()) != 0 and len(
            self.quantity4.get()) != 0 and len(self.factor2.get()) != 0 and len(self.factor3.get()) != 0 and len(
            self.factor4.get()) != 0 and self.tons.get().isnumeric() and self.quantity2.get().isnumeric() and self.quantity3.get().isnumeric()\
            and self.quantity4.get().isnumeric() and self.factor2.get().isnumeric() and self.factor3.get().isnumeric() \
            and self.factor4.get().isnumeric()

#main
if __name__ == '__main__':
    window = Tk()
    window.resizable(False, False)
    application = Product(window)
    window.mainloop()










