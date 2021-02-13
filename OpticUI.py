# OpticUI 1.0
# Copyright Paul-E and Opticos Studios 2020


import PIL, os
from PIL import ImageFilter as ImageFilterOrig
from PIL import Image
from winreg import *
import imtools, ctypes

# from io import BytesIO
# import cairosvg


pygame = None

WIDTH, HEIGHT = 0, 0
ppi = 0

icon_pack_path = None

asset_dir = ""

icons = {}


def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def get_color():
    """
    Return the Windows 10 accent color used by the user in a HEX format
    """
    try:
        # Open the registry
        registry = ConnectRegistry(None, HKEY_CURRENT_USER)
        # Navigate to the key that contains the accent color info
        # key = OpenKey(registry, r'SOFTWARE\Microsoft\Windows\DWM')
        # key_value = QueryValueEx(key,'AccentColor')

        key = OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent')
        key_value = QueryValueEx(key, 'StartColorMenu')
        key_value2 = QueryValueEx(key, 'AccentPalette')
        value = key_value2[0]
        import codecs
        c = codecs.encode(value, "hex")

        bins = str(" ".join([hex(ch)[2:] for ch in value])).split(" ")
        bins = [b + "0" if b == "0" else b for b in bins]
        # print(bins[0] + bins[1] + bins[2])

        color = 4

        color = color * 3
        rgb = list(hex_to_rgb('#' + bins[color] + bins[color + 1] + bins[color + 2]))

        rgb = rgb[:3]

        if len(rgb) > 3:
            rgb = [rgb[0], rgb[1], rgb[2]]

        if rgb[0] < 0 or rgb[0] > 255 or rgb[1] < 0 or rgb[1] > 255 or rgb[2] < 0 or rgb[2] > 255:
            rgb = [0, 150, 150]

        # Make the color lighter if needed
        lightness = int((rgb[0] + rgb[1] + rgb[2]) / 3)
        if lightness < 30:
            rgb = [0, 150, 150]
        
        return rgb

        # Junk code
        """
        # Convert the interger to Hex and remove its offset
        accent_int = key_value[0]
        accent_hex = hex(accent_int + 4278190080)  # Remove FF offset and convert to HEX again
        accent_hex = str(accent_hex)[5:]  # -1] #Remove prefix and suffix

        accent = accent_hex[4:6] + accent_hex[2:4] + accent_hex[0:2]
        rgb = hex_to_rgb('#' + accent)
        rgb = rgb[:2]
        print(1, rgb)
        if rgb[0] < 0 or rgb[0] > 255 or rgb[1] < 0 or rgb[1] > 255 or rgb[2] < 0 or rgb[2] > 255:
            rgb = [0, 200, 200]
        print(2, rgb)
        return rgb
        """
    except:
        print("failing")
        return [0, 200, 200]


def set_icons(iconpack_path):
    global icon_pack_path, icons
    icon_pack_path = iconpack_path
    icons = {}
    for root, dirs, files in os.walk(icon_pack_path):
        for file in files:
            full = os.path.join(root, file)
            icons.update({file: full})


def icon(name, spec=None):
    filename = None  # "assets/chat.png"
    name = name.lower()
    names = None
    n = 0
    if " " in name:
        names = name.split(" ")
        name = names[0]
        name = name.lower()
    elif "." in name:
        names = name.split(".")
        name = names[0]
        name = name.lower()

    # name = name.replace(" ", "-")
    if names == None:
        names = [name]
    for name in names:
        for f in icons:
            full = icons[f]
            files = f[:-4].split("-")
            if str(name) == str(f)[:-4].lower():
                filename = full
                break

            elif str(name) == str(f).lower():
                filename = full
                break
            elif str(name) == files[0]:
                filename = full
            elif name in full:
                if spec == None:
                    filename = full
                    break
                else:
                    if spec in full:
                        filename = full
                        break
            if filename != None:
                break
        if filename != None:
            break

    if filename == None:
        filename = "link.png"
    if name == "":
        filename = "link.png"
    try:
        if filename.endswith(".svg") == True:
            pass
            # out = BytesIO()
            # cairosvg.svg2png(url=filename, write_to=out)
            # imager = Image.open(out)
        else:
            try:
                imager = Image.open(filename)
            except:
                with open(filename) as f:
                    reader = f.read()
                    if ".png" in reader:
                        filename = os.path.dirname(filename) + "\\" + reader
                        imager = Image.open(filename)
                    else:
                        imager = Image.open(asset_dir + "link.png")
        return imager

    except:
        imager = Image.open(asset_dir + "link.png")
        return imager
    return img


