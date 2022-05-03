import json
from json import JSONEncoder
import os
from operator import attrgetter
import random
from func_timeout import func_timeout, FunctionTimedOut
import numpy as np
import decimal
from pade.core.agent import Agent
import copy
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message, start_loop, call_later
import subprocess
from collections import Counter, defaultdict
from pade.behaviours.protocols import TimedBehaviour
import os.path as path
import time
from os import remove
from os import rename
import psutil
from psutil import process_iter
from signal import SIGTERM # or SIGKILL



#function that calculates the mode
def moda(datos):
    repeticiones = 0

    for i in datos:
        n = datos.count(i)
        if n > repeticiones:
            repeticiones = n

    moda = [ ]

    for i in datos:
        n = datos.count(i)
        if n == repeticiones and i not in moda:
            moda.append(i)

    if len(moda) != len(datos):
        return moda
    else:
        return [ ]


#classes that contain the elements of the json
#Convert a Position object to JSON
class PosicionesosEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Position):
            return object.__dict__
        else:
            # call base class implementation which takes care of
            # raising exceptions for unsupported types
            return json.JSONEncoder.default(self, object)

#Converts a Roll object to JSON
class CilindrosEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Roll):
            return object.__dict__
        else:
            # call base class implementation which takes care of
            # raising exceptions for unsupported types
            return json.JSONEncoder.default(self, object)

#Converts constraints objects to JSON
class RestriccionesEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, Restricciones):
            return object.__dict__
        else:
            # call base class implementation which takes care of
            # raising exceptions for unsupported types
            return json.JSONEncoder.default(self, object)


#Converts a RollSolucion object to JSON
class CilindrosSolucionEncoder(JSONEncoder):
    def default(self, object):
        if isinstance(object, RollSolucion):
            return object.__dict__
        else:
            # call base class implementation which takes care of
            # raising exceptions for unsupported types
            return json.JSONEncoder.default(self, object)

#Roll read from the configuration file
class Roll:
    def __init__(self, cod_interno, diam_inicial, diam_final, diam_actual, cod_estado, geometria,numposiciones):
        self.cod_interno = cod_interno
        self.diam_inicial = diam_inicial
        self.diam_final = diam_final
        self.diam_actual = diam_actual
        self.cod_estado = cod_estado
        self.geometria = geometria
        self.numposiciones = numposiciones

#Result of the rolls used for each job indicating its internal code, index of the job as well as the position, vein and stand they use
class RollSolucion:
    def __init__(self, cod_interno, pos, trabajo, vena, caja, iteracion):
        self.cod_interno = cod_interno
        self.pos = pos
        self.trabajo = trabajo
        self.vena = vena
        self.caja = caja
        self.iteracion = iteracion

#Positions read from the configuration file
class Position:
    def __init__(self, cod_interno, cod_posicion, num_plano_tallado, cod_estado_posicion, toneladas, diam_rectif,numposiciones):
        self.cod_interno = cod_interno
        self.cod_posicion = cod_posicion
        self.num_plano_tallado = num_plano_tallado
        self.cod_estado_posicion = cod_estado_posicion
        self.toneladas = toneladas
        self.diam_rectif = diam_rectif
        self.numposiciones = numposiciones


#Shapes read from the configuration file
class Carvings:
    def __init__(self, num_plano_tallado, descripcion, cod_caja):
        self.num_plano_tallado = num_plano_tallado
        self.descripcion = descripcion
        self.cod_caja = cod_caja


#Possible states of each position, it is read from the configuration file
class PositionStates:
    def __init__(self, cod_estado_posicion, estado):
        self.cod_estado_posicion = cod_estado_posicion
        self.estado = estado


#Possible states of the rolls, it is read from the configuration file
class RollStates:
    def __init__(self, cod_estado, estado):
        self.cod_estado = cod_estado
        self.estado = estado


#Possible geometries of the rolls, it is read from the configuration file
class Geometrias:
    def __init__(self, cod_caja, geometria, cod_geometria):
        self.cod_caja = cod_caja
        self.geometria = geometria
        self.cod_geometria = cod_geometria


#constraints, the set changes for each job. It is incated the two stands involved in the constraint, the quantity, the factor and the type (read from the configuration file)
class Restricciones:
    def __init__(self, caja1, caja2, cantidad, factor, tipo):
        self.caja1 = caja1
        self.caja2 = caja2
        self.cantidad = cantidad
        self.factor = factor
        self.tipo = tipo


#Jobs read from the configuration file, the stands involved, the hardness of the material and the tons to roll are indicated
class Trabajos:
    def __init__(self, toneladaslaminadas, calidadmaterial, cajas):
        self.toneladaslaminadas = toneladaslaminadas
        self.calidadmaterial = calidadmaterial
        self.cajas = cajas


#Determines the types of rolls that are gonna be created
class TiposRodillosAGenerar:
    def __init__(self, cantidad, geometria, tallado, posiciones, diam_inicial, diam_final, diam_actual):
        self.cantidad = cantidad
        self.geometria = geometria
        self.tallado = tallado
        self.posiciones = posiciones
        self.diam_inicial = diam_inicial
        self.diam_final = diam_final
        self.diam_actual = diam_actual

#Stands involved in a particular job, indicating its number, geometry and shape
class CajasTrabajos:
    def __init__(self, numcaja, geometria, tallado):
        self.numcaja = numcaja
        self.geometria = geometria
        self.tallado = tallado

#Compatible rolls with a stand of a job, it is indicated the set of compatible rolls and the set of compatible positions separately
class CilindrosCompatibles:
    def __init__(self, caja, compatibles, positions):
        self.caja = caja
        self.compatibles = compatibles
        self.positions = positions


#Compatible rolls it is indicated the set of rolls and the set of positions
class CilindrosCompatiblesCaja:
    def __init__(self, compatibles, positions):
        self.compatibles = compatibles
        self.positions = positions


#it is indicated for each stand geometry and shape the compatible rolls to buy
class CilindrosCompatiblesComprar:
    def __init__(self, caja, compatibles, geometria, tallado):
        self.caja = caja
        self.compatibles = compatibles
        self.geometria = geometria
        self.tallado = tallado

#Relation among the grade of hardness and the reduction suffered, from the configuration file
class DurezaDesgaste:
    def __init__(self, dureza, desgaste):
        self.dureza = dureza
        self.desgaste = desgaste


#if there is a solution for a job, this is saved in sample.json, rolls valid for that job (two veins simultaneously)
def process_solution(solucion, solucion2, solucion3, solucion4):
    a = solucionesencontradas
    Cilindros = solucion + solucion2 + solucion3 + solucion4
    cadena = "["
    for element in Cilindros:
        cadena = cadena + CilindrosEncoder().encode(element) + ","
    cadena = cadena[ :len(cadena) - 1 ]
    cadena = "{\"Cilindros\":" + cadena + "]}"
    fhand = open('sample.json', 'w')
    fhand.write(cadena)
    fhand.close()

#if there is a solution for a job, this is saved in sample.json, rolls valid for a vein of that job
def process_solutionvena(solucion, solucion2):
    a = solucionesencontradas
    Cilindros = solucion + solucion2
    cadena = "["
    for element in Cilindros:
        cadena = cadena + CilindrosEncoder().encode(element) + ","
    cadena = cadena[ :len(cadena) - 1 ]
    cadena = "{\"Cilindros\":" + cadena + "]}"
    fhand = open('sample.json', 'w')
    fhand.write(cadena)
    fhand.close()

