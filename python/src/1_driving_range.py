#HOW TO RUN: change variables if wanted - lines 8-10 - and run without arguments

from threading import Thread, Semaphore
from time import sleep
import sys, random

#Program variables
NUMBER_GOLFERS = 5
STASH_SIZE = 25    
BUCKET_SIZE = 5
RUNTIME = 5 #length of the simulation


#Thread safe stdout print hack
    # http://stackoverflow.com/questions/7877850/python-2-7-print-thread-safe
printf = lambda x: sys.stdout.write("%s\n" % x)

#Global variables
    
    #while loop variables
run = True
cart_run = True

    #field
balls_on_field = 0
field_lock = Semaphore(1)       # protects balls_on_field variable

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
        field_lock.acquire()
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

            #shoot
            field_lock.acquire()
            balls_on_field += 1             # swing (maybe simulate with a random sleep)
            sleep(random.Random().random())
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
    
    sleep(RUNTIME)
    run = False
    printf("Range is closing, calling for a bucket is not allowed past this point.")
    sleep(1)
    for i in range(0,n_golfers):
        golfers_th[i].join()
    printf("##############################################\nSTASH = " + str(stash) + "; Car is doing a last run")
    cart_run = False
    stash_empty.release()
    cart_th.join()
    
    print("\n///---------\\\\\\\n    SUCCESS\n\\\\\\---------///")   
    
##