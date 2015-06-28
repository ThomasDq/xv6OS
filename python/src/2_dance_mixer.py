#HOW TO RUN: change variables if wanted - lines 12-13 - and run without arguments

from threading import Thread, Semaphore
from time import sleep
import sys
from collections import deque

# Thread safe print
printf = lambda x: sys.stdout.write("%s\n" % x)

## Main setup
n_leaders = 2
n_followers = 5
##

## Advanced setup
# number of time each dance is played
n_periods = 1
# time each dance is played
dancelength = 5
# time each dancer spend on dancefloor
timeondancefloor = 2
#list of dances
dances = ['waltz', 'tango', 'foxtrot']
# Dancers name prefixes
leader = "Leader  "
follower = "Follower"
##

## Global variables
# Global variable that allows a leader to know and print whom he is dancing with
follower_name = "Follower -1"
# rdv semaphores
leaderArrived = Semaphore(0)
followerArrived = Semaphore(0)
# Loop condition for dances
DANCETIME = True
##

## Dancefloor representation
class Dancefloor:
    # Mutex that block access to dancefloor status is given by closed value
    dancefloor_open = Semaphore(0)
    # Mutex protecting count  variables
    dancefloor_mtx = Semaphore(1)
    # Mutex that wakes up band leader when dancefloor is empty
    dancefloor_empty = Semaphore(0)
    #number of dancing couples on the dancefloor
    count = 0
    closed = True
     
    @staticmethod
    def open():
        Dancefloor.dancefloor_open.release()
         
    @staticmethod
    def close():
        Dancefloor.dancefloor_open.acquire()
        Dancefloor.dancefloor_empty.acquire()
     
    @staticmethod   
    def enter():
        Dancefloor.dancefloor_open.acquire()
        Dancefloor.dancefloor_mtx.acquire()
        Dancefloor.count += 1
        Dancefloor.dancefloor_mtx.release()
        Dancefloor.dancefloor_open.release()
         
    @staticmethod
    def exit():
        Dancefloor.dancefloor_mtx.acquire()
        Dancefloor.count -= 1
        if Dancefloor.count == 0 and Dancefloor.closed:
            Dancefloor.dancefloor_empty.release()
        Dancefloor.dancefloor_mtx.release()
## 
        
## FIFO Queues for both leaders and followers
class Queues:
    leadersQ = deque()
    followersQ = deque()
    # to avoid pulling from empty queues, we protect them with semaphores 
    nleaders = Semaphore(0)
    nfollowers = Semaphore(0)
    @staticmethod
    def append(role, ticket):
        if role == leader:
            Queues.leadersQ.appendleft(ticket)
            Queues.nleaders.release()
        else:
            Queues.followersQ.appendleft(ticket)
            Queues.nfollowers.release()
            
    @staticmethod
    def pop():
        Queues.nleaders.acquire()
        Queues.nfollowers.acquire()
        Queues.leadersQ.pop().release()
        Queues.followersQ.pop().release()
        
##    
    
## Generic dancer class -init makes it a leader or a follower-
class Dancer:
    
    def __init__(self, role, idx):
        global leader, leaderArrived, followerArrived
        self.role = role
        self.idx = idx
        self.name = role + " " + str(idx)
        self.queue_ticket = Semaphore(0)
        if role == leader:
            self.arrivedSem = leaderArrived
            self.partnerSem = followerArrived
        else:
            self.arrivedSem = followerArrived
            self.partnerSem = leaderArrived
        
    def run(self):
        global DANCETIME, dancefloor_open, timeondancefloor
        printf(self.name + " gets in line.")
        
        while(True):
            # registering to Queues
            Queues.append(self.role, self.queue_ticket)
            
            # waiting for its turn
            self.queue_ticket.acquire()

            # waiting for partner
            Dancefloor.enter()
            # check if dancing is over at wake up
            if not DANCETIME:
                printf(self.name + " PARTY IS OVER!")
                break
            printf(self.name + " entering the floor.")
            
            if self.role == leader:
                global follower_name
                
                self.partnerSem.acquire()
                partner_name = follower_name
                self.arrivedSem.release()
                printf(self.name + " and " + partner_name + " are dancing.")
                # call to Queue to unlock next couple
                Queues.pop() 
                # This configuration blocks the Leader until the follower actually arrived,
                # hence protection of the follower_name variable
            else:
                follower_name = self.name
                self.arrivedSem.release()
                self.partnerSem.acquire()
                
            
            sleep(timeondancefloor)
            
            Dancefloor.exit()
            printf(self.name + " gets back in line.")               
            

##

## Band leader, switches between songs
class BandLeader:
    def __init__(self):
        global n_periods, dancelength
        self.periods = n_periods
        self.length = dancelength
    
    def run(self):
        global dances, leader, follower
        
        # kick the first couple out of the waiting queue
        Queues.pop()
        for _ in range(0,self.periods):
            for dance in dances:
                printf("\n** Band Leader start playing " + dance + " **")
                Dancefloor.open()
                sleep(dancelength)
                Dancefloor.close()
                printf("** Band Leader stop playing " + dance + " **\n")
##                

                
if __name__ == '__main__':
    printf("Note : the message printing and the action it describe are not atomic, so it sometimes messes things up")
    # Bandleader
    bl = BandLeader()
    bandleader_th = Thread(target= bl.run)
    dancers = []
    # Leaders
    leaders_th = []
    for i in range(0, n_leaders):
        d = Dancer(leader,i)
        dancers.append(d)
        leaders_th.append(Thread(target = d.run))
        leaders_th[i].start()
    
    # Followers
    followers_th = []
    for i in range(0, n_followers):
        d = Dancer(follower,i)
        dancers.append(d)
        followers_th.append(Thread(target = d.run))
        followers_th[i].start()
    
    bandleader_th.start()
    bandleader_th.join()
    # wait for the last couple to finish their dance
    sleep(timeondancefloor)
    DANCETIME = False
    
    # wake up all dancers
        # when exiting the band leader still holds the dancefloor_open mutex
    Dancefloor.open()
    for d in dancers:
        d.queue_ticket.release()
        
    # thread join on all dancers
    for i in range(0, n_leaders):
        leaders_th[i].join()
    for i in range(0, n_followers):
        followers_th[i].join()
    
    print("\n///---------\\\\\\\n    SUCCESS\n\\\\\\---------///")