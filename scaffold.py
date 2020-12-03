# day 17

import intcode

class Camera:
    def __init__(self, prog):
        self.prog = prog

    def get_image(self):
        chars = []
        def output(val):
            chars.append(chr(val))
        intcode.rund7(self.prog, intcode.reader(), output)
        return ''.join(chars)

def parse_image(image):
    lines = image.splitlines()
    height = len(lines)
    width = max(map(len, lines))
    pixels = {}
    for y, line in enumerate(lines):
        for x, c in enumerate(line):
            pixels[x, y] = c
    return pixels, width, height

def find_junctions(image):
    pixels, width, height = parse_image(image)
    for (x, y), c in pixels.items():
        if x == 0 or y == 0 or x == width - 1 or y == height - 1:
            continue
        if c != '#':
            continue
        if (pixels[x - 1, y] != '#'
            or pixels[x, y-1] != '#'
            or pixels[x+1, y] != '#'
            or pixels[x, y+1] != '#'):
            continue
        yield x, y

if __name__ == "__main__":
    c = Camera(intcode.load(17))
    image = c.get_image()
    print(image)
    print(sum(a * b for a, b in find_junctions(image)))
