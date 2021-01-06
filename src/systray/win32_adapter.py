import ctypes
import ctypes.wintypes
import locale
import sys

u32 = ctypes.windll.user32
RegisterWindowMessage = u32.RegisterWindowMessageA
LoadCursor = u32.LoadCursorA
LoadIcon = u32.LoadIconA
LoadImage = u32.LoadImageA
RegisterClass = u32.RegisterClassA
CreateWindowEx = u32.CreateWindowExA
UpdateWindow = u32.UpdateWindow
DefWindowProc = u32.DefWindowProcA
GetSystemMetrics = u32.GetSystemMetrics
InsertMenuItem = u32.InsertMenuItemA
PostMessage = u32.PostMessageA
PostQuitMessage = u32.PostQuitMessage
SetMenuDefaultItem = u32.SetMenuDefaultItem
GetCursorPos = u32.GetCursorPos
SetForegroundWindow = u32.SetForegroundWindow
TrackPopupMenu = u32.TrackPopupMenu
CreatePopupMenu = u32.CreatePopupMenu
GetDC = u32.GetDC
GetSysColorBrush = u32.GetSysColorBrush
FillRect = u32.FillRect
DrawIconEx = u32.DrawIconEx
DestroyWindow = u32.DestroyWindow
GetMessage = u32.GetMessageA
TranslateMessage = u32.TranslateMessage
DispatchMessage = u32.DispatchMessageA
DestroyIcon = u32.DestroyIcon

gdi32 = ctypes.windll.gdi32
CreateCompatibleDC = gdi32.CreateCompatibleDC
CreateCompatibleBitmap = gdi32.CreateCompatibleBitmap
SelectObject = gdi32.SelectObject
DeleteDC = gdi32.DeleteDC
GetModuleHandle = ctypes.windll.kernel32.GetModuleHandleA
Shell_NotifyIcon = ctypes.windll.shell32.Shell_NotifyIcon

NIM_ADD = 0
NIM_MODIFY = 1
NIM_DELETE = 2
NIF_ICON = 2
NIF_MESSAGE = 1
NIF_TIP = 4
MIIM_ID = 2
MIIM_SUBMENU = 4
MIIM_STRING = 64
MIIM_BITMAP = 128
WM_DESTROY = 2
WM_CLOSE = 16
WM_COMMAND = 273
WM_USER = 1024
WM_LBUTTONDBLCLK = 515
WM_RBUTTONUP = 517
WM_LBUTTONUP = 514
WM_NULL = 0
CS_VREDRAW = 1
CS_HREDRAW = 2
IDC_ARROW = 32512
COLOR_WINDOW = 5
WS_OVERLAPPED = 0
WS_SYSMENU = 524288
CW_USEDEFAULT = -2147483648
LR_LOADFROMFILE = 16
LR_DEFAULTSIZE = 64
IMAGE_ICON = 1
IDI_APPLICATION = 32512
TPM_LEFTALIGN = 0
SM_CXSMICON = 49
SM_CYSMICON = 50
COLOR_MENU = 4
DI_NORMAL = 3

WPARAM = ctypes.wintypes.WPARAM
LPARAM = ctypes.wintypes.LPARAM
HANDLE = ctypes.wintypes.HANDLE
_void_p_size = ctypes.sizeof(ctypes.c_void_p)
if ctypes.sizeof(ctypes.c_long) == _void_p_size:
    LRESULT = ctypes.c_long
elif ctypes.sizeof(ctypes.c_longlong) == _void_p_size:
    LRESULT = ctypes.c_longlong

SZTIP_MAX_LENGTH = 128
LOCALE_ENCODING = locale.getpreferredencoding()


def encode_for_locale(s):
    """
    Encode text items for system locale. If encoding fails, fall back to ASCII.
    """
    try:
        return s.encode(LOCALE_ENCODING, "ignore")
    except (AttributeError, UnicodeDecodeError):
        return s.decode("ascii", "ignore").encode(LOCALE_ENCODING)


POINT = ctypes.wintypes.POINT
RECT = ctypes.wintypes.RECT
MSG = ctypes.wintypes.MSG

LPFN_WNDPROC = ctypes.CFUNCTYPE(LRESULT, HANDLE, ctypes.c_uint, WPARAM, LPARAM)


class WNDCLASS(ctypes.Structure):
    _fields_ = [
        ("style", ctypes.c_uint),
        ("lpfnWndProc", LPFN_WNDPROC),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", HANDLE),
        ("hIcon", HANDLE),
        ("hCursor", HANDLE),
        ("hbrBackground", HANDLE),
        ("lpszMenuName", ctypes.c_char_p),
        ("lpszClassName", ctypes.c_char_p),
    ]


class MENUITEMINFO(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("fMask", ctypes.c_uint),
        ("fType", ctypes.c_uint),
        ("fState", ctypes.c_uint),
        ("wID", ctypes.c_uint),
        ("hSubMenu", HANDLE),
        ("hbmpChecked", HANDLE),
        ("hbmpUnchecked", HANDLE),
        ("dwItemData", ctypes.c_void_p),
        ("dwTypeData", ctypes.c_char_p),
        ("cch", ctypes.c_uint),
        ("hbmpItem", HANDLE),
    ]


class NOTIFYICONDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", ctypes.c_uint),
        ("hWnd", HANDLE),
        ("uID", ctypes.c_uint),
        ("uFlags", ctypes.c_uint),
        ("uCallbackMessage", ctypes.c_uint),
        ("hIcon", HANDLE),
        ("szTip", ctypes.c_char * SZTIP_MAX_LENGTH),
        ("dwState", ctypes.c_uint),
        ("dwStateMask", ctypes.c_uint),
        ("szInfo", ctypes.c_char * 256),
        ("uTimeout", ctypes.c_uint),
        ("szInfoTitle", ctypes.c_char * 64),
        ("dwInfoFlags", ctypes.c_uint),
        ("guidItem", ctypes.c_char * 16),
    ]
    if sys.getwindowsversion().major >= 5:
        _fields_.append(("hBalloonIcon", HANDLE))


def PackMENUITEMINFO(text=None, hbmpItem=None, wID=None, hSubMenu=None):
    res = MENUITEMINFO()
    res.cbSize = ctypes.sizeof(res)
    res.fMask = 0
    if hbmpItem is not None:
        res.fMask |= MIIM_BITMAP
        res.hbmpItem = hbmpItem
    if wID is not None:
        res.fMask |= MIIM_ID
        res.wID = wID
    if text is not None:
        text = encode_for_locale(text)
        res.fMask |= MIIM_STRING
        res.dwTypeData = text
    if hSubMenu is not None:
        res.fMask |= MIIM_SUBMENU
        res.hSubMenu = hSubMenu
    return res


def LOWORD(w):
    return w & 0xFFFF


def PumpMessages():
    msg = MSG()
    while GetMessage(ctypes.byref(msg), None, 0, 0) > 0:
        TranslateMessage(ctypes.byref(msg))
        DispatchMessage(ctypes.byref(msg))


def NotifyData(hWnd=0, uID=0, uFlags=0, uCallbackMessage=0, hIcon=0, szTip=""):
    szTip = encode_for_locale(szTip)[:SZTIP_MAX_LENGTH]
    res = NOTIFYICONDATA()
    res.cbSize = ctypes.sizeof(res)
    res.hWnd = hWnd
    res.uID = uID
    res.uFlags = uFlags
    res.uCallbackMessage = uCallbackMessage
    res.hIcon = hIcon
    res.szTip = szTip
    return res
