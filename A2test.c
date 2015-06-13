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
  sleep(100);
  printf(1,"child end sleep\n", i);
  exit();
//  int pid = getpid();
//  kill(pid);
}

void parent (){
  char stack[128];
  printf(1,"parent i = %d\n", i);
  int i = thread_create(*threadmain, (void*)stack, (void*)(0));
//  sleep(2);
  printf(1,"parent i = %d\n", i);
  thread_join((void**)&stack);
//  printf(1,"parent over\n", i);
}


int main(int argc, char** argv){

  parent();
  return 0;
}
