'''Spell check the markdown text in IPython notebooks

As much as I love the IPython notebook, there is one big drawback (at least in
my installation). When I type into a cell in the browser (I use firefox) there
is no automatic spell checking of the input. Sure, the notebook has syntax
highlighting for code cells in python, but I want to do my entire paper
writing in the notebook and for me that means that a spell checker for cells
with markdown, headings or raw text is absolutely essential. 
On the other hand, I cannot just run e.g. ``ispell`` on the ipynb file, since
most of its contents is actually code and not plain English.
So, I want to write a spell checker, that parses the ipynb file and spell checks
only the markdown, heading and raw text input cells.

There are several python bindings for spell checkers, but I have recently read
`good things <http://doughellmann.com/2011/05/creating-a-spelling-checker-for-restructuredtext-documents-2.html>`_ 
about `pyEnchant <http://pythonhosted.org/pyenchant/>`_ .
PyEnchant is an interface to the 
`Enchant <http://www.abisource.com/projects/enchant/>`_ library, which in turn
is a wrapper around one or more of your system spell checkers like ispell,
aspell or myspell. Enchant is installed by default on common Linux
distributions or available from package managers. Binary installers for Mac and
Windows are available from the Enchant website.
I installed pyenchant with a simple::

    pip install pyenchant

(Pyenchant lives on `<https://github.com/rfk/pyenchant>`_ if you want to read
the source.)
With this, the code for the spell checker is barely a dozen lines long (see
below).

Oh, one more thing: Because I type a lot of raw LaTeX in my notebooks (see my 
other post on ``ipynb2article.py``) as opposed to real markdown that resembles
English much better I define a custom filter function that
makes sure that strings which look like LaTeX commands will not be spell checked
(since very few LaTeX command are valid English words so that would give a lot of 
apparent typos).
More complicated filters that avoid spell checking within equations or
commands like ``\label{XXX}`` or ``\cite{}`` are possible (they would be called
a ``chunker`` in ``pyenchant``). Check the `github repository <https://github.com/hamogu/ipythontools>`_
for this code if you want to see if I have an improved version.


How to use this script
----------------------
Close down the notebook you want to spell check in IPython, then simply type on
the command line::

    > python spellchecker.py filein.ipynb fileout.ipynb

Open the new file in IPython, run all cells again and keep working.

filein and fileout can be the same filename (in this case the old file will get
overwritten with the spelling corrected version), but I recommend to keep a copy
just in case something gets screwed up.
'''
import re
import json
import sys

import enchant
import enchant.tokenize
import enchant.checker
from enchant.checker.CmdLineChecker import CmdLineChecker

class LatexCommandFilter(enchant.tokenize.EmailFilter):
    _pattern = re.compile(r"\\([^a-zA-Z]|[a-zA-Z]+)")

chkr = enchant.checker.SpellChecker("en_US", filters=[LatexCommandFilter])
cmdln = CmdLineChecker()
cmdln.set_checker(chkr)


with open(sys.argv[1], 'r') as f:
    print 'Parsing ', sys.argv[1]
    ipynb = json.load(f)

for cell in ipynb['worksheets'][0]['cells']:
    if cell['cell_type'] in ['markdown', 'raw', 'heading']:
        for i, line in enumerate(cell['source']):
            chkr.set_text(line)
            cmdln.run()
            cell['source'][i] = chkr.get_text()

with open(sys.argv[2], 'w') as f:
    print 'Writing ', sys.argv[2]
    json.dump(ipynb, f)

