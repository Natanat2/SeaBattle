from random import randint

print('   -------------------- \n '
      '    Игра морской бой \n'
      '   -------------------- \n'
      '   ходы в формате x, y:\n'
      '      x - строка\n'
      '      y - столбец')


class MyException(Exception):
    pass


class OutException(MyException):
    def __str__(self):
        return 'Вы стреляете за пределы поля'


class UsedException(MyException):
    def __str__(self):
        return 'Вы уже сюда стреляли'


class MissShipException(MyException):
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class Ship:
    def __init__(self, bow, length, direction):
        self.bow = bow
        self.length = length
        self.direction = direction
        self.lives = length

    @property
    def dots(self):
        shipdots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.direction == 0:
                cur_x += i
            elif self.direction == 1:
                cur_y += i

            shipdots.append(Dot(cur_x, cur_y))
        return shipdots

    def shoot(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hide = False, size = 6):
        self.size = size
        self.hide = hide

        self.count = 0

        self.field = [[' '] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f'\n{i + 1} | ' + ' | '.join(row) + ' |'

        if self.hide:
            res = res.replace('■', ' ')
        return res

    def out(self, d):
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb = False):
        near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = '•'
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise MissShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = '■'
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
            raise OutException()

        if d in self.busy:
            raise UsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print('Потопил!')
                    return False
                else:
                    print('Ранил!')
                    return True

        self.field[d.x][d.y] = 'x'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except MyException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход соперника: {d.x + 1} {d.y + 1}')
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input('Ваш ход: ').split()

            if len(cords) != 2:
                print('Введите 2 цифры координат!')
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print('Введите числа!')

            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hide = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def gen_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for i in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except MissShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.gen_board()
        return board

    def loop(self):
        num = 0
        while True:
            print('-' * 20)
            print('Доска игрока:')
            print(self.us.board)
            print('-' * 20)
            print('Доска противника:')
            print(self.ai.board)
            if num % 2 == 0:
                print('-' * 20)
                print('Ходит игрок:')
                repeat = self.us.move()
            else:
                print('-' * 20)
                print('Ходит противник:')
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.count == 7:
                print('-' * 20)
                print('Игрок выиграл!')
                break
            if self.us.board.count == 7:
                print('-' * 20)
                print('Противник выиграл!')
                break
            num += 1

    def start(self):
        self.loop()


g = Game()
g.start()
