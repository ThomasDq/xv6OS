#HOW TO RUN: change variables if wanted - lines 11-15 - and run python3 3_philosophers.py number_of_philosophers number_of_meals
#python3 3_philosophers.py will use default values

import sys, random
from threading import Thread, Semaphore
from time import sleep
from timeit import Timer


# Which implementation to test?
FOOTMAN = True
LEFTHANDED = True
TANENBAUM = True
maxlength = 1         #rng result multiplier
rng_seed = 42

#default values
n_philosophers = 5
meals = 2
eatinglength = 3
thinkinglength = 3

# Thread safe print
printf = lambda x: sys.stdout.write("%s\n" % x)

#Tanenbaum solution global variables
state = [] 
sem = []
mutex = Semaphore(1)

class Philosopher:
    
    def getforkfootman(self):
        global forks
        footman.acquire()
        forks[self.rfork].acquire()
        forks[self.lfork].acquire()
            
    def putforkfootman(self):
        global forks
        forks[self.rfork].release()
        forks[self.lfork].release()
        footman.release()
                              
    def footman_run(self):
        global footman, eatinglength, thinkinglength, meals
        for _ in range(0,meals):
#             printf(self.name + " waits for forks")
            self.getforkfootman()
#             printf(self.name + " eats")
            sleep(eatinglength)
            self.putforkfootman()
#             printf(self.name + " puts forks " + str(self.lfork)+" "+ str(self.rfork) + " back")
            sleep(thinkinglength)
        
    def getfork(self):
        global forks
        if self.righthanded:
            forks[self.rfork].acquire()
            forks[self.lfork].acquire()
        else:
            forks[self.lfork].acquire()
            forks[self.rfork].acquire()
            
    def putfork(self):
        global forks
        forks[self.rfork].release()
        forks[self.lfork].release()  
            
    def lefthanded_run(self):
        global eatinglength, thinkinglength, meals
        for _ in range(0,meals):
#             printf(self.name + " waits for forks")
            self.getfork()
#             printf(self.name + " eats")
            sleep(eatinglength)
            self.putfork()
#             printf(self.name + " puts forks " + str(self.lfork)+" "+ str(self.rfork) + " back")
            sleep(thinkinglength) 
    
    ## Tanenbaum implementation        
    def getforktanenbaum(self):
        global mutex, sem, state
        mutex.acquire()
        state[self.idx] = 'hungry'
        self.test(self.idx)                             # check neighbors’ states
        mutex.release()
        sem[self.idx].acquire()                         # acquire on my own semaphore
        
    def putforktanenbaum(self):
        global mutex, state, n_philosophers
        mutex.acquire()
        state[self.idx] = 'thinking'
        self.test((self.idx + 1) % n_philosophers)      # release neighbors if they can eat
        self.test((self.idx - 1) % n_philosophers)
        mutex.release()
    
    def test(self,i):
        global sem, state, n_philosophers
        if state[i] == 'hungry' and not state[(i+1)% n_philosophers] == 'eating' and not state[(i-1)% n_philosophers] == 'eating':
            state[i] = 'eating'
            sem[i].release()                            # this releases me OR a neighbor   

    def tanenbaum_run(self):
        global eatinglength, thinkinglength, meals
        for _ in range(0,meals):
#             printf(self.name + " waits for forks")
            self.getforktanenbaum()
#             printf(self.name + " eats")
            sleep(eatinglength)
#             printf(self.name + " puts forks " + str(self.lfork)+" "+ str(self.rfork) + " back")
            self.putforktanenbaum()
            sleep(thinkinglength)        
    ##
    
    def __init__(self, idx):
        global n_philosophers
        self.lfork = idx
        self.rfork = (idx - 1) % n_philosophers
        self.idx = idx
        self.name = "Philosopher " + str(idx)
        self.righthanded = True


def timefootman():
    threads = [Thread(target = philosophers[i].footman_run) for i in range(0,n_philosophers)]
    for t in threads: t.start()
    for t in threads: t.join()

def timelefthanded():
    threads = [Thread(target = philosophers[i].lefthanded_run) for i in range(0,n_philosophers)]
    for t in threads: t.start()
    for t in threads: t.join()
    
def timetanenbaum():
    threads = [Thread(target = philosophers[i].lefthanded_run) for i in range(0,n_philosophers)]
    for t in threads: t.start()
    for t in threads: t.join()
    
if __name__ == '__main__':
    
    rng = random.Random()
    rng.seed(rng_seed) 
    eatinglength = maxlength*rng.random()
    thinkinglength = maxlength*rng.random()

    if len(sys.argv) == 3:
        n_philosophers = int(sys.argv[1])
        meals = int(sys.argv[2])
    
    printf("\nConfiguration:")
    printf("Number of philosopher = " + str(n_philosophers) +". Number of meals = " + str(meals)+ ". Seed = " + str(rng_seed) + ".")
    printf("Eating length = " + str(eatinglength) +". Thinking length = " + str(thinkinglength)+ ".\n")
    printf("Time spend sleeping per philosopher = " + str((eatinglength+thinkinglength)*meals))
     
    philosophers = []   
    
    # forks for Footman and Lefthanded solutions
    forks = []
    for i in range(0,n_philosophers):
        forks.append(Semaphore(1))
            
    for i in range(0,n_philosophers):
        philosophers.append(Philosopher(i))
    
    if FOOTMAN :
        footman = Semaphore(n_philosophers-1)
        
        timer = Timer(timefootman)
        print("Footman solution,     time elapsed: {:0.3f}s".format(timer.timeit(number = 1)))
     
    if LEFTHANDED :
        philosophers[0].righthanded = False
        timer = Timer(timelefthanded)
        print("Left-handed solution, time elapsed: {:0.3f}s".format(timer.timeit(number = 1)))
             
    if TANENBAUM :
        state = ['thinking'] * n_philosophers 
        for i in range(0,n_philosophers):
            sem.append(Semaphore(0))
         
        timer = Timer(timetanenbaum)
        print("Tanenbaum's solution, time elapsed: {:0.3f}s".format(timer.timeit(number = 1)))
         
    print("\n///---------\\\\\\\n    SUCCESS\n\\\\\\---------///")   