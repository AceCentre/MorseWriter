from Quartz import *
from PyObjCTools.AppHelper import runConsoleEventLoop

def key_callback(proxy, type_, event, refcon):
    # Get the key code
    key_code = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode)
    print("Key pressed:", key_code)
    return event

def main():
    tap = CGEventTapCreate(
        kCGSessionEventTap,
        kCGHeadInsertEventTap,
        kCGEventTapOptionDefault,
        CGEventMaskBit(kCGEventKeyDown),  # Listening only to key down events
        key_callback,
        None
    )
    if tap:
        runloop_source = CFMachPortCreateRunLoopSource(None, tap, 0)
        CFRunLoopAddSource(CFRunLoopGetCurrent(), runloop_source, kCFRunLoopCommonModes)
        CGEventTapEnable(tap, True)
        runConsoleEventLoop()
    else:
        print("Failed to create event tap")

if __name__ == '__main__':
    main()
