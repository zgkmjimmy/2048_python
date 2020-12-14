#curses 用来在终端上显示图形界面
import curses

#random模块用来生成随机数
from random import randrange, choice

#collections提供了一个字典的子类defaultdict。可以指定key值不存在时，value的默认值
from collections import defaultdict

actions=['Up','Left','Down','Right','Restart','Exit']
#ord()函数以一个字符作为参数，返回参数对应的ASCII数值，便于和后面捕捉的键位关联
letter_codes = [ord(ch) for ch in 'WASDRQwasdrq']

actions_dict = dict(zip(letter_codes, actions * 2))
#actions_dict的输出结果为
#{87: 'Up', 65: 'Left', 83: 'Down', 68: 'Right', 82: 'Restart', 81: 'Exit', 119: 'Up', 97: 'Left', 115: 'Down', 100: 'Right', 114: 'Restart', 113: 'Exit'}


#矩阵转置
def transpose(field):
    return [list(row) for row in zip(*field)]

#矩阵逆转
def invert(field):
    return [row[::-1] for row in field]



#用户输入处理
def get_user_action(keyboard):
    char = "N"
    while char not in actions_dict:
        #按下返回键位的ASCII码值
        char = keyboard.getch()
    #返回输入键位对应的行为
    return actions_dict[char]

#创建棋盘
class GameField(object):
    def __init__(self, height=4, width=4, win=2048):
        self.height = height  #高
        self.width = width  #宽
        self.win_value = win  #过关分数
        self.score = 0  #当前分数
        self.highscore = 0  #最高分
        self.reset()  #棋盘重置

    #重置棋盘
    def reset(self):
        #更新分数
        if self.score > self.highscore:
            self.highscore = self.score
        self.score = 0
        #初始化游戏开始界面
        self.field = [[0 for i in range(self.width)] for j in range(self.height)]
        self.spawn()
        self.spawn()

    #棋盘走一步
    def move(self, direction):
        #一行向左合并
        def move_row_left(row):
            def tighten(row):
                #'''把零散的非零单元挤到一块'''
                #先将非零的元素全拿出来加入到新列表
                new_row = [i for i in row if i != 0]
                #按照原列表的大小，给新列表后面补零
                new_row += [0 for i in range(len(row) - len(new_row))]
                return new_row

            def merge(row):
                #'''对邻近元素进行合并'''
                pair = False
                new_row = []
                for i in range(len(row)):
                    if pair:
                        #合并后，加入乘2后的元素在0元素的后面
                        new_row.append(2 * row[i])
                        #更新分数
                        self.score+=2*row[i]
                        pair = False
                    else:
                        #判断邻近元素能否合并
                        if i + 1 < len(row) and row[i] == row[i + 1]:
                            pair = True
                            #可以合并时，新列表加入元素0
                            new_row.append(0)
                        else:
                            #不能合并，新列表中加入该元素
                            new_row.append(row[i])
                #断言合并后不会改变行大小，否则报错
                assert len(new_row) == len(row)
                return new_row
            #先挤到一块再合并再挤到一块
            return tighten(merge(tighten(row)))

        #创建moves字典，把不同的棋盘操作作为不同的key，对应不同的方法函数
        moves = {}
        moves['Left'] = lambda field: [move_row_left(row) for row in field]
        moves['Right'] = lambda field: invert(moves['Left'](invert(field)))
        moves['Up'] = lambda field: transpose(moves['Left'](transpose(field)))
        moves['Down'] = lambda field: transpose(moves['Right'](transpose(field)))
        #判断棋盘操作是否存在且可行
        if direction in moves:
            if self.move_is_possible(direction):
                self.field = moves[direction](self.field)
                self.spawn()
                return True
            else:
                return False

    #判断输赢
    def is_win(self):
        #任意一个位置的数大于设定的win值时，游戏胜利
        return any(any(i>=self.win_value for i in row) for row in self.field)

    def is_gameover(self):
        #无法移动和合并时，游戏失败
        return not any(self.move_is_possible(move) for move in actions)

    def draw(self, screen):
        help_string1 = '(W)Up (S)Down (A)Left (D)Right'
        help_string2 = '    (R)Restart (Q)Exit'
        gameover_string = '       GAME OVER'
        win_string = '        YOU WIN!'
        
        #绘制函数
        def cast(string):
            #addstr()方法将传入的内容展示到终端
            screen.addstr(string + '\n')
            
        #绘制水平分割线的函数
        def draw_hor_separator():
            line = '+' + ('+-----' * self.width + '+')[1:]
            separator=defaultdict(lambda: line)
            if not hasattr(draw_hor_separator,"counter"):
                draw_hor_separator.counter=0
            cast(separator[draw_hor_separator.counter])
            draw_hor_separator.counter+=1

        #绘制竖直分割线的函数
        def draw_row(row):
            cast(''.join('|{: ^5}'.format(num) if num > 0 else '|     ' for num in row) + '|')
        
        #清空屏幕
        screen.clear()
        #绘制分数和最高分
        cast('SCORE:' + str(self.score))
        if 0 != self.highscore:
            cast('HIGHSCORE:' + str(self.highscore))
            
        #绘制行列边框分割线
        for row in self.field:
            draw_hor_separator()
            draw_row(row)
        draw_hor_separator()

        #绘制提示文字
        if self.is_win():
            cast(win_string)
        else:
            if self.is_gameover():
                cast(gameover_string)
            else:
                cast(help_string1)
        cast(help_string2)

    #随机生成一个2或者4
    def spawn(self):
        #从100中取一个随机数，如果这个随机数大于89，new_element等于4，否则等于2
        new_element = 4 if randrange(100) > 89 else 2
        #得到一个随机空白位置的元组坐标
        (i, j) = choice([(i, j) for i in range(self.width) for j in range(self.height) if self.field[i][j] == 0])
        self.field[i][j] = new_element
    
    #判断能否移动
    def move_is_possible(self, direction):
        '''传入要移动的方向
        判断能否向这个方向移动
        '''
        def row_is_left_movable(row):
            '''判断一行里面能否有元素进行左移动或合并
            '''
            def change(i):
                #当左边有空位（0）,右边有数字时，可以向左移动
                if row[i] == 0 and row[i + 1] != 0:
                    return True
                #当左边有一个数和右边的数相等时，可以向左合并
                if row[i] != 0 and row[i + 1] == row[i]:
                    return True
                return False
            return any(change(i) for i in range(len(row) - 1))
            
        #检查能否移动（合并也可以看作是在移动）
        check = {}
        #判断矩阵每一行有没有可以左移的元素
        check['Left'] = lambda field: any(row_is_left_movable(row) for row in field)
        #判断矩阵每一行有没有可以右移的元素。这里只用进行判断，所以矩阵变换之后，不用再变换复原
        check['Right'] = lambda field: check['Left'](invert(field))
        check['Up'] = lambda field: check['Left'](transpose(field))
        check['Down'] = lambda field: check['Right'](transpose(field))
        
        #如果direction是“左右上下”即字典check中存在的操作，那就执行它对应的函数
        if direction in check:
            #传入矩阵，执行对应函数
            return check[direction](self.field)
        else:
            return False


