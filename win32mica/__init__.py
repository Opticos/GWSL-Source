import ctypes, sys

class MICAMODE():
    DARK = True
    LIGHT = False


debugging = False


def ApplyMica(HWND: int, ColorMode: bool = MICAMODE.LIGHT) -> int:
    """Apply the new mica effect on a window making use of the hidden win32api and return an integer depending on the result of the operation
    
    Keyword arguments:
    HWND -- a handle to a window (it being an integer value)
    ColorMode -- MICAMODE.DARK or MICAMODE.LIGHT, depending on the preferred UI theme. A boolean value can also be passed, True meaning Dark and False meaning Light
    """
    try:
        HWND = int(HWND)
    except ValueError:
        HWND = int(str(HWND), 16)
    
    if sys.platform == "win32" and sys.getwindowsversion().build >= 22000:
        user32 = ctypes.windll.user32
        dwm = ctypes.windll.dwmapi

        class AccentPolicy(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_uint),
                ("AccentFlags", ctypes.c_uint),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_uint)
            ]

        class WindowCompositionAttribute(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ctypes.c_int)),
                ("SizeOfData", ctypes.c_size_t)
            ]

        class _MARGINS(ctypes.Structure):
            _fields_ = [("cxLeftWidth", ctypes.c_int),
                        ("cxRightWidth", ctypes.c_int),
                        ("cyTopHeight", ctypes.c_int),
                        ("cyBottomHeight", ctypes.c_int)
                        ]

        DWM_UNDOCUMENTED_MICA_ENTRY = 1029 # Undocumented MICA (Windows 11 22523-)
        DWM_UNDOCUMENTED_MICA_VALUE = 0x01 # Undocumented MICA (Windows 11 22523-)
        
        DWM_DOCUMENTED_MICA_ENTRY = 38     # Documented MICA (Windows 11 22523+)
        DWM_DOCUMENTED_MICA_VALUE = 0x02   # Documented MICA (Windows 11 22523+)
        DWMW_USE_IMMERSIVE_DARK_MODE = 20


        SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
        DwmSetWindowAttribute = dwm.DwmSetWindowAttribute 
        DwmExtendFrameIntoClientArea = dwm.DwmExtendFrameIntoClientArea

        Acp = AccentPolicy()
        Acp.GradientColor = int("00cccccc", base=16)
        Acp.AccentState = 5
        Acp.AccentPolicy = 19

        Wca = WindowCompositionAttribute()
        Wca.Attribute = 19
        Wca.SizeOfData = ctypes.sizeof(Acp)
        Wca.Data = ctypes.cast(ctypes.pointer(Acp), ctypes.POINTER(ctypes.c_int))

        Mrg = _MARGINS(-1, -1, -1, -1)
        
        o = DwmExtendFrameIntoClientArea(HWND, ctypes.byref(Mrg))
        if debugging:
            if o != 0:
                print("Win32mica: Failed to DwmExtendFrameIntoClientArea", hex(o+0xffffffff))
            else:
                print("Win32mica: DwmExtendFrameIntoClientArea Ok")
        o = SetWindowCompositionAttribute(HWND, Wca)
        if debugging:
            if o != 0:
                print("Win32mica: Failed to SetWindowCompositionAttribute", o)
            else:
                print("Win32mica: SetWindowCompositionAttribute Ok")
        
        if ColorMode == MICAMODE.DARK:
            Wca.Attribute = 26
            o = SetWindowCompositionAttribute(HWND, Wca)
            if debugging:
                if o != 0:
                    print("Win32mica: Failed to SetWindowCompositionAttribute (dark mode)", o)
                else:
                    print("Win32mica: SetWindowCompositionAttribute OK (dark mode)", o)
        else:
            if debugging:
                print("Win32mica: No SetWindowCompositionAttribute (light mode)")

        
        if ColorMode == True: # Apply dark mode
            DwmSetWindowAttribute(HWND, DWMW_USE_IMMERSIVE_DARK_MODE, ctypes.byref(ctypes.c_int(0x01)), ctypes.sizeof(ctypes.c_int))
        else: # Apply light mode
            DwmSetWindowAttribute(HWND, DWMW_USE_IMMERSIVE_DARK_MODE, ctypes.byref(ctypes.c_int(0x00)), ctypes.sizeof(ctypes.c_int)) 

        if sys.getwindowsversion().build < 22523: # If mica is not a public API
            return DwmSetWindowAttribute(HWND, DWM_UNDOCUMENTED_MICA_ENTRY, ctypes.byref(ctypes.c_int(DWM_UNDOCUMENTED_MICA_VALUE)), ctypes.sizeof(ctypes.c_int))
        else: # If mica is present in the public API
            return DwmSetWindowAttribute(HWND, DWM_DOCUMENTED_MICA_ENTRY, ctypes.byref(ctypes.c_int(DWM_DOCUMENTED_MICA_VALUE)), ctypes.sizeof(ctypes.c_int))    
    else:
        print(f"Win32Mica Error: {sys.platform} version {sys.getwindowsversion().build} is not supported")
        return 0x32


