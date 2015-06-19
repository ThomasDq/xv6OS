/*
 * A2test.c
 *
 *  Created on: Jun 11, 2015
 *      Author: thomas
 */
#include"types.h"
#include"user.h"

int i = 0;
//void threadmain(void* arg){
//  i++;
//  printf(1,"child i = %d\n", i);
//  sleep(100);
//  printf(1,"child end sleep\n", i);
//  exit();
////  int pid = getpid();
////  kill(pid);
//}

//void parent (){
//  uint* stack = (uint*) malloc(128*sizeof(uint));
//  printf(1,"parent i = %d\n", i);
//  int i = thread_create(*threadmain, (void*)stack, (void*)(0));
////  sleep(2);
//  printf(1,"parent i = %d\n", i);
//  thread_join((void**)&stack);
////  printf(1,"parent over\n", i);
//  free(stack);
//}
uint* stack;

void stackswitch(void* arg){
  char* c = (char*)arg;
  //annouce that function has benn entered + check argument
  printf(1, "stackswitched correctly %s\n", c);
  //stack printing
  for(i = 0; i < 32; i++){
    printf(1,"%d %d -- ", i, stack[i]);
    if(i % 4 == 0 && i > 0 ){
      printf(1,"\n");
    }
  }
  printf(1,"\n\n");
}

int main(int argc, char** argv){

  //parent();
  stack = (uint*) malloc(32*sizeof(uint));
  char arg[4] = "test";

  //intial stack printing
  for(i = 0; i < 32; i++){
    printf(1,"%d %d -- ", i, stack[i]);
    if(i % 4 == 0 && i > 0 ){
      printf(1,"\n");
    }
  }
  printf(1,"\n\n");

  thread_create(stackswitch, (void*)stack, (void*)arg);
  free(stack);
  return 0;
}
