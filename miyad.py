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
        self.depart_at_server = 0
        self.total_customer = 0
        #________________________Above_mycCoe_________________________________
    def config_state(self, params):
        for i in range(params.total_q):
            self.queue.append([])
        for i in range(params.k):
            self.is_server_busy.append(False)
    def is_all_server_idle(self):
        is_idle = True
        for i in self.is_server_busy:
            if i:
                is_idle = False
                break
        return is_idle
    def depart_from_which_server(self,sim):
        busy_server_set = []
        for i in range(sim.params.k):
            if sim.states.is_server_busy[i]:
                busy_server_set.append(i)
        #as depart happening busy_server_set is definitly not empty
        ind_in_busy_set = int(np.random.uniform(0,len(busy_server_set)-0.1,1)[0])
        return busy_server_set[ind_in_busy_set]


    def update(self, sim, event):
        sum_qlen, tota_busy_server = 0, 0
        for i in range(sim.params.total_q):
            sum_qlen+=len(self.queue[i])
        for i in range(sim.params.k):
            if self.is_server_busy[i]:
                tota_busy_server+=1
        self.area_bt+=tota_busy_server*(event.eventTime-self.last_event_time)
        self.area_qt += sum_qlen*(event.eventTime-self.last_event_time)
        
        if event.eventType == 'ARRIVAL':
            self.total_customer += 1
        if event.eventType == 'DEPART':
            self.served+=1
            self.depart_at_server = self.depart_from_which_server(sim)
            queq_no = min(sim.params.total_q-1,self.depart_at_server)
            if len(self.queue[queq_no]) > 0:
                self.total_delay+=(event.eventTime-self.queue[queq_no][0])
        
    def finish(self, sim):
        # Complete this function
        self.avgQlength = self.area_qt/sim.max_sim_time
        self.avgQdelay = self.total_delay/self.served
        self.util = self.area_bt / sim.max_sim_time
        """print("areaqt = ",self.area_qt)
        print("total cust = ",self.total_customer, " served= ",self.served)
        print("average Q len = ",self.area_qt/sim.max_sim_time)
        print("my avg_delay = ",self.area_qt/self.total_customer)
        print("actual avg delay = ",self.total_delay/self.served)
        print("utility = ",self.area_bt/sim.max_sim_time)
        None"""

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
        sim.scheduleEvent(ArrivalEvent(sim,first_arrival_time))
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
        if sim.states.is_all_server_idle():
            next_depart_time = self.eventTime+np.random.exponential(1/sim.params.mu,1)[0]
            sim.scheduleEvent(DepartureEvent(sim,next_depart_time))
        sim.scheduleEvent(ArrivalEvent(sim,next_arrial_time))
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
            sim.states.queue[index_of_shortes_queue].append(self.eventTime)


        
        

class DepartureEvent(Event):
    # Write __init__ function
    def __init__(self,sim,eventTime):
        Event.__init__(self,sim,'DEPART',eventTime)
    def process(self, sim):
        queq_no = min(sim.params.total_q-1,sim.states.depart_at_server)
        if len(sim.states.queue[queq_no]) > 0:
            sim.states.queue[queq_no].pop(0)
        else:
            sim.states.is_server_busy[sim.states.depart_at_server] =  False
        if queq_no > 0:
            if len(sim.states.queue[queq_no-1])-len(sim.states.queue[queq_no]) >= 2:
                sim.states.queue[queq_no].append(sim.states.queue[queq_no-1].pop(-1))
        if queq_no < sim.params.total_q-1:
            if len(sim.states.queue[queq_no+1])-len(sim.states.queue[queq_no]) >= 2:
                sim.states.queue[queq_no].append(sim.states.queue[queq_no+1].pop(-1))
        if not sim.states.is_all_server_idle():
            next_depart = self.eventTime+np.random.exponential(1/sim.params.mu,1)[0]
            sim.scheduleEvent(DepartureEvent(sim,next_depart))

class Simulator:
    def __init__(self, seed,max_sim_time):
        self.eventQ = []
        self.simclock = 0
        self.seed = seed
        self.params = None
        self.states = None
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
                break
            
            self.states.last_event_time = self.simclock
            self.simclock = time
            if self.states != None:
                self.states.update(self, event)
            #print(event.eventTime, 'Event', event)
            
            
            #self.simclock = event.eventTime
             # i didn't use eventTime in event Because each event is pushed with associated time in heap
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


def experiment3(max_sim_time):
    seed = 110
    lambd, mu = 5.0/60, 8.0 / 60
    k_set = [u for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for k in k_set:
        sim = Simulator(seed,max_sim_time)
        sim.configure(Params(lambd, mu, k,1), States())
        sim.run()

        length, delay, utl = sim.getResults()
        avglength.append(length/k)
        avgdelay.append(delay)
        util.append(utl/k)
    print(util)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(k_set, avglength)
    plt.xlabel('Number of Server (k)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(k_set, avgdelay)
    plt.xlabel('Number of Server (k)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(k_set, util)
    plt.xlabel('Number of Server (k)')
    plt.ylabel('Util')
    plt.show()
    # Similar to experiment2 but for different values of k; 1, 2, 3, 4
    # Generate the same plots
    # Fix lambd = (5.0/60), mu = (8.0/60) and change value of k

def experiment4(max_sim_time):
    seed = 110
    lambd, mu = 5.0/60, 8.0 / 60
    k_set = [u for u in range(1, 11)]

    avglength = []
    avgdelay = []
    util = []

    for k in k_set:
        sim = Simulator(seed,max_sim_time)
        sim.configure(Params(lambd, mu, k,k), States())
        sim.run()

        length, delay, utl = sim.getResults()
        avglength.append(length/k)
        avgdelay.append(delay)
        util.append(utl/k)
    print(util)

    plt.figure(1)
    plt.subplot(311)
    plt.plot(k_set, avglength)
    plt.xlabel('Number of Server (k) and Q(k)')
    plt.ylabel('Avg Q length')

    plt.subplot(312)
    plt.plot(k_set, avgdelay)
    plt.xlabel('Number of Server (k) and Q(k)')
    plt.ylabel('Avg Q delay (sec)')

    plt.subplot(313)
    plt.plot(k_set, util)
    plt.xlabel('Number of Server (k) and Q(k)')
    plt.ylabel('Util')
    plt.show()

def main():
    max_sim_time = int(sys.argv[1])
    experiment1(max_sim_time)
    experiment2(max_sim_time)
    experiment3(max_sim_time)
    experiment4(max_sim_time)
    


if __name__ == "__main__":
    main()
