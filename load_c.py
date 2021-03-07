#!/usr/bin/python3
# Alexander Steffen - Writing unit tests for C code in Python
# https://www.youtube.com/watch?v=zW_HyDTPjO0

# sudo apt install gcc python3 python3-cffi python3-pycparser

# TODO list
# [ ] Generate files in a directory

import cffi, importlib, uuid, re, pycparser, pycparser.c_generator

def preprocess(source):
  import subprocess
  return subprocess.run(['gcc', '-E', '-P', '-'],
      input=source, stdout=subprocess.PIPE,
      universal_newlines=True, check=True).stdout

class FunctionList(pycparser.c_ast.NodeVisitor):
  def __init__(self, source):
    self.funcs = set()
    self.visit(pycparser.CParser().parse(source))
  def visit_FuncDef(self, node):
    self.funcs.add(node.decl.name)

class CFFIGenerator(pycparser.c_generator.CGenerator):
  def __init__(self, blacklist):
    super().__init__()
    self.blacklist = blacklist
  def visit_Decl(self, n, *args, **kwargs):
    result = super().visit_Decl(n, *args, **kwargs)
    if isinstance(n.type, pycparser.c_ast.FuncDecl):
      if n.name not in self.blacklist:
        return 'extern "Python+C" ' + result
    return result

def convert_function_declarations(source, blacklist):
  return CFFIGenerator(blacklist).visit(pycparser.CParser().parse(source))

def load(filename):
  
  # Generate random name
  name = filename + '_' + uuid.uuid4().hex + '_'
  
  # Load source code
  source = open(filename + '.c').read()
  
  # Preprocess all header files for CFFI
  includes = preprocess(''.join(re.findall('\s*#include\s+.*', source)))
  
  # Prefix external functions with extern "Python+C"
  local_functions = FunctionList(preprocess(source)).funcs
  includes = convert_function_declarations(includes, local_functions)
  
  # Pass source code to CFFI
  ffibuilder = cffi.FFI()
  ffibuilder.cdef(includes)
  ffibuilder.set_source(name, source)
  ffibuilder.compile()
  
  # Import and return resulting module
  module = importlib.import_module(name)

  # Return both the library object and the ffi object
  return module.lib, module.ffi

