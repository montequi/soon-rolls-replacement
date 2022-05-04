import json
from json import JSONEncoder
import os
import decimal
import numpy as np
import random
import copy
import subprocess
import pickle
import pandas as pd
import math
import statistics as stats
import time
import sys

#data to store about the roll
datoscilindro = ""
diametrosiniciales = []
cantidadcompatibles = []
reduccionespasadas = []




#Converts a Roll To JSON
class Cilindros2Encoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Roll):
            return object.__dict__
        else:
            # call base class implementation which takes care of
            # raising exceptions for unsupported types
            return json.JSONEncoder.default(self, object)



# Converts Position to JSON
class PosicionesosEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Position):
            return object.__dict__
        else:
            # call base class implementation which takes care of
            # raising exceptions for unsupported types
            return json.JSONEncoder.default(self, object)

# Roll read from the configuration file
class Roll2:
    def __init__(self, cod_interno, diam_inicial, diam_final, diam_actual, cod_estado, geometria, calidad,densidad,numposiciones,tabla,coste):
        self.cod_interno = cod_interno
        self.diam_inicial = diam_inicial
        self.diam_final = diam_final
        self.diam_actual = diam_actual
        self.cod_estado = cod_estado
        self.geometria = geometria
        self.calidad = calidad
        self.densidad = densidad
        self.numposiciones = numposiciones
        self.tabla = tabla
        self.coste = coste

# costs of the roll given its quality
class Costemmvol:
    def __init__(self, COD_CALIDAD, costemm3):
        self.COD_CALIDAD = COD_CALIDAD
        self.costemm3 = costemm3


#diameter reduction calculated using the model
class CilindrosReducciones:
    def __init__(self, codigo_interno, cod_posicion, reduccion):
        self.codigo_interno = codigo_interno
        self.cod_posicion = cod_posicion
        self.reduccion = reduccion


#compatible rolls with a given stand
class CajaCompatibles:
    def __init__(self, caja, cilindros):
        self.caja = caja
        self.cilindros = cilindros


# compatible rolls and positions given a stand
class CilindrosCompatibles:
    def __init__(self, caja, compatibles, positions):
        self.caja = caja
        self.compatibles = compatibles
        self.positions = positions


#rolls read from the configuration file
class Roll:
    def __init__(self, cod_interno, diam_inicial, diam_final, diam_actual, cod_estado, geometria, numposiciones,
                 calidad, densidad, tabla, coste):
        self.cod_interno = cod_interno
        self.diam_inicial = diam_inicial
        self.diam_final = diam_final
        self.diam_actual = diam_actual
        self.cod_estado = cod_estado
        self.geometria = geometria
        self.numposiciones = numposiciones
        self.calidad = calidad
        self.densidad = densidad
        self.tabla = tabla
        self.coste = coste


# Positions read from the configuration file
class Position:
    def __init__(self, cod_interno, cod_posicion, num_plano_tallado, cod_estado_posicion, toneladas, diam_rectif,
                 numposiciones):
        self.cod_interno = cod_interno
        self.cod_posicion = cod_posicion
        self.num_plano_tallado = num_plano_tallado
        self.cod_estado_posicion = cod_estado_posicion
        self.toneladas = toneladas
        self.diam_rectif = diam_rectif
        self.numposiciones = numposiciones


# geometries read from the configuration file
class Geometrias:
    def __init__(self, cod_caja, geometria, cod_geometria):
        self.cod_caja = cod_caja
        self.geometria = geometria
        self.cod_geometria = cod_geometria


# quality of the rolls read from the configuration file
class Calidades:
    def __init__(self, cod_calidad, calidad):
        self.cod_calidad = cod_calidad
        self.calidad = calidad



# shapes read from the configuration file
class Carvings:
    def __init__(self, num_plano_tallado, descripcion, cod_caja):
        self.num_plano_tallado = num_plano_tallado
        self.descripcion = descripcion
        self.cod_caja = cod_caja


#measures of the rolls
class Tablas:
    def __init__(self, num_plano_bruto, tabla, nombre):
        self.num_plano_bruto = num_plano_bruto
        self.tabla = tabla
        self.nombre = nombre


# jobs read from the configuration file, the number of rolled tons, the quality of the material, the stands involved and the duration of the job is indicated
class Trabajos:
    def __init__(self, toneladaslaminadas, calidadmaterial, cajas):
        self.toneladaslaminadas = toneladaslaminadas
        self.calidadmaterial = calidadmaterial
        self.cajas = cajas


#Stands involved in a job, indicating its number, geometry and carving
class CajasTrabajos:
    def __init__(self, numcaja, geometria, tallado):
        self.numcaja = numcaja
        self.geometria = geometria
        self.tallado = tallado


#constraints of a job, indicating the two stands involved, the quantity, the factor and the type
class Restricciones:
    def __init__(self, caja1, caja2, cantidad, factor, tipo):
        self.caja1 = caja1
        self.caja2 = caja2
        self.cantidad = cantidad
        self.factor = factor
        self.tipo = tipo


# function that calculates the reduction of a roll
def calculoreduccioncondurezacalidad(rodillo, posicionescil, posicionusada, toneladas, geometrias, calidades, model,
                                     trabajo):
    #maximum number of tons rolled by a position
    attrs = max([o.toneladas for o in posicionescil])
    #the tons that the used position is going to roll are added and it is considered if given this tons the max changes
    if posicionusada.toneladas + toneladas > attrs:
        attrs = posicionusada.toneladas + toneladas
    # sum of the tons rolled by the positions
    acumulado = sum([o.toneladas for o in posicionescil])
    acumulado = acumulado + toneladas
    # code of the geometry of the roll
    geomet = list(filter(lambda p: p.geometria == rodillo.geometria, geometrias))
    # code of the quality of the roll
    codcalidad = list(filter(lambda p: p.calidad == rodillo.calidad, calidades))
    #different arguments used to calculate the reduction
    args = [str(acumulado), codcalidad[0].cod_calidad, str(attrs), geomet[0].cod_geometria,
            posicionusada.num_plano_tallado, rodillo.diam_actual, str(acumulado / rodillo.numposiciones),
            max(trabajo.calidadmaterial)]
    #the data of the roll is stored
    global datoscilindro
    datoscilindro = "codigo: " + str(rodillo.cod_interno) + " AddToneladas: " + str(args[0]) + " COD_CALIDAD: " + str(
        args[1]) + " MaxToneladas: " + str(
        args[2]) + " NUM_PLANO_BRUTO: " + str(args[3]) + " NUM_PLANO_TALLADO: " + str(
        args[4]) + " diametro: " + str(args[5]) + " mediatoneladas: " + str(args[6]) + " dureza: " + str(args[7])
    #the series are created in order to create the frame and then with the Dataframe predict using the model trained
    serie = pd.Series([args[0]])
    serie1 = pd.Series([args[1]])
    serie2 = pd.Series([args[2]])
    serie3 = pd.Series([args[3]])
    serie4 = pd.Series([args[4]])
    serie5 = pd.Series([args[5]])
    serie6 = pd.Series([args[6]])
    serie7 = pd.Series([args[7]])
    # frame
    frame = {'AddToneladas': serie, 'COD_CALIDAD': serie1, 'MaxToneladas': serie2, 'NUM_PLANO_BRUTO': serie3,
             'NUM_PLANO_TALLADO': serie4, 'diametro': serie5, 'mediatoneladas': serie6, 'dureza': serie7}
    # dataframe
    dframe = pd.DataFrame(frame)
    # predicted reduction
    predictions = model.predict(dframe)
    #it is converted to diameter
    equis = ((-math.pi * rodillo.diam_actual * rodillo.tabla / 2) + abs(math.sqrt(
        (math.pi * rodillo.diam_actual * rodillo.tabla / 2) ** 2 - math.pi * rodillo.tabla * predictions[0]))) / (
                    -math.pi * rodillo.tabla / 2)
    return equis


