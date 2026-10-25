# I❤️LA (iheartinduction) — Agent Notes

A DSL for linear algebra that compiles to NumPy / Eigen(C++) / MATLAB / LaTeX / MathJax /
MathML / MacroMathjax. Python package `iheartla/`.

## Commands

```bash
# compile a file (writes <name>.py, .cpp, .tex, .m next to the input)
python -m iheartla path/to/file.ihla -o numpy,eigen,latex,matlab
python -m iheartla - < file.ihla          # read from stdin

# tests
./run_test.sh                              # python3 -m unittest discover -s test
python3 -m unittest discover -s test       # same, without the cleanup step
```

`run_test.sh` deletes the generated `test/*.cpp` afterwards. `test/base_python_test.py`
generates Python + C++ (and optionally MATLAB) from a source string, imports the Python
module and numerically compares results against a reference implementation.

Environment flags live in `iheartla/la_tools/la_helper.py`:
`DEBUG_MODE`, `DEBUG_PARSER`, `DEBUG_TIME`, `TEST_MATLAB`.

## Repository layout

```
iheartla/
  __main__.py            CLI entry point
  compiler.py            public API: compile(content), show_gui()
  la_grammar/            grammar as Python string constants (LA, SIMPLIFIED)
  la_parser/             parser driver, type walker, IR, per-target code generators
  la_tools/              logger, messages, helpers, parser manager
  la_local_parsers/      PRE-COMPILED TatSu parsers (checked into git!)
  la_gui/                wxPython GUI (ignore unless asked)
  pygments/              syntax highlighting lexer
test/                    unittest suite
```

## The compile pipeline

```
.ihla file
 └─ read_from_file                                la_tools/la_helper.py:138
    └─ parser.parse  (simplified/init parser)    la_parser/parser.py:469
       └─ TypeWalker.walk(pre_walk=True)          la_parser/parser.py:475
          └─ parse_ir_node                        la_parser/parser.py:239
             ├─ patch grammar: ids / funcs / pkg  la_parser/parser.py:326-372
             ├─ load dependent .ihla modules      la_parser/parser.py:288-320
             ├─ parser.parse (patched parser)     la_parser/parser.py:377
             └─ TypeWalker.walk                   la_parser/parser.py:382
                └─ walk_model per target          la_parser/parser.py:88
                   └─ CodeGen*.visit_code → CodeFrame → code string
                      └─ write next to input      la_parser/parser.py:568
```

Public entry points:

| Function | Purpose |
|---|---|
| `compile_la_content(content, parser_type=..., func_name=None, path=None, struct=False, get_json=False, get_vars=False, class_only=False)` — `la_parser/parser.py:452` | compile from a string; returns `{ParserTypeEnum: code}`, optionally `+ json` and/or `var_data` |
| `compile_la_file(la_file, parser_type=..., class_only=False)` — `la_parser/parser.py:522` | CLI path; reads the file, writes `<stem>.<suffix>` |
| `parse_la(content, parser_type)` — `la_parser/parser.py:586` | used by tests |

`ParserTypeEnum` is a `Flag` (`la_tools/la_helper.py:22`): `LATEX=1, NUMPY=2, EIGEN=4,
MATLAB=8, MATHJAX=256, MATHML=512, MACROMATHJAX=1024` (also unused `JULIA`, `PYTORCH`,
`ARMADILLO`, `TENSORFLOW`). Targets are iterated in the hardcoded list at
`la_parser/parser.py:479` and `la_parser/parser.py:492`.

### Key modules

| File | Role |
|---|---|
| `la_parser/parser.py` | driver: parse orchestration, `parse_ir_node`, `compile_la_*`, `walk_model` |
| `la_parser/type_walker.py` | semantic analysis + type inference; **converts TatSu nodes into IR nodes** |
| `la_parser/ir.py` | pure IR node classes (`IRNodeType` enum + node classes) |
| `la_parser/ir_visitor.py` | `IRVisitor`: IR → target code dispatch (`type_func` dict at :298) |
| `la_parser/ir_printer.py` | `IRPrinter` (base of `CodeGen`) |
| `la_parser/codegen.py` | `CodeGen` + `CodeFrame` (`desc/include/struct/rand_data/main/expr`) |
| `la_parser/codegen_{numpy,eigen,matlab,latex,mathjax,macromathjax,mathml}.py` | per-target `visit_*` implementations |
| `la_parser/la_types.py` | `LaVarType` hierarchy: `ScalarType`, `SequenceType`, `MatrixType`, `VectorType`, `SetType`, `IndexType`, `FunctionType`; `NodeInfo`, `CodeNodeInfo` |
| `la_parser/la_data.py` | `ParamsData`, `LocalFuncData` |
| `la_tools/parser_manager.py` | parser acquisition, caching, runtime grammar patching |
| `la_tools/la_msg.py` | `LaMsg.getInstance().get_parse_error(e)` → user-facing error text |

