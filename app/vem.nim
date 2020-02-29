import os

let dep = execShellCmd("lsbaa -la")
if dep > 0:
  echo("command not found")
