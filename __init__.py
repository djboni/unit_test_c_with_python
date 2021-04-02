#!/usr/bin/python3

# Unit-Test C with Python:
# https://github.com/djboni/unit-test-c-with-python
#
# Stuff you need to install:
# sudo apt install gcc python3 python3-cffi python3-pycparser

# Copyright 2021 Djones A. Boni
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cffi, importlib, pycparser.c_generator
import re, os, sys, subprocess, uuid

Remove_Unknowns = """\
#define __attribute__(x)
#define __restrict
"""

def load(source_files, include_paths=[], compiler_options=[], remove_unknowns='', module_name='pysim_', avoid_cache=False, en_code_coverage=False, en_sanitize_undefined=False, en_sanitize_address=False):
  """Load a C file into Python as a module.

source_files:     ['file1.c', file2.c'] or just 'file1.c'
include_paths:    ['.', './includes']
compiler_options: ['-std=c90', '-O0', '-Wall', '-Wextra']

module_name: sets the module name (and names of created files).

avoid_cache=True: makes random names to allow testing code with global variables.

en_code_coverage=True: enables Gcov code coverage.

en_sanitize_undefined=True: enables undefined behavior sanitizer.

en_sanitize_address=True: enables address sanitizer (not working).
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
  header_content = ''.join(x[0] for x in re.findall(
      r'(\s*\#\s*(include\s|define\s|undef\s|if(n?def)?\s|else|endif|error|warning)[^\n\r\\]*((\\\n|\\\r|\\\n\r|\\\r\n)[^\n\r\\]*)*)',
      source_content))

  # Preprocess include files
  header_content = Remove_Unknowns + remove_unknowns + header_content
  header_content = preprocess(header_content, include_paths, compiler_options)

  # Preprocess source code
  source_content = Remove_Unknowns + remove_unknowns + source_content
  source_content = preprocess(source_content, include_paths, compiler_options)

  # Remove conflicts
  #header_content = header_content.replace('typedef struct { int __val[2]; } __fsid_t;', '')
  source_content = source_content.replace('typedef struct { int __val[2]; } __fsid_t;', '')

  # Rename main, to avoid any conflicts, and declare it in the header
  if 'int main(' in source_content:
    # TODO REGEX
    source_content = source_content.replace('int main(', 'int mpmain(')
    header_content += '\nint mpmain(int argc, char **argv);\n'
  elif 'void main(' in source_content:
    # TODO REGEX
    source_content = source_content.replace('void main(', 'void mpmain(')
    header_content += '\nvoid mpmain(void argc, char **argv);\n'

  # TODO Compile only if source_content is different than module_name.c

  # Prepend 'extern "Python+C" ' to functions declarations with no definitions
  try:
    ast_header = pycparser.CParser().parse(header_content)
    header_generator = HeaderGenerator()
    header_generator.set_SourceContent(source_content)
    header_content = header_generator.visit(ast_header)
  except:
    print()
    print(80 * '-')
    print('HEADER:')
    print(header_content)
    print(80 * '-')
    print()
    raise

  # Run CFFI
  ffibuilder = cffi.FFI()
  ffibuilder.cdef(header_content)
  include_dirs = [ x.replace('-I', '') for x in include_paths ]

  extra_compile_args = []
  extra_link_args = []
  libraries = []

  if en_sanitize_address:
    # Address sanitizer
    # export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libasan.so.4
    extra_compile_args += ['-fsanitize=address']
    #extra_link_args += ['-fsanitize=address', '-static-libasan']
    #extra_link_args += ['-fsanitize=address', '-shared-libasan']
    libraries += ['asan']

  if en_sanitize_undefined:
    extra_compile_args += ['-fsanitize=undefined', ]
    extra_link_args += ['-fsanitize=undefined', ]

  if en_code_coverage:
    # Code coverage
    extra_compile_args += ['--coverage', ]
    extra_link_args += ['--coverage', ]
    libraries += []

  ffibuilder.set_source(module_name, source_content, include_dirs=include_dirs, extra_compile_args=extra_compile_args, libraries=libraries, extra_link_args=extra_link_args)
  ffibuilder.compile()

  # Import and return resulting module
  module = importlib.import_module(module_name)

  # Return both the library object and the ffi object
  return module.lib, module.ffi

def preprocess(source, include_paths, compiler_options):
  try:
    #command = ['gcc', *compiler_options, *include_paths, '-E', '-P', '-']
    command = ['gcc', ] + compiler_options + include_paths + ['-E', '-P', '-']
    return subprocess.check_output(command, input=source, universal_newlines=True)
  except:
    print()
    print(80 * '-')
    print('SOURCE/HEADER:')
    print(source)
    print(80 * '-')
    print()
    raise

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
      elif re.search((
                      re.escape(result)
                          .replace('\\*', '\\*\\s*')
                          .replace('\\ ', '\\s*')
                          + '\\s*\{'
                     ), self.source_content) != None:
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

class FFIMocks:
  """\
Define 'extern "Pyton+C"' function as a mock object.

from unit_test_c_with_python import load, FFIMocks
module, ffi = load('gpio.c')

Mocks = FFIMocks()

# Create mocks
Mocks.CreateMock(ffi, 'read_gpio0', return_value=42)
Mocks.CreateMock(ffi, 'read_gpio1', return_value=21)

# Reset mocks [Useful in setUp()]
Mocks.ResetMocks()
"""
  from unittest.mock import call
  def CreateMock(self, ffi, name, *args, **kwargs):
    import unittest.mock
    mock = unittest.mock.Mock(*args, **kwargs)
    setattr(self, name, mock)
    ffi.def_extern(name)(mock)
  def ResetMocks(self):
    import unittest.mock
    for name in dir(self):
      obj = getattr(self, name)
      if isinstance(obj, unittest.mock.Mock):
        obj.reset_mock()
