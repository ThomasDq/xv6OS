/*
 * A2test.c
 *
 *  Created on: Jun 11, 2015
 *      Author: thomas
 */
#include"types.h"
#include"user.h"

int i = 0;
void threadmain(void* arg){
  i++;
  printf(1,"child i = %d\n", i);
//  int pid = getpid();
//  kill(pid);
}
void parent (){
  char* stack = (char*)malloc(64*sizeof(char));
  printf(1,"parent i = %d\n", i);
  int i = thread_create(*threadmain, (void*)stack, (void*)(0));
//  sleep(10);
  thread_join((void**)&stack);
  printf(1,"parent i = %d\n", i);
//  printf(1,"parent over\n", i);
}


int main(int argc, char** argv){

  parent();
  return 0;
}
