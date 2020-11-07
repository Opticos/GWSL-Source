#WIN32BLUR
import ctypes
from enum import IntEnum, Enum
user32 = ctypes.windll.user32
c_ulong = ctypes.c_ulong

class ACCENTSTATE(ctypes.c_int):
    ACCENT_DISABLED = 0
    ACCENT_ENABLE_GRADIENT = 1
    ACCENT_ENABLE_TRANSPARENTGRADIENT = 2
    ACCENT_ENABLE_BLURBEHIND = 3
    ACCENT_ENABLE_ACRYLICBLURBEHIND = 4
    ACCENT_INVALID_STATE = 5

class ACCENTPOLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ACCENTSTATE),
        ("AccentFlags", ctypes.c_uint),
        ("GradientColor", ctypes.c_uint),
        ("AnimationId", ctypes.c_uint)
    ]

class WINDOWCOMPOSITIONATTRIB (ctypes.c_int): #look into this type
    WCA_UNDEFINED = 0
    WCA_NCRENDERING_ENABLED = 1
    WCA_NCRENDERING_POLICY = 2
    WCA_TRANSITIONS_FORCEDISABLED = 3
    WCA_ALLOW_NCPAINT = 4
    WCA_CAPTION_BUTTON_BOUNDS = 5
    WCA_NONCLIENT_RTL_LAYOUT = 6
    WCA_FORCE_ICONIC_REPRESENTATION = 7
    WCA_EXTENDED_FRAME_BOUNDS = 8
    WCA_HAS_ICONIC_BITMAP = 9
    WCA_THEME_ATTRIBUTES = 10
    WCA_NCRENDERING_EXILED = 11
    WCA_NCADORNMENTINFO = 12
    WCA_EXCLUDED_FROM_LIVEPREVIEW = 13
    WCA_VIDEO_OVERLAY_ACTIVE = 14
    WCA_FORCE_ACTIVEWINDOW_APPEARANCE = 15
    WCA_DISALLOW_PEEK = 16
    WCA_CLOAK = 17
    WCA_CLOAKED = 18
    WCA_ACCENT_POLICY = 19
    WCA_FREEZE_REPRESENTATION = 20
    WCA_EVER_UNCLOAKED = 21
    WCA_VISUAL_OWNER = 22
    WCA_HOLOGRAPHIC = 23
    WCA_EXCLUDED_FROM_DDA = 24
    WCA_PASSIVEUPDATEMODE = 25
    WCA_USEDARKMODECOLORS = 26
    WCA_LAST = 27

    
class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", WINDOWCOMPOSITIONATTRIB),
        ("Data", ctypes.POINTER(ctypes.c_int)),
        ("SizeOfData", ctypes.c_size_t)
    ]

accent = ACCENTPOLICY()

accent.AccentState = ACCENTSTATE.ACCENT_ENABLE_ACRYLICBLURBEHIND
accent.GradientColor = ctypes.c_uint(0xCC000000)
#accent.AccentFlags = 0
accentStructSize = ctypes.sizeof(accent)

data = WINDOWCOMPOSITIONATTRIBDATA()

data.Attribute = WINDOWCOMPOSITIONATTRIB.WCA_ACCENT_POLICY
data.SizeOfData = accentStructSize
data.Data = ctypes.cast(ctypes.pointer(accent), ctypes.POINTER(ctypes.c_int))

def blur(HWND):
    return user32.SetWindowCompositionAttribute(ctypes.cast(HWND, ctypes.POINTER(ctypes.c_int)), ctypes.byref(data))
    #print(ctypes.GetLastError())




    
