#include "types.h"
#include "user.h"
#include "syscall.h"

int
main(int argc, char *argv[])
{
  printf(1, "initial fork count %d\n", getcount(SYS_fork));
  if (fork() == 0) {
    printf(1, "child fork count %d\n", getcount(SYS_fork));
    printf(1, "child write count %d\n", getcount(SYS_write));
	printf(1, "child getcount count %d\n", getcount(SYS_getcount));
  } else {
    wait();
    printf(1, "parent fork count %d\n", getcount(SYS_fork));
    printf(1, "parent write count %d\n", getcount(SYS_write));
	printf(1, "parent getcount count %d\n", getcount(SYS_getcount));
  }
  printf(1, "wait count %d\n", getcount(SYS_wait));
  exit();
}
