#!/usr/bin/env python3

from typing import *

from os import path
from .util import flatten
from .log import Logging
from .config import *

log = Logging(LOGLEVEL)()


backends: List[str]     = ["GHC", "GHCNoMain", "LaTeX", "QuickLaTeX"]
rewriteModes: List[str] = ["AsIs", "Instantiated", "HeadNormal", "Simplified", "Normalised"]
computeModes: List[str] = ["DefaultCompute", "IgnoreAbstract", "UseShowInstance"]
removeOrKeep: List[str] = ["Remove", "Keep"]
useForce: List[str]     = ["WithForce", "WithoutForce"]

class Position:
  def __init__(self:Any, srcFile:str, position:int, line:int, column:int):
    assert path.exists(srcFile)

    self.srcFile = srcFile
    self.position = position
    self.line = line
    self.column = column

  def __call__(self) -> List[str]:
    return ['(Pn ()', str(self.position), str(self.line), str(self.column), ')']

class Interval:
  def __init__(self:Any, start:Position, end:Position):
    self.start = start
    self.end = end

  def __call__(self:Any):
    return ['[Interval '] + self.start() + self.end() + [']']

class Range:
  def __init__(self:Any, intervals:List[Interval]=[]):
    self.intervals = intervals

  def __call__(self:Any):
    p = self.intervals[0].start.srcFile if len(self.intervals) > 0 else None
    intervals = flatten([i() for i in self.intervals ])
    return 'noRange' if len(self.intervals) == 0 else \
      '(intervalsToRange (Just (mkAbsolute "{p}")) {intervals})'.format(p=p, intervals=' '.join(intervals))


def rangeBuilder(f:str, p1:int, l1:int, c1:int, p2:int, l2:int, c2:int):
  assert path.exists(f)

  pos1 = Position(f, str(p1), str(l1), str(c1))
  pos2 = Position(f, str(p2), str(l2), str(c2))

  intr = Interval(pos1, pos2)
  return Range([intr])

