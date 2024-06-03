import ctypes
import objc
from Foundation import NSDictionary

Carbon = ctypes.CDLL('/System/Library/Frameworks/Carbon.framework/Carbon')

# Define the type of the TISCreateInputSourceList function
Carbon.TISCreateInputSourceList.restype = ctypes.c_void_p
Carbon.TISCreateInputSourceList.argtypes = [ctypes.c_void_p, ctypes.c_bool]

# Define the type of the TISGetInputSourceProperty function
Carbon.TISGetInputSourceProperty.restype = ctypes.c_void_p
Carbon.TISGetInputSourceProperty.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

# Define the kTISPropertyInputSourceID constant
# Define the kTISPropertyInputSourceID constant
# Define the kTISPropertyInputSourceID constant
kTISPropertyInputSourceID = ctypes.c_void_p.in_dll(Carbon, 'kTISPropertyInputSourceID')
kTISPropertyInputSourceID = objc.objc_object(c_void_p=kTISPropertyInputSourceID)
# Create a list of all input sources
input_sources = Carbon.TISCreateInputSourceList(None, False)

from ctypes import CFUNCTYPE, c_void_p, c_bool

# Define the CFArrayGetCount function
CFArrayGetCount = CFUNCTYPE(c_void_p, c_void_p)(('CFArrayGetCount', Carbon))

# Define the CFArrayGetValueAtIndex function
CFArrayGetValueAtIndex = CFUNCTYPE(c_void_p, c_void_p, c_void_p)(('CFArrayGetValueAtIndex', Carbon))

# Create a list of all input sources
input_sources = Carbon.TISCreateInputSourceList(None, False)

# Get the number of input sources
num_sources = CFArrayGetCount(input_sources)

# Define the kTISPropertyInputSourceID constant
kTISPropertyInputSourceID = ctypes.c_void_p.in_dll(Carbon, 'kTISPropertyInputSourceID')

# Print details about each input source
for i in range(num_sources):
    source = CFArrayGetValueAtIndex(input_sources, i)
    source_id_ptr = Carbon.TISGetInputSourceProperty(source, kTISPropertyInputSourceID)
    if source_id_ptr is not None:
        source_id = ctypes.c_char_p(source_id_ptr).value
        print(f"Input source {i}: {source_id}")