#function that does the backtracking algorithm in each of the veins of the rolling mill
def backtrackporvenas(solucion, solucion2, solucion3, solucion4, caja, comp, restricciones):
    #do the backtracking in one of the veins
    backtrackvena(solucion,solucion2,caja, comp, restricciones)
    rodillos=[]
    elementoselegidos=[]
    #read the solution
    with open('sample.json', 'r') as openfile:
        # Reading from json file
        datos = json.load(openfile)
        for p in datos['Cilindros']:
            elementoselegidos.append(p['cod_interno'])
            rodillos.append(
                Roll(p['cod_interno'], p['diam_inicial'], p['diam_final'], p['diam_actual'],
                     p['cod_estado'],
                     p['geometria'],p['numposiciones']))
    cadena = "{\"Cilindros\":[]}"
    fhand = open('sample.json', 'w')
    fhand.write(cadena)
    fhand.close()
    #if a solution is found for that vein
    if (len(elementoselegidos)>0):
        #remove the rolls already used
        for i in comp:
            for j in i.compatibles:
                if j.cod_interno in elementoselegidos:
                    i.compatibles.remove(j)
        caja = 0
        global solucionesencontradas
        solucionesencontradas = False
        #do the backtracking to the other vein
        backtrackvena(solucion3,solucion4,caja,comp,restricciones)
        #read the solution
        with open('sample.json', 'r') as openfile:
            # Reading from json file
            datos = json.load(openfile)
            for p in datos['Cilindros']:
                rodillos.append(
                    Roll(p['cod_interno'], p['diam_inicial'], p['diam_final'], p['diam_actual'],
                         p['cod_estado'],
                         p['geometria'],p['numposiciones']))
        #if a solution has been found write the solution to file
        if len(rodillos) == 56:
            cadena = "["
            for element in rodillos:
                cadena = cadena + CilindrosEncoder().encode(element) + ","
            cadena = cadena[:len(cadena) - 1]
            cadena = "{\"Cilindros\":" + cadena + "]}"
            fhand = open('sample.json', 'w')
            fhand.write(cadena)
            fhand.close()
        else:
            #no solution has been found
            print("No hay solucion")
            cadena = "{\"Cilindros\":[]}"
            fhand = open('sample.json', 'w')
            fhand.write(cadena)
            fhand.close()
    else:
        #No solution is found
        print("No hay solucion")

#function that does the backtracking to a vein of the rolling mill
def backtrackvena(solucion, solucion2, caja, comp, restricciones):
    global solucionesencontradas
    a = solucionesencontradas
    # Si la solucion del trabajo no se ha encontrado todavia
    #if the solution of the job has not been found yet
    if not a:
        #if it is a solution
        if is_a_solutionvena(solucion, solucion2, caja, restricciones):
            #indicate solution found
            solucionesencontradas = True
            #Process, that is, store in sample.json
            process_solutionvena(solucion, solucion2)
        else:
            #if it is not a solution
            #if the stand is less than 14, the considered stands are from 16 to 29, 14 in total
            if caja < len(solucion):
                #if the solution until now is valid
                if is_validvena(solucion, solucion2, caja, restricciones):
                    #Determine the possible candidates for the next stand
                    # Determinar los posibles candidatos para la siguiente caja
                    ncandidates = construct_candidatesvena(solucion, solucion2, caja, comp,
                                                       restricciones)
                    #If the number of candidates is not empty
                    if ncandidates is not None:
                        #The positions and rolls compatibles are obtained
                        posiciones = ncandidates.positions
                        ncandidates = ncandidates.compatibles
                        if len(ncandidates) >= 4:
                            #if there are more than 4 candidates move forward to the next stand
                            caja = caja + 1
                            filtered_compatibles = [ ]
                            filtered_compatibles2 = [ ]
                            #The candidates for each of the members of the pairs and the veins are processed
                            i = 0
                            while i < min(len(ncandidates),10) and not solucionesencontradas:
                                solucion[ caja - 1 ] = ncandidates[ i ]
                                #For the next part of the pair the rolls which have the same diameter are filtered removing the actual one
                                filtered_compatibles = []
                                if (ncandidates[i].cod_interno%2==0):
                                    filtered_compatibles = list(filter(
                                        lambda x: x.cod_interno == ncandidates[ i ].cod_interno + 1, ncandidates))
                                else:
                                    filtered_compatibles = list(filter(
                                        lambda x: x.cod_interno == ncandidates[i].cod_interno - 1, ncandidates))
                                if len(filtered_compatibles)>0:
                                    solucion2[ caja - 1 ] = filtered_compatibles[ 0 ]
                                    if caja <= len(solucion) and not solucionesencontradas:
                                        #The backtracking continues while the stand is smaller than the last one and the solution has not been found
                                        backtrackvena(solucion, solucion2, caja, comp,
                                                  restricciones)
                                i = i + 1


#it is determined if it is a solution, rolls from solucion and solucion2; solucion3 and solucion4 must have equal diameter being the position in the array the same
#and diameter constraints must meet among solucion and solucion3 respectively. solucion2 and solucion4 are not checked as its diameters are the same
def is_a_solution(solucion, solucion2, solucion3, solucion4, caja, restricciones):
    if caja == len(solucion):
        for i in range(caja):
            if solucion[ i ].diam_actual != solucion2[ i ].diam_actual:
                return False
            if solucion3[ i ].diam_actual != solucion4[ i ].diam_actual:
                return False
        cajas = list(range(16, 16 + caja))
        for element in restricciones:
            if element.caja2 in cajas and element.caja1 in cajas:
                if element.tipo == "+-":
                    if not (abs(solucion[ element.caja2 % 16 ].diam_actual - solucion[
                        element.caja1 % 16 ].diam_actual) / element.factor) < element.cantidad:
                        return False
                    if not (abs(solucion3[ element.caja2 % 16 ].diam_actual - solucion3[
                        element.caja1 % 16 ].diam_actual) / element.factor) < element.cantidad:
                        return False
                elif element.tipo == "=":
                    if not ((solucion[ element.caja2 % 16 ].diam_actual - solucion[
                        element.caja1 % 16 ].diam_actual) / element.factor) == element.cantidad:
                        return False
                    if not ((solucion3[ element.caja2 % 16 ].diam_actual - solucion3[
                        element.caja1 % 16 ].diam_actual) / element.factor) == element.cantidad:
                        return False
        #it is checked whether the same roll is used twice
        #in case this happens, the solution is not valid
        prueba = solucion + solucion2 + solucion3 + solucion4
        for cilin in prueba:
            c = sum(cilindro.cod_interno == cilin.cod_interno for cilindro in prueba)
            if (c > 1):
                return False
        print("solucion encontrada")
        return True
    else:
        return False


#it is determined if it is a solution, rolls from solucion and solucion2must have equal diameter being the position in the array the same
#and diameter constraints must meet among solucion . solucion2 is not checked as its diameters are the same
def is_a_solutionvena(solucion, solucion2, caja, restricciones):
    if caja == len(solucion):
        for i in range(caja):
            if solucion[ i ].diam_actual != solucion2[ i ].diam_actual:
                return False

        cajas = list(range(16, 16 + caja))
        for element in restricciones:
            if element.caja2 in cajas and element.caja1 in cajas:
                if element.tipo == "+-":
                    if not (abs(solucion[ element.caja2 % 16 ].diam_actual - solucion[
                        element.caja1 % 16 ].diam_actual) / element.factor) < element.cantidad:
                        return False
                elif element.tipo == "=":
                    if not ((solucion[ element.caja2 % 16 ].diam_actual - solucion[
                        element.caja1 % 16 ].diam_actual) / element.factor) == element.cantidad:
                        return False

        # it is checked whether the same roll is used twice
        # in case this happens, the solution is not valid
        prueba = solucion + solucion2
        for cilin in prueba:
            c = sum(cilindro.cod_interno == cilin.cod_interno for cilindro in prueba)
            if (c > 1):
                return False
        print("solucion vena encontrada")
        return True
    else:
        return False

#It is determined wheter solucion and solucion2 is a solution for that vein given the constraints
def is_a_solution_venaabt(solucion, solucion2, restricciones):
        for i in range(len(solucion)):
            if solucion[ i ].diam_actual != solucion2[ i ].diam_actual:
                return False
        cajas = list(range(16, 16 + len(solucion)))
        for element in restricciones:
            if element.caja2 in cajas and element.caja1 in cajas:
                if element.tipo == "+-":
                    if not (abs(solucion[ element.caja2 % 16 ].diam_actual - solucion[
                        element.caja1 % 16 ].diam_actual) / element.factor) < element.cantidad:
                        return False
                elif element.tipo == "=":
                    if not ((solucion[ element.caja2 % 16 ].diam_actual - solucion[
                        element.caja1 % 16 ].diam_actual) / element.factor) == element.cantidad:
                        return False
        #It is checked wheter the same roll is used twice
        #In case this happens, the solution is not valid
        prueba = solucion + solucion2
        for cilin in prueba:
            c = sum(cilindro.cod_interno == cilin.cod_interno for cilindro in prueba)
            if (c > 1):
                return False
        return True



