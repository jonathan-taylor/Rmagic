import rpy2.rinterface as ri
import numpy as np
import rpy2.robjects as ro
import sys
import tempfile
from glob import glob
from shutil import rmtree
from getopt import getopt

# for publishing the information to the frontends

from IPython.core.displaypub import publish_display_data

# enable conversion of numpy arrays into R objects (following to rpy2 documentation)
from rpy2.robjects.numpy2ri import numpy2ri
ro.conversion.py2ri = numpy2ri

class Rmagic(object):

    def __init__(self, shell=None):
        self.r = ro.R()
        self.output = []
        self.eval = ri.baseenv['eval']
        self.shell = shell

    def write_console(self, output):
        self.output.append(output)

    def flush(self):
        value = ''.join(self.output)
        self.output = []
        return value

    def cell_magic(self, args, text):
        # need to get the ipython instance for assigning

        opts, args = getopt(args.strip().split(' '), None, ['inputs=',
                                                            'outputs=',
                                                            # these are options for png
                                                            'width=',
                                                            'height=',
                                                            'units=',
                                                            'pointsize=',
                                                            'bg='])

        opts = dict(opts)
        outputs = []
        for option, value in opts.items():
            if option == '--inputs':
                # need to have access the shell to assign these
                # python variables to variables in R
                opts.pop('--inputs')
                # with self.shell, we will assign the values to variables in the shell 
                # for now, this is a hack, with self.shell a dictionary
                for input in value.split(','):
                    self.r.assign(input, self.shell[input])
            if option == '--outputs':
                outputs = value.split(',')
                opts.pop('--outputs')
            
        png_args = ','.join(['%s=%s' % (o[2:],v) for o, v in opts.items()])

        # execute the R code in a temporary directory 

        tmpd = tempfile.mkdtemp()
        self.r('png("%s/Rplots%%03d.png",%s)' % (tmpd, png_args))
        self.eval(ri.parse(text))
        self.r('dev.off()')

        # read out all the saved .png files

        images = [file(imgfile).read() for imgfile in glob("%s/Rplots*png" % tmpd)]
        
        # now publish the images
        # mimicking IPython/zmq/pylab/backend_inline.py
        fmt = 'png'
        mimetypes = { 'png' : 'image/png', 'svg' : 'image/svg+xml' }
        mime = mimetypes[fmt]

        # publish the printed R objects, if any
        publish_display_data('Rmagic.cell_magic', {'text/plain':self.flush()})

        # flush text streams before sending figures, helps a little with output                                                                
        for image in images:
            # synchronization in the console (though it's a bandaid, not a real sln)                           
            sys.stdout.flush(); sys.stderr.flush()
            publish_display_data(
                'Rmagic.cell_magic',
                {mime : image}
            )
        value = {}

        # try to turn every output into a numpy array
        # this means that outputs are assumed to be castable
        # as numpy arrays

        for output in outputs:
            # with self.shell, we will assign the values to variables in the shell 
            self.shell[output] = np.asarray(self.r(output))

        # kill the temporary directory
        rmtree(tmpd)

from rrunner import EmbeddedRShell

class Rshell(object):

    def __init__(self):
        self.shell = EmbeddedRShell()

    def cell_magic(self, args, text):
        # need to get the ipython instance for assigning

        opts, args = getopt(args.strip().split(' '), None, [# these are options for png
                                                            'width=',
                                                            'height=',
                                                            'units=',
                                                            'pointsize=',
                                                            'bg='])

        png_args = ','.join(['%s=%s' % (o[2:],v) for o, v in opts])

        # execute the R code in a temporary directory 

        tmpd = tempfile.mkdtemp()
        # flush the output
        self.shell.astext()

        # set the plotting device and record an error, if any
        # maybe will be used for an exception
        self.shell.process('png("%s/Rplots%%03d.png",%s)' % (tmpd, png_args))
        png_error = self.shell.astext()

        # execute the code
        self.shell.process(text)
        text_result = self.shell.astext()

        # turn off the png device
        self.shell.process('dev.off()')

        # read out all the saved .png files

        images = [file(imgfile).read() for imgfile in glob("%s/Rplots*png" % tmpd)]
        
        # now publish the images
        # mimicking IPython/zmq/pylab/backend_inline.py
        fmt = 'png'
        mimetypes = { 'png' : 'image/png', 'svg' : 'image/svg+xml' }
        mime = mimetypes[fmt]

        # publish the printed R objects, if any
        publish_display_data('Rmagic.cell_magic', {'text/plain':text_result})

        # flush text streams before sending figures, helps a little with output                                                                
        for image in images:
            # synchronization in the console (though it's a bandaid, not a real sln)                           
            sys.stdout.flush(); sys.stderr.flush()
            publish_display_data(
                'Rmagic.cell_magic',
                {mime : image}
            )
        value = {}

        # kill the temporary directory
        rmtree(tmpd)


rmagic = Rmagic()
ri.set_writeconsole(rmagic.write_console)

rshell = Rshell()

if __name__ == '__main__':

    snippet = '''
    a=lm(Y~X)
    print(summary(a))
    plot(X, Y, pch=23, bg='orange', cex=2)
    plot(Y, X)
    print(summary(X))
    r = resid(a)
    '''

    opts = '--bg="gray" --width=700 --inputs=X,Y --outputs=r'

    # for now, this is a placeholder that will eventually be
    # a full ipython shell
    #
    # it is only used to retrieve the value of the variables to 
    # be assigned as inputs into R
    rmagic.shell = {'X': np.random.standard_normal(40),
                    'Y': np.random.standard_normal(40)}

    result = rmagic.cell_magic(opts, snippet)
