# -*- coding: utf-8 -*-
# <nbformat>3</nbformat>

# <headingcell level=1>

# RPY2 mode: transferring variables back and forth from python

# <codecell>

import Rmagic; reload(Rmagic)
import numpy as np
from Rmagic import rmagic
rmagic.shell = {'X': np.random.standard_normal(40),
                'Y': np.random.standard_normal(40)}

# <headingcell level=2>

# Line magic

# <codecell>

The line magic allows passing variables from python to rpy2 in one line calls.

# <headingcell level=2>

# Cell level magic

# <markdowncell>

# The cell magic executes a cell of R code, capturing the stdout of R as well as any plots made. The args to the magic allow
# passing python objects back and forth from python to rpy2 with --inputs denoting variables to be assigned in R and
# --outputs to be variables retrieved from rpy2 after executing the code.

# <markdowncell>

# In this example, data that is generated in python will be passed to R, a linear model will be fit and the variable 'r' (which happens to be the residuals from the linear model) will be passed back to ipython.

# <codecell>

snippet = '''
a=lm(Y~X)
# since I called print, I will see the summary of the model
print(summary(a))
# this will produce one plot
plot(X, Y, pch=23, bg='orange', cex=2)
# by default R creates 4 plots for plotting an lm, so there will be five plots in total
plot(a)

# this next print statement will show me summary(X)
print(summary(X))
r = resid(a)
'''

# <codecell>

opts = '--inputs=X,Y --outputs=r --bg="gray" --width=700'

# <codecell>

rmagic.cell_magic(opts, snippet)

# <markdowncell>

# As we can see, the ipython shell now has a variable 'r'.

# <codecell>

rmagic.shell['r']

# <markdowncell>

# For now, all outputs are cast to be np.arrays (good or bad)

# <codecell>

opts_a = '--inputs=X,Y --outputs=a --bg="gray" --width=700'
rmagic.cell_magic(opts_a, snippet)

# <codecell>

rmagic.shell['a']

# <headingcell level=1>

# R shell

# <markdowncell>

# Sometimes, for teaching, it might be nice to really mimic an R session. The rshell cell magic does this in the notebook.
# We will repeat essentially the same example above but now $X$ and $Y$ are generated in R as we are not able
# to pass data back and forth. It could be possible to pass arrays as strings, if we __really__ want to, but this seems wasteful.
# 
# Note that this R process is completely unrelated to the one in rpy2 mode: it is a separate process run through ipython's InteractiveRunner.

# <codecell>

from Rmagic import rshell
# in shell mode, the process is a completely separate R process so no variables
# are passed between R and python hence there are no --inputs --outputs args

opts_shell = ' --bg="yellow" --width=400'

snippet_shell = '''
Y = rnorm(40)
X = rnorm(40) + 2 * Y
a=lm(Y~X)
# since I called print, I will see the summary of the model
print(summary(a))
# this will produce one plot
plot(X, Y, pch=23, bg='orange', cex=2)
# by default R creates 4 plots for plotting an lm, so there will be five plots in total
plot(a)

# this next print statement will show me summary(X)
print(summary(X))
r = resid(a)
'''

# <codecell>

rshell.cell_magic(opts_shell, snippet_shell)

# <codecell>


# <codecell>


