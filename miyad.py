import heapq
import random
import matplotlib.pyplot as plt
import numpy as np
import sys
# Parameters
class Params:
    def __init__(self, lambd, mu, k,total_q):
        self.lambd = lambd  # interarrival rate
        self.mu = mu  # service rate
        self.k = k
        self.total_q = total_q #number of queue
    # Note lambd and mu are not mean value, they are rates i.e. (1/mean)

# Write more functions if required
 

# States and statistical counters
class States:
    def __init__(self):
        # States
        self.queue = [] #here i didn't uese this default queue. I used server's indivigual queue_list for this purpose 
        # Declare other states variables that might be needed

        # Statistics
        self.util = 0.0
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0
        #________________________MIYAD's Code_________________________________
        self.is_server_busy = []
        self.total_delay = 0
        self.area_qt = 0
        self.area_bt = 0
        self.last_event_time = 0
        #________________________Above_mycCoe_________________________________
    def config_state(self, params):
        for i in range(params.k):
            self.queue.append([])
        for i in range(params.total_q):
            self.is_server_busy.append(False)

    def update(self, sim, event):
        if event.eventType == 'ARRIVAL':
            is_getting_service = False
            for i in range(sim.params.k):
                if not sim.states.is_server_busy[i]:
                    sim.states.is_server_busy[i] = True
                    is_getting_service = True
                    break
            if not is_getting_service:
                min_len = 10**18 #infinity 10^18 initally
                index_of_shortes_queue = -1
                for i in range(sim.params.total_q):
                    if min_len > len(sim.states.queue[i]):
                        min_len = len(sim.states.queue[i])
                        index_of_shortes_queue = i
                    sim.states.queue[index_of_shortes_queue].append(event.eventTime)

        elif event.eventType == 'DEPART':
            busy_server_set = []
            for i in range(sim.params.k):
                if sim.states.is_server_busy[i]:
                    busy_server_set.append(i)
            #as depart happening busy_server_set is definitly not empty
            depart_at_server = int(np.random.uniform(0,len(busy_server_set)-0.1,1)[0])
            queq_no = min(sim.params.total_q-1,busy_server_set[depart_at_server])
            arival_last_person = -1
            if len(self.queue[queq_no]) > 0:
                arrival_last_person = self.queue[queq_no].pop(0)
            else:
                self.is_server_busy[busy_server_set[depart_at_server]] =  False
            #arival_time_of_departing_cust = self.queue

            

    def finish(self, sim):
        # Complete this function
        None

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
    def __init__(self, sim, eventType, eventTime):
        self.eventType = eventType
        self.sim = sim
        self.eventTime = eventTime

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
        # Complete this function
        first_arrival_time = np.random.exponential(1/sim.params.lambd,1)[0] #after this time nex arrive 
        first_depart_time = first_arrival_time + np.random.exponential(1/sim.params.mu,1)[0]
        sim.scheduleEvent(ArrivalEvent(sim,first_arrival_time))
        sim.scheduleEvent(DepartureEvent(sim,first_depart_time))
        sim.scheduleEvent(ExitEvent(sim.max_sim_time,'EXIT'))


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
    def __init__(self, sim, eventTime):
        Event.__init__(self, sim, 'ARRIVAL', eventTime)
    def process(self, sim):
        next_arrial_time = self.eventTime + np.random.exponential(1/sim.params.lambd,1)[0]
        next_depart_time = next_arrial_time + np.random.exponential(1/sim.params.mu,1)[0]
        sim.scheduleEvent(ArrivalEvent(sim,next_arrial_time))
        sim.scheduleEvent(DepartureEvent(sim,next_depart_time))

class DepartureEvent(Event):
    # Write __init__ function
    def __init__(self,sim,eventTime):
        Event.__init__(self,sim,'DEPART',eventTime)
    def process(self, sim):
        None



class Simulator:
    def __init__(self, seed,max_sim_time):
        self.eventQ = []
        self.simclock = 0
        self.seed = seed
        self.params = None
        self.states = None
        #__________________________
        self.max_sim_time = max_sim_time
    def initialize(self):
        self.simclock = 0
        self.scheduleEvent(StartEvent(0, self))

    def configure(self, params, states):
        self.params = params
        self.states = states
        self.states.config_state(params)

    def now(self):
        return self.simclock

    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))

    def run(self):
        random.seed(self.seed)
        self.initialize()

        while len(self.eventQ) > 0:
            time, event = heapq.heappop(self.eventQ)
            if event.eventType == 'EXIT':
                print("Simulation ended with ExitEvent at time ",time)
                break

            if self.states != None:
                self.states.update(self, event)

            print(event.eventTime, 'Event', event)
            self.states.last_event_time = self.simclock
            #self.simclock = event.eventTime
            self.simclock = time # i didn't use eventTime in event Because each event is pushed with associated time in heap
            event.process(self)

        self.states.finish(self)

    def printResults(self):
        self.states.printResults(self)

    def getResults(self):
        return self.states.getResults(self)


def experiment1(max_sim_time):
    seed = 101
    sim = Simulator(seed,max_sim_time)
    sim.configure(Params(5.0 / 60, 8.0 / 60, 1, 1), States())
    sim.run()
    sim.printResults()


def experiment2(max_sim_time):
    seed = 110
    mu = 1000.0 / 60
    ratios = [u / 10.0 for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for ro in ratios:
        sim = Simulator(seed,max_sim_time)
        sim.configure(Params(mu * ro, mu, 1,1), States())
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
    None


def main():
    max_sim_time = int(sys.argv[1])
    experiment1(max_sim_time)
    #experiment2(max_sim_time)
    #experiment3()


if __name__ == "__main__":
    main()
