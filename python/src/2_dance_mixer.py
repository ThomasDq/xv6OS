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
# Mutex that block access to dancefloor
dancefloor_open = Semaphore(0)     
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
    def pop(role):
        if role == leader:
            Queues.nleaders.acquire()
            Queues.leadersQ.pop().release()
        else:
            Queues.nfollowers.acquire()
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

            # check if dancing is over at wake up
            if not DANCETIME:
                printf(self.name + " PARTY IS OVER!")
                break

            # waiting for partner
            printf(self.name + " entering the floor.")
            
            # check if song is not finished
            dancefloor_open.acquire()
            dancefloor_open.release()

            if self.role == leader:
                global follower_name
                
                self.partnerSem.acquire()
                partner_name = follower_name
                self.arrivedSem.release()
                printf(self.name + " and " + partner_name + " are dancing.")
                # This configuration blocks the Leader until the follower actually arrived,
                # hence protection the follower_name variable
            else:
                follower_name = self.name
                self.arrivedSem.release()
                self.partnerSem.acquire()
                
            # call to Queue to unlock next couple
            Queues.pop(self.role) 
            
            sleep(timeondancefloor)
            
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
        Queues.pop(leader)
        Queues.pop(follower)
        for _ in range(0,self.periods):
            for dance in dances:
                printf("\n** Band Leader start playing " + dance + " **")
                dancefloor_open.release()
                sleep(dancelength)
                printf("** Band Leader stop playing " + dance + " **\n")
                dancefloor_open.acquire()
##                

                
if __name__ == '__main__':
    
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
    dancefloor_open.release()
    for d in dancers:
        d.queue_ticket.release()
        
    # thread join on all dancers
    for i in range(0, n_leaders):
        leaders_th[i].join()
    for i in range(0, n_followers):
        followers_th[i].join()
    
    print("\n///---------\\\\\\\n    SUCCESS\n\\\\\\---------///")