#It is checked that the solution until now is valid
def is_valid(solucion, solucion2, solucion3, solucion4, caja, restricciones):
    #If the stand is 0 there are not elements in the solution yet
    if caja == 0:
        return True
    #If the stand is 1 it is checked that the diameters are equal in the same pair and there are no repeated rolls
    if caja == 1:
        prueba = [ ]
        for i in range(caja):
            prueba.append(solucion[ i ])
            prueba.append(solucion2[ i ])
            prueba.append(solucion3[ i ])
            prueba.append(solucion4[ i ])
            if solucion[ i ].diam_actual != solucion2[ i ].diam_actual:
                return False
            if solucion3[ i ].diam_actual != solucion4[ i ].diam_actual:
                return False
        #If the same roll is used twice the solution is not valid
        for cilin in prueba:
            c = sum(cilindro.cod_interno == cilin.cod_interno for cilindro in prueba)
            if (c > 1):
                return False
        return True
    #In other case, the diameter constraints are checked
    cajas = list(range(16, 16 + caja))
    for element in restricciones:
        if element.caja2 in cajas and element.caja1 in cajas:
            if element.tipo == "+-":
                if not (abs(solucion[ element.caja2 % 16 ].diam_actual - solucion[
                    element.caja1 % 16 ].diam_actual) / element.factor) < element.cantidad:
                    return False
                if not (abs(solucion3[ element.caja2 % 16 ].diam_actual - solucion3[
                    element.caja1 % 16 ].diam_actual) / element.factor) < element.cantidad:
                    return False
            elif element.tipo == "=":
                if not ((solucion[element.caja2 % 16].diam_actual - solucion[
                    element.caja1 % 16].diam_actual) / element.factor) == element.cantidad:
                    return False
                if not ((solucion3[element.caja2 % 16].diam_actual - solucion3[
                    element.caja1 % 16].diam_actual) / element.factor) == element.cantidad:
                    return False
    #Also it is checked that the diameters are equal in a pair and that there are no repeated rolls
    prueba = [ ]
    for i in range(caja):
        prueba.append(solucion[ i ])
        prueba.append(solucion2[ i ])
        prueba.append(solucion3[ i ])
        prueba.append(solucion4[ i ])
        if solucion[ i ].diam_actual != solucion2[ i ].diam_actual:
            return False
        if solucion3[ i ].diam_actual != solucion4[ i ].diam_actual:
            return False
    #If the same roll is used twice the solution is not valid
    for cilin in prueba:
        c = sum(cilindro.cod_interno == cilin.cod_interno for cilindro in prueba)
        if (c > 1):
            return False
    return True

#It is determined wheter solucion and solucion2 is a solution for that vein given the constraints and the stand
def is_validvena(solucion, solucion2, caja, restricciones):
    #if the stand is 0 there are no elements in the solution yet
    if caja == 0:
        return True
    #If the stand is 1 it is checked that the diameters are equal in the same pair and that there are no repeated rolls
    if caja == 1:
        prueba = [ ]
        for i in range(caja):
            prueba.append(solucion[ i ])
            prueba.append(solucion2[ i ])
            if solucion[ i ].diam_actual != solucion2[ i ].diam_actual:
                return False
        #If the same roll is used twice the solution is not valid
        for cilin in prueba:
            c = sum(cilindro.cod_interno == cilin.cod_interno for cilindro in prueba)
            if (c > 1):
                return False
        return True
    #In other case the diameter constraints are checked
    cajas = list(range(16, 16 + caja))
    for element in restricciones:
        if element.caja2 in cajas and element.caja1 in cajas:
            if element.tipo == "+-":
                if not (abs(solucion[ element.caja2 % 16 ].diam_actual - solucion[
                    element.caja1 % 16 ].diam_actual) / element.factor) < element.cantidad:
                    return False
            elif element.tipo == "=":
                if not ((solucion[ element.caja2 % 16 ].diam_actual - solucion[
                    element.caja1 % 16 ].diam_actual) / element.factor) == element.cantidad:
                    return False
    #Also it is checked that the diameters are equal in a pair and that there are no repeated rolls
    prueba = [ ]
    for i in range(caja):
        prueba.append(solucion[ i ])
        prueba.append(solucion2[ i ])
        if solucion[ i ].diam_actual != solucion2[ i ].diam_actual:
            return False
    #If the same roll is used twice in a solution, this is not valid
    for cilin in prueba:
        c = sum(cilindro.cod_interno == cilin.cod_interno for cilindro in prueba)
        if (c > 1):
            return False
    return True


#For each stand of both veins the candidates are obtained removing those that are already part of the solution
def construct_candidates(solucion, solucion2, solucion3, solucion4, caja, comp, restricciones):
    if (caja < len(comp)):
        retorno = [ ]
        pos = [ ]
        compatibles = [ ]
        conjunto = solucion + solucion2 + solucion3 + solucion4
        cont = 0
        for element in comp[ caja ].compatibles:
            if not element in conjunto:
                pos.append(comp[ caja ].positions[ cont ])
                compatibles.append(comp[ caja ].compatibles[ cont ])
            cont = cont + 1
        retorno = CilindrosCompatiblesCaja(compatibles, pos)
        return retorno
    else:
        return None

#For each stand of each of the veins the candidates are obtained removing those that are already part of the solution
def construct_candidatesvena(solucion, solucion2, caja, comp, restricciones):
    if (caja < len(comp)):
        retorno = [ ]
        pos = [ ]
        compatibles = [ ]
        conjunto = solucion + solucion2
        cont = 0
        for element in comp[ caja ].compatibles:
            if not element in conjunto:
                pos.append(comp[ caja ].positions[ cont ])
                compatibles.append(comp[ caja ].compatibles[ cont ])
            cont = cont + 1
        retorno = CilindrosCompatiblesCaja(compatibles, pos)
        return retorno
    else:
        return None

#function that calls the backtrack algorithm for the veins and measures the time it lasts in executing
def medirbacktrack (solucion,solucion2,solucion3,solucion4,caja,comp,restricciones):
    start_time = time.time()
    backtrackporvenas(solucion,solucion2,solucion3,solucion4,caja,comp,restricciones)
    elapsed_time = time.time()-start_time
    fhand = open('tiemposmedidos.json', 'a')
    fhand.write(str(elapsed_time)+",")
    fhand.close()
    print(str(elapsed_time))

