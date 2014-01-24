#!/usr/bin/env python

from __future__ import print_function

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.enums import ENUM_ST_INFO_TYPE

INVALID_ADDR = -1

class MyELFFile(ELFFile):
  def __init__(self, fd):
    super(MyELFFile, self).__init__(fd)
    self._load_addr = INVALID_ADDR

  def get_symbol(self, name):
    """Lookup a symbol by its name."""
    for section in self.iter_sections():
      if not isinstance(section, SymbolTableSection):
          continue

      #return the first symbol that was found
      for sym in section.iter_symbols():
        if sym.name == name:
          return sym

  def get_segment_at(self, addr):
    for seg in self.iter_segments():
      if seg['p_type'] != "PT_LOAD":
        continue

      vaddr = seg['p_vaddr']
      filesz = seg['p_vaddr']
      if vaddr <= addr < vaddr+filesz:
        return seg

  def symbol_is_ifunc(self, sym):
    #TODO check if the architecture supports IFUNCS
    return sym['st_info'].type == "STT_LOOS"

  @property
  def load_addr(self):
    if self._load_addr != INVALID_ADDR:
      return self._load_addr

    load_addr = INVALID_ADDR

    for seg in self.iter_segments():
      if seg['p_type'] != "PT_LOAD":
        continue

      vaddr = seg['p_vaddr']

      if load_addr == INVALID_ADDR or vaddr < load_addr:
        load_addr = vaddr

    self._load_addr = load_addr

    return self._load_addr

def fail(msg, ret_code=1):
    print("Error: " + msg, file=sys.stderr)
    exit(ret_code)

#from stackoverflow user Ned Batchelder
def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

if __name__ == "__main__":
  import sys

  if len(sys.argv) < 4 or (len(sys.argv) % 2) != 0:
    fail("Invalid argument count.", 1)

  filename = sys.argv[1]
  func_list = chunks(sys.argv[2:], 2)

  libc_elf = MyELFFile(open(filename, "r"))

  bin_base = 0

  for func_name, real_addr in func_list:
    #try to parse it in decimal first
    try:
      real_addr = int(real_addr)
    except ValueError as e:
      #try hex instead
      real_addr = int(real_addr, 16)

    sym = libc_elf.get_symbol(func_name)
    if sym == None:
      fail("Symbol {} not found".format(func_name), 2)

    if libc_elf.symbol_is_ifunc(sym):
      fail("IFUNCs not supported yet.".format(func_name), 3)

    sym_addr = sym['st_value']
    sym_off = sym_addr - libc_elf.load_addr
    new_bin_base = real_addr - sym_off

    if new_bin_base == 0:
      fail("Calculated base is NULL.", 4)

    if new_bin_base < 0:
      fail("Calculated base is negative.", 5)

    if bin_base != 0 and new_bin_base != bin_base:
      fail("Offsets don't fit.", 5)

    bin_base = new_bin_base

  print("0x{:x}".format(bin_base))
  exit(0)