#function that gets the rolls that have its geometry and shape matching those of the stand and enough diameter to roll the tons of the job
#that are active and that has an active position
#the order is randomized
def validarcilindros(trabajo, cilindros, posiciones, geometrias, reduccionescilindros):
    cajastrabajo = []
    cilcompatibles = []
    # geometrias = []
    for p in trabajo.cajas:
        cajastrabajo.append(CajasTrabajos(p.numcaja, p.geometria, p.tallado))
    indice = 0
    global diametrosiniciales
    global cantidadcompatibles
    diametrinosiniciales = []
    cantidadinascompatibles = []
    # for each of the stands of that job
    for elemento in cajastrabajo:
        cils = []
        positions = []
        #the total tons of a job are calculated
        toneladastotales = sum(trabajo.toneladaslaminadas)
        #the rolls are checked
        cantidadcompatible = 0
        sumadiametros = 0
        for elemento2 in cilindros:
            entra = False
            #if the geometry and shape meet the requirements and is available
            if elemento.geometria == elemento2.geometria:
                #the positions of that roll
                posicionescil = list(filter(lambda p: p.cod_interno == elemento2.cod_interno, posiciones))
                # the reductions of the rolls for that stand are obtained
                cilindroscaja = reduccionescilindros[indice]
                # determino la reduccion para el cilindro correspondiente
                reduccionesposcil = list(
                    filter(lambda p: p.codigo_interno == elemento2.cod_interno, cilindroscaja.cilindros))
                #for each position of the roll
                for posicion in posicionescil:
                    # if the shape meets the requirements and is active
                    if posicion.num_plano_tallado == elemento.tallado and posicion.cod_interno == elemento2.cod_interno:
                        entra = True
                        if elemento2.cod_estado == 1 and posicion.cod_estado_posicion == 1:
                            #check that the reduction has been calculated
                            if len(reduccionesposcil) > 0:
                                #the reduction for that position of the roll
                                reduccioncilinpos = list(
                                    filter(lambda p: p.cod_posicion == posicion.cod_posicion, reduccionesposcil))
                                #if that reduction exists
                                if len(reduccioncilinpos) > 0:
                                    #the value is obtained
                                    red = reduccioncilinpos[0].reduccion
                                    # if the current diameter is greater than the final plus the reduction
                                    if elemento2.diam_actual > elemento2.diam_final + red:

                                        #the roll is added if it was not
                                        if not elemento2 in cils:
                                            cils.append(elemento2)
                                        #the position is added if it was not
                                        if not posicion in positions:
                                            positions.append(posicion)
                if entra:
                    #increase number of compatible rolls and accumulate its diameter
                    cantidadcompatible = cantidadcompatible + 1
                    sumadiametros = sumadiametros + elemento2.diam_actual
        indice = indice + 1
        #the rolls and the positions are added to the compatibles of that stand
        cilcompatibles.append(CilindrosCompatibles(elemento.numcaja, cils, positions))
        #add the average diameters and the number of compatibles
        diametrinosiniciales.append(sumadiametros/cantidadcompatible)
        cantidadinascompatibles.append(cantidadcompatible)
    diametrosiniciales.append(diametrinosiniciales)
    cantidadcompatibles.append(cantidadinascompatibles)
    return cilcompatibles


#determines if a solution is valid
#checking the diameter constraints
def cumplerestricciones(solucion, rodillo, restricciones, caja):
    for element in restricciones:
        if element.caja1 == (caja + 16):
            if element.tipo == "+-":
                if not (solucion[caja + 1].diam_actual - rodillo.diam_actual) / element.factor < element.cantidad:
                    return False
            elif element.tipo == "=":
                if not (solucion[caja + 1].diam_actual - rodillo.diam_actual) / element.factor == element.cantidad:
                    return False
        if element.caja2 == (caja + 16):
            if element.tipo == "+-":
                if not (rodillo.diam_actual - solucion[caja - 1].diam_actual) / element.factor < element.cantidad:
                    return False
            elif element.tipo == "=":
                if not (rodillo.diam_actual - solucion[caja - 1].diam_actual) / element.factor == element.cantidad:
                    return False
    return True


#determines the reductions of the rolls if they were assembled in each of the stands and it stores it to file
def candidatos2(trabajo, cilindros, posiciones, geometrias, calidades, modelito):
    model = modelito
    cajastrabajo = []
    cilcompatibles = []
    # geometrias = []
    cadena = "{\"cajas\":["
    for p in trabajo.cajas:
        cajastrabajo.append(CajasTrabajos(p.numcaja, p.geometria, p.tallado))
    indice = 0
    #for each stand of the job
    for elemento in cajastrabajo:
        cils = []
        positions = []
        cadena = cadena + "{\"caja\":" + str(elemento.numcaja) + ",\"cilindros\":["
        #determine the total number of tons rolled for that batch considering the different individual jobs that compose it
        toneladastotales = sum(trabajo.toneladaslaminadas)
        #for each of the rolls
        for elemento2 in cilindros:
            # if they are active and its geometry matches the required
            if elemento.geometria == elemento2.geometria and elemento2.cod_estado == 1:
                #its positions are determined
                posicionescil = list(filter(lambda p: p.cod_interno == elemento2.cod_interno, posiciones))
                #the maximum number of tons rolled by the positions
                attrs = max([o.toneladas for o in posicionescil])
                #flag to determine if a position of that roll has already been added
                anadido = False
                # for each of its positions
                for posicion in posicionescil:
                    #maximum number of tons rolled by a position provided the ones rolled by the used
                    attrs = max([attrs, posicion.toneladas + toneladastotales])
                    #check that the position has the required shape, that belongs to the roll, is not used, has not been added any position of that roll and that the number of tons rolled by that position since the last reconditioning is 0
                    if posicion.num_plano_tallado == elemento.tallado and posicion.cod_interno == elemento2.cod_interno and posicion.cod_estado_posicion == 1 and not anadido and posicion.toneladas == 0:
                        #call to the function that calculates the reduction
                        reduccion = anadirelementoarchivo(elemento2, posicionescil, posicion,
                                                          sum(trabajo.toneladaslaminadas), geometrias, calidades, model,
                                                          max(trabajo.calidadmaterial))
                        #to write to file tle code of the roll, the position and the reduction
                        cadena = cadena + "{\"codigo_interno\":" + str(
                            elemento2.cod_interno) + ",\"cod_posicion\":" + str(
                            posicion.cod_posicion) + ",\"reduccion\":" + str(reduccion) + "},"
        indice = indice + 1
        cadena = cadena[:len(cadena) - 1]
        cadena = cadena + "]},"
    cadena = cadena[:len(cadena) - 1]
    fhand = open('salidarandomfores.json', 'w')
    cadena = cadena + "]}"
    fhand.write(cadena)
    fhand.close()


#function that calculates the diameter reduction of each roll
def anadirelementoarchivo(rodillo, posicionescil, posicionusada, toneladas, geometrias, calidades, model, dureza):
    #it calculates the maximum number of tons rolled by a position
    attrs = max([o.toneladas for o in posicionescil])
    if posicionusada.toneladas + toneladas > attrs:
        attrs = posicionusada.toneladas + toneladas
    #calculates the sum of tons rolled by all the positions of the roll
    acumulado = sum([o.toneladas for o in posicionescil])
    acumulado = acumulado + toneladas
    #determines the code of the geometry of the roll
    geomet = list(filter(lambda p: p.geometria == rodillo.geometria, geometrias))
    #determines the code of the quality of the roll
    codcalidad = list(filter(lambda p: p.calidad == rodillo.calidad, calidades))
    #arguments needed to calculate the reduction in args
    args = [str(acumulado), codcalidad[0].cod_calidad, str(attrs), geomet[0].cod_geometria,
            posicionusada.num_plano_tallado, rodillo.diam_actual, str(acumulado / rodillo.numposiciones), dureza]
    #the series are created
    serie = pd.Series([args[0]])
    serie1 = pd.Series([args[1]])
    serie2 = pd.Series([args[2]])
    serie3 = pd.Series([args[3]])
    serie4 = pd.Series([args[4]])
    serie5 = pd.Series([args[5]])
    serie6 = pd.Series([args[6]])
    serie7 = pd.Series([args[7]])
    # with the series a frame is created
    frame = {'AddToneladas': serie, 'COD_CALIDAD': serie1, 'MaxToneladas': serie2, 'NUM_PLANO_BRUTO': serie3,
             'NUM_PLANO_TALLADO': serie4, 'diametro': serie5, 'mediatoneladas': serie6, 'dureza': serie7}
    # with the frame a dataframe is created
    dframe = pd.DataFrame(frame)
    predictions = model.predict(dframe)
    #then the diameter reduction is calculated
    equis = ((-math.pi * rodillo.diam_actual * rodillo.tabla / 2) + abs(math.sqrt(
        (math.pi * rodillo.diam_actual * rodillo.tabla / 2) ** 2 - math.pi * rodillo.tabla * predictions[0]))) / (
                    -math.pi * rodillo.tabla / 2)
    return equis