#ApplyMica(1181804, MICAMODE.DARK)

def Disable(HWND: int) -> int:
    """Apply the new mica effect on a window making use of the hidden win32api and return an integer depending on the result of the operation
    
    Keyword arguments:
    HWND -- a handle to a window (it being an integer value)
    ColorMode -- MICAMODE.DARK or MICAMODE.LIGHT, depending on the preferred UI theme. A boolean value can also be passed, True meaning Dark and False meaning Light
    """
    try:
        HWND = int(HWND)
    except ValueError:
        HWND = int(str(HWND), 16)
    
    if sys.platform == "win32" and sys.getwindowsversion().build >= 22000:
        user32 = ctypes.windll.user32
        dwm = ctypes.windll.dwmapi

        class AccentPolicy(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_uint),
                ("AccentFlags", ctypes.c_uint),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_uint)
            ]

        class WindowCompositionAttribute(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ctypes.c_int)),
                ("SizeOfData", ctypes.c_size_t)
            ]

        class _MARGINS(ctypes.Structure):
            _fields_ = [("cxLeftWidth", ctypes.c_int),
                        ("cxRightWidth", ctypes.c_int),
                        ("cyTopHeight", ctypes.c_int),
                        ("cyBottomHeight", ctypes.c_int)
                        ]

        DWM_UNDOCUMENTED_MICA_ENTRY = 1029 # Undocumented MICA (Windows 11 22523-)
        DWM_UNDOCUMENTED_MICA_VALUE = 0x01 # Undocumented MICA (Windows 11 22523-)
        
        DWM_DOCUMENTED_MICA_ENTRY = 38     # Documented MICA (Windows 11 22523+)
        DWM_DOCUMENTED_MICA_VALUE = 0x02   # Documented MICA (Windows 11 22523+)
        DWMW_USE_IMMERSIVE_DARK_MODE = 20


        SetWindowCompositionAttribute = user32.SetWindowCompositionAttribute
        DwmSetWindowAttribute = dwm.DwmSetWindowAttribute 
        DwmExtendFrameIntoClientArea = dwm.DwmExtendFrameIntoClientArea

        Acp = AccentPolicy()
        Acp.GradientColor = int("00cccccc", base=16)
        Acp.AccentState = 0
        Acp.AccentPolicy = 19

        Wca = WindowCompositionAttribute()
        Wca.Attribute = 19
        Wca.SizeOfData = ctypes.sizeof(Acp)
        Wca.Data = ctypes.cast(ctypes.pointer(Acp), ctypes.POINTER(ctypes.c_int))

        Mrg = _MARGINS(0, 0, 0, 0)
        
        o = DwmExtendFrameIntoClientArea(HWND, ctypes.byref(Mrg))


        #o = SetWindowCompositionAttribute(HWND, Wca)


        Wca.Attribute = 26
        #o = SetWindowCompositionAttribute(HWND, Wca)
        
           
        
        #DwmSetWindowAttribute(HWND, DWMW_USE_IMMERSIVE_DARK_MODE, ctypes.byref(ctypes.c_int(3)), ctypes.sizeof(ctypes.c_int)) 


