/*
 * prod.c
 *
 *  Created on: Jun 11, 2015
 *      Author: thomas
 */
//int thread_create(void (*tmain)(void *), void *stack, void *arg)
#include"types.h"
#include"user.h"

#define SIZEOFQUEUE 5
#define CSLEEP 1
#define PSLEEP 1
#define NITEMS 8

int mutex;
struct warehouse {
  int items;
  int spaces;
  int storage[SIZEOFQUEUE];
};
struct warehouse warehouse;

void prod (void*arg){
  int i,j, found;
  //loopto create items i
  for(i = 0; i < NITEMS; i++){
    mtx_lock(mutex);
    if(warehouse.spaces == 0){
      mtx_unlock(mutex);
      sleep(PSLEEP);
    }else{
      found = 0;
      j = 0;
      // find empty spot in storage
      while(found ==0 && j < SIZEOFQUEUE){
        if(warehouse.storage[j] == 0){
          found = 1;
          printf(1,"prod produced item %d\n", i);
          //put i in storage spot j
          warehouse.storage[j] = i;
          //update warehouse data
          warehouse.items ++;
          warehouse.spaces --;
        }
        j++;
      }//end while
      mtx_unlock(mutex);
    }//end else

  }//end for i
  exit();
}

void cons (void*arg){
  warehouse.items = 0;
  warehouse.spaces = SIZEOFQUEUE;

  int i,j, found;
  //loopto create items i
  for(i = 0; i < NITEMS; i++){
    mtx_lock(mutex);
    if(warehouse.items == 0){
      mtx_unlock(mutex);
      sleep(CSLEEP);
    }else{
      found = 0;
      j = 0;
      // find non empty spot in storage
      while(found == 0 && j < SIZEOFQUEUE){
        if(warehouse.storage[j] != 0){
          found = 1;
          printf(1,"prod consumed item %d\n", warehouse.storage[j]);
          //delete i in storage spot j
          warehouse.storage[j] = 0;
          //update warehouse data
          warehouse.items --;
          warehouse.spaces ++;
        }
        j++;
      }//end while
      mtx_unlock(mutex);
    }//end else

  }//end for i
  exit();
}

int main(int argc, char**argv){
  mutex = mtx_create(0);
  uint* returnstack = 0;
  uint* stack1[128];
  uint* stack2[128];


  thread_create(*prod,stack1,(void*)0);
  thread_create(*cons,stack2,(void*)0);
  thread_join((void*)returnstack);
  thread_join((void*)returnstack);
  exit();
  return 0;
}