def pygame_icon(name, spec=None):
    filename = None  # "assets/chat.png"
    name = name.lower()
    names = None
    n = 0
    if " " in name:
        names = name.split(" ")
        name = names[0]
        name = name.lower()
    elif "." in name:
        names = name.split(".")
        name = names[0]
        name = name.lower()
    # name = name.replace(" ", "-")
    if names == None:
        names = [name]
    for name in names:
        for f in icons:
            full = icons[f]
            files = f[:-4].split("-")
            if str(name) == str(f)[:-4].lower():
                filename = full
                break

            elif str(name) == str(f).lower():
                filename = full
                break
            elif str(name) == files[0]:
                filename = full
            elif name in full:
                if spec == None:
                    filename = full
                    break
                else:
                    if spec in full:
                        filename = full
                        break
            if filename != None:
                break
        if filename != None:
            break

    if filename == None or filename == "":
        filename = asset_dir + "\\link.png"

    try:
        try:
            imager = pygame.image.load(filename).convert_alpha()
        except:
            with open(filename) as f:
                reader = f.read()
                if ".png" in reader:
                    filename = os.path.dirname(filename) + "\\" + reader
                    imager = pygame.image.load(filename).convert_alpha()

                else:
                    imager = pygame.image.load(asset_dir + "\\link.png").convert_alpha()
        return imager

    except:
        imager = pygame.image.load(asset_dir + "\\link.png").convert_alpha()
        return imager


def iris(canvas, pos, size, tint, radius=10, shadow_enabled=True, shadow_size=0.08, alpha=255):
    intensity = int((alpha / 255) * 30)
    s = pygame.Surface(size)
    s.blit(canvas, [0, 0], [pos[0], pos[1], size[0], size[1]])
    pygame.gfxdraw.filled_polygon(s, [[0, 0], [size[0], 0], size, [0, size[1]]], tint + [intensity])
    rad = radius
    b = pygame.image.tostring(s, "RGBA", False)
    b = PIL.Image.frombytes("RGBA", size, b)
    b = b.filter(PIL.ImageFilter.GaussianBlur(radius=int(rad)))
    b = pygame.image.frombuffer(b.tobytes(), b.size, b.mode).convert()
    b.set_alpha(alpha)

    if shadow_enabled == True:
        w_expand = (size[0] / size[1]) - 1
        if w_expand == 0:
            w_expand = 1
        shade = pygame.transform.scale(shadow, [size[0] + 2 * w(shadow_size * w_expand),
                                                size[1] + 2 * h(shadow_size)])
        shadow_alpha = int((alpha / 255) * 150)

        shade.set_alpha(shadow_alpha)

        canvas.blit(shade, [pos[0] - w(shadow_size * w_expand),
                            pos[1] - h(shadow_size)])
    canvas.blit(b, pos)


