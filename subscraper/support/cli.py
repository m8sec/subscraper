import os

STYLE = {'None'      : '0',
         'bold'      : '1'}

FG = {'gray'  : ';30',
      'red'   : ';31',
     'green' : ';32',
      'yellow': ';33',
      'blue'  : ';34'}

def code_gen(data, style, color, windows=False):
    return data if windows else '\033[0{}{}m{}\033[0m'.format(STYLE[style], FG[color], data)

def highlight(data, fg='blue', style='bold'):
    return code_gen(data, style, fg, windows=True if os.name == 'nt' else False)
