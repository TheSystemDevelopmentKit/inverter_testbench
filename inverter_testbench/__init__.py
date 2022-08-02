"""
==================
Inverter testbench
==================

This class demonstrates how you can construct testbeches for your model
Entities to gain more versatilyty that can be provided by self tests in the 
mainguard.

Initially written by Marko Kosunen, marko.kosunen@aalto.fi, 2022.

"""

import os
import sys
if not (os.path.abspath('../../thesdk') in sys.path):
    sys.path.append(os.path.abspath('../../thesdk'))

from thesdk import *

from inverter import *
from inverter.controller import controller as inverter_controller
from inverter.signal_source import signal_source
from inverter.signal_plotter import signal_plotter


import numpy as np

class inverter_testbench(thesdk):
    @property
    def _classfile(self):
        return os.path.dirname(os.path.realpath(__file__)) + "/"+__name__

    def __init__(self,*arg): 
        self.print_log(type='I', msg='Inititalizing %s' %(__name__)) 
        self.proplist = [ 'Rs' ];    # Properties that can be propagated from parent
        self.Rs =  100e6;            # Sampling frequency
        self.vdd = 1.0               # Suplly voltage
        self.model='py';             # Can be set externally, but is not propagated
        self.models=['py','sv','vhdl','eldo','spectre']
        self.configuration='parallel'
        #self.models=['ngspice']
        self.par= False              # By default, no parallel processing
        self.queue= []               # By default, no parallel processing

        if len(arg)>=1:
            parent=arg[0]
            self.copy_propval(parent,self.proplist)
            self.parent =parent;

        self.init()

    def init(self):
        pass #Currently nohing to add

    def parallel(self):
        ''' Implements a configuration with a signal source, parallel inverters and plotters

        '''
        length=2**8
        controller=inverter_controller()
        controller.Rs=self.Rs
        #controller.reset()
        #controller.step_time()
        controller.start_datafeed()

        # Here we instantiate the signal source
        duts=[]
        plotters=[]
        #Here we construct the 'testbench'
        s_source=signal_source()
        for model in self.models:
            # Create an inverter
            d=inverter(self) # this is self is the parent
            duts.append(d) 
            d.model=model
            # Enable debug messages
            #d.DEBUG = True
            # Run simulations in interactive modes to monitor progress/results
            #d.interactive_spice=True
            #d.interactive_rtl=True
            # Preserve the IO files or simulator files for debugging purposes
            # d.preserve_iofiles = True
            # d.preserve_spicefiles = True
            # Save the entity state after simulation
            #d.save_state = True
            #d.save_database = True
            # Optionally load the state of the most recent simulation
            #d.load_state = 'latest'
            # This connects the input to the output of the signal source
            d.IOS.Members['A']=s_source.IOS.Members['data']
            # This connects the clock to the output of the signal source
            d.IOS.Members['CLK']=s_source.IOS.Members['clk']
            d.IOS.Members['control_write']=controller.IOS.Members['control_write']
            ## Add plotters
            p=signal_plotter()
            plotters.append(p) 
            p.plotmodel=d.model
            p.plotprefix='parallel'
            p.plotvdd=self.vdd
            p.Rs = self.Rs
            p.IOS.Members['A']=d.IOS.Members['A']
            p.IOS.Members['Z']=d.IOS.Members['Z']
            p.IOS.Members['A_OUT']=d.IOS.Members['A_OUT']
            p.IOS.Members['A_DIG']=d.IOS.Members['A_DIG']
            p.IOS.Members['Z_ANA']=d.IOS.Members['Z_ANA']
            p.IOS.Members['Z_RISE']=d.IOS.Members['Z_RISE']
        

        # Here we run the instances
        s_source.run() # Creates the data to the output
        for d in duts:
            d.init()
            d.run()
        for p in plotters:
            p.init()
            p.run()

    def serial(self):
        """ Configuration for inverter chain according to self.models
        Plots from intermediate outputs

        """
        # Construct first
        controller=inverter_controller()
        s_source=signal_source()
        duts=[]
        plotters=[]
        for k in range(len(self.models)):
            d=inverter(self)
            duts.append(d)
            if k==0:
                d.IOS.Members['A']=s_source.IOS.Members['data']
            else:
               d.IOS.Members['A']=duts[k-1].IOS.Members['Z']

            d.model=self.models[k]
            d.IOS.Members['control_write']=controller.IOS.Members['control_write']
            # Passing the same clock to all inverters (used in spice simulations)
            d.IOS.Members['CLK']=s_source.IOS.Members['clk']
            p=signal_plotter()
            plotters.append(p) 
            p.plotmodel=d.model
            p.plotprefix='serial'
            print(p.plotmodel)
            p.plotvdd=self.vdd
            p.Rs = self.Rs
            p.IOS.Members['A']=d.IOS.Members['A']
            p.IOS.Members['Z']=d.IOS.Members['Z']
            p.IOS.Members['A_OUT']=d.IOS.Members['A_OUT']
            p.IOS.Members['A_DIG']=d.IOS.Members['A_DIG']
            p.IOS.Members['Z_ANA']=d.IOS.Members['Z_ANA']
            p.IOS.Members['Z_RISE']=d.IOS.Members['Z_RISE']

        s_source.run() # Creates the data to the output
        controller.start_datafeed()
        for d in duts:
            d.init()
            d.run()
        for p in plotters:
            p.init()
            p.run()


    def main(self):
        """ Chooses the model to construct

        """
        if self.configuration == 'parallel':
            self.parallel()
        elif self.configuration == 'serial':
            self.serial()
        else:
            self.print_log(type='E' , msg='Test %s not implemented' %(self.configuration))

    def run(self,*arg):
        '''Guideline: Define model depencies of executions in `run` method.

        '''
        if self.model=='py':
            self.main()
            if self.par:
                # Return empty dict not to block the execution
                self.queue.put({})

if __name__=="__main__":
    from  inverter_testbench import *
    import pdb
    tb=inverter_testbench()
    tb.models=['py','sv','vhdl','eldo','spectre']
    #tb.configuration='parallel'
    tb.configuration='serial'
    tb.run()
    #This is here to keep the images visible
    #For batch execution, you should comment the following line 
    input()