def iris_light(canvas, pos, size, tint, radius=10, shadow_enabled=True, shadow_size=0.08, alpha=255):
    intensity = int((alpha / 255) * 30)
    size = [int(size[0]), int(size[1])]
    resolution = 30  # percentage of pixels to use for blur

    s = pygame.Surface(size)  # , pygame.SRCALPHA)
    s.blit(canvas, [0, 0], [pos[0], pos[1], size[0], size[1]])
    s = pygame.transform.rotozoom(s, 0, (resolution / 100.0) * 1)

    size2 = s.get_size()
    pygame.gfxdraw.filled_polygon(s, [[0, 0], [size2[0], 0], size2, [0, size2[1]]], tint + [intensity])
    rad = radius
    b = pygame.image.tostring(s, "RGBA", False)
    b = PIL.Image.frombytes("RGBA", size2, b)

    b = replace_color(b, [0, 0, 0], [255, 0, 0])

    b = b.filter(PIL.ImageFilter.GaussianBlur(radius=int(rad)))
    b = pygame.image.frombuffer(b.tobytes(), b.size, b.mode).convert_alpha()

    if shadow_enabled == True:
        w_expand = (size[0] / size[1]) - 1
        if w_expand == 0:
            w_expand = 1
        shade = pygame.transform.scale(shadow, [size[0] + 2 * w(shadow_size * w_expand),
                                                size[1] + 2 * h(shadow_size)])
        shadow_alpha = int((alpha / 255) * 150)

        shade.set_alpha(shadow_alpha)

        canvas.blit(shade, [pos[0] - w(shadow_size * w_expand),
                            pos[1] - h(shadow_size)])

    # b = pygame.transform.rotozoom(b, 0, (100.0 / resolution) * 1)
    b = pygame.transform.scale(b, size)
    b.set_alpha(alpha)

    canvas.blit(b, pos)  # , special_flags=pygame.BLEND_RGBA_BLEND)


fancy = True
mode = "dark"


def set_blur(blur_on):
    global fancy
    fancy = blur_on


def toggle_quality():
    global fancy
    if fancy == True:
        fancy = False
    else:
        fancy = True


def toggle_mode():
    global mode
    if mode == "light":
        mode = "dark"
    else:
        mode = "light"


