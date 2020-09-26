
import heapq
import random
import matplotlib.pyplot as plt
import numpy as np
#np.random.exponential(1/lambda, 5) generates 5 exponental random variable 


# Parameters
class Params:
    def __init__(self, lambd, mu, k):
        self.lambd = lambd  # interarrival rate
        self.mu = mu  # service rate
        self.k = k
    # Note lambd and mu are not mean value, they are rates i.e. (1/mean)

# Write more functions if required


# States and statistical counters
class States:
    def __init__(self,sim):
        # States
        self.queue = []
        # Declare other states variables that might be needed
        #________________________________miyad codes below________________________
        self.serverStatus = []
        for i in range(sim.params.k):
            self.serverStatus.append('IDLE')
        self.timeLastEvent = 0
        #self.numCustDelayed = 0
        self.totalDelay = 0 #total spent time of served customer 
        self.areaUnderQt = 0
        self.areaUnderBt = 0 # how much time the server is busy
        self.lastArrivalTime = 0
        self.lastDepartTime = 0
        self.serverStartTime = 0
        self.noOfCustDelayed = 0

        #________________________________miyad codes above________________________
        # Statistics
        self.util = 0.0
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0
    def update(self, sim, event):
        self.totalDelay += (len(self.queue)*(sim.simclock-self.timeLastEvent))
        busyServer = 0
        for i in range(sim.params.k):
            if self.serverStatus[i] == 'BUSY':
                busyServer += 1
        self.areaUnderBt = self.areaUnderBt + (sim.simclock-self.timeLastEvent)*busyServer
        self.timeLastEvent = sim.simclock #as sim time is not updated yet
        
        if event.eventType == 'ARRIVAL':
            self.areaUnderQt += len(self.queue)*(event.eventTime-self.lastArrivalTime)
            if busyServer < sim.params.k:
                j = 0
                while self.serverStatus[j] == 'BUSY':
                    j = j+1
                if j < sim.params.k:
                    self.serverStatus[j] = 'BUSY'
                #self.serverStartTime = sim.simclock
            else:
                self.queue.append(event.eventTime)
                self.noOfCustDelayed+=1
            self.lastArrivalTime = event.eventTime
        elif event.eventType == 'DEPART':
            self.areaUnderQt += len(self.queue)*(event.eventTime-self.lastDepartTime)
            #print("One DepartHappened________________________________________")
            if len(self.queue) > 0:
                front = self.queue.pop(0)
            else:
                j = 0
                while self.serverStatus[j] == 'IDLE':
                    j = j+1
                    if j >= sim.params.k:
                        break
                if j < sim.params.k:
                    self.serverStatus[j] = 'IDLE'
                #self.areaUnderBt += (sim.simclock-self.serverStartTime)
            self.lastDepartTime = event.eventTime
            self.served += 1


        #self.timeLastEvent = event.eventTime
        # Complete this function
        #None

    def finish(self, sim):
        # Complete this function
        #print(self.queue)
        self.avgQlength = self.areaUnderQt/sim.simclock
        self.util = self.areaUnderBt/sim.maxSimTime
        self.avgQdelay = self.totalDelay / self.noOfCustDelayed
        #print("simclock = ",sim.simclock," areaUnderQt = ",self.areaUnderQt)
        #None

    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print('MMk Results: lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        print('MMk Total customer served: %d' % (self.served))
        print('MMk Average queue length: %lf' % (self.avgQlength))
        print('MMk Average customer delay in queue: %lf' % (self.avgQdelay))
        print('MMk Time-average server utility: %lf' % (self.util))

    def getResults(self, sim):
        return (self.avgQlength, self.avgQdelay, self.util)

# Write more functions if required


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType


class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim): 
        #Complete this function
        #********************miyad code below****************************
        #this should start every machine of this simulator such as start next arival time 
        #scheduler, to begin 
        # it may start the first event(arrival event) then arrival event will determine next
        #arrival
        #print("I am startevent process. lambda= ",sim.params.lambd)
        a = np.random.exponential(1/sim.params.lambd,1) #next arrival time
        #print(a)
        eventTime = a[0]+sim.states.lastArrivalTime
        sim.scheduleEvent(ArrivalEvent(eventTime,sim))
        sim.scheduleEvent(ExitEvent(sim.maxSimTime,sim))
        #None


class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        # Complete this function
        None


