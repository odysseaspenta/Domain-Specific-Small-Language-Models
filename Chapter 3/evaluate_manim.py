import ast

def is_syntax_valid(code_str):
  try:
    ast.parse(code_str)
    return True, ""
  except SyntaxError as e:
    return False, str(e)

class ManimCodeAnalyzer(ast.NodeVisitor):
  def __init__(self):
    self.imports_manim = False
    self.scene_subclass_names = []
    self.play_calls = 0
    self.create_calls = 0
    self.errors = []

  def visit_Import(self, node):
    for alias in node.names:
      if alias.name == "manim":
        self.imports_manim = True
    self.generic_visit(node)
  
  def visit_ImportFrom(self, node):
    if node.module and node.module.startswith("manim"):
      self.imports_manim = True
    self.generic_visit(node)

  def visit_ClassDef(self, node):
    for base in node.bases:
      if isinstance(base, ast.Name) and base.id == "Scene":
        self.scene_subclass_names.append(node.name)
      elif isinstance(base, ast.Attribute):
        if base.attr == "Scene":
          self.scene_subclass_names.append(node.name)
    self.generic_visit(node)

  def visit_Call(self, node):
    if isinstance(node.func, ast.Attribute):
      if (isinstance(node.func.value, ast.Name) and node.func.value.id == "self" and node.func.attr == "play"):
        self.play_calls += 1
      if isinstance(node.func, ast.Name) and node.func.id == "Create":
        self.create_calls += 1
    self.generic_visit(node)

def analyze_manim_code(code_str):
  analyzer = ManimCodeAnalyzer()
  try:
    tree = ast.parse(code_str)
  except SyntaxError as e:
    return {
      "syntax_valid": False,
      "syntax_error": str(e),
      "imports_manim": False,
      "scene_subclass_names": [],
      "play_calls": 0,
      "create_calls": 0,
      }
  analyzer.visit(tree)
  return {
    "syntax_valid": True,
    "syntax_error": None,
    "imports_manim": analyzer.imports_manim,
    "scene_subclass_names": analyzer.scene_subclass_names,
    "play_calls": analyzer.play_calls,
    "create_calls": analyzer.create_calls,
  }

# Test it out using some manim code
#
manim_code_sample = """
from manim import *

class MyScene(Scene):
  def construct(self):
    circle = Circle()
    self.play(Create(circle))
"""

result = analyze_manim_code(manim_code_sample)
print(result)

import os
import subprocess
import tempfile

def evaluate_manim_code(code_str, scene_class_name="CustomScene"):
  with tempfile.TemporaryDirectory() as tmpdir:
    code_path = os.path.join(tmpdir, "generated_scene.py")
    with open(code_path, "w") as f:
      f.write(code_str)
      
    cmd = [
        "manim",
        "-ql",
        code_path,
        scene_class_name,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        success = result.returncode == 0
        output = result.stdout + "\n" + result.stderr
    except subprocess.TimeoutExpired:
        success = False
        output = "Timeout expired during rendering."
    return success, output

# Test the evaluate_manim_code function
#
success, output = evaluate_manim_code(manim_code_sample, scene_class_name="MyScene")
print("Render success:", success)
print("Output:", output)