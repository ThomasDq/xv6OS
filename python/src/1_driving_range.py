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
        #signal golfers that field is unavailable
        field_open = False
        field_lock.acquire()
        field_open = True               # since this thread has field_lock, no one can shoot a ball
        printf("##############################################\nSTASH = " + str(stash) + ";")
        stash_empty.release()           # signal cart
        stash_filled.acquire()          # wait for cart signal
        field_lock.release()
    
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
        bucket = grab_bucket(golfer_id)
        for i in range(0,bucket):      # for each ball in bucket, shoot it
            #check if field is safe
            waiting_lock.acquire()
            if not field_open:
                printf(golfer_id + "has to wait to pursue.")
                waiting_golfers += 1
                waiting_lock.release()
                field_open_wait.acquire()
            else:
                waiting_lock.release()
            #shoot
            field_lock.acquire()
            balls_on_field += 1             # swing (maybe simulate with a random sleep)
            printf(golfer_id + " hit ball " + str(i) + ".")
            field_lock.release()
    printf(golfer_id + " stops.") 
##

#Cart
def cart():
    global cart_run, stash_empty, field_open, field_lock, stash, balls_on_field, waiting_lock, waiting_golfers, field_open_wait
    while cart_run:
        #wait for grab_bucket signal
        stash_empty.acquire()
        #get field lock to access balls_on field
        #field_lock.acquire()
        printf("Cart entering field.")
                    
        # The thread that woke up cart has both the field and stash lock
        # therefore it's safe to modify ball_on_field and stash
        stash += balls_on_field
        printf("Cart done, gathered "+ str(balls_on_field) +" balls. STASH = " + str(stash) + 
               ".\n##############################################")
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
    
    sleep(5)
    run = False
    printf("Range is closing, calling for a bucket is not allowed past this point.")
    sleep(1)
    cart_run = False
    stash_empty.release()
    for i in range(0,n_golfers):
        golfers_th[i].join()
    cart_th.join()
    
    print("\n///---------\\\\\\\n    SUCCESS\n\\\\\\---------///")   
    
##