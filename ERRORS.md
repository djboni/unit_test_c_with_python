# Errors and problems

## Where is `main()`?

The function `main()` is renamed to `mpmain()`, so it does not conflict with Python's `main()` function. Just use `module.mpmain(args)`.

## How to reset global variables?

To reset global variables you have two options:

* Create reset function (in C or in Python) and call it in `setUp()`.
* Reload module with parameter `avoid_cache=True` in `setUp()`. This will recompile the module with a random name and avoid Python module caching.

There may be other options, however.

## Static local variables with the same name

You cannot use two "file-scoped" static variables with the same name. When creating the Python module, all the C souce code is accumulated into one single C file. Therefore you get a redefinition error.

This will cause a redefinition error:

```c
/* File: file1.c */
static uint32_t static_variable;

/* File: file2.c */
static uint32_t static_variable;
```

This is OK:

```c
/* File: file1.c */
static uint32_t file1_static_variable;

/* File: file2.c */
static uint32_t file2_static_variable;
```

## Function redefined

This an example of an error related to a function redefinition:

```
pysim_.c:1997:6: error: redefinition of ‘FunctionName’
 void FunctionName(int a0)
      ^~~~~~~~~
pysim_.c:947:6: note: previous definition of ‘FunctionName’ was here
 void FunctionName(int num) {
      ^~~~~~~~~
Traceback (most recent call last):
  File "/usr/lib/python3.6/distutils/unixccompiler.py", line 118, in _compile
    extra_postargs)
  File "/usr/lib/python3.6/distutils/ccompiler.py", line 909, in spawn
    spawn(cmd, dry_run=self.dry_run)
  File "/usr/lib/python3.6/distutils/spawn.py", line 36, in spawn
    _spawn_posix(cmd, search_path, dry_run=dry_run)
  File "/usr/lib/python3.6/distutils/spawn.py", line 159, in _spawn_posix
    % (cmd, exit_status))
distutils.errors.DistutilsExecError: command 'x86_64-linux-gnu-gcc' failed with exit status 1

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/usr/lib/python3/dist-packages/cffi/ffiplatform.py", line 51, in _build
    dist.run_command('build_ext')
  File "/usr/lib/python3.6/distutils/dist.py", line 974, in run_command
    cmd_obj.run()
  File "/usr/lib/python3.6/distutils/command/build_ext.py", line 339, in run
    self.build_extensions()
  File "/usr/lib/python3.6/distutils/command/build_ext.py", line 448, in build_extensions
    self._build_extensions_serial()
  File "/usr/lib/python3.6/distutils/command/build_ext.py", line 473, in _build_extensions_serial
    self.build_extension(ext)
  File "/usr/lib/python3.6/distutils/command/build_ext.py", line 533, in build_extension
    depends=ext.depends)
  File "/usr/lib/python3.6/distutils/ccompiler.py", line 574, in compile
    self._compile(obj, src, ext, cc_args, extra_postargs, pp_opts)
  File "/usr/lib/python3.6/distutils/unixccompiler.py", line 120, in _compile
    raise CompileError(msg)
distutils.errors.CompileError: command 'x86_64-linux-gnu-gcc' failed with exit status 1

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "test_librertos.py", line 29, in <module>
    module, ffi = load(source_files, include_paths, compiler_options, module_name=module_name)
  File ".../PATH/load_c.py", line 118, in load
    ffibuilder.compile()
  File "/usr/lib/python3/dist-packages/cffi/api.py", line 697, in compile
    compiler_verbose=verbose, debug=debug, **kwds)
  File "/usr/lib/python3/dist-packages/cffi/recompiler.py", line 1520, in recompile
    compiler_verbose, debug)
  File "/usr/lib/python3/dist-packages/cffi/ffiplatform.py", line 22, in compile
    outputfilename = _build(tmpdir, ext, compiler_verbose, debug)
  File "/usr/lib/python3/dist-packages/cffi/ffiplatform.py", line 58, in _build
    raise VerificationError('%s: %s' % (e.__class__.__name__, e))
cffi.error.VerificationError: CompileError: command 'x86_64-linux-gnu-gcc' failed with exit status 1
```

The problem is likely to be in `visit_Decl()`: your function definition is not being found in the code by the regex. You would need to change your function definition name or the regex.

This is an example of a change that was made to allow pointers to have spaces after the `*`, for example, `int * i_ptr`:

```python
# File: load_c.py

# From
re.search(re.escape(result).replace('\\ ', '\\s*'), self.source_content)

# To
re.search(re.escape(result).replace('\\*', '\\*\\s*').replace('\\ ', '\\s*'), self.source_content)
```

## Cannot parse header

This an example of an error related to header that could not be parsed:

```
Traceback (most recent call last):
  File "test_librertos.py", line 29, in <module>
    module, ffi = load(source_files, include_paths, compiler_options, module_name=module_name)
  File ".../PATH/load_c.py", line 84, in load
    ast_header = pycparser.CParser().parse(header_content)
  File ".../PATH/c_parser.py", line 152, in parse
    debug=debuglevel)
  File ".../PATH/ply/yacc.py", line 331, in parse
    return self.parseopt_notrack(input, lexer, debug, tracking, tokenfunc)
  File ".../PATH/ply/yacc.py", line 1199, in parseopt_notrack
    tok = call_errorfunc(self.errorfunc, errtoken, self)
  File ".../PATH/ply/yacc.py", line 193, in call_errorfunc
    r = errorfunc(token)
  File ".../PATH/c_parser.py", line 1861, in p_error
    column=self.clex.find_tok_column(p)))
  File ".../PATH/plyparser.py", line 67, in _parse_error
    raise ParseError("%s: %s" % (coord, msg))
pycparser.plyparser.ParseError: :258:39: before: __dest
```

The problem is likely to be a header (or source file) with directives that CFFI does not understand, such as `____attribute__()` or `__restrict`. Define the directive to the `Remove_Unknowns` variable to infor the C preprocessor to remove it.

This is an example of a change that was made to allow inclusion of the `string.h` header, which uses the `__restrict` directive:

```python
# File: load_c.py

# From
Remove_Unknowns = """\
#define __attribute__(x)
"""

# To
Remove_Unknowns = """\
#define __attribute__(x)
#define __restrict
"""
```
