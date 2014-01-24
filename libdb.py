#!/usr/bin/env python

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

  code = libc_elf.get_segment_at(sym['st_value']).data()

