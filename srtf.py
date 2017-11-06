import cola
import time
import procesos as ps
import recursos as rs
import queue
import threading
import numpy as np
class Procesador(threading.Thread):
    def __init__(self,idProcesador,*args):
        threading.Thread.__init__(self)
        self.idProcesador=idProcesador 
        self.proceso=None
        self.lis=cola.Cola()
        self.ter=cola.Cola()
        self.blo=cola.Cola()
        self.sus=cola.Cola()
        self._args=args
        self.uso=True
    def __str__(self):
        return str(self.idProcesador)
    def run(self):
        while self.uso:
            self.usarProcesador(*self._args)
    def usarProcesador(self,q):
        while not self.proceso==None or not q.empty() or not self.lis.es_vacia() or not self.sus.es_vacia() or not self.blo.es_vacia():
            time.sleep(0.01)
            
            if not q.empty():self.asignar(q.get())
            self.lis.ordenar()
 
            if not self.lis.es_vacia() and self.proceso==None:
                posible=self.lis.desencolar()
                if posible.recurso.libre:
                    self.ocupado=True
                    self.proceso=posible
                    self.proceso.recurso.utilizar()
                    print("\ncomenzando proceso",self.proceso,"en el procesador",self)
                else:
                    posible.bloquear()
                    self.blo.encolar(posible)
            elif not self.lis.es_vacia() and not self.proceso==None:
                posible=self.lis.desencolar()
                if self.proceso.t>posible.t and posible.recurso.libre:
                    print("el proceso",posible,"entro cuando",self.proceso,"estaba en el procesador",self)
                    self.proceso.suspender()
                    self.sus.encolar(self.proceso)

                    self.proceso=posible
                    self.proceso.recurso.utilizar()
                else:
                    self.lis.encolar(posible)
            self.contarColaBlo()
            self.contarColaLis()            
            self.revisarColaSus()
            self.revisarColaBlo()
            
            if not self.proceso==None:
                self.proceso.procesar()
                if self.proceso.t==0:
                    self.proceso.recurso.liberar()                
                    print("\nterminando proceso",self.proceso,"en el procesador",self,",sus",self.proceso.sus,",lis",self.proceso.lis,",blo",self.proceso.blo,",zona critica",self.proceso.zc)
                    self.ter.encolar(self.proceso)
                    self.proceso=None
                    q.task_done()
        print("termino el procesador",self,"lista de tareas completadas en este procesador:",end=" ")
        for i in range(self.ter.tam):
            print(self.ter.desencolar(),end=" ")
        self.uso=False
        
    def revisarColaSus(self):
        tam = self.sus.tam
        for i in range(tam):
            n=self.sus.desencolar()
            n.tr-=1
            n.sus+=1
            if n.tr==0:
                self.asignar(n)
                print("\nse saco el proceso",n,"de la cola de suspendidos y entro a la cola de listo")
            else:
                self.sus.encolar(n)


                
    def revisarColaBlo(self):

        for i in range(self.blo.tam):
            posible=self.blo.desencolar()
            if posible.recurso.libre:
                self.asignar(posible)
                print("\nse saco el proceso",posible," de la cola de bloqueados y entro en la cola de listos")
            else:
                self.blo.encolar(posible)

    def contarColaLis(self):
        tam = self.lis.tam

        for i in range(tam):
            n=self.lis.desencolar()
            n.lis+=1
            self.lis.encolar(n)
            

    def contarColaBlo(self):
        tam = self.blo.tam
        for i in range(self.blo.tam):
            n=self.blo.desencolar()
            n.blo+=1
            self.blo.encolar(n)
    
    def asignar(self,proceso):
        self.lis.encolar(proceso)

class cliente:
    def __init__(self):
        self.numPo=0
        self.numMa=0
        self.numEn=0
        
        self.recursos=[rs.Horno(),rs.Cuchillos(),rs.Licuadora()]
        
        self.cola1=queue.Queue()
        self.cola1.put(ps.Malteada(0,self.recursos[2]))
        self.numMa+=1

        self.cola2=queue.Queue()
        self.cola2.put(ps.PolloConPapas(0,self.recursos[0]))
        self.numPo+=1

        self.cola3=queue.Queue()
        self.cola3.put(ps.Ensalada(0,self.recursos[1])) 
        self.numEn+=1

        self.colaProcesadores=queue.Queue()
        
        self.procesador1=Procesador(1,self.cola1)        
        self.procesador2=Procesador(2,self.cola2)      
        self.procesador3=Procesador(3,self.cola3)

    def iniciar(self):
        self.procesador1.start()
        self.procesador2.start()
        self.procesador3.start()
        for i in range(15):
            s=np.random.randint(3)
            if s==0:
                self.cola1.put(self.crear_pedido_aleatorio())
            elif s==1:
                self.cola2.put(self.crear_pedido_aleatorio())
            else:
                self.cola3.put(self.crear_pedido_aleatorio())
        self.cola1.join()
        self.cola2.join()
        self.cola3.join()



    def crear_pedido_aleatorio(self):
        aleatorio=np.random.randint(3)
        if aleatorio==0:
            a=ps.PolloConPapas(self.numPo,self.recursos[0])
            self.numPo+=1
        elif aleatorio==1:
            a=ps.Ensalada(self.numEn,self.recursos[1])
            self.numEn+=1
        else:
            a= ps.Malteada(self.numMa,self.recursos[2])
            self.numMa+=1
        return a


cliente = cliente()
cliente.iniciar()