#状态机
def main(stdscr):
    def init():
        '''初始化游戏棋盘'''
        #重置游戏棋盘
        game_field.reset()
        return 'Game'

    def not_game(state):
        '''展示游戏结束界面。
        读取用户输入得到action，判断是重启游戏还是结束游戏
        '''
        #根据状态画出游戏的界面
        game_field.draw(stdscr)
        #读取用户输入得到action,判断是重启游戏还是结束游戏
        action=get_user_action(stdscr)
        #defaultdict参数是callable类型，所以需要传一个函数
        #如果没有'Restart'和'Exit'的action,将一直保持现有状态
        responses = defaultdict(lambda: state)
        #在字典中新建两个键值对
        responses['Restart'], responses['Exit'] = 'Init', 'Exit'
        return responses[action]
    def game():
        #画出当前棋盘状态
        #根据状态画出游戏的界面
        game_field.draw(stdscr)
        #读取用户输入得到action
        action = get_user_action(stdscr)
        if action == 'Restart':
            return 'Init'
        if action == 'Exit':
            return 'Exit'
        #if成功移动了一步
        if game_field.move(action):
            if game_field.is_win():
                return 'Win'
            if game_field.is_gameover():
                return 'Gameover'
        return 'Game'
    
    state_actions = {
        'Init': init,
        'Win': lambda: not_game('Win'),
        'Gameover': lambda: not_game('Gameover'),
        'Game':game
    }

    #使用颜色配置默认值
    curses.use_default_colors()

    #实例化游戏界面对象并设置游戏获胜条件为2048
    game_field=GameField(win=2048)

    state = 'Init'
    
    #状态机开始循环
    while state != 'Exit':
        state = state_actions[state]()

curses.wrapper(main)