#The rolls which have the geometry and shape equal to those of the stand of the job, which have a diameter that allows to roll the tons required
#that are active and that have an active position existing at least two with that diameter are obtained
#Then a random order is given to them in order that the result is not always the same
def candidatos(posiciontrabajo, durezadesgaste, cilindros):
    #The rolls compatible with each stand are filtered
    trabajo = trabajos[ posiciontrabajo ]
    cajastrabajo = [ ]
    cilcompatibles = [ ]
    cilsfinales = [ ]
    desgastetotal = [ ]

    for p in trabajo.cajas:
        cajastrabajo.append(CajasTrabajos(p.numcaja, p.geometria, p.tallado))
    indice = 0
    for elemento in cajastrabajo:
        cils = [ ]
        positions = [ ]
        toneladastotales = sum(trabajo.toneladaslaminadas)
        for elemento2 in cilindros:
            if elemento.geometria == elemento2.geometria and elemento2.cod_estado == 1:
                posicionescil = list(filter(lambda p: p.cod_interno == elemento2.cod_interno, posiciones))
                attrs = max([o.toneladas for o in posicionescil])
                for posicion in posicionescil:
                    attrs = max([attrs, posicion.toneladas+toneladastotales])
                    if posicion.num_plano_tallado == elemento.tallado and posicion.cod_interno == elemento2.cod_interno and posicion.cod_estado_posicion == 1:
                        geo = list(filter(lambda p: p.geometria == elemento2.geometria, geometrias))
                        coef0 = 5.284226
                        coef1 = - 0.00047862 * max([0, 228.34 - elemento2.diam_inicial])
                        coef2 = 0.0125193 * max([0,  elemento2.diam_inicial - 228.34])
                        coef3 = 0.2526212 * max([0, 20 - geo[0].cod_geometria])
                        coef4 = - 0.1769521 * max([0, geo[0].cod_geometria - 20])
                        coef5 = -5.837603 * pow(10,-5)* max([0, 55497 - attrs])
                        coef6 = 0.02159485 * max([0, attrs - 55497])
                        coef7 = 0.01568605 * max([0,540 - elemento2.diam_inicial]) * max([0,20 - geo[0].cod_geometria])
                        coef8 = -0.006458359 *max([0, elemento2.diam_inicial - 540]) * max([0,20 - geo[0].cod_geometria])
                        coef9 = -5.792337 * pow(10,-5) * max([0, elemento2.diam_inicial - 228.34]) * max([0, attrs - 55497])
                        coef10 = -1.224455 * pow(10,-7) * max([0, elemento2.diam_inicial - 228.34]) * max([0,55497 - attrs])
                        coef11 = 0.1414289 * max([0, 20 - geo[0].cod_geometria]) * max([0,posicion.num_plano_tallado - 425])
                        coef12 = 0.02109303 * max([0, 20 - geo[0].cod_geometria]) * max([0,425 - posicion.num_plano_tallado])
                        coef13 = -0.001316909 * max([0, 15 - geo[0].cod_geometria]) * max([0, attrs - 55497])
                        coef14 = - 0.003600006 * max([0, geo[0].cod_geometria - 15]) * max([0, attrs - 55497])
                        coef15 = -1.90485 * pow(10,-6)* max([0, 29 - geo[0].cod_geometria]) * max([0, 55497 - attrs])
                        coef16 = 9.154122 * pow(10,-6)*max([0, geo[0].cod_geometria - 29]) * max([0, 55497 - attrs])
                        coef17 = -0.001490068 * max([0, 540 - elemento2.diam_inicial]) * max([0, 20 - geo[0].cod_geometria]) * max([0, posicion.num_plano_tallado - 430])
                        coef18 = -0.0003063138 * max([0, 540 - elemento2.diam_inicial]) * max([0,20 - geo[0].cod_geometria]) * max([0, 430 - posicion.num_plano_tallado])
                        coef19 = 2.797927 * pow(10,-6) * max([0, elemento2.diam_inicial - 540]) * max([0, 20 - geo[0].cod_geometria]) * max([0,attrs - 51443])
                        coef20 = 3.788968 * pow(10,-8) * max([0, elemento2.diam_inicial -540]) * max([0, 20 - geo[0].cod_geometria]) * max([0, 51443 - attrs])
                        coef21 = + 1.786081e-05 * max(0,20 -geo[0].cod_geometria) * max(0,425 - posicion.num_plano_tallado) * max(0,attrs -57723)
                        margen = coef0+coef1+coef2+coef3+coef4+coef5+coef6+coef7+coef8+coef9+coef10+coef11+coef12+coef13+coef14+coef15+coef16+coef17+coef18+coef19+coef20+coef21
                        margen = margen/1000
                        decimal.getcontext().rounding = decimal.ROUND_CEILING
                        #the reduction of the diameter is calculated using a model based on the data from ten years of the rolls
                        margen = float(round(decimal.Decimal(str(margen*sum(
                            trabajos[ cont ].toneladaslaminadas))), ndigits=2))
                        if not elemento2 in cils and elemento2.diam_actual > elemento2.diam_final + margen:
                            cils.append(elemento2)
                            positions.append(posicion)
        indice = indice + 1
        cilcompatibles.append(CilindrosCompatibles(elemento.numcaja, cils, positions))
    for elemento in cilcompatibles:
        #it is determined how many rolls there are with the same diameter as the current one
        #there are only left those which at least have another one with the same diameter
        cantidades = [ ]
        cilscompute = [ ]
        posi = [ ]
        for cilin in range(len(elemento.compatibles)):
            c = sum(
                cilindro.diam_actual == elemento.compatibles[ cilin ].diam_actual for cilindro in elemento.compatibles)
            if c >= 2:
                cilscompute.append(elemento.compatibles[ cilin ])
                posi.append(elemento.positions[ cilin ])
            cantidades.append(c)
        cilstemp = [ ]
        positemp = [ ]
        for indice in range(len(cilscompute)):
            numeroAleatorio = random.randint(0, len(cilscompute) - 1)
            cilstemp.append(cilscompute[ numeroAleatorio ])
            positemp.append(posi[ numeroAleatorio ])
            cilscompute.remove(cilscompute[ numeroAleatorio ])
            posi.remove(posi[ numeroAleatorio ])
        cilscompute = cilstemp
        posi = positemp
        cilsfinales.append(CilindrosCompatibles(elemento.caja, cilscompute, posi))
    return cilsfinales