def iris2(canvas, pos, size, tint, radius=10, shadow_enabled=True, rounded=0, shadow_size=0.08, alpha=255,
          resolution=20, anti_glitch=False):
    global fancy, mode
    intensity = int((alpha / 255) * 30)
    if intensity > 255:
        intensity = 255
    elif intensity < 0:
        intensity = 0
    size = [int(size[0]), int(size[1])]
    if fancy == False:
        tnt = list(pygame.transform.average_color(canvas, [0, 0, 50, 50]))[:3]

    resolution = resolution  # percentage of pixels per inch to use. If one inch is 300 pixels, use 150 is var is set to 50%

    r = (resolution / 100.0) * inch2pix(1)

    inches_w = size[0] / inch2pix(1)

    r2 = inches_w * r

    resolution = (r2 / size[0]) * 100
    smooth_pad = 0
    if anti_glitch == True:
        smooth_pad = 5

    if fancy == False:
        smooth_pad = 0
    s = pygame.Surface([size[0] + int(2 * smooth_pad), size[1] + int(2 * smooth_pad)])  # , pygame.SRCALPHA)

    if fancy == True:
        s.blit(canvas, [0, 0], [pos[0] - smooth_pad, pos[1] - smooth_pad, size[0] + smooth_pad * 2,
                                size[1] + smooth_pad * 2])  # , special_flags=pygame.BLEND_RGBA_ADD)
        s = pygame.transform.rotozoom(s, 0, (resolution / 100.0) * 1)
        size2 = s.get_size()
        if tint != False:
            pygame.gfxdraw.filled_polygon(s, [[0, 0], [size2[0], 0], size2, [0, size2[1]]], tint + [intensity])
        if mode == "light":
            pygame.gfxdraw.filled_polygon(s, [[0, 0], [size2[0], 0], size2, [0, size2[1]]],
                                          [255, 255, 255] + [int(70 * (alpha / 255))])

        rad = radius
        b = pygame.image.tostring(s, "RGBA", False)
        b = PIL.Image.frombytes("RGBA", size2, b)

        # b = replace_color(b, [0, 0, 0], [255, 0, 0])

        b = b.filter(PIL.ImageFilter.GaussianBlur(radius=int(rad)))
        # b = b.crop((smooth_pad, smooth_pad, size2[0] - smooth_pad, size2[1] - smooth_pad))
        # maxsize = (size)
        # b.thumbnail(maxsize, PIL.Image.ANTIALIAS)
        if size[0] <= 0:
            size[0] = 1
        if size[1] <= 0:
            size[1] = 1

        b = b.resize(size)
        if rounded != 0:
            b = imtools.round_image(b, {}, False, None, rounded, 255, back_color="#00000000")

        b = pygame.image.frombuffer(b.tobytes(), b.size, b.mode).convert_alpha()

    else:
        pass
        """
        s.blit(canvas, [0, 0], [pos[0], pos[1], size[0], size[1]])
        size2 = size
        pygame.gfxdraw.filled_polygon(s, [[0, 0], [size2[0], 0], size2, [0, size2[1]]], tint + [200])
        b = s
        """

    # pygame.draw.rect(canvas, [0, 200, 0], [pos[0], pos[1], size[0], size[1]])

    if shadow_enabled == True:
        shadow_default = inch2pix(0.1)
        shadow_width = int(shadow_default * shadow_size)
        # Corners
        shadow_alpha = int((alpha / 255) * 150)
        s_cornera = s_corner.copy()
        s_cornera.set_alpha(shadow_alpha)
        scaled_corner = pygame.transform.scale(s_cornera, [shadow_width, shadow_width])

        # TR
        canvas.blit(scaled_corner, [pos[0] - shadow_width, pos[1] - shadow_width])
        # TL
        canvas.blit(pygame.transform.rotate(scaled_corner, -90), [pos[0] + size[0], pos[1] - shadow_width])
        # BR
        canvas.blit(pygame.transform.rotate(scaled_corner, -180), [pos[0] + size[0], pos[1] + size[1]])
        # BL
        canvas.blit(pygame.transform.rotate(scaled_corner, 90), [pos[0] - shadow_width, pos[1] + size[1]])
        # edges
        s_edgea = s_edge.copy()
        s_edgea.set_alpha(shadow_alpha)
        # R
        scaled_r = pygame.transform.scale(s_edgea, [shadow_width, size[1]])
        canvas.blit(scaled_r, [pos[0] - shadow_width, pos[1]])
        # T
        rotated_t = pygame.transform.rotate(s_edgea, -90)  # pygame.transform.rotozoom(s_edge, -90, 1)
        canvas.blit(pygame.transform.scale(rotated_t, [size[0], shadow_width]), [pos[0], pos[1] - shadow_width])
        # L
        rotated_l = pygame.transform.flip(s_edgea, True, False)
        canvas.blit(pygame.transform.scale(rotated_l, [shadow_width, size[1]]), [pos[0] + size[0], pos[1]])

        # B
        rotated_b = pygame.transform.rotate(s_edgea, 90)
        canvas.blit(pygame.transform.scale(rotated_b, [size[0], shadow_width]), [pos[0], pos[1] + size[1]])

    # b = pygame.transform.rotozoom(b, 0, (100.0 / resolution) * 1)

    # if fancy == True:
    #    b = pygame.transform.scale(b, size)

    if fancy == True:
        b.set_alpha(alpha)
        canvas.blit(b, pos)  # , special_flags=pygame.BLEND_RGBA_ADD)
    else:
        """
        pygame.gfxdraw.filled_polygon(canvas, [pos,
                                               [pos[0] + size[0], pos[1]],
                                               [pos[0] + size[0], pos[1] + size[1]],
                                              [pos[0], pos[1] + size[1]]], tint + [int(50 * (alpha / 255))])
        """
        if mode == "light":
            pygame.gfxdraw.filled_polygon(canvas, [pos,
                                                   [pos[0] + size[0], pos[1]],
                                                   [pos[0] + size[0], pos[1] + size[1]],
                                                   [pos[0], pos[1] + size[1]]],
                                          [255, 255, 255] + [int(255 * (alpha / 255))])
        else:
            pygame.gfxdraw.filled_polygon(canvas, [pos,
                                                   [pos[0] + size[0], pos[1]],
                                                   [pos[0] + size[0], pos[1] + size[1]],
                                                   [pos[0], pos[1] + size[1]]],
                                          [50, 50, 50] + [int(255 * (alpha / 255))])
        """
        pygame.gfxdraw.filled_polygon(canvas, [pos,
                                               [pos[0] + size[0], pos[1]],
                                               [pos[0] + size[0], pos[1] + size[1]],
                                               [pos[0], pos[1] + size[1]]], tnt + [int(100 * (alpha / 255))])
        """


