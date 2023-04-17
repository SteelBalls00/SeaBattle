# Я дико извиняюсь, что приложил код из разбора задания, но свой написать никак не могу.
# Если следовать алгоритму решения, то ничего другого в голову не приходит.
# По итогу я старался код переписать по памяти, подглядывал порой конечно, потом еще 2 дня ошибки исправлял.
# Резюмируя. Мне пока не хватает знаний для написания своего решения, как наберусь знаний я, восполню этот пробел.

from random import randint

class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'({self.x}, {self.y})'


class Ship: # класс корабля, bow это нос корабля который будет передаваться переменной класса Dot
    def __init__(self, bow: int, l: int, o: int): # остальные переменные это длина корабля, направление и жизни
        self.bow = bow
        self.l = l
        self.o = o
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            current_x = self.bow.x
            current_y = self.bow.y

            if self.o == 0:
                current_x += i

            if self.o == 1:
                current_y += i

            ship_dots.append(Dot(current_x, current_y))

        return ship_dots

    def shooten(self, shot): # возвращает выстрел по точке корабля
        return shot in self.dots()

    # def __repr__(self): # показать все точки корабля
    #     return f'Ship dots: {self.dots()}'

class Board(): # класс доски с параметром скываемости и размера поля
    def __init__(self, hid = False, size = 6):
        self.hid = hid
        self.size = size
        self.count = 0 # количество кораблей
        self.ships = [] # список всех кораблей
        self.busy = [] # список занятых точек
        self.field = [['O'] * size for _ in range(size)]

    def add_ship(self, ship): # добавляем корабль

        for d in ship.dots:
            if self.out(d) or d in self.busy: # проверка на выход за пределы доски и на занятость точки
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb = False): # расставляем контур вокруг корабля
        near = [
            (-1, 1), (0, 1), (1, 1),
            (-1, 0), (0, 0), (1, 0),
            (-1, -1), (0, -1), (1, -1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                current_dot = Dot(d.x + dx, d.y + dy) # если точки вокруг корабля не нарушают правил, то ставим точку
                if not (self.out(current_dot)) and current_dot not in  self.busy:
                    if verb:
                        self.field[current_dot.x][current_dot.y] = '.'
                    self.busy.append(current_dot)

    def __str__(self): # печать доски
        res = ''
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field): # офигенное применение функции enumerate
            res += f'\n{i + 1} | ' + " | ".join(row) + ' |'
        if self.hid: res = res.replace("■", "O")
        return res

    def out(self, d): # функция проверки точки на выход за пределы и занятость
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d): # функция выстрела, передаем точку
        if self.out(d): raise BoardOutException
        if d in self.busy: raise BoardUsedException
        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = 'X'
                if ship.lives == 0:
                    print('Корабль уничтожен!!!')
                    self.count += 1 # счетчик кораблей, по которому проверяется условие для победы
                    self.contour(ship, verb = True)
                    return True # дать все же еще раз пальнуть, если корабль уничтожен
                else:
                    print('Попадание, корабль подбит!')
                    return True
        self.field[d.x][d.y] = '.'
        print('Мимо!')
        return False

    def begin(self): # очистить доску при неудачной попытке расстановки
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
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self): # переопределяем ask для противника
        d = Dot(randint(0, 5), randint(0, 5))
        print(f'Ход компьютера {d.x + 1}{d.y + 1}')
        return d

class User(Player):
    def ask(self): # переопределяем ask для игрока
        while True:
            cords = input('Введите номер строки и столбца:').split()
            if len(cords) != 2:
                print('Введено не 2 координаты!')
                continue
            x, y = cords
            if not (x.isdigit() or y.isdigit()):
                print('Вводить нужно только цифры!')
                continue
            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True # параметр скрывающий вражеский корабли

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self): # расстановка доски в случае неудачной попытки
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self): # попытка установки кораблей
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self): # приветствие.
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        # all_boards = [[self.us.board],[self.ai.board]]
        # print(all_boards) думал так просто реализовать печать 2х досок рядом
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()