if __name__ == '__main__':
    #number of stands considered
    numerocajas = 14
    #determines if the solution has been found or not
    print("Use previously generated roll set")
    print("1 - No")
    print("2 - Yes")
    recarga = int(input("Your selection: "))
    solucionesencontradas = False
    #indicate the algorithm that is gonna be used
    print("Introduce the algorithm which will be used")
    print("1 - Backtracking")
    print("2 - ABT")
    print("3 - RL")
    #numero = int(input("Choice: "))
    numero = 2
    iteracion = 0
    fhand = open('cilindrosfinal.json', 'w')
    fhand.write("{\"iteracciones\":[")
    fhand.close()
    fhand = open('rectificados.json', 'w')
    fhand.write("{\"rectificados\":[")
    fhand.close()
    fhand = open('diametrosmedios.json', 'w')
    fhand.write("{\"diametrosmedios\":[")
    fhand.close()
    fhand = open('definitivostotales.json', 'w')
    fhand.write("{\"utilizados\":[")
    fhand.close()
    fhand = open('tiemposmedidos.json', 'w')
    fhand.write("{\"tiemposmedidos\":[")
    fhand.close()
    #reads the json
    durezadesgaste = [ ]
    cilindros = [ ]
    posiciones = [ ]
    tallados = [ ]
    estadosposicion = [ ]
    estados = [ ]
    geometrias = [ ]
    trabajos = [ ]
    restricciones = [ ]
    tiposRodillosAGenerar = [ ]
    cilindrosgenerados = [ ]
    posicionesgeneradas = [ ]
    tipos = [ ]
    #if it uses the previous roll set it is read from the file
    if recarga==2:
        with open('conjuntoalmacenado.json') as json_file:
            data = json.load(json_file)
            for p in data['Cilindros']:
                cilindrosgenerados.append(Roll(p['cod_interno'], p['diam_inicial'], p['diam_final'], p['diam_actual'],
                                     p['cod_estado'],
                                     p['geometria'],p['numposiciones']))
            for p in data['Posiciones']:
                posicionesgeneradas.append(Position(p['cod_interno'],p['cod_posicion'],p['num_plano_tallado'], p['cod_estado_posicion'], p['toneladas'], p['diam_rectif'],p['numposiciones']))
    #The data is loaded from the configuration file
    with open('cilindros.json') as json_file:
        data = json.load(json_file)
        for p in data[ 'TiposTrabajos' ]:
            tipos.append(CajasTrabajos(p[ 'caja' ], p[ 'geometria' ], p[ 'tallado' ]))
        for p in data[ 'tallado' ]:
            tallados.append(Carvings(p[ 'num_plano_tallado' ], p[ 'descripcion' ], p[ 'cod_caja' ]))
        for p in data[ 'TiposRodillosAGenerar' ]:
            tiposRodillosAGenerar.append(
                TiposRodillosAGenerar(p[ 'cantidad' ], p[ 'geometria' ], p[ 'tallado' ], p[ 'posiciones' ],
                                      p[ 'diam_inicial' ], p[ 'diam_final' ], p[ 'diam_actual' ]))
        diametro = 0
        #if it does not use the previous roll set a new roll set is generated and stored
        if recarga == 1:
            for element in range(0, len(tiposRodillosAGenerar)):
                #diametro = random.uniform(tiposRodillosAGenerar[ element ].diam_final,
                #                          tiposRodillosAGenerar[ element ].diam_inicial)
                diametro = tiposRodillosAGenerar[ element ].diam_inicial
                for element2 in range(0, int(tiposRodillosAGenerar[ element ].cantidad/2)):

                    for element3 in range(0, tiposRodillosAGenerar[ element ].posiciones):
                        print(str(element)+" "+str(tiposRodillosAGenerar[ element ].posiciones))
                        ultposicion = Position(element * 1000 + element2 *2, element3 + 1,
                                                            tiposRodillosAGenerar[ element ].tallado[ element3 ], 1, 0, 0,tiposRodillosAGenerar[element].posiciones)
                        posicionesgeneradas.append(ultposicion)
                        ultposicion = Position(element * 1000 + element2*2+1, element3 + 1,
                                               tiposRodillosAGenerar[element].tallado[element3], 1, 0, 0,tiposRodillosAGenerar[element].posiciones)
                        posicionesgeneradas.append(ultposicion)

                    valorinicial = (int(tiposRodillosAGenerar[ element ].diam_inicial * 100)/100
                                                                     - int(tiposRodillosAGenerar[ element ].diam_final *100)/100)*0.8 + int(tiposRodillosAGenerar[ element ].diam_final * 100)/100
                    vactual= random.randrange(int(valorinicial*100),int(tiposRodillosAGenerar[ element ].diam_inicial * 100))/100
                    valorcod = element2*2
                    elemento = Roll(element * 1000 + valorcod, tiposRodillosAGenerar[element].diam_inicial,
                                    tiposRodillosAGenerar[element].diam_final,
                                    vactual, 1,
                                    tiposRodillosAGenerar[element].geometria,
                                    tiposRodillosAGenerar[element].posiciones)
                    cilindrosgenerados.append(elemento)
                    elemento = Roll(element * 1000 + valorcod+1, tiposRodillosAGenerar[element].diam_inicial,
                                    tiposRodillosAGenerar[element].diam_final,
                                    vactual, 1,
                                    tiposRodillosAGenerar[element].geometria,
                                    tiposRodillosAGenerar[element].posiciones)
                    cilindrosgenerados.append(elemento)
        cilindros = cilindrosgenerados
        posiciones = posicionesgeneradas
        cadena = "["
        for element in cilindros:
            cadena = cadena + CilindrosEncoder().encode(element) + ","
        cadena = cadena[ :len(cadena) - 1 ]
        cadenaconjuntonuevo = "{\"Cilindros\":" + cadena + "],\"Posiciones\":["
        cadena = "{\"iteracion\":" + str(-1) + ",\"trabajo\":" + str(
            -1) + ",\"Cilindros\":" + cadena + "],\"Posiciones\":["

        for element in posiciones:
            cadena = cadena + PosicionesosEncoder().encode(element) + ","
            cadenaconjuntonuevo = cadenaconjuntonuevo + PosicionesosEncoder().encode(element) + ","
        cadena = cadena[ :len(cadena) - 1 ]
        cadenaconjuntonuevo = cadenaconjuntonuevo [ :len(cadenaconjuntonuevo) - 1]
        cadena = cadena + "]},"
        cadenaconjuntonuevo = cadenaconjuntonuevo + "]}"
        fhand = open('cilindrosfinal.json', 'a')
        fhand.write(cadena)
        fhand.close()
        fhand = open('conjuntoalmacenado.json', 'w')
        fhand.write(cadenaconjuntonuevo)
        fhand.close()
        for p in data[ 'estadosposicion' ]:
            estadosposicion.append(PositionStates(p[ 'cod_estado_posicion' ], p[ 'estado' ]))
        for p in data[ 'estadoscilindro' ]:
            estados.append(RollStates(p[ 'cod_estado' ], p[ 'estado' ]))
        for p in data[ 'geometria' ]:
            geometrias.append(Geometrias(p[ 'cod_caja' ], p[ 'geometria' ],p[ 'cod_geometria' ]))
        for p in data[ 'durezadesgaste' ]:
            durezadesgaste.append(DurezaDesgaste(p[ 'dureza' ], p[ 'desgaste' ]))
        for p in data[ 'TrabajosLaminacion' ]:
            cajas = [ ]
            for p2 in p[ 'cajas' ]:
                cajas.append(CajasTrabajos(p2[ 'caja' ], p2[ 'geometria' ], p2[ 'tallado' ]))
            trabajos.append(Trabajos(p[ 'toneladaslaminadas' ], p[ 'calidadmaterial' ], cajas))
    #for each of the jobs scheduled
    #number of times they are repeated
    numiteraciones = 10
    diametrossolucionestotal = []
    for iteracion in range(0, numiteraciones):
        for cont in range(len(trabajos)):
            rectificados = 0
            #select the active rolls with active positions, valid for each stand (geometry and shape and at least two of equal diameter) and they are shown
            miscompatibles = candidatos(cont, durezadesgaste, cilindros)
            #The solutions for each element of the pair are None at the beginning
            solucion = [None] * numerocajas
            solucion2 = [None] * numerocajas
            solucion3 = [None] * numerocajas
            solucion4 = [None] * numerocajas
            caja = 0
            #now depending on the algorithm selected an abt or backtracking is performed
            #The constraints are loaded for that job
            restricciones = [ ]
            for p in data[ 'restricciones' ][ cont ]:
                restricciones.append(Restricciones(p[ 'caja1' ], p[ 'caja2' ], p[ 'cantidad' ], p[ 'factor' ], p[ 'tipo' ]))
            cadena2 = ""
            sol = []
            if numero == 1:
                #backtracking is performed to obtain the solution
                medirbacktrack(solucion,solucion2,solucion3,solucion4,caja,miscompatibles,restricciones)
                #The solution is loaded from sample.json
                with open('sample.json', 'r') as openfile:
                    # Reading from json file
                    datos = json.load(openfile)
                    for p in datos['Cilindros']:
                        sol.append(
                            Roll(p['cod_interno'], p['diam_inicial'], p['diam_final'], p['diam_actual'],
                                 p['cod_estado'],
                                 p['geometria'],p['numposiciones']))
            elif numero == 2:
                #ABT is performed
                essolucion = False
                start_time = time.time()
                diametrossoluciones = []
                agents_per_process = numerocajas
                c = 0
                listaagentes=[]
                agents = list()
                vecinos=[]
                cilindrosporcaja={}
                #The list of compatible rolls for each stand of this job is generated
                aescribir="{\"Compatibles\":["
                for i in range(agents_per_process):
                    cadena = ""
                    for element in miscompatibles[i].compatibles:
                        cadena = cadena + CilindrosEncoder().encode(element) + ","
                    cadena = cadena[:len(cadena) - 1]
                    cadena = "{\"caja\":" + str(+16+i) + ",\"Cilindros\":[" + cadena + "]},"
                    aescribir = aescribir + cadena
                    diametrosabt = []
                #The list of constraints for this job are written as well
                cadena1 = ",\"Restricciones\":["
                for element in restricciones:
                    cadena1 = cadena1 + RestriccionesEncoder().encode(element) + ","
                cadena1 = cadena1[:len(cadena1) - 1]
                cadena1 =  cadena1 + "]}"
                aescribir = aescribir[:len(aescribir) - 1]
                aescribir = aescribir + "]"+cadena1
                fhand = open('datos14.json', 'w')
                fhand.write(aescribir)
                fhand.close()
                fhand = open('datos'+str(iteracion)+'_'+str(cont)+'.json', 'w')
                fhand.write(aescribir)
                fhand.close()
                #wait for the file to be written
                time.sleep(10)
                inicio_tiempos = time.time()
                #launches the abt algorithm for the first vein
                subprocess.Popen(['pade', 'start-runtime', '--username', 'as', '--password', 'pass', 'lanzar.py'])
                #When the file with the diameters and the codes of the rolls is created, the execution ends
                while not path.isfile('resultadoabt2.json'):
                    time.sleep(0.5)
                #The pade process is ended then
                os.system(
                    "taskkill /IM \"pade.exe\" /T /F")
                #wait until it ends
                time.sleep(10)
                fin_tiempos = time.time()-inicio_tiempos
                #time it lasts in performing the first vein
                print(str(fin_tiempos))
                parte0 = []
                parte1 = []
                error = False
                parte0total=[]
                parte1total=[]
                #The codes of the rolls used are read
                with open('resultadoabt2.json', 'r') as openfile:
                    # Reading from json file
                    datos = json.load(openfile)
                    for p in datos['Cajas']:
                        if(len(p['codigos'])!=2 or p['diametro']==0):
                            #a solution has not been found
                            error = True
                        else:
                            parte0.append(p['codigos'][0])
                            parte1.append(p['codigos'][1])
                #The file is renamed in order to execute the next vein
                rename(r'C:\Users\ana.valdeon\Music\trenprueba\resultadoabt2.json', r'C:\Users\ana.valdeon\Music\trenprueba\resultadoabt2_'+str(1)+'_'+str(iteracion)+'_'+str(cont)+'.json')
                Cilindros = []
                #if a solution was found
                if not error:
                    #we are left with the rolls with that codes
                    codigos0 = list(filter(lambda t: t.cod_interno in parte0, cilindrosgenerados))
                    codigos1 = list(filter(lambda t: t.cod_interno in parte1, cilindrosgenerados))
                    codigos0final = []
                    codigos1final = []
                    for element in parte0:
                        codigos0final.append(list(filter(lambda t: t.cod_interno == element, codigos0))[0])
                        parte0total.append(list(filter(lambda t: t.cod_interno == element, codigos0))[0])
                    for element in parte1:
                        codigos1final.append(list(filter(lambda t: t.cod_interno == element, codigos1))[0])
                        parte1total.append(list(filter(lambda t: t.cod_interno == element, codigos1))[0])
                    #check if it is a solution
                    essolucion = is_a_solution_venaabt(codigos0final,codigos1final,restricciones)
                    if essolucion:
                        #If it is a solution, the used rolls in the vein are removed from the compatible ones and the solution is written in order to execute lanzar.py once more
                        for i in range(0,numerocajas):
                            matches = list(filter(lambda x: miscompatibles[i].compatibles[x].cod_interno == parte0[i],
                                                  range(len(miscompatibles[i].compatibles))))
                            miscompatibles[i].compatibles.pop(matches[0])
                            matches = list(filter(lambda x: miscompatibles[i].compatibles[x].cod_interno == parte1[i],
                                                  range(len(miscompatibles[i].compatibles))))
                            miscompatibles[i].compatibles.pop(matches[0])
                            if i < (numerocajas-1) :
                                matches = list(
                                    filter(lambda x: miscompatibles[i+1].compatibles[x].cod_interno == parte0[i],
                                           range(len(miscompatibles[i+1].compatibles))))
                                if len(matches) > 0:
                                    miscompatibles[i+1].compatibles.pop(matches[0])
                                matches = list(
                                    filter(lambda x: miscompatibles[i+1].compatibles[x].cod_interno == parte1[i],
                                           range(len(miscompatibles[i+1].compatibles))))
                                if len(matches) > 0:
                                    miscompatibles[i+1].compatibles.pop(matches[0])
                        #Vuelvo a escribir a archivo los compatibles y las restricciones
                        #The compatible ones and the constraints are written to file
                        aescribir = "{\"Compatibles\":["
                        for i in range(agents_per_process):
                            cadena = ""
                            for element in miscompatibles[i].compatibles:
                                cadena = cadena + CilindrosEncoder().encode(element) + ","
                            cadena = cadena[:len(cadena) - 1]
                            cadena = "{\"caja\":" + str(+16 + i) + ",\"Cilindros\":[" + cadena + "]},"
                            aescribir = aescribir + cadena
                            diametrosabt = []
                        cadena1 = ",\"Restricciones\":["
                        for element in restricciones:
                            cadena1 = cadena1 + RestriccionesEncoder().encode(element) + ","
                        cadena1 = cadena1[:len(cadena1) - 1]
                        cadena1 = cadena1 + "]}"
                        aescribir = aescribir[:len(aescribir) - 1]
                        aescribir = aescribir + "]" + cadena1
                        fhand = open('datos14.json', 'w')
                        fhand.write(aescribir)
                        fhand.close()
                        time.sleep(30)
                        #wait until the file is created
                        #lanzar.py is executed for the other vein
                        subprocess.Popen(['pade', 'start-runtime', '--username', 'as', '--password', 'pass', 'lanzar.py'])
                        #wait to have the file with the solutions
                        while not path.isfile('resultadoabt2.json'):
                            time.sleep(10)
                        #once the file is written the process is ended
                        os.system(
                            "taskkill /IM \"pade.exe\" /T /F")
                        #wait to the end of the process
                        time.sleep(10)

                        #check if they are a solution
                        parte0 = []
                        parte1 = []
                        parte11total = []
                        parte12total = []
                        error = False
                        #read the codes of the rolls used
                        with open('resultadoabt2.json', 'r') as openfile:
                            # Reading from json file
                            datos = json.load(openfile)
                            for p in datos['Cajas']:
                                if(len(p['codigos'])!=2 or p['diametro']==0):
                                    error = True
                                else:
                                    parte0.append(p['codigos'][0])
                                    parte1.append(p['codigos'][1])
                        # rename the file
                        rename(r'C:\Users\ana.valdeon\Music\trenprueba\resultadoabt2.json',
                               r'C:\Users\ana.valdeon\Music\trenprueba\resultadoabt2_' + str(0) + '_' + str(
                                   iteracion) + '_' + str(cont) + '.json')
                        #if it is a solution
                        if not error:
                            #filter the rolls corresponding to that codes
                            codigos0 = list(filter(lambda t: t.cod_interno in parte0, cilindrosgenerados))
                            codigos1 = list(filter(lambda t: t.cod_interno in parte1, cilindrosgenerados))
                            codigos02final = []
                            codigos12final = []
                            for element in parte0:
                                codigos02final.append(list(filter(lambda t: t.cod_interno == element, codigos0))[0])
                                parte11total.append(list(filter(lambda t: t.cod_interno == element, codigos0))[0])
                            for element in parte1:
                                codigos12final.append(list(filter(lambda t: t.cod_interno == element, codigos1))[0])
                                parte12total.append(list(filter(lambda t: t.cod_interno == element, codigos1))[0])
                            #check if it is a solution
                            essolucion = is_a_solution_venaabt(codigos02final, codigos12final, restricciones)
                            Cilindros= []
                            if essolucion:
                                #Cilindros = codigos0final + codigos1final + codigos02final + codigos12final
                                Cilindros = parte0total + parte1total + parte11total + parte12total
                                sol = Cilindros
                cadena = "["
                for element in Cilindros:
                    cadena = cadena + CilindrosEncoder().encode(element) + ","
                cadena = cadena[:len(cadena) - 1]
                #write the solution to file
                cadena = "{\"Cilindros\":" + cadena + "]}"
                fhand = open('sample.json', 'w')
                fhand.write(cadena)
                fhand.close()
                elapsed_time = -1
                #calculate the time it lasts in finding a solution
                if essolucion:
                    elapsed_time = time.time() - start_time
                else:
                    elapsed_time = -1
                fhand = open('tiemposmedidos.json', 'a')
                fhand.write(str(elapsed_time) + ",")
                fhand.close()
                print(str(elapsed_time))
            else:
                print("It is not implemented yet")

            desgaste = 0


            #The diameter reduction due to the rolling of the job is applied to the rolls of the solution
            cadena = ""
            anters = [ ]
            cilindroSolucion = [ ]
            contapos = 0
            desgastetotal = [ ]
            cajastrabajo = [ ]
            margenes = [ ]
            for p in trabajos[ cont ].cajas:
                cajastrabajo.append(CajasTrabajos(p.numcaja, p.geometria, p.tallado))
            indice = 0
            #The diameter of the rolls and the state of the position is updated
            p = 0
            for k in range(len(sol)):
                #index of the roll belonging to the solution
                ind = [ i for i in range(len(cilindros)) if cilindros[ i ].cod_interno == sol[ k ].cod_interno ]
                #index of the positions of the roll belonging to the solution
                indpos = [ i for i in range(len(miscompatibles[ k % numerocajas ].positions)) if
                           miscompatibles[ k % numerocajas ].positions[ i ].cod_interno == sol[ k ].cod_interno ]
                #position used in the solution
                pos = miscompatibles[ k % numerocajas ].positions[ indpos[ 0 ] ]
                #code of the position used in the solution
                codposition = pos.cod_posicion
                #index of the position of the roll used in the solution
                indstatepos = [ i for i in range(len(posiciones)) if
                                posiciones[ i ].cod_interno == sol[ k ].cod_interno and codposition == posiciones[
                                    i ].cod_posicion ]
                for j in cilindros:
                    if sol[ k ].cod_interno == j.cod_interno:
                        toneladastotales = sum(trabajos[cont].toneladaslaminadas)
                        #The number of tons rolled is updated in the solution
                        # actualizo el numero de toneladas laminadas de la posicion
                        posiciones[ indstatepos[ 0 ] ].toneladas = posiciones[ indstatepos[ 0 ] ].toneladas + sum(
                            trabajos[ cont ].toneladaslaminadas)
                        posicionescil = list(filter(lambda p: p.cod_interno == j.cod_interno, posiciones))
                        attrs = max([ o.toneladas for o in posicionescil ])
                        attrs = max([ attrs, posiciones[ indstatepos[ 0 ] ].toneladas + toneladastotales ])
                        geo = list(filter(lambda p: p.geometria == j.geometria, geometrias))
                        coef0 = 5.284226
                        coef1 = - 0.00047862 * max([ 0, 228.34 - j.diam_inicial ])
                        coef2 = 0.0125193 * max([ 0, j.diam_inicial - 228.34 ])
                        coef3 = 0.2526212 * max([ 0, 20 - geo[ 0 ].cod_geometria ])
                        coef4 = - 0.1769521 * max([ 0, geo[ 0 ].cod_geometria - 20 ])
                        coef5 = -5.837603 * pow(10, -5) * max([ 0, 55497 - attrs ])
                        coef6 = 0.02159485 * max([ 0, attrs - 55497 ])
                        coef7 = 0.01568605 * max([ 0, 540 - j.diam_inicial ]) * max(
                            [ 0, 20 - geo[ 0 ].cod_geometria ])
                        coef8 = -0.006458359 * max([ 0, j.diam_inicial - 540 ]) * max(
                            [ 0, 20 - geo[ 0 ].cod_geometria ])
                        coef9 = -5.792337 * pow(10, -5) * max([ 0, j.diam_inicial - 228.34 ]) * max(
                            [ 0, attrs - 55497 ])
                        coef10 = -1.224455 * pow(10, -7) * max([ 0, j.diam_inicial - 228.34 ]) * max(
                            [ 0, 55497 - attrs ])
                        coef11 = 0.1414289 * max([ 0, 20 - geo[ 0 ].cod_geometria ]) * max(
                            [ 0, posiciones[ indstatepos[ 0 ] ].num_plano_tallado - 425 ])
                        coef12 = 0.02109303 * max([ 0, 20 - geo[ 0 ].cod_geometria ]) * max(
                            [ 0, 425 - posiciones[ indstatepos[ 0 ] ].num_plano_tallado ])
                        coef13 = -0.001316909 * max([ 0, 15 - geo[ 0 ].cod_geometria ]) * max([ 0, attrs - 55497 ])
                        coef14 = - 0.003600006 * max([ 0, geo[ 0 ].cod_geometria - 15 ]) * max([ 0, attrs - 55497 ])
                        coef15 = -1.90485 * pow(10, -6) * max([ 0, 29 - geo[ 0 ].cod_geometria ]) * max(
                            [ 0, 55497 - attrs ])
                        coef16 = 9.154122 * pow(10, -6) * max([ 0, geo[ 0 ].cod_geometria - 29 ]) * max(
                            [ 0, 55497 - attrs ])
                        coef17 = -0.001490068 * max([ 0, 540 - j.diam_inicial ]) * max(
                            [ 0, 20 - geo[ 0 ].cod_geometria ]) * max(
                            [ 0, posiciones[ indstatepos[ 0 ] ].num_plano_tallado - 430 ])
                        coef18 = -0.0003063138 * max([ 0, 540 - j.diam_inicial ]) * max(
                            [ 0, 20 - geo[ 0 ].cod_geometria ]) * max(
                            [ 0, 430 - posiciones[ indstatepos[ 0 ] ].num_plano_tallado ])
                        coef19 = 2.797927 * pow(10, -6) * max([ 0, j.diam_inicial - 540 ]) * max(
                            [ 0, 20 - geo[ 0 ].cod_geometria ]) * max([ 0, attrs - 51443 ])
                        coef20 = 3.788968 * pow(10, -8) * max([ 0, j.diam_inicial - 540 ]) * max(
                            [ 0, 20 - geo[ 0 ].cod_geometria ]) * max([ 0, 51443 - attrs ])
                        coef21 = + 1.786081e-05 * max(0, 20 - geo[ 0 ].cod_geometria) * max(0,
                                                                                            425 - posiciones[ indstatepos[
                                                                                                0 ] ].num_plano_tallado) * max(
                            0, attrs - 57723)
                        margen = coef0 + coef1 + coef2 + coef3 + coef4 + coef5 + coef6 + coef7 + coef8 + coef9 + coef10 + coef11 + coef12 + coef13 + coef14 + coef15 + coef16 + coef17 + coef18 + coef19 + coef20 + coef21
                        #the diameter after the reconditioning is updated for the position
                        margen = margen / 1000
                        decimal.getcontext().rounding = decimal.ROUND_CEILING
                        margen = margen*sum(trabajos[ cont ].toneladaslaminadas)
                        if posiciones[ indstatepos[ 0 ] ].diam_rectif == 0:
                            posiciones[ indstatepos[ 0 ] ].diam_rectif = float(round(decimal.Decimal(str( cilindros[ ind[ 0 ] ].diam_actual - margen)), ndigits=2))
                        else:
                            posiciones[ indstatepos[ 0 ] ].diam_rectif = float(round(decimal.Decimal(str(posiciones[ indstatepos[ 0 ] ].diam_rectif - \
                                                                         margen)), ndigits=2))

                        #it is indicated that the position has been used
                        posiciones[ indstatepos[ 0 ] ].cod_estado_posicion = 3
                        cilindroSolucion.append(
                            RollSolucion(sol[ k ].cod_interno, posiciones[ indstatepos[ 0 ] ].cod_posicion, cont,
                                         contapos // (numerocajas * 2),
                                         (contapos % numerocajas) -2, iteracion))
                        contapos = contapos + 1
                #The rolls used are stored
                cadena = cadena + CilindrosSolucionEncoder().encode(cilindroSolucion[ k ]) + ","
                p = p + 1
            cadena = cadena[ :len(cadena) - 1 ]
            cadena2 = "{\"Cilindros\":[" + cadena + "]}"
            cadena = "{\"Cilindros\":[" + cadena + "]},"

            fhand = open('definitivostotales.json', 'a')
            fhand.write(cadena)
            fhand.close()
            #sample.json is put to 0 for the next job and solucionesencontradas to False
            fhand = open('sample.json', 'w')
            fhand.write("{\"Cilindros\":[]}")
            fhand.close()
            solucionesencontradas = False
            #It is determined the rolls that have used positions, if they have all, they are put as active simulating the reconditioning
            desgastados = list(filter(lambda p: p.cod_estado_posicion == 3, posiciones))
            desgastadosamecanizar = [ ]
            cilins = [ ]
            for i in desgastados:
                c = sum(posx.cod_interno == i.cod_interno for posx in desgastados)
                # Cada cilindro tiene sus x posiciones
                if (c == i.numposiciones and not i.cod_interno in desgastadosamecanizar):
                    desgastadosamecanizar.append(i.cod_interno)
                    cilins.append(i)
            #The positions are turned active if they are all used
            #Update the diameter to the smaller of the indicated by the positions
            for i in cilindros:
                desgas = [ x for x in cilins if x.cod_interno == i.cod_interno ]
                if (len(desgas) != 0):
                    menordiametro = min(desgas, key=attrgetter('diam_rectif'))
                    if (menordiametro.diam_rectif != 0):
                        i.diam_actual = menordiametro.diam_rectif
            for i in posiciones:
                for j in desgastadosamecanizar:
                    if i.cod_interno == j:
                        i.cod_estado_posicion = 1
                        i.diam_rectif = 0
            rectificados = (len(cilins) / len(cilindros)) * 100
            cadena = "{\"iteracion\":" + str(iteracion) + ",\"trabajo\":" + str(
                cont) + ",\"porcentaje_rectificados\":" + str(rectificados) + "},"
            fhand = open('rectificados.json', 'a')
            fhand.write(cadena)
            fhand.close()
            # Finalmente se guarda el estado final de los cilindros y sus posiciones tras los trabajos
            #Finally it is stored the final state of the rolls and its positions after the jobs
            cadena = "["
            for element in cilindros:
                cadena = cadena + CilindrosEncoder().encode(element) + ","
            cadena = cadena[ :len(cadena) - 1 ]
            cadena = "{\"iteracion\":" + str(iteracion) + ",\"trabajo\":" + str(
                cont) + ",\"Cilindros\":" + cadena + "],\"Posiciones\":["
            for element in posiciones:
                cadena = cadena + PosicionesosEncoder().encode(element) + ","
            cadena = cadena[ :len(cadena) - 1 ]
            cadena = cadena + "]},"
            fhand = open('cilindrosfinal.json', 'a')
            fhand.write(cadena)
            fhand.close()
            tipotallado = [ ]
            cantidadcilindros = np.zeros(192)
            diametromediocilindros = np.zeros(192)
            ind = 0
            diametrostipos = [ ]
            #It is determined the average, the range, the variance of the diameter of the rolls for each of the types possibles
            for element2 in tipos:
                diametrotipo = [ ]
                filtered_compatibles = list(filter(
                    lambda x: element2.tallado == x.num_plano_tallado, posiciones))
                codigosprocesados = [ ]
                for element in filtered_compatibles:
                    if not element.cod_interno in codigosprocesados:
                        codigosprocesados.append(element.cod_interno)
                        indstatepos = [ i for i in range(len(cilindros)) if
                                        cilindros[ i ].cod_interno == element.cod_interno and cilindros[
                                            i ].geometria == element2.geometria ]
                        if len(indstatepos) != 0:
                            cantidadcilindros[ind] = cantidadcilindros[ind] + 1
                            diametrotipo.append(cilindros[ indstatepos[0]].diam_actual)
                            diametromediocilindros[ind] = cilindros[indstatepos[0]].diam_actual + \
                                                            diametromediocilindros[ind]
                ind = ind + 1
                diametrostipos.append(diametrotipo)
            medianas = [ ]
            modas = [ ]
            rango = [ ]
            for it in range(len(diametrostipos)):
                di = diametrostipos[ it ]
                di.sort()
                #print(diametrostipos.)
                rango.append(di[ len(di) - 1 ] - di[ 0 ])
                modas.append(moda(diametrostipos[ it ]))
                if (len(diametrostipos[ it ]) % 2 == 0):
                    medianas.append((di[ int(len(di) / 2) ] + di[ int((len(di) / 2) - 1) ]) / 2)
                else:
                    medianas.append(di[ int(len(di) / 2) ])
            cadena = "{\"iteracion\":" + str(iteracion) + ",\"trabajo\":" + str(
                cont) + ",\"diametros\":["
            for i in range(0, len(cantidadcilindros)):
                diametromediocilindros[ i ] = diametromediocilindros[ i ] / cantidadcilindros[ i ]
                cadena = cadena + "{" + "\"diametro\":" + str(diametromediocilindros[ i ]) + "," + "\"rango\":" + str(
                    rango[ i ]) + ",\"mediana\":" + str(medianas[ i ]) + ",\"varianza\":" + str(
                    np.var(diametrostipos[ i ])) + ",\"geometria\":\"" + tipos[ i ].geometria + "\",\"tallado\":" + str(
                    tipos[ i ].tallado) + ",\"modas\":["
                for element in modas[ i ]:
                    cadena = cadena + str(element) + ","
                cadena = cadena[ :len(cadena) - 1 ]
                cadena = cadena + "]},"
            cadena = cadena[ :len(cadena) - 1 ]
            cadena = cadena + "]},"
            fhand = open('diametrosmedios.json', 'a')
            fhand.write(cadena)
            fhand.close()
    with open('diametrosmedios.json', 'rb+') as filehandle:
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    with open('tiemposmedidos.json', 'rb+') as filehandle:
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    with open('rectificados.json', 'rb+') as filehandle:
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    with open('cilindrosfinal.json', 'rb+') as filehandle:
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    fhand = open('cilindrosfinal.json', 'a')
    fhand.write("]}")
    fhand.close()
    fhand = open('diametrosmedios.json', 'a')
    fhand.write("]}")
    fhand.close()
    fhand = open('tiemposmedidos.json', 'a')
    fhand.write("]}")
    fhand.close()
    fhand = open('rectificados.json', 'a')
    fhand.write("]}")
    fhand.close()
    with open('definitivostotales.json', 'rb+') as filehandle:
        filehandle.seek(-1, os.SEEK_END)
        filehandle.truncate()
    fhand = open('definitivostotales.json', 'a')
    fhand.write("]}")
    fhand.close()
    cilslast = [ ]


    #in types there are the different jobs possible, it is determined the number of rolls of each type that exist
    cilincomp = [ ]
    for elemento in tipos:
        cils = [ ]
        positions = [ ]
        for elemento2 in cilindros:
            if elemento.geometria == elemento2.geometria and elemento2.diam_actual > elemento2.diam_final + 4:
                for posicion in posiciones:
                    if posicion.num_plano_tallado == elemento.tallado and posicion.cod_interno == elemento2.cod_interno:
                        if not elemento2 in cils:
                            cils.append(elemento2)
        cilincomp.append(CilindrosCompatiblesComprar(elemento.numcaja, cils, elemento.geometria, elemento.tallado))



    for elemento in cilincomp:
        #it is determined how many rolls there are that have the same diameter as the current one
        cantidades = [ ]
        cilscompute = [ ]
        posi = [ ]
        for cilin in range(len(elemento.compatibles)):
            c = sum(cilindro.diam_actual == elemento.compatibles[ cilin ].diam_actual for cilindro in elemento.compatibles)
            if (c >= 2):
                cilscompute.append(elemento.compatibles[ cilin ])
            cantidades.append(c)
        cilslast.append(CilindrosCompatiblesComprar(elemento.caja, cilscompute, elemento.geometria, elemento.tallado))
    #if there are less than 50 it is indicated that new have to be bought
    cadenacomprar = "{\"Cilindros\":[ "
    for elemento in cilslast:
        if len(elemento.compatibles) < 50:
            cantidad = 50 - len(elemento.compatibles)
            cadenacomprar = cadenacomprar + "{\"cantidad\":" + str(cantidad) + ",\"tallado\":" + str(
                elemento.tallado) + ",\"geometria\":\"" + elemento.geometria + "\"},"
    cadenacomprar = cadenacomprar[ :len(cadenacomprar) - 1 ]
    cadenacomprar = cadenacomprar + "]}"
    fhand = open('compras.json', 'w')
    fhand.write(cadenacomprar)
    fhand.close()