### TypeWalker state worth knowing

`TypeWalker` subclasses TatSu's `NodeWalker`; dispatch is by **grammar node name**, so a
grammar rule `foo::Foo` is handled by `walk_Foo`. Each `walk_*` returns a `NodeInfo`
(`la_types.py:300`) carrying `la_type`, `content`, `symbols`, `ir`.

Key attributes: `symtable` (name → `LaVarType`), `parameters` (where/given-block params),
`lhs_list` (defined symbols), `ret_symbol` (synthesized as `"ret"` if the last statement
isn't an assignment), `multi_lhs_list`, `func_data_dict` (local funcs), `opt_dict`,
`expr_dict`, `import_module_list`.

Useful methods: `reset_state(content)` (`:326`), `get_func_symbols()` (`:364`),
`gen_json_content()` (`:308`, the glossary JSON), `create_math_node_info` (`:2966`),
`create_trig_node_info` (`:3017`).

### IR

`IRNodeType` (`ir.py:5`) is a plain `Enum` with numeric ranges: base 0–8, control 50–55,
conditions 99–108, operators 200–222, matrix 300–312, index 320–323, where-block 399–406,
`Import = 500`. `StartNode` (`ir.py:140`) is the root; `BlockNode` (`:285`) holds
statements; `AssignNode` (`:316`); `ImportNode` (`:262`); expression nodes from `:426`
onwards; `MathFuncType` (`:999`) + `MathFuncNode` (`:1035`).

---

# Adding new syntax / semantics

Work is **node-level**: grammar → TypeWalker → IR → IRVisitor → **all 7 codegens**.
`compile_la_content` / `compile_la_file` / `__main__` are target-agnostic drivers and
usually need no change (the target list at `parser.py:479`/`:492` only matters when adding
a new *output language*).

## The 5 layers

| # | Layer | File | What to add |
|---|---|---|---|
| 1 | Grammar rule | `la_grammar/*.ebnf.py` | e.g. `my_func::MyFunc = MYFUNC '(' {hspace} param:expression {hspace} ')'`; keyword token in `la_grammar/keywords_ebnf.py` |
| 2 | Type walker | `la_parser/type_walker.py` | `walk_MyFunc(self, node, **kwargs)` → returns `NodeInfo`; **this is where the semantics live** (type inference, symtable updates, assertions) |
| 3 | IR | `la_parser/ir.py` | new `IRNodeType` + node class, **or** reuse an existing node with a new enum value (e.g. `MathFuncType`) |
| 4 | Visitor dispatch | `la_parser/ir_visitor.py` | entry in the `type_func` dict (`:298-375`) + base `visit_xxx` stub (`:462`) |
| 5 | Per-target codegen | all 7 `codegen_*.py` | a `visit_xxx` (or a branch in an existing `visit_*`) in **each** target |

Step 2 is not boilerplate: the TypeWalker is what converts TatSu nodes into IR nodes, so
without a `walk_*` the new node never reaches the IR.

## Two routes

**Cheap — new built-in function** (`myfunc(x)`), no new IR node type:
1. `la_grammar/keywords_ebnf.py`: `MYFUNC = /myfunc/;`
2. `la_grammar/trigonometry_ebnf.py` (or a new file): `my_func::MyFunc = MYFUNC '(' ... ')'`
3. `la_parser/ir.py:999`: add `MathFuncType.MathFuncMyFunc = 30`
4. `la_parser/type_walker.py`: `walk_MyFunc` → `self.create_math_node_info(MathFuncType.MathFuncMyFunc, self.walk(node.param))` (mirror `walk_TraceFunc`, `:3110`)
5. each `codegen_*.py`: one `elif node.func_type == MathFuncType.MathFuncMyFunc:` branch (mirror `codegen_numpy.py:1679`)

**Expensive — new operator / statement / IR node**: all 5 layers, plus
`walk_Statements` (`type_walker.py:1175`) and `StartNode.stat` / `BlockNode` for
statement-level features.

## Gotchas

### 1. `la_local_parsers/` must be regenerated after any grammar change

`iheartla/la_local_parsers/{init_parser,default_parser}.py` are **pre-compiled TatSu
parsers checked into git**. In normal mode (`DEBUG_PARSER = False`) the grammar strings in
`la_grammar/` are *never compiled* — the shipped `.py` parsers are used. So a grammar edit
has no effect until they are regenerated.

```bash
# 1. flip the flag in iheartla/la_tools/la_helper.py:14
DEBUG_PARSER = True
# 2. regenerate (wipes and rebuilds la_local_parsers/ + the user cache)
python -m iheartla --regenerate-grammar
# 3. flip DEBUG_PARSER back to False and commit the regenerated files
```

`--regenerate-grammar` alone is **not** enough: `__main__.py` imports
`iheartla.la_parser.parser` at module load (line 4), which builds `_parser_manager`
(`parser.py:120`) while `DEBUG_PARSER` is still `False`, so `recreate_local_parser_cache()`
(`parser_manager.py:602`) hits a non-debug manager with no `.cache_dir` attribute. Set the
flag in `la_helper.py` first.

### 2. The runtime grammar patcher is fragile

`parser_manager.py` patches the default parser by **exact string replacement**
(`gen_parser_code` at `:257`, `generate_new_parser_files` at `:385`). The docstring at
`parser_manager.py:603-606` warns: the parser keeps working only if the grammar change
does not touch these rules:

`KEYWORDS`, `constant`, `builtin_operators`, `func_id`, `identifier_alone`

Editing them silently breaks the injection of new identifiers / functions / packages
(the `replace` simply doesn't match).

### 3. `MathFuncType` values are range-checked numerically

`create_math_node_info` (`type_walker.py:2966-3010`) is an if/elif chain over **numeric
ranges**:

- `Invalid < t < Atan2` (0–14) → scalar/vector/matrix allowed
- `t < Trace` (15–21) → scalar only
- `== Trace / Diag / Vec / Det / Rank / Null / Orth / Inv` → per-function checks

Appending `MathFuncMyFunc = 30` matches **no** branch: no type assertion runs and
`ret_type` silently becomes a copy of the parameter type. Add an explicit `elif` for it,
and mind the ordering.

### 4. All 7 codegen targets are mandatory

There is no fallback: a missing `visit_xxx` reaches `walk_object` →
`Exception('Unexpected type %s walked')` (`ir_visitor.py:617`). LaTeX / MathJax /
MathML / MacroMathjax render a *visual* form of the formula, so a new construct usually
needs a rendering, not just a textual translation.

### 5. New identifier shapes require touching `parser.py`

The second parse pass injects `extra_dict['ids']` (multi-word identifiers),
`['funcs']` (function names) and `['pkg']` (package symbols) into the grammar
(`parser.py:326-372`). New *keyword* syntax doesn't need this; new *identifier* syntax does.

### 6. Glossary JSON

`type_walker.gen_json_content()` (`type_walker.py:308`) produces the glossary JSON; update
it if you introduce a new kind of symbol.

## Suggested workflow

1. Write the `.ihla` snippet you want to support, plus a unittest in `test/`
   (follow `test/base_python_test.py`; e.g. `test/test_python_others.py`).
2. Grammar + `DEBUG_PARSER = True` + `--regenerate-grammar`.
3. `walk_X` in `type_walker.py` — get the type assertions right here.
4. IR node / enum value.
5. `ir_visitor.py` dispatch + **numpy codegen first** (fastest feedback), then the other 6.
6. `python -m iheartla file.ihla -o numpy` to inspect the output.
7. `./run_test.sh`.

## Conventions

- `##!#` and `##?#` prefixes in source are the author's inline notes (some are stale).
- `get_err_msg_info(parse_info, "msg")` is the standard way to raise a positioned error
  from the TypeWalker.
- `record("msg")` (`la_helper.py:128`) is used for opt-in timing instrumentation
  (`DEBUG_TIME`).
- Comments in this codebase are sparse; match the surrounding style rather than adding
  new commentary.
