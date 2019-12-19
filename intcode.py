# day 5 part 1

class Op:
    def __init__(self, pos, value):
        self.pos = pos
        rest, self.opcode = divmod(value, 100)
        modes = []
        while rest:
            rest, mode = divmod(rest, 10)
            modes.append(mode)
        while len(modes) < 3:
            modes.append(0)
        self.modes = modes

    def execute(self, prog, read, write):
        if self.opcode == 99:
            raise StopError(self.pos)
        if self.opcode == 1:
            newpos = self.add(prog)
        elif self.opcode == 2:
            newpos = self.mul(prog)
        elif self.opcode == 3:
            newpos = self.inp(prog, read)
        elif self.opcode == 4:
            newpos = self.outp(prog, write)
        elif self.opcode == 5:
            newpos = self.jump_if_true(prog)
        elif self.opcode == 6:
            newpos = self.jump_if_false(prog)
        elif self.opcode == 7:
            newpos = self.less_than(prog)
        elif self.opcode == 8:
            newpos = self.equals(prog)
        elif self.opcode == 9:
            newpos = self.set_rbase(prog)
        else:
            raise ValueError(f"unknown opcode {self.opcode}")
        return newpos

    def add(self, prog):
        arg1 = self.get_arg(1, prog)
        arg2 = self.get_arg(2, prog)
        res = arg1 + arg2
        self.set_dest(prog, 3, res)
        return self.pos + 4

    def mul(self, prog):
        arg1 = self.get_arg(1, prog)
        arg2 = self.get_arg(2, prog)
        res = arg1 * arg2
        self.set_dest(prog, 3, res)
        return self.pos + 4

    def inp(self, prog, read):
        val = next(read)
        self.set_dest(prog, 1, val)
        return self.pos + 2

    def outp(self, prog, write):
        arg = self.get_arg(1, prog)
        write(arg)
        return self.pos + 2

    def jump_if_true(self, prog):
        arg1 = self.get_arg(1, prog)
        arg2 = self.get_arg(2, prog)
        if arg1 != 0:
            return arg2
        return self.pos + 3

    def jump_if_false(self, prog):
        arg1 = self.get_arg(1, prog)
        arg2 = self.get_arg(2, prog)
        if arg1 == 0:
            return arg2
        return self.pos + 3

    def less_than(self, prog):
        arg1 = self.get_arg(1, prog)
        arg2 = self.get_arg(2, prog)
        res = 0
        if arg1 < arg2:
            res = 1
        self.set_dest(prog, 3, res)
        return self.pos + 4

    def equals(self, prog):
        arg1 = self.get_arg(1, prog)
        arg2 = self.get_arg(2, prog)
        res = 0
        if arg1 == arg2:
            res = 1
        self.set_dest(prog, 3, res)
        return self.pos + 4

    def set_rbase(self, prog):
        arg = self.get_arg(1, prog)
        prog.rbase += arg
        return self.pos + 2

    def get_arg(self, i, prog):
        val = prog[self.pos + i]
        mode = self.modes[i-1]
        if mode == 0:
            # position mode
            val = prog[val]
        elif mode == 2:
            # relative mode
            val = prog[prog.rbase + val]
        return val

    def set_dest(self, prog, i, val):
        mode = self.modes[i-1]
        pos = self.pos + i
        dest = prog[pos]
        if mode == 2:
            # position mode
            dest = prog.rbase + dest
        prog[dest] = val

class OutOfInputError(Exception):
    pass

def reader(*values):
    for val in values:
        yield val
    raise OutOfInputError()

def d5execute(prog, pos, read, write):
    op = Op(pos, prog[pos])
    return op.execute(prog, read, write)

def rund5(prog, read, loud=True):
    pos = 0
    try:
        while True:
            pos = d5execute(prog, pos, read, print)
    except StopError as e:
        if loud:
            print(f"stopped at {e}")
    return prog

class ProgState:
    def __init__(self, prog):
        self.prog = prog
        self.extra = {}
        self.rbase = 0

    def __getitem__(self, index):
        if isinstance(index, slice):
            if index == slice(None, None, None):
                return ProgState(self.prog[:])
            raise ValueError(index)
        if index < 0:
            raise ValueError(index)
        if index < len(self.prog):
            return self.prog[index]
        return self.extra.get(index, 0)

    def __setitem__(self, index, value):
        if index < 0:
            raise ValueError(index)
        if index < len(self.prog):
            self.prog[index] = value
        else:
            self.extra[index] = value

    def clone(self):
        p = ProgState(self.prog[:])
        p.rbase = self.rbase
        p.extra = self.extra.copy()
        return p

def readprog(text):
    return ProgState([int(v) for v in text.split(',')])

def run(prog, loud=True):
    pos = 0
    try:
        while True:
            pos = execute(prog, pos)
    except StopError as e:
        if loud:
            print(f"stopped at {e}")
    return prog


def load(day):
    with open(f'day{day}-input') as f:
        return readprog(f.read().strip())


class Output:
    def __init__(self):
        self.sent = False
        self.val = None

    def __call__(self, val):
        self.sent = True
        self.val = val
