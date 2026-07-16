#pragma once
#include "sysdefs.h"

namespace vdac2
{
  bool is_interrupt();
  void set_ss(bool);
  u8 transfer(u8);
  int open_ft8xx(const char **);
  void close_ft8xx();
  void dump_ftstate();   // HMM2 debug: по триггеру ftdump.req читает RAM_DL+регистры FT812 по SPI → ftdump.bin
}