def replace_color(img, color):
    data = np.array(img)
    red, green, blue, alpha = data.T
    replaced_areas = (alpha != 0)
    data[..., :][replaced_areas.T] = tuple(color + [255])
    img2 = Image.fromarray(data)
    return img2


def add_shadow(surface):
    new_surf = pygame.Surface([surface.get_width() + 15, surface.get_height() + 15], pygame.SRCALPHA)
    drop_shadow(new_surf, surface, [3, 3], alpha=80)
    new_surf.blit(surface, [8, 8], special_flags=pygame.BLEND_RGBA_ADD)
    return new_surf


def drop_shadow(canvas, surface, posit, radius=2, alpha=255, resolution=100):
    global fancy, mode
    intensity = int((alpha / 255) * 30)
    if intensity > 255:
        intensity = 255
    elif intensity < 0:
        intensity = 0

    size = surface.get_size()

    resolution = resolution  # percentage of pixels per inch to use. If one inch is 300 pixels, use 150 is var is set to 50%

    r = (resolution / 100.0) * inch2pix(1)

    inches_w = size[0] / inch2pix(1)

    r2 = inches_w * r

    resolution = (r2 / size[0]) * 100

    s = pygame.Surface([size[0] + int((100 / resolution) * radius * 3), size[1] + int((100 / resolution) * radius * 3)],
                       pygame.SRCALPHA)
    s.blit(surface, [int((100 / resolution) * radius), int((100 / resolution) * radius)])

    size = s.get_size()

    s = pygame.transform.rotozoom(s, 0, (resolution / 100.0) * 1)
    size2 = s.get_size()

    rad = radius
    b = pygame.image.tostring(s, "RGBA", False)
    b = PIL.Image.frombytes("RGBA", size2, b)

    b = replace_color(b, [0, 0, 0])

    b = b.filter(PIL.ImageFilter.GaussianBlur(radius=int(rad)))
    # b = b.crop((smooth_pad, smooth_pad, size2[0] - smooth_pad, size2[1] - smooth_pad))

    if size[0] <= 0:
        size[0] = 1
    if size[1] <= 0:
        size[1] = 1

    b = b.resize(size)

    b = pygame.image.frombuffer(b.tobytes(), b.size, b.mode).convert_alpha()

    b.set_alpha(int(80 * (alpha / 255)))
    canvas.blit(b, [posit[0] - int(int((100 / resolution) * (radius / 2))),
                    posit[1] - int((100 / resolution) * int(radius / 2))])


