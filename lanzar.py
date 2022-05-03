import json
import signal
from json import JSONEncoder
import os
from operator import attrgetter
import random

import psutil
from func_timeout import func_timeout, FunctionTimedOut
import numpy as np
from pade.core.agent import Agent
import copy
from pade.acl.aid import AID
from pade.acl.messages import ACLMessage
from pade.misc.utility import display_message, start_loop, call_later
from pade.behaviours.protocols import TimedBehaviour
from os import remove

#number of stands considered
numerocajas = 6
#function that checks if it is a json
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError as e:
        return False
    return True

# Roll read from the configuration file
class Roll:
    def __init__(self, cod_interno, diam_inicial, diam_final, diam_actual, cod_estado, geometria, numposiciones):
        self.cod_interno = cod_interno
        self.diam_inicial = diam_inicial
        self.diam_final = diam_final
        self.diam_actual = diam_actual
        self.cod_estado = cod_estado
        self.geometria = geometria
        self.numposiciones = numposiciones

#compatible rolls with a specific stand
class CilindrosCompatibles:
    def __init__(self, caja, compatibles):
        self.caja = caja
        self.compatibles = compatibles


#constraints, the set changes for each job scheduled the two stands that participate are indicated, the quantity, the factor and the type (configuration file)
class Restricciones:
    def __init__(self, caja1, caja2, cantidad, factor, tipo):
        self.caja1 = caja1
        self.caja2 = caja2
        self.cantidad = cantidad
        self.factor = factor
        self.tipo = tipo


#agent that is in charge of supervising whether it has been reached a solution or not
class SuperAgente(Agent):
    def __init__(self, aid,agent_list):
        super(SuperAgente, self).__init__(aid=aid, debug=False)
        #values stored of the diameter of the agents
        self.valores = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, -1,-1,-1,-1]
        #previous values of the diameter of the agents
        self.old_values = [-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2]
        #internal code of one of the rolls of a stand
        self.valorescodigo1 = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, -1,-1,-1,-1]
        #previous values of the internal code of the roll of a stand
        self.old_valuescodigo1 = [-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2]
        #valorescodigo2 almacena el codigo interno de uno de los cilindros de una caja
        #internal codes of the other roll of a stand
        self.valorescodigo2 = [-1,-1,-1,-1,-1,-1,-1,-1,-1,-1, -1,-1,-1,-1]
        #previous values of the internal code of the other roll of a stand
        self.old_valuescodigo2 = [-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2,-2]
        #indica si ya se han escrito los diametros y los codigos a archivo
        #it indicates whether it has been written to file or not
        self.escrito = False
        #complete list of the agents
        self.agent_list = copy.deepcopy(agent_list)

    #function that sends inform messages without waiting for acknowledgement
    def sendINFORMnoAck(self,name,variablex):
        message = ACLMessage(ACLMessage.INFORM)
        message.add_receiver(AID(name))
        message.set_content(variablex)
        self.send(message)

    #reaction of the agent after receiving messages
    def react(self, message):
        super(SuperAgente, self).react(message)
        display_message(self.aid.localname, 'Mensaje SUPERAGENTE recibido from {}'.format(message.content))
        # if the message is of type inform
        if message.performative == ACLMessage.INFORM and is_json(message.content):
            mensaje = json.loads(message.content)
            for el in self.agent_list:
                if str(message.sender.name) in str(el):
                    #an inform message is sent to the agent that sent the message to acknowledge its reception
                    self.sendINFORMnoAck(el, "{\"tipo\":" + str(2) + ",\"indice\":" + str(mensaje['indice']) + "}")
            display_message(self.aid.localname, 'Mensaje INFORM recibido from {}'.format(message.sender.name))
            display_message(self.aid.localname, 'Mensaje INFORM recibido from {}'.format(message.content))
            daerror = False
            contenido = ""
            #check if there is any element different of -1 in the message, if not it is an error
            algunodistintomenosuno = False
            for element in range(0, len(mensaje['estadiam'])):
                if mensaje['estadiam'][element] == -1 or mensaje['estacod1'][element] == -1 or mensaje['estacod2'][element] == -1:
                    daerror = True
                else:
                    algunodistintomenosuno = True
            #if there is no element different from -1 there is no solution
            if daerror and not algunodistintomenosuno:
                display_message(self.aid.localname, 'Error')
                for element in range(0, len(mensaje['estadiam'])):
                    contenido = contenido + "{\"diametro\":" + str(0) + ",\"codigos\":[]},"
                contenido = contenido[:len(contenido) - 1]
                nogoodstexto = ""
                for element in range(0, len(mensaje['indicesnogood'])):
                    nogoodstexto = nogoodstexto + str(mensaje['indicesnogood'][element]) + ","
                nogoodstexto = nogoodstexto[:len(nogoodstexto) - 1]
                okstexto = ""
                for element in range(0, len(mensaje['indicesok'])):
                    okstexto = okstexto + str(mensaje['indicesok'][element]) + ","
                okstexto = okstexto[:len(okstexto) - 1]
                #the number of nogoods and oks is stored
                cadena = "{\"Cajas\":[" + contenido + "],"+"\"Nogoods\":["+nogoodstexto+"],"+"\"Oks\":["+okstexto+"]}"
                fhand = open('resultadoabt2.json', 'w')
                display_message(self.aid.localname, os.path.realpath('resultadoabt2.json'))
                fhand.write(cadena)
                fhand.close()
                display_message(self.aid.localname, 'Encontrado error')
            else:
                #if there is a solution
                if not daerror:
                    display_message(self.aid.localname, 'Encontrado solucion')
                    #the values of diameters and internal codes of the rolls are stored
                    for element in range(0, len(mensaje['estadiam'])):
                        contenido = contenido + "{\"diametro\":" + str(mensaje['estadiam'][element]) + ",\"codigos\":[" + str(
                            mensaje['estacod1'][element]) + "," + str(mensaje['estacod2'][element]) + "]},"
                    contenido = contenido[:len(contenido) - 1]
                    nogoodstexto = ""
                    for element in range(0, len(mensaje['indicesnogood'])):
                        nogoodstexto = nogoodstexto+ str(mensaje['indicesnogood'][element])+","
                    nogoodstexto = nogoodstexto[:len(nogoodstexto) - 1]
                    okstexto = ""
                    #also the number of nogoods and ok messages are stored
                    for element in range(0, len(mensaje['indicesok'])):
                        okstexto = okstexto + str(mensaje['indicesok'][element]) + ","
                    okstexto = okstexto[:len(okstexto) - 1]
                    cadena = "{\"Cajas\":[" + contenido + "],"+"\"Nogoods\":["+nogoodstexto+"],"+"\"Oks\":["+okstexto+"]}"
                    fhand = open('resultadoabt2.json', 'w')
                    display_message(self.aid.localname, os.path.realpath('resultadoabt2.json'))
                    fhand.write(cadena)
                    fhand.close()
                    display_message(self.aid.localname, 'Encontrado solucion')