class Commands:
  def __init__(self:Any, srcFile:str):
    assert path.exists(srcFile)

    self.history:List[str] = []
    self.srcFile = srcFile

  def __get__(self:Any, command:str):
    assert hasattr(self, command)

    method = getattr(self, command)
    return method

  def wrap(self:Any, command:str):
    return 'IOTCM "{srcFile}" NonInteractive Indirect ({command})'\
      .format(srcFile=self.srcFile, command=command)

  def wrap_global(self:Any, command:str):
    return 'IOTCM "{srcFile}" None Indirect ({command})'\
      .format(srcFile=self.srcFile, command=command)

  def compile(self:Any, backend:str, cmds:List[str]) -> str:

    assert backend in backends, \
        backend + ' should be on of ' + ', '.join(backends)

    command = 'Cmd_compile {backend} "{src}" [{commands}]'.format(
      backend=backend,
      src=self.srcFile,
      commands=','.join([ "\"" + c + "\"" for c in cmds ])
    )

    self.history.append(command)
    return self.wrap(command)

  def load(self:Any, cmds:List[str]) -> str:

    command = 'Cmd_load "{src}" [{commands}]'.format(
      src=self.srcFile,
      commands=','.join([ "\"" + c + "\"" for c in cmds ])
    )

    self.history.append(command)
    return self.wrap(command)

  def constraints(self:Any) -> str:
    command = 'Cmd_constraints'

    self.history.append(command)
    return self.wrap(command)

  def metas(self:Any) -> str:
    command = 'Cmd_metas'

    self.history.append(command)
    return self.wrap(command)

  def show_module_contents_toplevel(self:Any, rewrite:str, expr:str) -> str:
    assert rewrite in rewriteModes, \
        rewrite + ' should be on of ' + ', '.join(rewriteModes)

    command = 'Cmd_show_module_contents_toplevel {rewrite} "{expr}"'.format(
      rewrite=rewrite,
      expr=expr
    )

    self.history.append(command)
    return self.wrap_global(command)

  def search_about_toplevel(self:Any, rewrite:str, expr:str) -> str:
    assert rewrite in rewriteModes, \
        rewrite + ' should be on of ' + ', '.join(rewriteModes)

    command = 'Cmd_search_about_toplevel {rewrite} "{expr}"'.format(
      rewrite=rewrite,
      expr=expr
    )

    self.history.append(command)
    return self.wrap(command)

  def solveAll(self:Any, rewrite:str) -> str:
    assert rewrite in rewriteModes, \
        rewrite + ' should be on of ' + ', '.join(rewriteModes)

    command = 'Cmd_solveAll {rewrite}'.format(rewrite=rewrite)

    self.history.append(command)
    return self.wrap(command)

  def solveOne(self:Any, rewrite:str, interactionId:int, where:Range, expr:str) -> str:
    assert rewrite in rewriteModes, \
        rewrite + ' should be on of ' + ', '.join(rewriteModes)

    command = 'Cmd_solveOne {rewrite} {interactionId} {where} "{expr}"'.format(
      rewrite=rewrite,
      interactionId=str(interactionId),
      where=where(),
      expr=expr
    )

    self.history.append(command)
    return self.wrap(command)

  def autoAll(self:Any) -> str:
    command = 'Cmd_autoAll'

    self.history.append(command)
    return self.wrap(command)

  def autoOne(self:Any, interactionId:int, where:Range, expr:str) -> str:

    command = 'Cmd_autoOne {interactionId} {where} "{expr}"'.format(
      interactionId=str(interactionId),
      where=where(),
      expr=expr
    )

    self.history.append(command)
    return self.wrap(command)

  def auto(self:Any, interactionId:int, where:Range, expr:str) -> str:

    command = 'Cmd_auto {interactionId} {where} "{expr}"'.format(
      interactionId=str(interactionId),
      where=where(),
      expr=expr
    )

    self.history.append(command)
    return self.wrap(command)

  def infer_toplevel(self:Any, rewrite:str, expr:str) -> str:
    assert rewrite in rewriteModes, \
        rewrite + ' should be on of ' + ', '.join(rewriteModes)

    command = 'Cmd_infer_toplevel {rewrite} "{expr}"'.format(
      rewrite=rewrite,
      expr=expr
    )

    self.history.append(command)
    return self.wrap(command)

  def compute_toplevel(self:Any, computeMode:str, expr:str) -> str:
    assert computeMode in computeModes, \
        computeMode + ' should be on of ' + ', '.join(computeModes)

    command = 'Cmd_compute_toplevel {computeMode} "{expr}"'.format(
      computeMode=computeMode,
      expr=expr
    )

    self.history.append(command)
    return self.wrap_global(command)

  def load_highlighting_info(self:Any) -> str:

    command = ['Cmd_load_highlighting_info']
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def tokenHighlighting(self:Any, remove:str) -> str:
    assert remove in removeOrKeep, \
        remove + ' should be on of ' + ', '.join(removeOrKeep)

    command = ['Cmd_tokenHighlighting']
    command += ['"{src}"'.format(src=self.srcFile)]
    command += [remove]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def highlight(self:Any, interactionId:int, where:Range) -> str:

    command = ['Cmd_highlight']
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def give(self:Any, force:str, interactionId:int, where:Range) -> str:
    assert force in useForce, \
        force + ' should be on of ' + ', '.join(useForce)

    command = ['Cmd_give']
    command += [force]
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def refine(self:Any, interactionId:int, where:Range) -> str:

    command = ['Cmd_refine']
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def intro(self:Any, whether:bool, interactionId:int, where:Range) -> str:

    command = ['Cmd_intro']
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def refine_or_intro(self:Any, whether:bool, interactionId:int, where:Range) -> str:

    command = ['Cmd_refine_or_intro']
    command += ['True' if whether else 'False']
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def context(self:Any, rewrite:str, interactionId:int, where:Range) -> str:
    assert rewrite in rewriteModes, \
        rewrite + ' should be on of ' + ', '.join(rewriteModes)

    command = ['Cmd_context']
    command += [rewrite]
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def helper_function(self:Any, rewrite:str, interactionId:int, where:Range) -> str:
    assert rewrite in rewriteModes, \
        rewrite + ' should be on of ' + ', '.join(rewriteModes)

    command = ['Cmd_helper_function']
    command += [rewrite]
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def infer(self:Any, rewrite:str, interactionId:int, where:Range) -> str:
    assert rewrite in rewriteModes, \
        rewrite + ' should be on of ' + ', '.join(rewriteModes)

    command = ['Cmd_infer']
    command += [rewrite]
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def goal_type(self:Any, rewrite:str, interactionId:int, where:Range) -> str:
    assert rewrite in rewriteModes, \
        rewrite + ' should be on of ' + ', '.join(rewriteModes)

    command = ['Cmd_goal_type']
    command += [rewrite]
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def elaborate_give(self:Any) -> str:
    command = ['Cmd_elaborate_give']

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def goal_type_context(self:Any, rewrite:str, interactionId:int, where:Range) -> str:
    assert rewrite in rewriteModes, \
        rewrite + ' should be on of ' + ', '.join(rewriteModes)

    command = ['Cmd_goal_type_context']
    command += [rewrite]
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def goal_type_context_infer(self:Any) -> str:
    command = ['Cmd_goal_type_context_infer']

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def goal_type_context_check(self:Any) -> str:
    command = ['Cmd_goal_type_context_check']

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def show_module_contents(self:Any) -> str:
    command = ['Cmd_show_module_contents']

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def make_case(self:Any, interactionId:int, where:Range) -> str:

    command = ['Cmd_make_case']
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def why_in_scope(self:Any, interactionId:int, where:Range) -> str:

    command = ['Cmd_why_in_scope']
    command += [str(interactionId)]
    command += where()
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def compute(self:Any, computeMode:str) -> str:
    assert computeMode in computeModes, \
        computeMode + ' should be on of ' + ', '.join(computeModes)

    command = ['Cmd_compute']

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def why_in_scope_toplevel(self:Any) -> str:

    command = ['Cmd_why_in_scope_toplevel']
    command += ['"{src}"'.format(src=self.srcFile)]

    self.history.append(' '.join(command).strip())
    return self.wrap_global(' '.join(command).strip())

  def show_version(self:Any) -> str:
    command = ['Cmd_show_version']

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())

  def abort(self:Any) -> str:
    command = ['Cmd_abort']

    self.history.append(' '.join(command).strip())
    return self.wrap(' '.join(command).strip())