class ArrivalEvent(Event):
    # Write __init__ function
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim
    def process(self, sim):
        #sim.states.queue.append(self.eventTime)
        a = np.random.exponential(1/sim.params.lambd,1)
        eventTime = a[0]+sim.states.lastArrivalTime
        sim.scheduleEvent(ArrivalEvent(eventTime,sim))
        isAtleastOneServerBusy = False
        for i in range(sim.params.k):
            if sim.states.serverStatus[i] == 'BUSY':
                isAtleastOneServerBusy = True
                break
        if isAtleastOneServerBusy and len(sim.states.queue)==0:
            b = np.random.exponential(1/sim.params.mu,1)
            sim.scheduleEvent(DepartureEvent(b[0]+sim.simclock,sim))
        # Complete this function
        #None


class DepartureEvent(Event):
    # Write __init__ function
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'DEPART'
        self.sim = sim 
    def process(self, sim):
        # Complete this function
        #None
        isAtleastOneServerBusy = False
        for i in range(sim.params.k):
            if sim.states.serverStatus[i] == 'BUSY':
                isAtleastOneServerBusy = True
                break
        if isAtleastOneServerBusy:
            serviceTime = np.random.exponential(1/sim.params.mu,1)
            sim.scheduleEvent(DepartureEvent(sim.states.lastDepartTime+serviceTime[0],sim))
        #$print("Yes one DepartureEvent happened___________________________")



class Simulator:
    def __init__(self, seed, maxSimTime):
        self.maxSimTime = maxSimTime
        self.eventQ = []
        self.simclock = 0
        self.seed = seed
        self.params = None
        self.states = None

    def initialize(self):
        self.simclock = 0
        self.scheduleEvent(StartEvent(0, self))

    def configure(self, params, states):
        self.params = params
        self.states = states
    def configParam(self, params):
        self.params = params

    def now(self):
        return self.simclock

    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))

    def run(self):
        random.seed(self.seed)
        self.initialize()

        while len(self.eventQ) > 0:
            #print(len(self.states.queue))
            time, event = heapq.heappop(self.eventQ)

            if event.eventType == 'EXIT':
                #print("Yes this is exit event , i am quiting from here")
                break

            
            if self.states != None:
                self.states.update(self, event)

            #print(event.eventTime, 'Event', event)
            self.simclock = event.eventTime
            event.process(self)
            

        self.states.finish(self)

    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)
    def printAnalyticExp1(self):
        print("Aanlytic results are: ")
        l = self.params.lambd
        m = self.params.mu 
        print("Average Queue length = ", l*l/(m*(m-l)))
        print("Average customer Delay = ", l/(m*(m-l)))
        print("Time-Average Server utility = ", l/m)


def experiment1():
    seed = 101
    maxSimTime = 500000
    sim = Simulator(seed, maxSimTime)
    params = Params(5.0/60,8.0/60,1)
    sim.configParam(params)
    sim.configure(params, States(sim))
    sim.run()
    print("____________EXPERIMENT01________________________")
    sim.printResults()
    sim.printAnalyticExp1()



def experiment2():
    seed = 110
    maxSimTime = 500
    mu = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for ro in ratios:
        sim = Simulator(seed,maxSimTime)
        sim.configParam(Params(mu*ro,mu,1))
        sim.configure(Params(mu * ro, mu, 1), States(sim))
        sim.run()

        length, delay, utl = sim.getResults()
        avglength.append(length)
        avgdelay.append(delay)
        util.append(utl)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(ratios, avglength)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(ratios, avgdelay)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(ratios, util)
    plt.xlabel('Ratio (ro)')
    plt.ylabel('Util')

    plt.show()


def experiment3():
    # Similar to experiment2 but for different values of k; 1, 2, 3, 4
    # Generate the same plots
    # Fix lambd = (5.0/60), mu = (8.0/60) and change value of k
    seed = 110
    maxSimTime = 500
    mu = 1000.0 / 60
    k_set = [u for u in range(1, 11)]
    #ratios hols the set of k values 1,2,3,4,5,6..,k
    avglength = []
    avgdelay = []
    util = []
    mu = 8.0/60
    lambd = 5.0/60
    for k in k_set:
        sim = Simulator(seed,maxSimTime)
        sim.configParam(Params(lambd,mu,k))
        sim.configure(Params(lambd, mu, k), States(sim))
        sim.run()

        length, delay, utl = sim.getResults()
        avglength.append(length/k)
        avgdelay.append(delay)
        util.append(utl/k)

    plt.figure(2)
    plt.subplot(311)
    plt.plot(k_set, avglength)
    plt.xlabel('# of Server (k)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(k_set, avgdelay)
    plt.xlabel('# of Server (k)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(k_set, util)
    plt.xlabel('# of Server (k)')
    plt.ylabel('Util')

    plt.show()

def main():
    experiment1()
    experiment2()
    experiment3()


if __name__ == "__main__":
    main()
