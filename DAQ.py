import ctypes
from ctypes.util import find_library
import numpy
from string import atoi
from time import sleep

# Class constants
#nidaq = ctypes.windll.nicaiu
nidaq  = ctypes.cdll.LoadLibrary(find_library('nidaqmxbase'))
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Default     = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Amps  = 10342
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_GroupByChannel = 0
DAQmx_Val_GroupByScanNumber = 1
max_num_samples = 2
sampling_frequency = 1000
data = numpy.zeros((max_num_samples,),dtype=numpy.float64)

def CHK(err):
    """a simple error checking routine"""
    if err < 0:
        buf_size = 100
        buf = ctypes.create_string_buffer('\000' * buf_size)
        nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
        raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))

class DAQ:
    def __init__(self, channel):
        #Channel sets the analogue input channel to measure from as a string
        # e.g. "Dev1/ai0"
        CHK(nidaq.DAQmxResetDevice (channel[0:4]))
        sleep(0.25)
        self.channel = channel

        #Does channel have a range?
        index = channel.rfind(":")
        if index != -1:
            self.number_of_channels = atoi(channel[index+1:len(channel)]) + 1
        else:
            self.number_of_channels = 1

        print "Using device " + channel[0:4] + " and %d channel(s):" % self.number_of_channels
        for i in range(0,self.number_of_channels):
            print channel[4:index-1] + "%d" % i
    
    
    def voltage(self):
        taskHandle = taskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle)))
        CHK(nidaq.DAQmxCreateAIVoltageChan(taskHandle,self.channel,"",DAQmx_Val_Cfg_Default,float64(-10.0),float64(10.0),DAQmx_Val_Volts,None))
        CHK(nidaq.DAQmxCfgSampClkTiming(taskHandle,"",float64(sampling_frequency),
                                DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
                                uInt64(max_num_samples)));
        CHK(nidaq.DAQmxStartTask(taskHandle))
        
        read = int32()
        data = numpy.zeros((max_num_samples*self.number_of_channels,),dtype=numpy.float64)
        CHK(nidaq.DAQmxReadAnalogF64(taskHandle,max_num_samples,float64(10.0),
                             DAQmx_Val_GroupByScanNumber,data.ctypes.data,
                             len(data),ctypes.byref(read),None))
        recorded_points = read.value
        CHK(nidaq.DAQmxStopTask(taskHandle))
        CHK(nidaq.DAQmxClearTask(taskHandle))
        return data[0:self.number_of_channels]
    
    def current(self):
        taskHandle = TaskHandle(0)
        CHK(nidaq.DAQmxCreateTask("",ctypes.byref(taskHandle)))
        # Is this the current channel ? "SC1Mod1/ai0"
        CHK(nidaq.DAQmxCreateAICurrentChan(taskHandle,self.channel,"",DAQmx_Val_Cfg_Default,float64(0.0),float64(0.02),DAQmx_Val_Amps,DAQmx_Val_Default,float64(249.0),""))
        CHK(nidaq.DAQmxCfgSampClkTiming(taskHandle,"",float64(sampling_frequency),
                                DAQmx_Val_Rising,DAQmx_Val_FiniteSamps,
                                uInt64(max_num_samples)));
        CHK(nidaq.DAQmxStartTask(taskHandle))
        
        read = int32()
        data = numpy.zeros((max_num_samples*self.number_of_channels,),dtype=numpy.float64)
        CHK(nidaq.DAQmxReadAnalogF64(taskHandle,max_num_samples,float64(10.0),
                             DAQmx_Val_GroupByScanNumber,data.ctypes.data,
                             len(data),ctypes.byref(read),None))
        
        recorded_points = read.value
        CHK(nidaq.DAQmxStopTask(taskHandle))
        CHK(nidaq.DAQmxClearTask(taskHandle))
        return data[0:self.number_of_channels]

if False:
	daq = DAQ("Dev1/ai0:2")
	volts = daq.voltage()
	print "Voltage", volts
	amps  = daq.current()
	print "Current", amps





