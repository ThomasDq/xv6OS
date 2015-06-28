/*
 * A2test.c
 *
 *  Created on: Jun 11, 2015
 *      Author: thomas
 */
#include"types.h"
#include"user.h"

#define THREADTEST
#define SHAREDMEM
#define MUTEXTEST
//#define PRODCONS
int i = 0;
uint* stack;
int mutex;

void sharedmemth(void* arg){
  i++;
  printf(1,"shared mem child i = %d\n", i);
  exit();
}

void sharedmemparent(){
  uint* returnstack = (uint*)0;
  printf(1,"shared mem parent i = %d\n", i);
  thread_create(*sharedmemth, (void*)stack, (void*)(0));
  sleep(5);
  printf(1,"shared mem parent i = %d\n", i);
  thread_join((void**)&returnstack);
  printf(1,"shared mem parent over\n");
}

void mutextestth(void*arg){
  sleep(1);
  printf(1,"mutex test child waiting for mutex\n");
  mtx_lock(mutex);
  printf(1,"mutex test child acquired mutex\n");
  mtx_unlock(mutex);
  exit();
}

void mutextestparent(){
  uint* returnstack = (uint*)0;
  mutex = mtx_create(1);
  printf(1,"mutex test parent \n");
  thread_create(*mutextestth, (void*)stack, (void*)(0));
  printf(1,"mutex test parent sleeping while holding mutex\n");
  sleep(5);
  mtx_unlock(mutex);
  printf(1,"mutex test parent mutex released\n");
  thread_join((void**)&returnstack);
  printf(1,"mutex test parent over\n");
}

// stackwitching + arg passing testing
void stackswitch(void* arg){
  char* c = (char*)arg;
  //annouce that function has benn entered + check argument
  printf(1, "stackswitched correctly argument passed = %s\n", c);
  //stack printing
  for(i = 0; i < 32; i++){
    printf(1,"%d %d -- ", i, stack[i]);
    if(i % 4 == 0 && i > 0 ){
      printf(1,"\n");
    }
  }
  printf(1,"\n\n");
  printf(1,"end of thread\n");
  exit();
}

int main(int argc, char** argv){

  //parent();
  stack = (uint*) malloc(32*sizeof(uint));


#ifdef THREADTEST
  uint* returnstack = (uint*)0;
  char arg[8] = "testarg";

  //intial stack printing
  for(i = 0; i < 32; i++){
    printf(1,"%d %d -- ", i, stack[i]);
    if(i % 4 == 0 && i > 0 ){
      printf(1,"\n");
    }
  }
  printf(1,"\n\n");

  int pid = thread_create(stackswitch, (void*)stack, (void*)arg);
  printf(1,"start of sleep in main . main pid = %d, thread pid = %d\n", getpid(), pid);
  sleep(50);
  thread_join((void**)&returnstack);
  printf(1, "returnstack address %d, stack address %d\n",(uint)(returnstack), stack);

#endif

#ifdef SHAREDMEM
  sharedmemparent();
#endif

#ifdef MUTEXTEST
  mutextestparent();
#endif
  free(stack);
  printf(1,"end of main\n");
  exit();
  return 0;
}