#each stand of the rolling mill is an agent
class Agente(Agent):
    def __init__(self, name, orden, neighbor_list, domain, agent_list, constraints,cilindrosporcaja):
        super(Agente, self).__init__(aid=name)
        #name of the agent p16@localhost:20000 for example
        self.name = name
        #order of the stand 16 17 ....
        self.orden = orden
        #list of the agent neighbours
        self.neighbors_list = copy.deepcopy(neighbor_list)
        #complete domain of the agent given the geometry and shape constraints
        self.agent_domain = copy.deepcopy(domain)
        #agents known by the current agent
        self.agentview = {}
        #codes in the OK message
        self.agentcodigos = []
        self.consistent = True
        #constraints
        self.constraints = copy.deepcopy(constraints)
        #complete list of agents
        self.agent_list = copy.deepcopy(agent_list)
        #given the stand that represents the agent, compatible rolls with it
        self.cilindrosporcaja = cilindrosporcaja
        #diameter nogoods
        self.nogoods = {}
        #nogoods that are received by the agent
        self.nogoodspropios = []
        #nogoods of internal codes, those that are received from the next agent
        self.nogoodscodigos = []
        #internal codes used by the stand currently
        self.codigoscilindros = []
        #acknowledgment received
        self.recibidosconfirmacionok = []
        self.recibidosconfirmacionnogood = []
        self.recibidosconfirmacionaddlink = []
        self.recibidosconfirmacioninform = []
        #number of the sent message by the stand
        self.indiceok = 0
        self.indicenogood = -1
        self.indiceaddlink = 0
        self.indiceinform = 0
        #number of the sent messages by the other stands
        self.indicesok= [-1] * numerocajas
        self.indicesnogood=[-1] * numerocajas
        #values of diameters and internal codes known by the agent
        self.estadoagentesdiametro=[-1]*numerocajas
        self.estadoagentescodigos1=[-1]*numerocajas
        self.estadoagentescodigos2=[-1]*numerocajas
        self.enviarokcambioestado = False
        # value of the diameter of the agent
        self.value = 0
        # current domain of the agent
        self.dominio_actual = []
        #if the agent has domain
        if len(self.agent_domain) > 0:
            #a random value of those available is given
            self.value = random.choice(self.agent_domain)
            #the original domain is copied
            #provided the nogoods the domain is reduced, if backtracking it is the original once again
            self.dominio_actual = copy.deepcopy(self.agent_domain)
            #the rolls to select are those with the diameter selected previously
            elementoscaja = copy.deepcopy(self.cilindrosporcaja[self.value])
            #randomly two values are chosen given the diameter selected
            if len(elementoscaja) >= 2:
                valor1 = random.choice(elementoscaja)
                self.codigoscilindros.append(valor1)
                valor2 = valor1+1 if valor1 % 2 == 0 else valor1-1
                self.codigoscilindros.append(valor2)
                self.estadoagentesdiametro[self.orden - 16] = self.value
                self.estadoagentescodigos1[self.orden - 16] = self.codigoscilindros[0]
                self.estadoagentescodigos2[self.orden - 16] = self.codigoscilindros[1]

    #at the beginning
    def on_start(self):
        super(Agente, self).on_start()
        #if the agent has domain
        if len(self.agent_domain) > 0:
            #the rolls from which the selection is performed are those with the diameter selected
            elementoscaja = copy.deepcopy(self.cilindrosporcaja[self.value])
            #if there are enough rolls
            if len(elementoscaja) >= 2:
                #the OK message which is going to be sent is prepared
                codigos = ""
                for element in self.codigoscilindros:
                    codigos = codigos + str(element) + ","
                codigos = codigos[:len(codigos) - 1]

                estadiam = ""
                for element in self.estadoagentesdiametro:
                    estadiam = estadiam + str(element) + ","
                estadiam = estadiam[:len(estadiam) - 1]
                estacod1 = ""
                for element in self.estadoagentescodigos1:
                    estacod1 = estacod1 + str(element) + ","
                estacod1 = estacod1[:len(estacod1) - 1]
                estacod2 = ""
                for element in self.estadoagentescodigos2:
                    estacod2 = estacod2 + str(element) + ","
                estacod2 = estacod2[:len(estacod2) - 1]
                self.indicesok[self.orden - 16] = self.indiceok
                indicesoktexto = ""
                for element in self.indicesok:
                    indicesoktexto = indicesoktexto + str(element) + ","
                indicesoktexto = indicesoktexto[:len(indicesoktexto) - 1]
                indicesnogoodtexto= ""
                for element in self.indicesnogood:
                    indicesnogoodtexto = indicesnogoodtexto + str(element) + ","
                indicesnogoodtexto = indicesnogoodtexto[:len(indicesnogoodtexto) - 1]
                muestrame = ""
                for ele in self.neighbors_list:
                    muestrame=muestrame+" "+str(ele)
                display_message(self.aid.localname, "envia ok "+muestrame)
                for ele in self.neighbors_list:
                    self.recibidosconfirmacionok.append(self.indiceok)
                    call_later(8, self.sendOK, ele, "{\"key\":" + str(self.orden) + ",\"value\":" + str(
                        self.value) + ",\"cilindros\":[" + codigos + "]"+
                    ",\"estadiam\":[" + estadiam + "],"+
                    "\"estacod1\":[" + estacod1 + "],"+
                    "\"estacod2\":[" + estacod2 + "],"+
                    "\"indice\":"+str(self.indiceok)+
                    ",\"indicesok\":[" + indicesoktexto +"],"+
                    "\"indicesnogood\":[" + indicesnogoodtexto + "]" +
                    "}",self.indiceok)
            else:
                #if there are not enough codes a message is sent so the controller agent knows that
                display_message(self.aid.localname, "no tiene codigos")
                self.value = 0
                self.estadoagentesdiametro[self.orden % 16] = 0
                self.estadoagentescodigos1[self.orden % 16] = -1
                self.estadoagentescodigos2[self.orden % 16] = -1
                self.codigoscilindros = []
                self.indiceinform = self.indiceinform + 1
                indicesoktexto = ""
                for element in self.indicesok:
                    indicesoktexto = indicesoktexto + str(element) + ","
                indicesoktexto = indicesoktexto[:len(indicesoktexto) - 1]
                indicesnogoodtexto = ""
                for element in self.indicesnogood:
                    indicesnogoodtexto = indicesnogoodtexto + str(element) + ","
                indicesnogoodtexto = indicesnogoodtexto[:len(indicesnogoodtexto) - 1]
                menosunos = ""
                for ele in self.agent_list:
                    menosunos = menosunos + "-1,"
                menosunos = menosunos[:len(menosunos) - 1]
                dictio = "{\"estadiam\":[" + menosunos + "],\"estacod1\":[" + menosunos + "],\"estacod2\":[" + menosunos + "],"+"\"indice\":"+str(self.indiceinform)+\
                         ",\"indicesok\":[" + indicesoktexto +"],"+"\"indicesnogood\":[" + indicesnogoodtexto + "]" +"}"
                for el in self.agent_list:
                    display_message(self.aid.localname, str(el))
                    if 'super' in str(el):
                        display_message(self.aid.localname, "envia inform")
                        display_message(self.aid.localname, "envia terminate")
                        self.recibidosconfirmacioninform.append(self.indiceinform)
                        call_later(8, self.sendINFORM, el, dictio,self.indiceinform)

        else:
            # if the agent has no domain a message is sent so the controller agent knows that
            display_message(self.aid.localname, "no tiene dominio")
            self.value = 0
            self.estadoagentesdiametro[self.orden % 16] = 0
            self.estadoagentescodigos1[self.orden % 16] = -1
            self.estadoagentescodigos2[self.orden % 16] = -1
            self.codigoscilindros = []
            self.indiceinform = self.indiceinform + 1
            indicesoktexto = ""
            for element in self.indicesok:
                indicesoktexto = indicesoktexto + str(element) + ","
            indicesoktexto = indicesoktexto[:len(indicesoktexto) - 1]
            indicesnogoodtexto = ""
            for element in self.indicesnogood:
                indicesnogoodtexto = indicesnogoodtexto + str(element) + ","
            indicesnogoodtexto = indicesnogoodtexto[:len(indicesnogoodtexto) - 1]
            menosunos=""
            for ele in self.agent_list:
                menosunos=menosunos+"-1,"
            menosunos = menosunos[:len(menosunos)-1]
            dictio = "{\"estadiam\":[" + menosunos + "],\"estacod1\":[" + menosunos + "],\"estacod2\":[" + menosunos + "],"+"\"indice\":"+str(self.indiceinform)+\
                     ",\"indicesok\":[" + indicesoktexto +"],"+"\"indicesnogood\":[" + indicesnogoodtexto + "]" +"}"
            for el in self.agent_list:
                display_message(self.aid.localname, str(el))
                if 'super' in str(el):
                    display_message(self.aid.localname, "envia inform")
                    display_message(self.aid.localname, "envia terminate")
                    self.recibidosconfirmacioninform.append(self.indiceinform)
                    call_later(8, self.sendINFORM, el, dictio,self.indiceinform)

    #function to send Nogoods
    def sendNo_Good(self,name,nogood,indice):
        if indice in self.recibidosconfirmacionnogood:
            for ele in self.recibidosconfirmacionnogood:
                if ele < indice:
                    self.recibidosconfirmacionnogood.remove(ele)
            message = ACLMessage(ACLMessage.REJECT_PROPOSAL)
            message.add_receiver(AID(name))
            message.set_content(nogood)
            self.send(message)
            call_later(10, self.sendNo_Good, name, nogood, indice)


    #function to send OKs
    def sendOK(self,name,variablex,indice):
        if indice in self.recibidosconfirmacionok:
            for ele in self.recibidosconfirmacionok:
                if ele < indice:
                    self.recibidosconfirmacionok.remove(ele)
            message = ACLMessage(ACLMessage.PROPOSE)
            message.add_receiver(AID(name))
            message.set_content(variablex)
            self.send(message)
            call_later(10, self.sendOK, name, variablex,indice)

    #function to send INFORMS with acknowledgement
    def sendINFORM(self,name,variablex,indice):
        if indice in self.recibidosconfirmacioninform:
            for ele in self.recibidosconfirmacioninform:
                if ele < indice:
                    self.recibidosconfirmacioninform.remove(ele)
            message = ACLMessage(ACLMessage.INFORM)
            message.add_receiver(AID(name))
            message.set_content(variablex)
            self.send(message)
            call_later(10, self.sendINFORM, name, variablex, indice)

    #function to send INFORMS without acknowledgement
    def sendINFORMnoAck(self,name,variablex):
        message = ACLMessage(ACLMessage.INFORM)
        message.add_receiver(AID(name))
        message.set_content(variablex)
        self.send(message)

    #function to send ADDLINK it is not used
    def sendAddLink(self,key,value,destinatario,indice):
        if indice in self.recibidosconfirmacionaddlink:
            dictio= "{\"key\":"+str(key) + ",\"value\":" + str(value)+"}"
            message = ACLMessage(ACLMessage.PROPAGATE)
            message.add_receiver(AID(destinatario))
            message.set_content(dictio)
            self.send(message)


    #checkview
    def checkview(self):
        display_message(self.aid.localname, "longitud de la agent_list "+str(len(self.agent_list)))
        for el in self.agent_list:
            display_message(self.aid.localname, str(el))
        enviarok = False
        #updates the values with the value for the current stand
        #In valores the diameters of every agent seen by the current agent and its own value are present
        valores = copy.deepcopy(self.agentview)
        #valornuevo has the current value of diameter and codigosnuevo the current codes
        #then it is checked if given the current configuration they are valid or any different one is valid
        valornuevo = self.value
        codigosnuevo = copy.deepcopy(self.codigoscilindros)
        #the values are updated with the diameter value for the current stand
        valores.update({self.orden: self.value})
        display_message(self.aid.localname, "Checkview " + str(valores))
        #if the values are not valid fallo is false, fallo1 and fallo2 allow to know if it fails
        #because of the value of the diameter or because of the internal codes
        fallo = True
        #this is to know the remaining values to check if they are valid
        faltantesporprobar = copy.deepcopy(self.dominio_actual)
        #if it still is possible a solution, it is 0 when not
        if self.value != 0:
            #the agents seen by the current agent are shown included itself
            for element in valores.keys():
                display_message(self.aid.localname, str(element)+" "+str(valores[element]))
            #a value that accomplishes the constraints is searched while the previous ones fail and there are
            #still remaining values to check
            while fallo and len(faltantesporprobar) > 0:
                fallo = False
                if valornuevo == self.value and self.value not in faltantesporprobar and len(faltantesporprobar) > 0:
                    valornuevo = random.choice(faltantesporprobar)
                    valores.update({self.orden: valornuevo})
                elif valornuevo == self.value and self.value not in faltantesporprobar and len(faltantesporprobar) == 0:
                    fallo = True
                #codes that are available for that diameter value
                copiacilindrosporcaja = copy.deepcopy(self.cilindrosporcaja[valornuevo])
                #codes that are in nogoods are removed and also those received from the previous stand
                for b in self.nogoodscodigos:
                    if b in copiacilindrosporcaja:
                        copiacilindrosporcaja.remove(b)
                for b in self.agentcodigos:
                    if b in copiacilindrosporcaja:
                        copiacilindrosporcaja.remove(b)
                #how many rest to check
                display_message(self.aid.localname, str(len(faltantesporprobar)))
                #the constraints are checked
                for restric in self.constraints:
                    #if the agent sees the two stands in a constraint, the constraint is checked
                    if restric.caja1 in valores.keys() and restric.caja2 in valores.keys():
                        display_message(self.aid.localname,
                                        "entra")
                        if restric.tipo == "+-":
                            ca = abs(valores[restric.caja2] - valores[restric.caja1]) / restric.factor
                            display_message(self.aid.localname,
                                            str(restric.caja1) + " " + str(restric.caja2) + " " + str(ca) + " " + str(restric.cantidad) + " "+str(len(faltantesporprobar)))
                            if not (ca) < restric.cantidad:
                                #the constraints are not met
                                display_message(self.aid.localname,
                                                "entra2")
                                fallo = True
                        elif restric.tipo == "=":
                            ca = abs(valores[restric.caja2] - valores[restric.caja1]) / restric.factor
                            display_message(self.aid.localname,
                                            str(restric.caja1) + " " + str(restric.caja2) + " " + str(ca) + " " + str(restric.cantidad) + " "+str(len(faltantesporprobar)))
                            if not (ca) == restric.cantidad:
                                # the constraints are not met
                                display_message(self.aid.localname,
                                                "entra2")
                                fallo = True

                display_message(self.aid.localname, str(len(copiacilindrosporcaja)))
                #if there are not two rolls at least for the vein it is not feasible
                if len(copiacilindrosporcaja) < 2:
                    fallo = True
                else:
                    #if there are two are selected
                    cambiar = False
                    for element in self.codigoscilindros:
                        if element in self.nogoodscodigos or element in self.agentcodigos:
                            cambiar = True
                    if cambiar:
                        self.codigoscilindros = []
                        valor = random.choice(copiacilindrosporcaja)
                        self.codigoscilindros.append(valor)
                        valor2 = valor + 1 if valor % 2 == 0 else valor - 1
                        self.codigoscilindros.append(valor2)
                        enviarok = True
                #if the constraints are not met or if they are met for that diameter but there are not available rolls
                #another diameter is checked
                if fallo:
                    display_message(self.aid.localname, str(faltantesporprobar))
                    #if there are still remaining rolls
                    if len(faltantesporprobar) > 0:
                        #The value is removed and another is checked
                        display_message(self.aid.localname, "Elimina " + str(valornuevo))
                        faltantesporprobar.remove(valornuevo)
                        #if there are still remaining
                        if len(faltantesporprobar) > 0:
                            valornuevo = random.choice(faltantesporprobar)
                            valores.update({self.orden: valornuevo})
                            codigosnuevo = []
            #if no value is available it backtracks
            if fallo:
                display_message(self.aid.localname,
                                "fallo")
                #the domain is the original one
                self.dominio_actual = copy.deepcopy(self.agent_domain)
                self.backtrack()
                self.enviarokcambioestado = False
            else:
                #if there is some available value
                display_message(self.aid.localname,
                                "no fallo")
                #if a new value is assigned
                if valornuevo != self.value:
                    # the new value is assigned and compatible codes are searched that meet that diameter
                    self.value = valornuevo
                    self.codigoscilindros = []
                    copiacilindrosporcaja = copy.deepcopy(self.cilindrosporcaja[valornuevo])
                    #the rolls in nogoods and those used in other stand are removed from those that can be used
                    for b in self.nogoodscodigos:
                        if b in copiacilindrosporcaja:
                            copiacilindrosporcaja.remove(b)
                    for b in self.agentcodigos:
                        if b in copiacilindrosporcaja:
                            copiacilindrosporcaja.remove(b)
                    valor1 = random.choice(copiacilindrosporcaja)
                    valor2 = valor1 + 1 if valor1 % 2  == 0 else valor1 - 1
                    self.codigoscilindros.append(valor1)
                    self.codigoscilindros.append(valor2)
                    enviarok = True
                #if an OK message has to be sent, it is prepared
                if enviarok:
                    display_message(self.aid.localname,"envia ok")
                    self.estadoagentesdiametro[self.orden - 16] = self.value
                    self.estadoagentescodigos1[self.orden - 16] = self.codigoscilindros[0]
                    self.estadoagentescodigos2[self.orden - 16] = self.codigoscilindros[1]
                    #Preparo para enviar el sendOk a los vecinos
                    codigos = ""
                    for element in self.codigoscilindros:
                        codigos = codigos + str(element) + ","
                    codigos = codigos[:len(codigos) - 1]
                    estadiam = ""
                    for element in self.estadoagentesdiametro:
                        estadiam = estadiam + str(element) + ","
                    estadiam = estadiam[:len(estadiam) - 1]
                    estacod1 = ""
                    for element in self.estadoagentescodigos1:
                        estacod1 = estacod1 + str(element) + ","
                    estacod1 = estacod1[:len(estacod1) - 1]
                    estacod2 = ""
                    for element in self.estadoagentescodigos2:
                        estacod2 = estacod2 + str(element) + ","
                    estacod2 = estacod2[:len(estacod2) - 1]
                    self.indiceok = self.indiceok + 1
                    self.indicesok[self.orden - 16] = self.indiceok
                    self.indicesnogood[self.orden - 16] = self.indicenogood
                    indicesoktexto = ""
                    for element in self.indicesok:
                        indicesoktexto = indicesoktexto + str(element) + ","
                    indicesoktexto = indicesoktexto[:len(indicesoktexto) - 1]
                    indicesnogoodtexto = ""
                    for element in self.indicesnogood:
                        indicesnogoodtexto = indicesnogoodtexto + str(element) + ","
                    indicesnogoodtexto = indicesnogoodtexto[:len(indicesnogoodtexto) - 1]
                    self.recibidosconfirmacionok.append(self.indiceok)
                    dictio = "{\"key\":" + str(self.orden) + ",\"value\":" + str(self.value) + ",\"cilindros\":[" + codigos + "]" + ",\"estadiam\":[" + estadiam + "]," + "\"estacod1\":[" + estacod1 + "]," + "\"estacod2\":[" + estacod2 + "],"+"\"indice\":"+str(self.indiceok)+\
                             ",\"indicesok\":[" + indicesoktexto +"],"+"\"indicesnogood\":[" + indicesnogoodtexto + "]" +"}"
                    for ele in self.neighbors_list:
                        self.sendOK(ele, dictio,self.indiceok)
                    self.enviarokcambioestado = False
                else:
                    #if no ok message has to be sent it checks whether there has been a change of state that
                    #needs an OK message to be sent to update the knowledge
                    if self.enviarokcambioestado:
                        self.estadoagentesdiametro[self.orden - 16] = self.value
                        self.estadoagentescodigos1[self.orden - 16] = self.codigoscilindros[0]
                        self.estadoagentescodigos2[self.orden - 16] = self.codigoscilindros[1]
                        codigos = ""
                        for element in self.codigoscilindros:
                            codigos = codigos + str(element) + ","
                        codigos = codigos[:len(codigos) - 1]
                        estadiam = ""
                        for element in self.estadoagentesdiametro:
                            estadiam = estadiam + str(element) + ","
                        estadiam = estadiam[:len(estadiam) - 1]
                        estacod1 = ""
                        for element in self.estadoagentescodigos1:
                            estacod1 = estacod1 + str(element) + ","
                        estacod1 = estacod1[:len(estacod1) - 1]
                        estacod2 = ""
                        for element in self.estadoagentescodigos2:
                            estacod2 = estacod2 + str(element) + ","
                        estacod2 = estacod2[:len(estacod2) - 1]
                        self.indiceok = self.indiceok + 1
                        self.indicesok[self.orden - 16] = self.indiceok
                        self.indicesnogood[self.orden - 16] = self.indicenogood
                        indicesoktexto = ""
                        for element in self.indicesok:
                            indicesoktexto = indicesoktexto + str(element) + ","
                        indicesoktexto = indicesoktexto[:len(indicesoktexto) - 1]
                        indicesnogoodtexto = ""
                        for element in self.indicesnogood:
                            indicesnogoodtexto = indicesnogoodtexto + str(element) + ","
                        indicesnogoodtexto = indicesnogoodtexto[:len(indicesnogoodtexto) - 1]
                        self.recibidosconfirmacionok.append(self.indiceok)
                        dictio = "{\"key\":" + str(self.orden) + ",\"value\":" + str(
                            self.value) + ",\"cilindros\":[" + codigos + "]" + ",\"estadiam\":[" + str(estadiam) + "]" + ",\"estacod1\":[" + str(estacod1) + "]" + ",\"estacod2\":[" + str(estacod2) + "],"+"\"indice\":"+str(self.indiceok)+\
                                 ",\"indicesok\":[" + indicesoktexto +"],"+"\"indicesnogood\":[" + indicesnogoodtexto + "]"+"}"
                        display_message(self.aid.localname, "envia ok")
                        for ele in self.neighbors_list:

                            self.sendOK(ele, dictio, self.indiceok)
                        self.enviarokcambioestado = False
                #if it is the last agent
                if self.orden == (16+numerocajas-1):
                    for el in self.agent_list:
                        display_message(self.aid.localname, str(el))
                        if 'super' in str(el):
                            #it sends an inform message to the controller agent so that it checks whether a solution has been reached
                            estadiam = ""
                            for element in self.estadoagentesdiametro:
                                estadiam = estadiam + str(element) + ","
                            estadiam = estadiam[:len(estadiam) - 1]
                            estacod1 = ""
                            for element in self.estadoagentescodigos1:
                                estacod1 = estacod1 + str(element) + ","
                            estacod1 = estacod1[:len(estacod1) - 1]
                            estacod2 = ""
                            for element in self.estadoagentescodigos2:
                                estacod2 = estacod2 + str(element) + ","
                            estacod2 = estacod2[:len(estacod2) - 1]
                            self.indiceinform = self.indiceinform +1
                            indicesoktexto = ""
                            for element in self.indicesok:
                                indicesoktexto = indicesoktexto + str(element) + ","
                            indicesoktexto = indicesoktexto[:len(indicesoktexto) - 1]
                            indicesnogoodtexto = ""
                            for element in self.indicesnogood:
                                indicesnogoodtexto = indicesnogoodtexto + str(element) + ","
                            indicesnogoodtexto = indicesnogoodtexto[:len(indicesnogoodtexto) - 1]
                            dictio = "{" + "\"estadiam\":[" + estadiam + "]," + "\"estacod1\":[" + estacod1 + "]," + "\"estacod2\":[" + estacod2 + "],"+"\"indice\":"+str(self.indiceinform)+\
                                      ",\"indicesok\":[" + indicesoktexto +"],"+"\"indicesnogood\":[" + indicesnogoodtexto + "]" + "}"
                            self.recibidosconfirmacioninform.append(self.indiceinform)
                            display_message(self.aid.localname, "envia inform")
                            self.sendINFORM(el, dictio,self.indiceinform)


    #backtrack function
    def backtrack(self):
        if self.orden in self.nogoods:
            del self.nogoods[self.orden]
        if self.orden in self.agentview:
            del self.agentview[self.orden]
        #if there is any agent in the agentview and it is not the first agent
        if len(self.agentview) > 0 and self.orden != 16:
            #a nogood is sent to the highest one
            for element in self.agentview:
                if element < self.orden:
                    self.nogoods.update({element: self.agentview[element]})
                    display_message(self.aid.localname, "add nogoods "+str(element) + " " + str(self.agentview[element]))

        #if it is the first agent it has no agent to backtrack so it informs that no solution is possible
        if self.orden == 16:
            self.indiceinform = self.indiceinform + 1
            indicesoktexto = ""
            for element in self.indicesok:
                indicesoktexto = indicesoktexto + str(element) + ","
            indicesoktexto = indicesoktexto[:len(indicesoktexto) - 1]
            indicesnogoodtexto = ""
            for element in self.indicesnogood:
                indicesnogoodtexto = indicesnogoodtexto + str(element) + ","
            indicesnogoodtexto = indicesnogoodtexto[:len(indicesnogoodtexto) - 1]
            menosunos=""
            for ele in self.agent_list:
                menosunos=menosunos+"-1,"
            menosunos = menosunos[:len(menosunos)-1]
            dictio = "{\"estadiam\":[" + menosunos + "],\"estacod1\":[" + menosunos + "],\"estacod2\":[" + menosunos + "]," + "\"indice\":"+str(self.indiceinform) + \
                      ",\"indicesok\":[" + indicesoktexto +"],"+"\"indicesnogood\":[" + indicesnogoodtexto + "]" + "}"
            for el in self.agent_list:
                if 'super' in str(el):
                    display_message(self.aid.localname, "envia terminate")
                    self.recibidosconfirmacioninform.append(self.indiceinform)
                    self.sendINFORM(el, dictio, self.indiceinform)
            self.value = 0
            self.codigoscilindros = []
        #if there are nogoods
        if len(self.nogoods) > 0:
            #the nogood is sent to the highest one, in this case there is only one
            minimo = -1
            cadena = "{\"nogoods\":["
            for ele in self.nogoods:
                if minimo == -1:
                    if ele < self.orden:
                        minimo = ele
                else:
                    if ele > minimo and ele < self.orden:
                        minimo = ele
                problematicos = []
                codigos = ""
                #if it is the previous agent
                if ele == (self.orden - 1):
                    for element in self.agentcodigos:
                        #the codes in nogoods are sent to it
                        if element in self.codigoscilindros:
                            problematicos.append(element)
                    for element in problematicos:
                        codigos = codigos + str(element) + ","
                    codigos = codigos[:len(codigos) - 1]
                cadena = cadena + "{\"key\":" + str(ele) + ",\"value\":" + str(self.nogoods[ele]) + ",\"codigos\":[" + codigos + "]},"
            cadena = cadena[ :len(cadena) - 1 ]
            self.indicenogood = self.indicenogood + 1
            cadena = cadena+"],"+"\"indice\":"+str(self.indicenogood)+"}"
            display_message(self.aid.localname, 'tiene que enviar nogood')
            for nombres in self.agent_list:
                if str(minimo) in nombres:
                    display_message(self.aid.localname, 'lo envia'+str(nombres))
                    # The NOGOOD message is sent
                    self.recibidosconfirmacionnogood.append(self.indicenogood)
                    self.sendNo_Good(nombres, cadena,self.indicenogood)
                    self.estadoagentesdiametro[minimo % 16]=-1
                    self.estadoagentescodigos2[minimo % 16]=-1
                    self.estadoagentescodigos1[minimo % 16]=-1
                    #an OK message is sent
                    codigos = ""
                    for element in self.codigoscilindros:
                        codigos = codigos + str(element) + ","
                    codigos = codigos[:len(codigos) - 1]
                    estadiam = ""
                    for element in self.estadoagentesdiametro:
                        estadiam = estadiam + str(element) + ","
                    estadiam = estadiam[:len(estadiam) - 1]
                    estacod1 = ""
                    for element in self.estadoagentescodigos1:
                        estacod1 = estacod1 + str(element) + ","
                    estacod1 = estacod1[:len(estacod1) - 1]
                    estacod2 = ""
                    for element in self.estadoagentescodigos2:
                        estacod2 = estacod2 + str(element) + ","
                    estacod2 = estacod2[:len(estacod2) - 1]
                    self.indiceok = self.indiceok + 1
                    self.indicesok[self.orden - 16] = self.indiceok
                    self.indicesnogood[self.orden - 16] = self.indicenogood
                    indicesoktexto = ""
                    for element in self.indicesok:
                        indicesoktexto = indicesoktexto + str(element) + ","
                    indicesoktexto = indicesoktexto[:len(indicesoktexto) - 1]
                    indicesnogoodtexto = ""
                    for element in self.indicesnogood:
                        indicesnogoodtexto = indicesnogoodtexto + str(element) + ","
                    indicesnogoodtexto = indicesnogoodtexto[:len(indicesnogoodtexto) - 1]
                    self.recibidosconfirmacionok.append(self.indiceok)
                    dictio = "{\"key\":" + str(self.orden) + ",\"value\":" + str(
                        self.value) + ",\"cilindros\":[" + codigos + "]" + ",\"estadiam\":[" + estadiam + "]," + "\"estacod1\":[" + estacod1 + "]," + "\"estacod2\":[" + estacod2 + "],"+"\"indice\":"+str(self.indiceok)+\
                             ",\"indicesok\":[" + indicesoktexto +"],"+"\"indicesnogood\":[" + indicesnogoodtexto + "]"+"}"

                    for ele in self.neighbors_list:
                        self.sendOK(ele, dictio,self.indiceok)

            display_message(self.aid.localname, 'saca '+str(minimo))
            display_message(self.aid.localname, str(self.agentview))
            #when the nogoods are sent as the agent is gonna change its value, it is removed from the agentview and the agentview is checked again
            for ele in self.nogoods:
                if ele in self.agentview:
                    del self.agentview[ele]
            #when the nogood is sent every element in nogoods goes there
            #the one that receives the nogood stores those so the nogoods are put to empty
            self.nogoods = {}
            self.dominio_actual = copy.deepcopy(self.agent_domain)
            self.checkview()


    #function defining the reaction when a message is received
    def react(self, message):
        super(Agente, self).react(message)
        display_message(self.aid.localname, 'Mensaje  recibido from {}'.format(message.content))
        display_message(self.aid.localname, 'Mensaje  recibido from {}'.format(message.sender.name))
        #received OK
        if message.performative == ACLMessage.PROPOSE:
            display_message(self.aid.localname, 'Mensaje OK recibido from {}'.format(message.content))
            mensaje=json.loads(message.content)
            display_message(self.aid.localname, 'Mensaje OK recibido from {}'.format(message.sender.name))
            #the reception of the message is acknowledged
            for el in self.agent_list:
                if str(self.orden-1) in str(el):
                    self.sendINFORMnoAck(el,"{\"tipo\":"+str(0)+",\"indice\":"+str(mensaje['indice'])+"}")
            #revise agent_view
            self.agentview.update({mensaje['key']: mensaje['value']})
            #check if there are repeated codes
            if int(mensaje['key']) == (self.orden -1):
                self.agentcodigos = []
                for element in mensaje['cilindros']:
                    self.agentcodigos.append(int(element))
            posiestados = mensaje['key'] - 16
            self.enviarokcambioestado = False
            #update knowledge
            for element in range(0,posiestados+1):
                if self.estadoagentesdiametro[element] != mensaje['estadiam'][element]:
                    self.enviarokcambioestado = True
                    self.estadoagentesdiametro[element] = mensaje['estadiam'][element]
                if self.estadoagentescodigos1[element] != mensaje['estacod1'][element]:
                    self.enviarokcambioestado = True
                    self.estadoagentescodigos1[element] = mensaje['estacod1'][element]
                    self.estadoagentescodigos2[element] = mensaje['estacod2'][element]
                self.indicesnogood[element]=mensaje['indicesnogood'][element]
                self.indicesok[element]=mensaje['indicesok'][element]
            for element in range(0, len(self.estadoagentesdiametro)):
                display_message(self.aid.localname, 'Despues del Ok '+str(self.orden)+' tengo ' + str(self.estadoagentescodigos1[element]))
            #check agent_view
            self.checkview()
        #received nogood
        elif message.performative == ACLMessage.REJECT_PROPOSAL:
            display_message(self.aid.localname, 'Mensaje NOGOOD recibido from {}'.format(message.sender.name))
            display_message(self.aid.localname, 'Mensaje NOGOOD recibido from {}'.format(message.content))
            mensaje = json.loads(message.content)
            #send reception acknowledgement
            for el in self.agent_list:
                if str(self.orden+1) in str(el):
                    self.sendINFORMnoAck(el, "{\"tipo\":" + str(1) + ",\"indice\":" + str(mensaje['indice']) + "}")
            #for every nogood received
            for element in mensaje['nogoods']:
                #add to a dictionary with the key (stand) and the value an array
                #the nogood is recorded as a new constraint
                self.nogoods.update({element['key']: element['value']})
                vecino = ""
                #if the nogood contains an agent that is not the current agent
                if str(element['key']) not in str(self.orden):
                    for el in self.agent_list:
                        if str(element['key']) in el:
                            vecino = el
                    if not vecino in self.neighbors_list:
                        # when nogood contains an agent xk that is not its neighbour
                        #add xk to its neighbours
                        self.agentview.update({element['key']: element['value']})
                        self.neighbors_list.append(vecino)
                    else:
                        self.agentview.update({element['key']: element['value']})
                else:
                    #if the agent is the current agent
                    #if the problem are the codes
                    if len(element['codigos']) != 0:
                        display_message(self.aid.localname, 'El problema son los codigos')
                        #if the nogood comes from the next agent
                        if self.orden == element['key'] - 1:
                            # if there are two problematic codes
                            if len(element['codigos']) >= 1:
                                #the codes are put in nogoods
                                for e in element['codigos']:
                                    if not e in self.nogoodscodigos:
                                        self.nogoodscodigos.append(e)
                        self.checkview()
                    #if the problem is the diameter
                    if len(element['codigos']) == 0:
                        display_message(self.aid.localname,'El problema es el diametro')
                        if element['value'] in self.dominio_actual:
                            #the new nogood is removed from the domain
                            self.dominio_actual.remove(element['value'])
                            self.checkview()
        #if it is an inform message
        elif message.performative == ACLMessage.INFORM:

            display_message(self.aid.localname, 'Mensaje INFORM recibido from {}'.format(message.content))
            display_message(self.aid.localname, 'Mensaje INFORM recibido from {}'.format(message.sender.name))
            #check if content is a json
            if is_json(message.content):
                mensaje = json.loads(message.content)
                #check if it is an acknowledgement of reception the type and the number of message
                if mensaje['tipo']==0 and mensaje['indice'] in self.recibidosconfirmacionok:
                    display_message(self.aid.localname, "indice "+str(mensaje['indice']))
                    display_message(self.aid.localname, str(self.recibidosconfirmacionok))
                    self.recibidosconfirmacionok.remove(int(mensaje['indice']))

                elif mensaje['tipo']==1 and mensaje['indice'] in self.recibidosconfirmacionnogood:
                    self.recibidosconfirmacionnogood.remove(int(mensaje['indice']))
                elif mensaje['tipo']==2 and mensaje['indice'] in self.recibidosconfirmacioninform:
                    self.recibidosconfirmacioninform.remove(int(mensaje['indice']))


        #received terminate
        elif message.performative == ACLMessage.CANCEL:
            display_message(self.aid.localname, 'Mensaje CANCEL recibida from {}'.format(message.sender.name))
            self.value = 0
            self.codigoscilindros = []
        #received PROPAGATE
        elif message.performative == ACLMessage.PROPAGATE:
            display_message(self.aid.localname, 'Mensaje PROPAGATE {}'.format(message.content))
            mensaje = json.loads(message.content)
            for el in self.agent_list:
                if str(mensaje['key']) in str(el):
                    self.neighbors_list.append(el)
        else:
            #received other type of message
            pepito = 1


        for ele in range(0,len(self.estadoagentesdiametro)):
            display_message(self.aid.localname,  str(self.estadoagentesdiametro[ele])+" "+str(self.estadoagentescodigos1[ele])+" "+str(self.estadoagentescodigos2[ele]))

