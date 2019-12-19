import intcode
from curses import wrapper
import sys

dirs = {
    (0, -1): 1,
    (0, 1): 2,
    (-1, 0): 3,
    (1, 0): 4,
}

ezdirs = {
    'KEY_UP': (0, -1),
    'KEY_DOWN': (0, 1),
    'KEY_LEFT': (-1, 0),
    'KEY_RIGHT': (1, 0),
}

leftwards = {
    (0, -1): (-1, 0),
    (-1, 0): (0, 1),
    (0, 1): (1, 0),
    (1, 0): (0, -1),
}

rightwards = {v:k for k, v in leftwards.items()}

HIT_WALL = 0
MOVED = 1
FOUND = 2

WALL = '#'
SPACE = '.'
GOAL = 'x'

def step(loc, direction):
    return loc[0] + direction[0], loc[1] + direction[1]

class Maze:
    def __init__(self, prog):
        self.prog = prog
        self.pos = 0
        self.map = {}
        self.loc = 0, 0
        self.minx = self.maxx = self.miny = self.maxy = 0

    def move(self, direction):
        direction = ezdirs.get(direction, direction)
        dir_code = dirs[direction]
        result = self.run_to_output(dir_code)
        new_loc = step(self.loc, direction)
        self.update_bbox(new_loc)
        if result == HIT_WALL:
            self.map[new_loc] = WALL
        elif result == MOVED:
            self.loc = new_loc
            self.map[new_loc] = SPACE
        elif result == FOUND:
            self.loc = new_loc
            self.map[new_loc] = GOAL
        return result

    def at(self, pos):
        return self.map.get(pos, ' ')

    def update_bbox(self, new_loc):
        self.minx = min(self.minx, new_loc[0])
        self.miny = min(self.miny, new_loc[1])
        self.maxx = max(self.maxx, new_loc[0])
        self.maxy = max(self.maxy, new_loc[1])

    def run_to_output(self, dir_code):
        output = intcode.Output()
        while not output.sent:
            self.pos = intcode.d5execute(self.prog, self.pos, intcode.reader(dir_code), output)
        return output.val

    def dump(self):
        for line in self.render():
            print(line)

    def render(self):
        for y in range(self.miny, self.maxy+1):
            line = []
            for x in range(self.minx, self.maxx+1):
                c = 'D' if (x, y) == self.loc else self.map.get((x, y), ' ')
                line.append(c)
            yield ''.join(line)


    def checkpoint(self):
        return MazeState(
            self.prog.clone(),
            self.pos,
            self.loc,
        )

    def restore(self, state):
        self.prog = state.prog.clone()
        self.pos = state.pos
        self.loc = state.loc

class MazeState:
    def __init__(self, prog, pos, loc):
        self.prog = prog
        self.pos = pos
        self.loc = loc

def solve(maze, path):
    loc = maze.loc
    if maze.at(loc) == GOAL:
        return True, path
    cp = maze.checkpoint()
    for dn in dirs:
        newloc = step(loc, dn)
        if maze.at(newloc) == WALL:
            continue
        if newloc in path:
            continue
        result = maze.move(dn)
        if result == HIT_WALL:
            continue
        solved, final_path = solve(maze, path + [newloc])
        if solved:
            return True, final_path
        maze.restore(cp)
    return False, []

def full_explore(maze, path):
    loc = maze.loc
    cp = maze.checkpoint()
    for dn in dirs:
        newloc = step(loc, dn)
        if maze.at(newloc) == WALL:
            continue
        if newloc in path:
            continue
        result = maze.move(dn)
        if result == HIT_WALL:
            continue
        full_explore(maze, path + [newloc])
        maze.restore(cp)

def interactive_main(stdscr, m):
    stdscr.clear()

    while True:
        key = stdscr.getkey()
        if key == "q":
            break
        m.move(key)
        for i, line in enumerate(m.render()):
            stdscr.addstr(i, 0, line)
        stdscr.refresh()

def solve_main(m):
    success, path = solve(m, [])
    if success:
        print("yay!")
        m.dump()
        print(len(path))

def explore_main(m):
    full_explore(m, [])
    m.dump()

def flood(maze):
    i = 0
    locs = {loc for loc, item in maze.items() if item == GOAL}
    spaces = {loc for loc, item in maze.items() if item == SPACE}
    while spaces:
        newlocs = set()
        for loc in locs:
            for dn in dirs:
                newloc = step(loc, dn)
                if newloc in spaces:
                    spaces.remove(newloc)
                    newlocs.add(newloc)
        i += 1
        locs = newlocs
    return i

if __name__ == "__main__":
    m = Maze(intcode.load(15))
    mode = 'full'
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    if mode == 'curses':
        wrapper(interactive_main, m)
    elif mode == 'solve':
        solve_main(m)
    else:
        explore_main(m)
        print(flood(m.map))
