#!/usr/bin/env python

from elftools.elf.elffile import ELFFile
from elftools.elf.sections import SymbolTableSection
from elftools.elf.enums import ENUM_ST_INFO_TYPE

class MyELFFile(ELFFile):
  def __init__(self, fd):
    super(MyELFFile, self).__init__(fd)

  def get_symbol(self, name):
    """Lookup a symbol by its name."""
    for section in self.iter_sections():
      if not isinstance(section, SymbolTableSection):
          continue

      #return the first symbol that was found
      for sym in section.iter_symbols():
        if sym.name == name:
          return sym

  def symbol_is_ifunc(self, sym):
    #TODO check if the architecture supports IFUNCS
    return sym['st_info'].type == "STT_LOOS"

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

  print "{} is {}an IFUNC".format(sym.name, "" if libc_elf.symbol_is_ifunc(sym) else "not ")

