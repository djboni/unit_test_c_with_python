#!/usr/bin/python3
# Unit-Test C with Python:
# https://github.com/djboni/unit-test-c-with-python
#
# Stuff you need to install:
# sudo apt install gcc python3 python3-cffi python3-pycparser

import cffi, importlib, pycparser.c_generator
import re, os, sys, subprocess, uuid

Remove_Unknowns = """\
#define __attribute__(x)
#define __restrict
"""

def preprocess(source, include_paths, compiler_options):
  command = ['gcc', *compiler_options, *include_paths, '-E', '-P', '-']
  return subprocess.check_output(command, input=source, universal_newlines=True)

class HeaderGenerator(pycparser.c_generator.CGenerator):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.functions = set()
  def set_SourceContent(self, source_content):
    self.source_content = source_content
  def visit_Decl(self, n, *args, **kwargs):
    import os
    result = super().visit_Decl(n, *args, **kwargs)
    if isinstance(n.type, pycparser.c_ast.FuncDecl):
      # Is a function declaration
      if n.name in self.functions:
        # Is already in functions
        return result
      elif re.search(re.escape(result).replace('\\*', '\\*\\s*').replace('\\ ', '\\s*'), self.source_content) != None:
        # Is declared in source content
        return result
      else:
        # Not in functions, not in source
        self.functions.add(n.name)
        return 'extern "Python+C" ' + result
    else:
      # Not a function declaration
      return result
  def visit_FuncDef(self, n, *args, **kwargs):
    self.functions.add(n.decl.name)
    return ''

def load(source_files, include_paths=[], compiler_options=[], remove_unknowns='', module_name='pysim_', avoid_cache=False):
  """Load a C file into Python as a module.

source_files:     ['file1.c', file2.c'] or just 'file1.c'
include_paths:    ['.', './includes']
compiler_options: ['-std=c90', '-O0', '-Wall', '-Wextra']

module_name: sets the module name (and names of created files).

avoid_cache=True: makes random names to allow testing code with global variables.
"""
  # Avoid caching using random name to module
  if avoid_cache:
    module_name += uuid.uuid4().hex + '_'

  # Create a list if just one souce file in a string
  if type(source_files) == str:
    source_files = [source_files,]
  
  # Prepend -I on include paths
  include_paths = [ '-I' + x for x in include_paths ]
  
  # Collect source code
  source_content = []
  for file in source_files:
    with open(file) as fp:
      source_content.append(fp.read())
  source_content = '\n'.join(source_content)
  
  # Collect include files
  # TODO Remove inclusions inside comments
  header_content = ''.join(re.findall('\s*#include\s+.*', source_content))
  
  # Remove unknowns to CFFI
  header_content = Remove_Unknowns + remove_unknowns + header_content
  
  # Preprocess include files
  header_content = preprocess(header_content, include_paths, compiler_options)
  
  # Prepend 'extern "Python+C" ' to functions declarations with no definitions 
  ast_header = pycparser.CParser().parse(header_content)
  header_generator = HeaderGenerator()
  header_generator.set_SourceContent(source_content)
  header_content = header_generator.visit(ast_header)
  
  # Preprocess source code
  source_content = Remove_Unknowns + remove_unknowns + source_content
  source_content = preprocess(source_content, include_paths, compiler_options)
  
  # Remove conflicts
  source_content = source_content.replace('typedef struct { int __val[2]; } __fsid_t;', '')
  # Rename main, to avoid any conflicts, and declare it
  if 'int main(' in source_content:
    # TODO REGEX
    source_content = source_content.replace('int main(', 'int mpmain(')
    header_content += '\nint mpmain(int argc, char **argv);\n'
  elif 'void main(' in source_content:
    # TODO REGEX
    source_content = source_content.replace('void main(', 'void mpmain(')
    header_content += '\nvoid mpmain(void argc, char **argv);\n'
  
  # Run CFFI
  ffibuilder = cffi.FFI()
  ffibuilder.cdef(header_content)
  include_dirs = [x.replace('-I', '') for x in include_paths]
  if 0:
    # Did not work
    extra_compile_args = ['-fsanitize=address']
    libraries = ['asan']
  else:
    extra_compile_args = []
    libraries = []
  ffibuilder.set_source(module_name, source_content, include_dirs=include_dirs, extra_compile_args=extra_compile_args, libraries=libraries)
  ffibuilder.compile()
  
  # Import and return resulting module
  module = importlib.import_module(module_name)

  # Return both the library object and the ffi object
  return module.lib, module.ffi