def noise(size, color, transparency, difference_range):
    """size, color, transparency (0-255), difference range"""

    clear = pygame.Surface(size)

    b = pygame.image.tostring(clear, "RGBA", False)

    UI = PIL.Image.frombytes("RGBA", size, b)

    UI = UI.convert("RGBA")

    UIpix = UI.load()

    for x in range(size[0]):

        for y in range(size[1]):

            random_color = [color[0] + random.randrange(-difference_range, difference_range),

                            color[1] + random.randrange(-difference_range, difference_range),

                            color[2] + random.randrange(-difference_range, difference_range), transparency]

            if random_color[0] < 0 or random_color[0] > 255:
                random_color[0] = color[0]

            if random_color[1] < 0 or random_color[1] > 255:
                random_color[1] = color[1]

            if random_color[2] < 0 or random_color[2] > 255:
                random_color[2] = color[2]

            random_color = tuple(random_color)

            UIpix[x, y] = random_color

    UI = pygame.image.frombuffer(UI.tobytes(), UI.size, UI.mode).convert_alpha()

    return UI


font_names = {}


class fakefont:
    def __init__(self, font_name, font_size):
        self.font = pygame.font.Font(font_name, font_size)
        self.texts = {}

    def render(self, text, alias, color):
        if text not in self.texts:
            text_surface = self.font.render(text, alias, color)
            self.texts.update({text: text_surface})
            return text_surface
        else:
            return self.texts[text]


font_scale = 1


def font(font_name, size):
    global font_names
    font_size = int(size * font_scale)
    ##print(font_names)
    if font_name not in font_names:
        font = fonter(font_name, font_size)  # pygame.font.Font
        ##print("new name")
        font_names.update({font_name: {font_size: font}})
    elif font_name in font_names:
        current_font_name = font_names[font_name]
        if font_size not in current_font_name:
            font = fonter(font_name, font_size)  # pygame.font.Font
            font_names[font_name].update({font_size: font})
            ##print("new_size_needed")

        elif font_size in current_font_name:
            ##print("font_exists")
            font = current_font_name[font_size]

    return font


class iris_efficient:
    def __init__(self):
        self.last_image = None

    def draw(self, canvas, pos, size, tint, radius=10, shadow_enabled=True, shadow_size=0.08, alpha=255):
        iris_light(canvas, pos, size, tint, old_img, radius=10, shadow_enabled=True, shadow_size=0.08, alpha=255)


def update():
    pass


scale = 1


def set_scale(scale_factor):
    global scale
    scale = scale_factor


def get_ppi():
    # root = tkinter.Tk()
    # root.withdraw()
    ppi = 96
    sysDpi = ctypes.windll.user32.GetDpiForSystem()
    sf = sysDpi / 96  # root.winfo_id()) / 96
    ppi *= sf
    return ppi


def init(scale_mode):  # , tk, tk_root):
    global WIDTH, HEIGHT, scalemode, ppi, font_scale  # , tkinter, root
    # root = tk_root
    # tkinter = tk
    scalemode = scale_mode
    ppi = get_ppi()


def start_graphics(pg, assets):
    global s_edge, s_corner, pygame, asset_dir, fonter
    pygame = pg
    import pygame.gfxdraw
    class fonter(pygame.font.Font):
        font.bold = False
        font.italic = False

    pygame.display.init()
    pygame.font.init()
    asset_dir = assets
    s_corner = pygame.image.load(asset_dir + "shadows/corner.png").convert_alpha()
    s_edge = pygame.image.load(asset_dir + "shadows/edge.png").convert_alpha()


def set_size(size):
    global WIDTH, HEIGHT, scalemode, ppi
    WIDTH, HEIGHT = size[0], size[1]


def inch2pix(inches):
    return int(ppi * inches * scale)


def h(proportion):
    global WIDTH, HEIGHT
    if scalemode == "dpi":
        p = (proportion) * ppi * scale
    elif scalemode == "stretch":
        p = float(proportion) * (HEIGHT / 600.0)

    return int(p)


def w(proportion):
    global WIDTH, HEIGHT
    if scalemode == "dpi":
        p = (proportion) * ppi * scale
    elif scalemode == "stretch":
        p = float(proportion) * (WIDTH / 900.0)

    return int(p)
