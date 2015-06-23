from threading import Thread, Semaphore
from time import sleep
import sys

#Program variables
NUMBER_GOLFERS = 5
STASH_SIZE = 20    
BUCKET_SIZE = 5


#Thread safe stdout print hack
    # http://stackoverflow.com/questions/7877850/python-2-7-print-thread-safe
printf = lambda x: sys.stdout.write("%s\n" % x)

#Global variables
    # 5 binary semaphores
    # 1 semaphore
    # 5 global variables
    # 3 global constant
    
    #while loop variables
run = True
cart_run = True

    #field
balls_on_field = 0
field_lock = Semaphore(1)       # protects balls_on_field variable
field_open = True               # boolean modifed by cart when it wants to enter the field
waiting_lock = Semaphore(1)     # protects waiting_golfers variable
field_open_wait = Semaphore(0)  # waiting semaphore for golfers when cart is on field

waiting_golfers = 0             # golfers waiting for the field toopen

    #bucket
bucket_size = BUCKET_SIZE

    #ball stash
stash_lock = Semaphore(1)       # Semaphore protecting stash varable 
stash_empty = Semaphore(0)      # Semaphore cart is waiting on to proceed
stash_filled = Semaphore(0)     # Semaphore grab_bucket is waiting on
stash = STASH_SIZE

    #number of golfers
n_golfers = NUMBER_GOLFERS

##

#grab_bucket
def grab_bucket(golfer_id):
    global stash_lock, stash, bucket_size, stash_empty, stash_filled
    printf(golfer_id + " calling for bucket.")
    stash_lock.acquire()
    # if stash is empty, call cart 
    if stash == 0:
        printf("##############################################\nSTASH = " + str(stash) + ";")
        stash_empty.release()           # signal cart
#         stash_lock.release()            # release stash -> not necessary since cart was called, and is now the only one to modify stash
        stash_filled.acquire()          # wait for cart signal
    
    ball_taken = min(stash,bucket_size)
    stash -= ball_taken                 # grab balls
    printf(golfer_id + " got " + str(ball_taken) + " balls. STASH = " + str(stash))
    stash_lock.release()
    return ball_taken
##

#Golfer 
def golfer(number):
    global run, bucket_size, field_open, waiting_lock, waiting_golfers, field_open_wait, field_lock, balls_on_field
    bucket = 0
    golfer_id = "Golfer "+ str(number)
    while run:
        #fill one's bucket
        printf(golfer_id + " calling for bucket.")
        bucket = grab_bucket(golfer_id)
        for i in range(0,bucket):      # for each ball in bucket, shoot it
            #check if field is safe
            if not field_open:
                waiting_lock.acquire()
                waiting_golfers += 1
                waiting_lock.release()
                field_open_wait.acquire()
            
            #shoot
            field_lock.acquire()
            balls_on_field += 1             # swing (maybe simulate with a random sleep)
            field_lock.release()
            printf(golfer_id + " hit ball " + str(i) + ".")
    printf(golfer_id + " stops.") 
##

#Cart
def cart():
    global cart_run, stash_empty, field_open, field_lock, stash, balls_on_field, waiting_lock, waiting_golfers, field_open_wait
    while cart_run:
        #wait for grab_bucket signal
        stash_empty.acquire()
        #signal golfers that field is unavailable
        field_open = False
        #get field lock to access balls_on field
        field_lock.acquire()
        printf("Cart entering field.")
        
        field_open = True   # since this thread has field_lock, no one can shoot a ball
        
        sleep(1)            # wait for all threads that might have entered the "check if field is safe" if branch to wait for signal
                            # Since field_open is True, the other threads will block on field_lock
                    
        
        # The thread having the stash lock is the one that woke cart up
        # and this thread is blocked, waiting for cart to operate
        # Therefore it is safe to modify the stash variable without using its lock
        stash += balls_on_field
        printf("Cart done, gathered "+ str(balls_on_field) +" balls.\n-- STASH = " + str(stash) + " --")
        balls_on_field = 0 
        
        waiting_lock.acquire()
        local_wgolfers = waiting_golfers
        waiting_golfers = 0
        waiting_lock.release()
        
        # wake up all waiting golfers
        for _ in range(0,local_wgolfers):
            field_open_wait.release()

        field_lock.release()
        stash_filled.release()
    printf("Cart stops.")    
##

#Main
if __name__ == '__main__':

    #launch cart
    cart_th = Thread(target=cart)
    cart_th.start()

    #launch golfers
    golfers_th = []
    for i in range(0,n_golfers):
        golfers_th.append(Thread(target=golfer, args=[i]))
        golfers_th[i].start()
    
    sleep(10)
    run = False
    printf("Range is closing, golfers can finish their buckets.")
    sleep(1)
    cart_run = False
    stash_empty.release()
    for i in range(0,n_golfers):
        golfers_th[i].join()
    cart_th.join()
    
    print("\n///---------\\\\\\\n    SUCCESS\n\\\\\\---------///")   
    
##