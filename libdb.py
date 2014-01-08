#!/usr/bin/env python

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection

class MyELFFile(ELFFile):
  def __init__(self, fd):
    super(MyELFFile, self).__init__(fd)

  def get_symbol(self, name):
    """Lookup a symbol by its name."""
    for section in libc_elf.iter_sections():
      if not isinstance(section, SymbolTableSection):
          continue

      #return the first symbol that was found
      for sym in section.iter_symbols():
        if sym.name == name:
          return sym

if __name__ == "__main__":
  import sys

  libc_elf = MyELFFile(open("/lib/libc.so.6", "r"))

  if len(sys.argv) > 1:
    sym_name = sys.argv[1]
  else:
    sym_name = "strstr"
  sym = libc_elf.get_symbol(sym_name)

  if sym == None:
    print "Symbol {} not found.".format(sym_name)
    exit(1)