if __name__ == '__main__':
    # number of times the repeticionestrabajos*jobs are executed
    for histoelement in range(0, 1):
        #rolls loaded from the configuration file
        cilindrosgenerados = []
        #positions loaded from the configuration file
        posicionesgeneradas = []
        # jobs loaded from the configuration file
        trabajos = []
        #geometries loaded from the configuration file
        geometrias = []
        # qualities loaded from the configuration file
        calidades = []
        #shapes loaded from the configuration file
        diftallados = []
        #measures of the rolls loaded from the configuration file
        tablas = []
        #costs loaded from the configuration file. a different cost is supposed for each quality of the roll
        datoscostes = []
        #jobs are repeated in a loop in this case 1 time
        repeticionestrabajos = 1
        #index of the job to be performed
        indicetrabajo = 0
        # data from the geometries, qualities, shapes, measures and costs is loaded from the configuration file
        with open('trabajos.json') as json_file:
            data = json.load(json_file)
            # se cargan los diferentes tipos de geometrias
            for p in data['geometria']:
                geometrias.append(Geometrias(p['cod_caja'], p['geometria'], p['cod_geometria']))
            for p in data['calidades']:
                calidades.append(Calidades(p['cod_calidad'], p['calidad']))
            for p in data['tallado']:
                diftallados.append(Carvings(p['num_plano_tallado'], p['descripcion'], p['cod_caja']))
            for p in data['tablas']:
                tablas.append(Tablas(p['num_plano_bruto'], p['tabla'], p['nombre']))
            for p in data['costes']:
                datoscostes.append(Costemmvol(p['COD_CALIDAD'], p['costemm3']))
        trabajos = []
        # jobs scheduled to be done
        with open('pruebatrabajos.json') as json_file:
            data = json.load(json_file)
            for p3 in range(int(data['numerorepeticiones'])):
                for p in data['TrabajosLaminacion']:
                    cajas = []
                    for p2 in p['cajas']:
                        cajas.append(CajasTrabajos(p2['caja'], p2['geometria'], p2['tallado']))
                    trabajos.append(Trabajos(p['toneladaslaminadas'], p['calidadmaterial'], cajas))
        #the rolls are loaded from the configuration file
        with open('conjuntoalmacenadointerfaz.json') as json_file:
            data = json.load(json_file)
            for p in data['Cilindros']:

                cilindrosgenerados.append(
                    Roll(p['cod_interno'], p['diam_inicial'], p['diam_final'], p['diam_actual'],
                         p['cod_estado'],
                         p['geometria'], p['numposiciones'], p['calidad'], p['densidad'], p['tabla'],
                         p['coste']))
            for p in data['Posiciones']:
                posicionesgeneradas.append(
                    Position(p['cod_interno'], p['cod_posicion'], p['num_plano_tallado'], p['cod_estado_posicion'],
                             p['toneladas'], p['diam_rectif'], p['numposiciones']))
        cadenita = "{\"Trabajos\":["
        # output file
        fhand = open('salidaparagraficasnueva' + str(histoelement) + '.json', 'w')
        fhand.write(cadenita)
        fhand.close()
        reduccionesacumuladas = []

        cadenita = ""
        # reduction model
        filename = 'finalized_model2_nuevofiltro.sav'
        #load model
        modelito = pickle.load(open(filename, 'rb'))
        # damaged rolls
        rotosac = []
        rotostc = []

        terminar = False
        yaescrito = False
        tinicial = 0
        # for each job the algorithm is executed
        for trabajo in trabajos:
            cadenita = cadenita + "{\"trabajo\":" + str(indicetrabajo) + ",\"vueltas\":["
            # reduction from the previous round
            reduccionprevia = -1
            # reduction from the new round
            reduccionnueva = -2
            # final rolls selected for a job
            solucionfinal = []
            # positions of the roll selected to perform a job
            solucionespositionsfinal = []
            ejecuciontrabajo = 0
            restricciones = []

            # load of the job to perform
            with open('pruebatrabajos.json') as json_file:
                data = json.load(json_file)
                #the constraints for that job are loaded
                print(str(len(trabajos) / repeticionestrabajos))
                print(indicetrabajo % len(trabajos))
                print(indicetrabajo)
                print(len(trabajos))
                for p in data['restricciones'][indicetrabajo % len(data['TrabajosLaminacion'])]:
                    restricciones.append(
                        Restricciones(p['caja1'], p['caja2'], p['cantidad'], p['factor'], p['tipo']))
            # number of rounds performed by the algorithm for a particular job
            cuentavueltas = 0


            tinicial = time.time()

            # cuentavueltas = cuentavueltas + 1
            # diameter of the agents
            diametroagentes = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # diameter reductions of the agents
            reduccionesagentes = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # volume reductions of the agents
            reduccionesvolumenagentes = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # sum of the volume reductions of the agents
            reduccionestotalesvolumenagentes = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # monetary cost of the agents
            costesagentes = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # sum of the monetary cost of the agents
            costestotalesagentes = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # average diameter of the agents
            mediadiametros = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # media de las reducciones de los agentes
            mediareducciones = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # average volume reductions of the agents
            mediareduccionvolumen = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # average costs of the agents
            mediacostes = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # standard deviation of the diameter of the agents
            desviaciontipicadiametros = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # standard deviation of the diameter reductions of the agents
            desviaciontipicareducciones = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # standard deviation of the volume reductions of the agents
            desviaciontipicareduccionesvolumen = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # standard deviation of the costs of the agents
            desviacioncostes = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # data from the rolls assembled on each of the agents
            datoscilindroagentes = [
                [], [], [], [], [], [], [], [], [], []
            ]
            # determine the valid rolls given the conditions of the job
            # in this way, the active rolls with active positions, valid for each stand (geometry and shape) are selected and they are shown
            # call to get the compatibles and the reductions
            candidatos2(trabajo, cilindrosgenerados, posicionesgeneradas, geometrias, calidades, modelito)
            #the diameter reductions are read from the file provided the calculated ones by the model
            reduccionescompatibles = []
            # the file with the reductions is read
            with open('salidarandomfores.json') as json_file:
                data = json.load(json_file)
                for p in data['cajas']:
                    cilindrosreducciones = []
                    for p2 in p['cilindros']:
                        cilindrosreducciones.append(
                            CilindrosReducciones(p2['codigo_interno'], p2['cod_posicion'], p2['reduccion']))
                    reduccionescompatibles.append(CajaCompatibles(p['caja'], cilindrosreducciones))
            #determine if those reductions do not make that the diameter is less than the final one
            miscompatibles = validarcilindros(trabajo, cilindrosgenerados, posicionesgeneradas, geometrias,
                                              reduccionescompatibles)
            # random solutions are generated, the loop generates solutions, checks if they are valid and when the number reaches a certain one
            # or when a certain number of executions are performed it stops
            # number of solutions generated
            contadorsoluciones = 0
            # soluciones rodillos
            soluciones = []
            # positions of the rolls of the solution
            solucionespositions = []
            # number of executions of the loop that searches solutions
            numeroejecuciones = 0
            # rolls used in any solution
            rodillosusados = []
            # while the number of solutions is less than the number of agents and the executions of
            # the random solution search are less than 100
            while contadorsoluciones < 10 and numeroejecuciones < 100:
                # rolls of the current solution
                poblacioninicial = []
                #positions of the current solution
                posicionesiniciales = []
                #contains the number of the stands of the current job
                cajas = []
                # initialize the initial population
                # for each of the stands involved in the current job
                for caja in trabajo.cajas:
                    cajas.append(caja.numcaja)
                #number of stands processed
                contadorcajas = 0
                #for each of the elements in miscompatibles (number of stand, rolls and quality)
                for cajita in miscompatibles:
                    #the number of processed stands is increased
                    contadorcajas = contadorcajas + 1
                    rodillosposibles = copy.deepcopy(cajita.compatibles)
                    # if it is the first stand, a random one is selected
                    # if it is another, one of the compatible ones is selected once filtered the ones that accomplish the constraints
                    if contadorcajas > 1:
                        for element in restricciones:
                            if element.caja1 == cajas[contadorcajas - 1]:
                                if element.tipo == "+-":
                                    rodillosposibles = list(filter(lambda t: abs(t.diam_actual - poblacioninicial[
                                        len(poblacioninicial) - 1].diam_actual) / element.factor
                                                                             < element.cantidad,
                                                                   cajita.compatibles))
                                elif element.tipo == "=":
                                    rodillosposibles = list(filter(lambda t: abs(t.diam_actual - poblacioninicial[
                                        len(poblacioninicial) - 1].diam_actual) / element.factor
                                                                             == element.cantidad,
                                                                   cajita.compatibles))
                    # it determines whether there are possible rolls
                    if len(rodillosposibles) > 0:
                        #one roll is selected randomly
                        numeroAleatorio = random.randint(0, len(rodillosposibles) - 1)
                        # checks whether it is used in another stand
                        cilindrosentretodascajas = rodillosusados + poblacioninicial
                        cilindrousadosmismocodinterno = list(
                            filter(lambda p: p.cod_interno == rodillosposibles[numeroAleatorio].cod_interno,
                                   cilindrosentretodascajas))
                        rodilloelegido = rodillosposibles[numeroAleatorio]
                        #while the selected roll is being used elsewhere and there are rolls left
                        while len(cilindrousadosmismocodinterno) > 0 and len(rodillosposibles) > 0:
                            #another is selected randomly
                            numeroAleatorio = random.randint(0, len(rodillosposibles) - 1)
                            # the rolls used in another stands are added those selected
                            cilindrosentretodascajas = rodillosusados + poblacioninicial
                            #checks whether this also is being used elsewhere
                            cilindrousadosmismocodinterno = list(
                                filter(lambda p: p.cod_interno == rodillosposibles[numeroAleatorio].cod_interno,
                                       cilindrosentretodascajas))
                            rodilloelegido = rodillosposibles[numeroAleatorio]
                            #this roll is removed from the compatible ones of that stand for this solution
                            rodillosposibles.remove(rodillosposibles[numeroAleatorio])
                        #if it was not being used in another stand
                        if not len(cilindrousadosmismocodinterno) > 0:
                            #it is used as solution of the current stand
                            poblacioninicial.append(rodilloelegido)
                            #from the positions of the roll it is used that with less tons rolled
                            posicionescil = list(
                                filter(lambda p: p.cod_interno == rodilloelegido.cod_interno,
                                       cajita.positions))
                            attrs = min([o.toneladas for o in posicionescil])
                            for ele in posicionescil:
                                if ele.toneladas == attrs:
                                    posicionesiniciales.append(ele)
                                    #in case two positions have the same number of tons rolled
                                    break
                    else:
                        break
                #if an initial solution was found
                if len(poblacioninicial) == len(cajas):
                    #if it was, it is added to the solutions and the quantity of solutions is increased
                    soluciones.append(poblacioninicial)
                    solucionespositions.append(posicionesiniciales)
                    #it is removed from the set of compatible ones
                    acumuladoreducciones = 0
                    #diameter reductions of the solution
                    redss = []
                    # volume reductions of the solution
                    reduccionesvolumen = []
                    #costs of the solution
                    costesss = []
                    #data from the rolls of the solution
                    datostodos = []
                    #for each roll of the initial solution found
                    for element in range(len(poblacioninicial)):
                        posicionescilindrin = list(
                            filter(lambda p: p.cod_interno == poblacioninicial[element].cod_interno,
                                   posicionesgeneradas))
                        #the diameter reduction is determined
                        valorred = calculoreduccioncondurezacalidad(poblacioninicial[element], posicionescilindrin,
                                                                    posicionesiniciales[element],
                                                                    sum(trabajo.toneladaslaminadas), geometrias,
                                                                    calidades, modelito, trabajo)
                        #the data of the roll is added to the array
                        datostodos.append(datoscilindro)
                        #the sum of the reductions is calculated
                        acumuladoreducciones = acumuladoreducciones + valorred
                        #the diameter reduction is added to the array
                        redss.append(valorred)
                        #the volume reduction is added to the array
                        reduccionesvolumen.append(
                            (1 / 4) * math.pi * ((poblacioninicial[element].diam_actual) ** 2) * poblacioninicial[
                                element].tabla - (1 / 4) * math.pi * (
                                    (poblacioninicial[element].diam_actual - valorred) ** 2) * poblacioninicial[
                                element].tabla)
                        #the cost is added to the array
                        costesss.append(
                            reduccionesvolumen[len(reduccionesvolumen) - 1] * poblacioninicial[element].coste)
                    print("Agente " + str(contadorsoluciones) + " reduccion total " + str(acumuladoreducciones))
                    #the values of the diameters of the rolls are stored
                    diametrillos = []
                    for element in range(len(poblacioninicial)):
                        print(str(poblacioninicial[element].cod_interno) + " " + str(
                            posicionesiniciales[element].cod_posicion) + " " + str(redss[element]))
                        diametrillos.append(poblacioninicial[element].diam_actual)
                    #in order to be able to plot the results, the diameter and volume reductions, costs and diameter of the agents are added to an array
                    reduccionesagentes[contadorsoluciones].append(redss)
                    reduccionesvolumenagentes[contadorsoluciones].append(reduccionesvolumen)
                    reduccionestotalesvolumenagentes[contadorsoluciones].append(sum(reduccionesvolumen))
                    costestotalesagentes[contadorsoluciones].append(sum(costesss))
                    costesagentes[contadorsoluciones].append(costesss)
                    diametroagentes[contadorsoluciones].append(diametrillos)
                    #the used rolls are removed from miscompatibles
                    for element in range(len(miscompatibles)):
                        if poblacioninicial[element] in miscompatibles[element].compatibles:
                            miscompatibles[element].compatibles.remove(poblacioninicial[element])
                            miscompatibles[element].positions.remove(posicionesiniciales[element])
                    # it is stored
                    # average, standard deviation of diameter, diameter reduction, volume reduction and costs
                    # data of the rolls
                    mediadiametros[contadorsoluciones].append(stats.mean(diametrillos))
                    mediareducciones[contadorsoluciones].append(stats.mean(redss))
                    mediareduccionvolumen[contadorsoluciones].append(stats.mean(reduccionesvolumen))
                    mediacostes[contadorsoluciones].append(stats.mean(costesss))
                    desviaciontipicadiametros[contadorsoluciones].append(stats.pstdev(diametrillos))
                    desviaciontipicareducciones[contadorsoluciones].append(stats.pstdev(redss))
                    desviaciontipicareduccionesvolumen[contadorsoluciones].append(stats.pstdev(reduccionesvolumen))
                    desviacioncostes[contadorsoluciones].append(stats.pstdev(costesss))
                    datoscilindroagentes[contadorsoluciones].append(datostodos)
                    contadorsoluciones = contadorsoluciones + 1

                    rodillosusados = rodillosusados + poblacioninicial
                numeroejecuciones = numeroejecuciones + 1
            #if the number of solutions reached is equal to the number of agents defined
            if contadorsoluciones == 10:

                # the auctions for the rest of the rolls start
                # the round of auctions is repeated while some reduction is gained
                while reduccionprevia > reduccionnueva and (reduccionprevia - reduccionnueva) > 0.01 and not terminar:
                    #where is placed in the array the stand that is being processed
                    poscajaarray = 0
                    cadenita = cadenita + "{\"vuelta\":" + str(cuentavueltas) + "," + "\"valores\": ["
                    #for each of the solutions it is checked if any of the remaining rolls improves it
                    for cajita in miscompatibles:
                        #for each of the solutions it is checked if any of the remaining rolls improves it
                        for rodillo in cajita.compatibles:
                            #stores the different data that is gonna be saved while it is checked what agent and stand win the auction
                            almacendatoscilindros = []
                            almacendatoscostes = []
                            almacendatosreducciones = []
                            almacendatosreduccionesvol = []
                            almacendatosdiametros = []
                            # data that is saved from the roll to the winner agent and stand
                            datocilindrosol = ""
                            datocoste = 0
                            datoreduccion = 0
                            datoreduccionvol = 0
                            #array where it is stored how much improves each of the agents for the current stand changing the roll
                            mejoracostes = []
                            posicionescil = list(
                                filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                       cajita.positions))
                            posicionescil2 = list(
                                filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                       posicionesgeneradas))
                            datosnuevo = ""
                            rodilloscoincidentes = list(
                                filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                       rodillosusados))
                            #if the roll is not been used yet
                            if len(rodilloscoincidentes) == 0 and len(posicionescil) > 0:
                                #the positions are checked and it is selected that with less tons rolled
                                attrs = min([o.toneladas for o in posicionescil])
                                posicionusada = list(
                                    filter(lambda p: p.toneladas == attrs,
                                           posicionescil))[0]
                                #it is determined the reduction that the new roll has
                                reduccionrodillonuevo = calculoreduccioncondurezacalidad(rodillo, posicionescil2,
                                                                                         posicionusada,
                                                                                         sum(trabajo.toneladaslaminadas),
                                                                                         geometrias, calidades,
                                                                                         modelito, trabajo)
                                #it is stored in case it results the winner one
                                almacendatosreducciones.append(reduccionrodillonuevo)
                                # the data of the roll is stored
                                datosnuevo = datoscilindro
                                almacendatoscilindros.append(datosnuevo)
                                #determines the volume reduction that the roll has and it is stored
                                reduccionrodillovolnuevo = (1 / 4) * math.pi * (
                                        (rodillo.diam_actual) ** 2) * rodillo.tabla - (1 / 4) * math.pi * ((
                                                                                                                   rodillo.diam_actual - reduccionrodillonuevo) ** 2) * rodillo.tabla
                                almacendatosreduccionesvol.append(reduccionrodillovolnuevo)
                                #calculates the cost of rolling with that roll and it is stored
                                reduccionrodillovolnuevo = reduccionrodillovolnuevo * rodillo.coste
                                almacendatoscostes.append(reduccionrodillovolnuevo)
                                #solution that is being processed
                                contador = 0
                                # recorro las diferentes soluciones
                                for solucion in soluciones:
                                    # print("posicion"+str(poscajaarray)+" "+str(len(solucion)))
                                    posicionescil2 = list(
                                        filter(lambda p: p.cod_interno == solucion[poscajaarray].cod_interno,
                                               posicionesgeneradas))
                                    # for each one it is checked if the cost of the new roll is less than the one for the existing roll
                                    # contador indicates the number of the agent
                                    reduccionesmiagente = reduccionesvolumenagentes[contador]
                                    #array of volume reductions. The last is obtained for the stand that is being evaluated
                                    reduccionrodillovolensolucion = reduccionesmiagente[len(reduccionesmiagente) - 1][
                                        poscajaarray]
                                    #to obtain the cost it is multiplied the volume reduction by the cost in mm3
                                    reduccionrodillovolensolucion = reduccionrodillovolensolucion * solucion[
                                        poscajaarray].coste
                                    # if the cost is less and the diameter constraints are accomplished being this greater than the final,
                                    # the cost improvement is stored
                                    if reduccionrodillovolensolucion > reduccionrodillovolnuevo and (
                                            rodillo.diam_actual - reduccionrodillonuevo) > rodillo.diam_final and cumplerestricciones(
                                        solucion, rodillo, restricciones, poscajaarray):
                                        # si es menor incluyo la mejora de costes en el array
                                        mejoracostes.append(reduccionrodillovolensolucion - reduccionrodillovolnuevo)

                                    else:
                                        #if it is not 0 is included in the array
                                        mejoracostes.append(0)
                                    contador = contador + 1
                                # number that indicates if it is the current stand, the previous or the next
                                cajaquemejora = 0

                                # unless another stand improves more, the one with the greatest improvement is the current one 0
                                # and the data of this one is stored
                                # if another improves more, they will be changed
                                datocilindrosol = almacendatoscilindros[0]
                                datoreduccion = almacendatosreducciones[0]
                                datoreduccionvol = almacendatosreduccionesvol[0]
                                datocoste = almacendatoscostes[0]
                                # the previous and next ones are gonna be checked
                                # if it is the first one it has no previous one
                                # if it is the last one it has no next one
                                # in any other case, it has both
                                # if it is the first stand and it is compatible with the next one
                                if poscajaarray == 0 and rodillo in miscompatibles[poscajaarray + 1].compatibles:
                                    #the positions are checked and it is selected the one which has rolled less tons
                                    posicionescil = list(
                                        filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                               miscompatibles[poscajaarray + 1].positions))
                                    posicionescil2 = list(
                                        filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                               posicionesgeneradas))
                                    attrs = min([o.toneladas for o in posicionescil])
                                    #the chosen position is the compatible one with the less number of tons rolled
                                    posicionusada = list(
                                        filter(lambda p: p.toneladas == attrs,
                                               posicionescil))[0]
                                    #the reduction of the new roll is determined and it is stored
                                    reduccionrodillonuevo = calculoreduccioncondurezacalidad(rodillo, posicionescil2,
                                                                                             posicionusada,
                                                                                             sum(
                                                                                                 trabajo.toneladaslaminadas),
                                                                                             geometrias, calidades,
                                                                                             modelito, trabajo)
                                    almacendatosreducciones.append(reduccionrodillonuevo)
                                    # the data of the new roll is stored
                                    datosnuevo = datoscilindro
                                    almacendatoscilindros.append(datosnuevo)
                                    #the volume reduction of the roll is calculated and stored
                                    reduccionrodillovolnuevo = (1 / 4) * math.pi * (
                                            (rodillo.diam_actual) ** 2) * rodillo.tabla - (1 / 4) * math.pi * ((
                                                                                                                       rodillo.diam_actual - reduccionrodillonuevo) ** 2) * rodillo.tabla
                                    almacendatosreduccionesvol.append(reduccionrodillovolnuevo)
                                    # the cost is calculated and stored
                                    reduccionrodillovolnuevo = reduccionrodillovolnuevo * rodillo.coste

                                    almacendatoscostes.append(reduccionrodillovolnuevo)
                                    #array where it is stored the improvement of each of the agents in the next sstand
                                    mejoracostessiguiente = []
                                    #agent that is being processed from 0 to 9
                                    contador = 0
                                    for solucion in soluciones:
                                        posicionescil2 = list(
                                            filter(lambda p: p.cod_interno == solucion[poscajaarray + 1].cod_interno,
                                                   posicionesgeneradas))
                                        # for each one it is determined if the cost of the new roll is less than the current one
                                        # volume reductions of the agent number contador
                                        reduccionesmiagente = reduccionesvolumenagentes[contador]
                                        # volume reductions for the stand in which it is gonna be replaced
                                        # the array from the last replacement is used
                                        reduccionrodillovolensolucion = \
                                            reduccionesmiagente[len(reduccionesmiagente) - 1][
                                                poscajaarray + 1]
                                        #cost for the volume reduction of the roll in that stand
                                        reduccionrodillovolensolucion = reduccionrodillovolensolucion * solucion[
                                            poscajaarray + 1].coste
                                        #if it is less and accomplishes the constraints being the diameter after rolling greater than the final one it is stored the improvement
                                        if reduccionrodillovolensolucion > reduccionrodillovolnuevo and (
                                                rodillo.diam_actual - reduccionrodillonuevo) > rodillo.diam_final and cumplerestricciones(
                                            solucion, rodillo, restricciones, poscajaarray + 1):
                                            #if it less the cost improvement is included in the array
                                            mejoracostessiguiente.append(
                                                reduccionrodillovolensolucion - reduccionrodillovolnuevo)
                                            # print("mejora")
                                        else:
                                            #if it is not 0 is included in the array
                                            mejoracostessiguiente.append(0)
                                        contador = contador + 1

                                    # it is determined if improves more the current stand or stand+1, in case it occurs the second option, the stored data is changed
                                    if max(mejoracostes) > max(mejoracostessiguiente):
                                        cajaquemejora = 0

                                    else:
                                        cajaquemejora = 1
                                        mejoracostes = mejoracostessiguiente
                                        datocilindrosol = almacendatoscilindros[1]
                                        datoreduccion = almacendatosreducciones[1]
                                        datoreduccionvol = almacendatosreduccionesvol[1]
                                        datocoste = almacendatoscostes[1]
                                        # print("mejora la siguiente")
                                #if the roll is compatible with the previous stand and it is the last one
                                elif poscajaarray == (len(miscompatibles) - 1) and rodillo in miscompatibles[
                                    poscajaarray - 1].compatibles:
                                    #the position with less rolled tons is selected
                                    posicionescil = list(
                                        filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                               miscompatibles[poscajaarray - 1].positions))
                                    posicionescil2 = list(
                                        filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                               posicionesgeneradas))
                                    #it is gonna roll the compatible position of those possible with the less number of tons rolled
                                    attrs = min([o.toneladas for o in posicionescil])
                                    posicionusada = list(
                                        filter(lambda p: p.toneladas == attrs,
                                               posicionescil))[0]
                                    #the reduction of the new roll is determined and stored
                                    reduccionrodillonuevo = calculoreduccioncondurezacalidad(rodillo, posicionescil2,
                                                                                             posicionusada,
                                                                                             sum(
                                                                                                 trabajo.toneladaslaminadas),
                                                                                             geometrias, calidades,
                                                                                             modelito, trabajo)
                                    almacendatosreducciones.append(reduccionrodillonuevo)
                                    #the data of the new roll is stored
                                    datosnuevo = datoscilindro
                                    almacendatoscilindros.append(datosnuevo)
                                    #the volume reduction is calculated and stored
                                    reduccionrodillovolnuevo = (1 / 4) * math.pi * (
                                            (rodillo.diam_actual) ** 2) * rodillo.tabla - (1 / 4) * math.pi * ((
                                                                                                                       rodillo.diam_actual - reduccionrodillonuevo) ** 2) * rodillo.tabla
                                    almacendatosreduccionesvol.append(reduccionrodillovolnuevo)
                                    #the cost is calculated and stored
                                    reduccionrodillovolnuevo = reduccionrodillovolnuevo * rodillo.coste
                                    almacendatoscostes.append(reduccionrodillovolnuevo)
                                    mejoracostesanterior = []
                                    #agent that is being processed
                                    contador = 0
                                    #loop through the solutions and determine how much improves each agent changing the roll
                                    for solucion in soluciones:
                                        posicionescil2 = list(
                                            filter(lambda p: p.cod_interno == solucion[poscajaarray - 1].cod_interno,
                                                   posicionesgeneradas))
                                        #for each one it determines whether the cost of the new roll is less than that of the existent one
                                        reduccionesmiagente = reduccionesvolumenagentes[contador]
                                        reduccionrodillovolensolucion = \
                                            reduccionesmiagente[len(reduccionesmiagente) - 1][
                                                poscajaarray - 1]
                                        reduccionrodillovolensolucion = reduccionrodillovolensolucion * solucion[
                                            poscajaarray - 1].coste
                                        if reduccionrodillovolensolucion > reduccionrodillovolnuevo and (
                                                rodillo.diam_actual - reduccionrodillonuevo) > rodillo.diam_final and cumplerestricciones(
                                            solucion, rodillo, restricciones, poscajaarray - 1):

                                            #if it is less the cost improvement is included in the array
                                            mejoracostesanterior.append(
                                                reduccionrodillovolensolucion - reduccionrodillovolnuevo)

                                        else:
                                            #if it is not 0 is included in the array
                                            mejoracostesanterior.append(0)
                                        contador = contador + 1
                                    #it is determined whether the agents improve more for the current stand or for the previous one and the data is updated
                                    if max(mejoracostes) > max(mejoracostesanterior):
                                        cajaquemejora = 0
                                        datocilindrosol = almacendatoscilindros[0]
                                        datoreduccion = almacendatosreducciones[0]
                                        datoreduccionvol = almacendatosreduccionesvol[0]
                                        datocoste = almacendatoscostes[0]
                                    else:
                                        cajaquemejora = -1
                                        mejoracostes = mejoracostesanterior
                                        datocilindrosol = almacendatoscilindros[1]
                                        datoreduccion = almacendatosreducciones[1]
                                        datoreduccionvol = almacendatosreduccionesvol[1]
                                        datocoste = almacendatoscostes[1]
                                #if it is not the first stand or the last one
                                elif poscajaarray < (len(miscompatibles) - 1) and poscajaarray > 0:

                                    posicionescil = list(
                                        filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                               miscompatibles[poscajaarray - 1].positions))
                                    posicionescil2 = list(
                                        filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                               posicionesgeneradas))
                                    #if the roll has compatible positions with the previous one
                                    if rodillo in miscompatibles[poscajaarray - 1].compatibles and len(
                                            posicionescil) > 0:
                                        #checks the compatible positions with that stand and the one which has rolled less is selected
                                        attrs = min([o.toneladas for o in posicionescil])
                                        posicionusada = list(
                                            filter(lambda p: p.toneladas == attrs,
                                                   posicionescil))[0]
                                        #it determines the reduction the new roll has and it is stored
                                        reduccionrodillonuevo = calculoreduccioncondurezacalidad(rodillo,
                                                                                                 posicionescil2,
                                                                                                 posicionusada,
                                                                                                 sum(
                                                                                                     trabajo.toneladaslaminadas),
                                                                                                 geometrias, calidades,
                                                                                                 modelito, trabajo)

                                        almacendatosreducciones.append(reduccionrodillonuevo)
                                        #the data from the new roll is stored
                                        datosnuevo = datoscilindro
                                        almacendatoscilindros.append(datosnuevo)
                                        #the volume reduction is calculated and stored
                                        reduccionrodillovolnuevo = (1 / 4) * math.pi * (
                                                (rodillo.diam_actual) ** 2) * rodillo.tabla - (1 / 4) * math.pi * ((
                                                                                                                           rodillo.diam_actual - reduccionrodillonuevo) ** 2) * rodillo.tabla
                                        almacendatosreduccionesvol.append(reduccionrodillovolnuevo)
                                        #the cost is calculated and stored
                                        reduccionrodillovolnuevo = reduccionrodillovolnuevo * rodillo.coste
                                        almacendatoscostes.append(reduccionrodillovolnuevo)
                                        #array in which it is stored how much the agents improve for the previous stand
                                        mejoracostesanterior = []
                                        contador = 0
                                        # loop through the solutions of the agents
                                        for solucion in soluciones:
                                            posicionescil2 = list(
                                                filter(
                                                    lambda p: p.cod_interno == solucion[poscajaarray - 1].cod_interno,
                                                    posicionesgeneradas))
                                            #for each one it is determined whether the cost of the new roll is less than that of the existent roll for each solution
                                            reduccionesmiagente = reduccionesvolumenagentes[contador]
                                            reduccionrodillovolensolucion = \
                                                reduccionesmiagente[len(reduccionesmiagente) - 1][poscajaarray - 1]
                                            reduccionrodillovolensolucion = reduccionrodillovolensolucion * solucion[
                                                poscajaarray - 1].coste
                                            #if the cost improves and the constraints are accomplished and the diameter is greater than the final one, the improvement is stored
                                            if reduccionrodillovolensolucion > reduccionrodillovolnuevo and (
                                                    rodillo.diam_actual - reduccionrodillonuevo) > rodillo.diam_final and cumplerestricciones(
                                                solucion, rodillo, restricciones, poscajaarray - 1):
                                                #if it is less the cost improvement is included in the array
                                                mejoracostesanterior.append(
                                                    reduccionrodillovolensolucion - reduccionrodillovolnuevo)

                                            else:
                                                # if it is not 0 is included in the array
                                                mejoracostesanterior.append(0)
                                            contador = contador + 1

                                        # it is checked whether it improves more the current stand or the stand -1 and the data is updated

                                        if max(mejoracostes) > max(mejoracostesanterior):
                                            cajaquemejora = 0
                                            datocilindrosol = almacendatoscilindros[0]
                                            datoreduccion = almacendatosreducciones[0]
                                            datoreduccionvol = almacendatosreduccionesvol[0]
                                            datocoste = almacendatoscostes[0]
                                        else:
                                            cajaquemejora = -1
                                            mejoracostes = mejoracostesanterior
                                            datocilindrosol = almacendatoscilindros[1]
                                            datoreduccion = almacendatosreducciones[1]
                                            datoreduccionvol = almacendatosreduccionesvol[1]
                                            datocoste = almacendatoscostes[1]

                                    #if the roll is compatible with the next stand
                                    if rodillo in miscompatibles[poscajaarray + 1].compatibles:
                                        #the positions are checked and it is selected that which has rolled less tons
                                        posicionescil = list(
                                            filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                                   miscompatibles[poscajaarray + 1].positions))
                                        posicionescil2 = list(
                                            filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                                   posicionesgeneradas))
                                        #it is determined the position which would roll, the compatible one with less tons rolled
                                        attrs = min([o.toneladas for o in posicionescil])
                                        posicionusada = list(
                                            filter(lambda p: p.toneladas == attrs,
                                                   posicionescil))[0]
                                        #it is determined the reduction the new roll has and it is stored
                                        reduccionrodillonuevo = calculoreduccioncondurezacalidad(rodillo,
                                                                                                 posicionescil2,
                                                                                                 posicionusada,
                                                                                                 sum(
                                                                                                     trabajo.toneladaslaminadas),
                                                                                                 geometrias, calidades,
                                                                                                 modelito, trabajo)
                                        almacendatosreducciones.append(reduccionrodillonuevo)
                                        #the data of the new roll is stored
                                        datosnuevo = datoscilindro
                                        almacendatoscilindros.append(datosnuevo)
                                        #the volume reduction of the new roll is calculated and stored
                                        reduccionrodillovolnuevo = (1 / 4) * math.pi * (
                                                (rodillo.diam_actual) ** 2) * rodillo.tabla - (1 / 4) * math.pi * ((
                                                                                                                           rodillo.diam_actual - reduccionrodillonuevo) ** 2) * rodillo.tabla
                                        almacendatosreduccionesvol.append(reduccionrodillovolnuevo)
                                        #the cost of the new roll is calculated and stored
                                        reduccionrodillovolnuevo = reduccionrodillovolnuevo * rodillo.coste
                                        almacendatoscostes.append(reduccionrodillovolnuevo)
                                        #array where the costs of rolling with the new roll for the next stand in each of the agents are stored
                                        mejoracostessiguiente = []
                                        #agent that is being processed
                                        contador = 0
                                        #loop through the solutions of each of the agents
                                        for solucion in soluciones:
                                            posicionescil2 = list(
                                                filter(
                                                    lambda p: p.cod_interno == solucion[poscajaarray + 1].cod_interno,
                                                    posicionesgeneradas))
                                            #for each one it is determined whether the cost of the new roll is less than that of the existing one
                                            reduccionesmiagente = reduccionesvolumenagentes[contador]
                                            reduccionrodillovolensolucion = \
                                                reduccionesmiagente[len(reduccionesmiagente) - 1][poscajaarray + 1]
                                            reduccionrodillovolensolucion = reduccionrodillovolensolucion * solucion[
                                                poscajaarray + 1].coste
                                            #if the cost is less, the diameter constraints are accomplished and the diameter after rolling is greater than the final diameter it is added the cost improvement
                                            if reduccionrodillovolensolucion > reduccionrodillovolnuevo and (
                                                    rodillo.diam_actual - reduccionrodillonuevo) > rodillo.diam_final and cumplerestricciones(
                                                solucion, rodillo, restricciones, poscajaarray + 1):
                                                #if it is less the cost improvement is included in the array
                                                mejoracostessiguiente.append(
                                                    reduccionrodillovolensolucion - reduccionrodillovolnuevo)

                                            else:
                                                #if it is not 0 is included in the array
                                                mejoracostessiguiente.append(0)
                                            contador = contador + 1
                                        # if the improvement of the next stand is greater than the current one, the data is updated
                                        # the data is in the last position of the array
                                        if max(mejoracostes) < max(mejoracostessiguiente):
                                            cajaquemejora = 1
                                            mejoracostes = mejoracostessiguiente
                                            datocilindrosol = almacendatoscilindros[len(almacendatoscilindros) - 1]
                                            datoreduccion = almacendatosreducciones[len(almacendatoscilindros) - 1]
                                            datoreduccionvol = almacendatosreduccionesvol[
                                                len(almacendatoscilindros) - 1]
                                            datocoste = almacendatoscostes[len(almacendatoscilindros) - 1]
                                #the maximum is searched, bigger difference and the position where it is
                                posicionmaximo = 0
                                maximo = mejoracostes[0]
                                for elemento in range(len(mejoracostes)):
                                    if mejoracostes[elemento] > maximo:
                                        posicionmaximo = elemento
                                        maximo = mejoracostes[elemento]
                                #if the biggest improvement is greater than 0 there is a real improvement
                                if mejoracostes[posicionmaximo] > 0:
                                    #in this case, the roll is changed and the other is added in order to be auctioned again
                                    valormejora = mejoracostes[posicionmaximo]
                                    valorantes = 0
                                    valordespues = 0
                                    print("\n Agente: " + str(posicionmaximo) + " mejora: " + str(
                                        mejoracostes[posicionmaximo]) + " en caja " + str(
                                        16 + poscajaarray + cajaquemejora) + "\n")
                                    print(str(rodillo.cod_interno))
                                    #total cost of the winner agent
                                    acumuladocostes = 0
                                    #sum of diameter reductions
                                    acumuladocostesdiametros = 0
                                    #stand that is being processed
                                    cuentacajas = 0
                                    print("antes de cambiar rodillo")
                                    # for the winner agent
                                    for rodillito in soluciones[posicionmaximo]:
                                        posicionescil = list(
                                            filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                                   miscompatibles[cuentacajas].positions))
                                        posicionescil2 = list(
                                            filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                                   posicionesgeneradas))
                                        #the cost of the previous roll in the solution is determined
                                        reduccionesmiagente = reduccionesvolumenagentes[posicionmaximo]
                                        reduccionrodillovolensolucion = \
                                            reduccionesmiagente[len(reduccionesmiagente) - 1][
                                                cuentacajas]
                                        reduccionrodillovolensolucion = reduccionrodillovolensolucion * rodillito.coste



                                        acumuladocostes = acumuladocostes + reduccionrodillovolensolucion

                                        cuentacajas = cuentacajas + 1

                                    valorantes = acumuladocostes
                                    #the previous cost is shown and the roll is changed adding the previous one to the array of compatible ones to auction it
                                    print("Agente: " + str(posicionmaximo) + " coste total: " + str(acumuladocostes))
                                    miscompatibles[poscajaarray + cajaquemejora].compatibles.append(
                                        soluciones[posicionmaximo][poscajaarray + cajaquemejora])
                                    rodillosusados.remove(soluciones[posicionmaximo][poscajaarray + cajaquemejora])
                                    miscompatibles[poscajaarray + cajaquemejora].positions.append(
                                        solucionespositions[posicionmaximo][poscajaarray + cajaquemejora])

                                    soluciones[posicionmaximo][poscajaarray + cajaquemejora] = rodillo
                                    rodillosusados.append(rodillo)
                                    posicionusada = list(
                                        filter(lambda p: p.cod_interno == rodillo.cod_interno,
                                               miscompatibles[poscajaarray + cajaquemejora].positions))
                                    if len(posicionusada) == 0:
                                        print("aqui")
                                    posicionusada = posicionusada[0]
                                    solucionespositions[posicionmaximo][poscajaarray + cajaquemejora] = posicionusada
                                    miscompatibles[poscajaarray + cajaquemejora].compatibles.remove(rodillo)
                                    miscompatibles[poscajaarray + cajaquemejora].positions.remove(posicionusada)
                                    acumuladocostes = 0
                                    acumuladocostesdiametros = 0
                                    cuentacajas = 0
                                    print("despues de cambiar rodillo")
                                    reduccioncillas = []
                                    redsvolumen = []
                                    redscostes = []
                                    diametrillos = []
                                    datostodos = []
                                    # the new cost is calculated after changing the roll
                                    for rodillito in soluciones[posicionmaximo]:
                                        posicionescil2 = list(
                                            filter(lambda p: p.cod_interno == rodillito.cod_interno,
                                                   posicionesgeneradas))

                                        #if it is the roll that has been changed the data is picked from reductions and costs
                                        if cuentacajas == poscajaarray + cajaquemejora:
                                            redss = datoreduccion
                                            reduccioncillas.append(redss)
                                            datostodos.append(datocilindrosol)

                                            redss2 = datoreduccionvol
                                            redss3 = datocoste
                                            redsvolumen.append(redss2)
                                            redscostes.append(redss3)
                                        else:
                                            #if it is one of the others it is picked from the stored for the output
                                            redss = reduccionesagentes[posicionmaximo]
                                            redss = redss[len(redss) - 1][cuentacajas]
                                            redss2 = reduccionesvolumenagentes[posicionmaximo]
                                            redss2 = redss2[len(redss2) - 1][cuentacajas]
                                            redss3 = redss2 * rodillito.coste
                                            datinos = datoscilindroagentes[posicionmaximo]
                                            datinos = datinos[len(datinos) - 1][cuentacajas]
                                            datostodos.append(datinos)
                                            reduccioncillas.append(redss)
                                            redsvolumen.append(redss2)
                                            redscostes.append(redss3)
                                        #the diameters of the rolls assembled on each of the stands are stored, the costs are accumulated
                                        diametrillos.append(rodillito.diam_actual)
                                        acumuladocostes = acumuladocostes + redss3
                                        acumuladocostesdiametros = acumuladocostesdiametros + redss

                                        cuentacajas = cuentacajas + 1
                                    #data for the output
                                    datoscilindroagentes[posicionmaximo].append(datostodos)
                                    diametroagentes[posicionmaximo].append(diametrillos)
                                    reduccionesagentes[posicionmaximo].append(reduccioncillas)
                                    reduccionesvolumenagentes[posicionmaximo].append(redsvolumen)
                                    reduccionestotalesvolumenagentes[posicionmaximo].append(sum(redsvolumen))
                                    costestotalesagentes[posicionmaximo].append(acumuladocostes)
                                    costesagentes[posicionmaximo].append(redscostes)
                                    mediacostes[posicionmaximo].append(stats.mean(redscostes))
                                    desviacioncostes[posicionmaximo].append(stats.pstdev(redscostes))
                                    mediadiametros[posicionmaximo].append(stats.mean(diametrillos))
                                    mediareducciones[posicionmaximo].append(stats.mean(reduccioncillas))
                                    mediareduccionvolumen[posicionmaximo].append(stats.mean(redsvolumen))
                                    desviaciontipicadiametros[posicionmaximo].append(stats.pstdev(diametrillos))
                                    desviaciontipicareducciones[posicionmaximo].append(stats.pstdev(reduccioncillas))
                                    desviaciontipicareduccionesvolumen[posicionmaximo].append(stats.pstdev(redsvolumen))
                                    valordespues = acumuladocostes
                                    print("Agente: " + str(posicionmaximo) + " coste total: " + str(acumuladocostes))
                                    if abs(valorantes - valormejora - valordespues) > 0.1:
                                        diferencia = valorantes - valormejora - valordespues
                                        print("aqui")
                                    else:
                                        print(str(valorantes - valormejora - valordespues))
                        poscajaarray = poscajaarray + 1
                    cuentavueltas = cuentavueltas + 1
                    #it is determined the agent that has the best solution of this round, that which less reduces the cost of the roll
                    minimareduccion = 0
                    solucionmejor = []
                    solucionespositionsmejor = []
                    # loop through the agents
                    for element in range(10):
                        cadenita = cadenita + "{\"Agente\":" + str(element) + ",\"valoresdiametros\":" + str(
                            diametroagentes[element]) + ","
                        cadenita = cadenita + "\"datosrodillos\":" + json.dumps(datoscilindroagentes[element]) + ","
                        cadenita = cadenita + "\"costes\":" + str(costestotalesagentes[element]) + ","
                        cadenita = cadenita + "\"costesporrodillo\":" + str(costesagentes[element]) + ","
                        cadenita = cadenita + "\"valoresreducciones\":" + str(reduccionesagentes[element]) + ","
                        cadenita = cadenita + "\"valoresreduccionesvol\":" + str(
                            reduccionesvolumenagentes[element]) + ","
                        cadenita = cadenita + "\"totalreduccionvol\":" + str(
                            reduccionestotalesvolumenagentes[element]) + ","
                        cadenita = cadenita + "\"mediadiametros\":" + str(mediadiametros[element]) + ","
                        cadenita = cadenita + "\"mediareducciones\":" + str(mediareducciones[element]) + ","
                        cadenita = cadenita + "\"mediareduccionesvol\":" + str(mediareduccionvolumen[element]) + ","
                        cadenita = cadenita + "\"mediacostes\":" + str(mediacostes[element]) + ","
                        cadenita = cadenita + "\"desvdiametros\":" + str(desviaciontipicadiametros[element]) + ","
                        cadenita = cadenita + "\"desvreducciones\":" + str(desviaciontipicareducciones[element]) + ","
                        cadenita = cadenita + "\"desvcostes\":" + str(desviacioncostes[element]) + ","
                        cadenita = cadenita + "\"desvreduccionesvol\":" + str(
                            desviaciontipicareduccionesvolumen[element]) + "},"
                    cadenita = cadenita[:len(cadenita) - 1]
                    cadenita = cadenita + "],"
                    ganadorvuelta = -1
                    #loop through the agents
                    for element in range(10):
                        # print("solucion " + str(element) + "\n")
                        reduccionmm = 0
                        reduccionvol = 0
                        #it is calculated the sum of the cost for each of the rolls of the solution
                        for element2 in range(len(trabajo.cajas)):

                            posicionescil = list(
                                filter(lambda p: p.cod_interno == soluciones[element][element2].cod_interno,
                                       posicionesgeneradas))

                            reduccion = reduccionesvolumenagentes[element][
                                len(reduccionesvolumenagentes[element]) - 1]
                            reduccion = reduccion[element2] * soluciones[element][element2].coste
                            reduccionvol = reduccionvol + reduccion
                        #if the reduction of this agent for this round is better than the current one, it is selected this as the best
                        if reduccionvol < minimareduccion or minimareduccion == 0:
                            minimareduccion = reduccionvol
                            solucionmejor = soluciones[element]
                            solucionespositionsmejor = solucionespositions[element]
                            ganadorvuelta = element
                    cadenita = cadenita + "\"ganadorvuelta\":" + str(ganadorvuelta) + ","
                    cadenita = cadenita + "\"costeganador\":" + str(minimareduccion) + "},"

                    #the reductions are updated for the total of rounds
                    reduccionprevia = reduccionnueva
                    reduccionnueva = minimareduccion
                    #if it improves it is updated
                    if reduccionnueva < reduccionprevia or len(solucionfinal) == 0:
                        solucionfinal = solucionmejor
                        solucionespositionsfinal = solucionespositionsmejor
                    print("Reducciones " + str(reduccionnueva) + " " + str(reduccionprevia))
                    if (reduccionprevia == -2):
                        reduccionprevia = reduccionnueva + 0.2
            else:
                # when the number of solutions is not reached, terminar is True in order to end the execution
                print("No se ha alcanzado el numero de soluciones")
                terminar = True
            ejecuciontrabajo = ejecuciontrabajo + 1

            if not terminar:
                tfinal = time.time()
                cadenita = cadenita[:len(cadenita) - 1]
                cadenita = cadenita + "],\"tiempo\":" + str(tfinal - tinicial) + ","
                print("Trabajo " + str(indicetrabajo) + "\n")
                # for the final solution, it is calculated the diameter reduction, volume reduction and cost reduction, it is shown and
                # the positions of the rolls are marked as used indicating the rolled tons and the diameter after the reconditioning
                # when every position has been marked as used, then both are marked as active, the tons put to 0 and the reconditioning diameter (the one it is indicated
                # for each position once it rolls) to the mimimum of both
                dic = {}
                reduccionesrodillospasada = []
                for element2 in range(len(solucionfinal)):
                    posicionescil2 = list(
                        filter(lambda p: p.cod_interno == solucionfinal[element2].cod_interno,
                               posicionesgeneradas))
                    redss = calculoreduccioncondurezacalidad(solucionfinal[element2], posicionescil2,
                                                             solucionespositionsfinal[element2],
                                                             sum(trabajo.toneladaslaminadas),
                                                             geometrias, calidades, modelito, trabajo)
                    reduccio = (1 / 4) * math.pi * ((solucionfinal[element2].diam_actual) ** 2) * solucionfinal[
                        element2].tabla - (1 / 4) * math.pi * ((solucionfinal[element2].diam_actual - redss) ** 2) * \
                               solucionfinal[element2].tabla
                    cost = reduccio * solucionfinal[element2].coste
                    print("Caja " + str(16 + element2) + " " + str(solucionfinal[element2].cod_interno) + " " + str(
                        solucionespositionsfinal[element2].cod_posicion) + " " + str(redss) + " " + str(
                        reduccio) + " " + str(
                        cost) + "\n")
                    posicionesgeneradas = list(filter(lambda x: not (
                            x.cod_interno == solucionespositionsfinal[element2].cod_interno and x.cod_posicion ==
                            solucionespositionsfinal[element2].cod_posicion), posicionesgeneradas))

                    solucionespositionsfinal[element2].toneladas = sum(trabajo.toneladaslaminadas)
                    solucionespositionsfinal[element2].cod_estado_posicion = 3
                    solucionespositionsfinal[element2].diam_rectif = solucionfinal[element2].diam_actual - redss
                    posicionesgeneradas.append(solucionespositionsfinal[element2])

                    #the probability of breaking is simulated, provided the hardness of the rolled material
                    probruptura = random.randint(0, 9999)
                    umbral = 9999 - max(trabajo.calidadmaterial)
                    if probruptura > umbral:
                        cilindrosgenerados = list(
                            filter(lambda x: x.cod_interno != solucionfinal[element2].cod_interno, cilindrosgenerados))
                        solucionfinal[element2].cod_estado = 3
                        cilindrosgenerados.append(solucionfinal[element2])
                        dic[str(trabajo.cajas[element2].numcaja)] = 1
                    else:
                        dic[str(trabajo.cajas[element2].numcaja)] = 0

                    posicionescilindrin = list(filter(lambda p: p.cod_interno == solucionespositionsfinal[
                        element2].cod_interno and p.cod_estado_posicion == 1, posicionesgeneradas))
                    #if every position has rolled and the roll is not broken
                    if len(posicionescilindrin) == 0 and solucionfinal[element2].cod_estado == 1:
                        posicionescilindrin2 = list(filter(lambda p: p.cod_interno == solucionespositionsfinal[
                            element2].cod_interno and p.cod_estado_posicion == 3, posicionesgeneradas))
                        minimo = min([o.diam_rectif for o in posicionescilindrin2])
                        for elementin in posicionescilindrin2:
                            posicionesgeneradas.remove(elementin)
                            elementin.cod_estado_posicion = 1
                            elementin.toneladas = 0
                            posicionesgeneradas.append(elementin)
                        cilindrosgenerados = list(
                            filter(lambda x: x.cod_interno != solucionfinal[element2].cod_interno, cilindrosgenerados))
                        reduccionesrodillospasada.append(solucionfinal[element2].diam_actual - minimo)
                        solucionfinal[element2].diam_actual = minimo


                        cilindrosgenerados.append(solucionfinal[element2])
                    else:
                        reduccionesrodillospasada.append(0)
                reduccionespasadas.append(reduccionesrodillospasada)
                #auxiliary dictionary for the broken rolls
                rotosac2 = {}
                #loop through the keys of the dictionary where the broken in the current job are
                for clave in dic.keys():
                    #if there were previous jobs and previous broken rolls
                    if len(rotosac) > 0:
                        #check if there were broken rolls for that stand in previous jobs
                        if clave in rotosac[len(rotosac) - 1]:
                            #if there were, they are accumulated to the possible broken ones of the current job
                            rotosac2[clave] = rotosac[len(rotosac) - 1][clave] + dic[clave]
                        else:
                            #if there were not, the broken ones in this job are added
                            rotosac2[clave] = dic[clave]
                    else:
                        # if there were not previous broken rolls
                        rotosac2[clave] = dic[clave]
                #now the dictionary is added to the array
                rotosac.append(rotosac2.copy())
                dic['dureza'] = max(trabajo.calidadmaterial)
                rotostc.append(dic.copy())
                cadenita = cadenita + "\"rotostotal\":["
                for element in rotosac2.keys():
                    cadenita = cadenita + "{\"" + str(element) + "\":" + str(dic[element]) + "},"
                cadenita = cadenita[:len(cadenita) - 1]
                cadenita = cadenita + "]" + ","

                cadenita = cadenita + "\"rotostrabajo\":["
                for element in dic.keys():
                    cadenita = cadenita + "{\"" + str(element) + "\":" + str(dic[element]) + "},"
                cadenita = cadenita[:len(cadenita) - 1]
                cadenita = cadenita + "]"
                cadenita = cadenita + ",\"diametrosmediosporcajas\":" + str(diametrosiniciales) + "},"
                #cadenita = cadenita + "\"cantidadesmediasporcajas\":" + str(cantidadcompatibles) + ","
                #cadenita = cadenita + "\"reduccionesporcajas\":" + str(reduccionespasadas) + "},"

                indicetrabajo = indicetrabajo + 1
                print("acaba")

                cadena = "["
                for element in cilindrosgenerados:
                    cadena = cadena + Cilindros2Encoder().encode(element) + ","
                cadena = cadena[:len(cadena) - 1]
                cadenaconjuntonuevo = "{\"Cilindros\":" + cadena + "],\"Posiciones\":["
                cadena = "{\"iteracion\":" + str(-1) + ",\"trabajo\":" + str(
                    -1) + ",\"Cilindros\":" + cadena + "],\"Posiciones\":["

                for element in posicionesgeneradas:
                    cadena = cadena + PosicionesosEncoder().encode(element) + ","
                    cadenaconjuntonuevo = cadenaconjuntonuevo + PosicionesosEncoder().encode(element) + ","
                cadena = cadena[:len(cadena) - 1]
                cadenaconjuntonuevo = cadenaconjuntonuevo[:len(cadenaconjuntonuevo) - 1]
                cadena = cadena + "]},"
                cadenaconjuntonuevo = cadenaconjuntonuevo + "]}"
                fhand = open('conjuntoalmacenadointerfaz.json', 'w')
                fhand.write(cadenaconjuntonuevo)
                fhand.close()



            else:
                if not yaescrito:
                    cadenita = cadenita + "{\"vuelta\":" + str(cuentavueltas) + "," + "\"valores\": ["
                    cadenita = cadenita + "],\"ganadorvuelta\":" + str(-1) + ",\"costeganador\":" + str(
                        -1) + "}],\"tiempo\":" + str(
                        time.time() - tinicial) + ",\"rotostotal\":[],\"rotostrabajo\":[]}]}"
                    fhand = open('salidaparagraficasnueva' + str(histoelement) + '.json', 'a')
                    fhand.write(cadenita)
                    fhand.close()
                    yaescrito = True
                    # sys.exit()
        if not terminar:
            cadenita = cadenita[:len(cadenita) - 1]
            cadenita = cadenita + "]}"
            fhand = open('salidaparagraficasnueva' + str(histoelement) + '.json', 'a')
            fhand.write(cadenita)
            fhand.close()