if __name__ == '__main__':
    #number of stands considered
    agents_per_process = numerocajas
    c = 0
    #agents
    listaagentes=[]
    agents = list()
    #neighbours
    vecinos=[]
    #rolls per stand
    cilindrosporcaja={}
    #constraints
    restricciones = []
    #compatible rolls with the stands
    miscompatibles=[]
    #jobs to be performed
    with open('datos14.json') as json_file:
        data = json.load(json_file)
        for p in data['Restricciones']:
            restricciones.append(Restricciones(p['caja1'], p['caja2'], p['cantidad'], p['factor'], p['tipo']))
        for p in data['Compatibles']:
            cilscompatibles = []
            for s in p['Cilindros']:
                cilscompatibles.append(Roll(s['cod_interno'], s['diam_inicial'], s['diam_final'], s['diam_actual'], s['cod_estado'],s['geometria'],s['numposiciones']))
            miscompatibles.append(CilindrosCompatibles(p['caja'],cilscompatibles))
    #the different agents are created given the number of stands considered
    for i in range(agents_per_process):
        #the port is 20000, 21000, 22000 etc
        port = 20000 + c
        #the number of agent is 16, 17, etc
        numagente=16+i
        #the neighbours are given by the constraints
        vecis=[]
        for restri in restricciones:
            if restri.caja1 == numagente:
                vecis.append(restri.caja2)
        vecinos.append(vecis)
        #name of the agent
        agent_name ='p'+str(numagente) + '@localhost:{}'.format(port)
        localname, adress = agent_name.split('@')
        listaagentes.append(localname)
        diametrosabt=[]
        codigocilindros = {}
        #compatible rolls with a stand
        for el in miscompatibles[i].compatibles:
            if not el.diam_actual in diametrosabt:
                diametrosabt.append(el.diam_actual)
                codigocilindros.update({el.diam_actual:[]})
                codigocilindros[el.diam_actual].append(el.cod_interno)
            else:
                codigocilindros[el.diam_actual].append(el.cod_interno)
        #an agent is created
        agente = Agente(AID(name=agent_name),numagente,[],diametrosabt,[],restricciones,codigocilindros)
        #it is appended to the list of agents
        agents.append(agente)
        c += 1000
    cuenta = 0
    port = 20000 + c
    agent_name = 'super_agent_{}@localhost:{}'.format(port, port)
    localname, adress = agent_name.split('@')
    #controller agent
    agente_super = SuperAgente(AID(name=agent_name),[])
    #the controller agent is added to the list of agents
    agente_super.agent_list = copy.deepcopy(listaagentes)
    for i in agents:
        for j in vecinos[cuenta]:
            if j%16<len(listaagentes):
                i.neighbors_list.append(listaagentes[j%16])
        cuenta = cuenta + 1
        i.agent_list = copy.deepcopy(listaagentes)
        i.agent_list.append(localname)
    agents.append(agente_super)
    #the algorithm is started
    start_loop(agents)