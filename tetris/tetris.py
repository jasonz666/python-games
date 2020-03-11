#!/usr/bin/env python
# encoding:utf-8
# file: tetris.py
# date: 2020-03-08
# author: Jason


# ##########################
# 终端俄罗斯方块Tetris
# ##########################


import time
import random


# #################
# 全局变量定义
# #################


# 下面的方块指7种基本方块 小方块指构成基本方块的最小单位
# 终端使用等宽字体时 小方块正好是个小正方形 1个小方块由2个英文字符组成
# 游戏区域即游戏地图的长与高
GAME_AREA_L, GAME_AREA_H = 20, 24
# 游戏区域内左上角坐标为坐标原点 X为横坐标 Y为纵坐标
GAME_AREA_X, GAME_AREA_Y = 2, 2
# 游戏边框图形 基本方块的小方块渲染图形 清除小方块图形
GAME_EDGE, GAME_SQUARE, GAME_CLEAR = '##', 'xx', '  '
# 游戏区域背景色
GAME_BKGCOLOR = '\033[40;30m'
# 清除方块的长与度
CLEAR_BLOCK_L, CLEAR_BLOCK_H = 4, 4
# 7方块初始状态位图 2,2位置为方块实际长与高 3,3位置为此方块颜色
BLOCK_DICT = {
    # 天蓝色
    'I': [[1, 1, 1, 1],
          [0, 0, 0, 0],
          [0, 0, [4, 1], 0],
          [0, 0, 0, '\033[46;36m']],
    # 蓝色
    'J': [[1, 0, 0, 0],
          [1, 1, 1, 0],
          # [3,2]表示此方块长3高2 索引正好相反 x=2为两行y=3为三列
          # 3,2为游戏区域的坐标表示法的长与度 2,3为对应的二维列表索引表示法
          [0, 0, [3, 2], 0],
          [0, 0, 0, '\033[44;34m']],
    # 白色
    'L': [[0, 0, 1, 0],
          [1, 1, 1, 0],
          [0, 0, [3, 2], 0],
          [0, 0, 0, '\033[47;37m']],
    # 黄色
    'O': [[1, 1, 0, 0],
          [1, 1, 0, 0],
          [0, 0, [2, 2], 0],
          [0, 0, 0, '\033[43;33m']],
    # 绿色
    'S': [[0, 1, 1, 0],
          [1, 1, 0, 0],
          [0, 0, [3, 2], 0],
          [0, 0, 0, '\033[42;32m']],
    # 紫色
    'T': [[0, 1, 0, 0],
          [1, 1, 1, 0],
          [0, 0, [3, 2], 0],
          [0, 0, 0, '\033[45;35m']],
    # 红色
    'Z': [[1, 1, 0, 0],
          [0, 1, 1, 0],
          [0, 0, [3, 2], 0],
          [0, 0, 0, '\033[41;31m']]
}
# 游戏区域位图
GAME_BITMAP = [[[0, GAME_BKGCOLOR] for y in range(GAME_AREA_L)] for x in range(GAME_AREA_H)]
# 方块临时存储位图
BLOCK_BITMAP = [[0, 0, [0, 0], 0] if i == 2 else [0, 0, 0, 0] for i in range(4)]
# 定义方块出生点的方块左上角的地图坐标
BLOCK_SX, BLOCK_SY = GAME_AREA_X + GAME_AREA_L // 2 - 2, GAME_AREA_Y
# 方块左上角地图坐标
BLOCK_COORD = {'x': BLOCK_SX, 'y': BLOCK_SY}


# #################
# 函数定义
# #################


# 初始化与通用函数
# 包括坐标定位 绘制地图边框 填充地图背景色等函数


def goto_blockxy(x=1, y=1):
    """
    将终端光标移动到方块的左上角位置 即坐标定位函数
    :param x: 方块的坐标x
    :param y: 方块的坐标y
    :return: None
    """
    if x < 1 or y < 1:
        x, y = 1, 1
    # 1个小方块占2个英文字符宽度
    # 实际坐标_x与方块坐标x的转换
    _x = (x - 1) * 2 + 1
    print('\033[{};{}H'.format(y, _x), end='', sep='')


def _edge_block(x=1, y=1, ln=1, h=1, b=GAME_EDGE):
    """
    绘制边框小方块
    :param x: 起点x
    :param y: 起点y
    :param ln: 边框小方块长
    :param h: 边框小方块高
    :param b: 边框小方块字符
    :return: None
    """
    for _y in range(y, y + h):
        goto_blockxy(x, _y)
        print('{}'.format(b * ln))


def draw_edge(x=1, y=1, ln=GAME_AREA_L, h=GAME_AREA_H):
    """
    绘制游戏边框
    """
    _edge_block(x, y, ln + 2, 1)
    _edge_block(x, y + 1, 1, h)
    _edge_block(x + ln + 1, y + 1, 1, h)
    _edge_block(x, y + h + 1, ln + 2, 1)


# 地图处理函数
# 包括地图中方块清除 地图中方块显示等


def _clear_map_area(x, y, ln, h):
    """
    清除地图位图
    :param x: 坐标表示法的x
    :param y: 坐标表示法的y
    :param ln: 清除区域长度
    :param h: 清除区域高度
    :return: None
    """
    map_x, map_y = x - GAME_AREA_X, y - GAME_AREA_Y
    for _x in range(map_x, map_x + ln):
        for _y in range(map_y, map_y + h):
            # 坐标表示法与索引表示法互换
            GAME_BITMAP[_y][_x] = [0, GAME_BKGCOLOR]


def _fill_map_point(x, y, color):
    """
    填充地图位图点
    :param x: 坐标x
    :param y: 坐标y
    :param color: 颜色字符串转义序列
    """
    map_x, map_y = x - GAME_AREA_X, y - GAME_AREA_Y
    GAME_BITMAP[map_y][map_x] = [1, color]


def _clear_blockline(lenght=1, block=GAME_CLEAR, bkg=GAME_BKGCOLOR):
    """
    填充指定长度方块为背景色 即清除方块
    :param lenght: 方块长度 每个小方块占2英文字符宽度
    :param block: 填充的小方块
    :param bkg: 填充的背景色
    :return: None
    """
    # 因为标准输出缓冲区的原因 不要传参end='' 否则打印内容可能不会立刻显示
    print('{}{}\033[0m'.format(bkg, block * lenght))


def clear_area(x=GAME_AREA_X, y=GAME_AREA_Y, ln=GAME_AREA_L, h=GAME_AREA_H):
    """
    清除指定矩形区域 清除的最小单位是小方块 即2个英文字符
    假定游戏区域为黑色背景
    :param x: 起始x坐标
    :param y: 起始y坐标
    :param ln: 区域长度
    :param h: 区域高度
    :return: None
    """
    for _y in range(y, y + h):
        goto_blockxy(x, _y)
        _clear_blockline(ln)
    _clear_map_area(x, y, ln, h)


def print_map_area(x, y, ln=GAME_AREA_L, h=GAME_AREA_H):
    """
    根据地图位图打印内容
    :param x: 地图起点坐标x
    :param y: 地图起点坐标y
    :param ln: 区域长
    :param h: 区域高
    :return: None
    """
    map_x, map_y = x - GAME_AREA_X, y - GAME_AREA_Y
    for _x in range(map_y, map_y + h):
        for _y in range(map_x, map_x + ln):
            if GAME_BITMAP[_x][_y][0] == 1:
                goto_blockxy(_y + GAME_AREA_Y, _x + GAME_AREA_X)
                print('{}{}\033[0m'.format(GAME_BITMAP[_x][_y][1], GAME_SQUARE))


def draw_background():
    """游戏区域背景色填充
    """
    clear_area()


def restore_cursor():
    """恢复隐藏的光标
    """
    print('\033[?25h')


def tetris_init():
    """初始化工作
    """
    # 清屏与隐藏光标
    print('\033[2J\033[?25l')
    # 绘制游戏区域边框
    draw_edge()
    # 地图填充背景色
    draw_background()


# 方块处理函数
# 包括选取方块 打印方块 方块旋转 方块平移等函数


def _pick_block(b_type):
    """
    选取特定类型的方块
    :param b_type: 方块类型
    :return: None
    """
    for x in range(4):
        for y in range(4):
            BLOCK_BITMAP[x][y] = BLOCK_DICT[b_type][x][y]


def print_block(x, y):
    """
    打印一种方块
    :param x: 起始点x
    :param y: 起始点y
    :return: None
    """
    b_l, b_h = BLOCK_BITMAP[-2][-2][0], BLOCK_BITMAP[-2][-2][1]
    b_color = BLOCK_BITMAP[-1][-1]
    # 这里的_x,_y为索引表示法 参数x,y为坐标表示法
    for _y in range(b_l):
        for _x in range(b_h):
            # 必须判断是否等于1 不要用True/False判断
            # b_bitmap坐标互换 让位图中所有1呈现的图像与实际打印的图像一致
            # 即b_bitmap中纵向扫描 print也纵向打印
            if BLOCK_BITMAP[_x][_y] == 1:
                # 方块位图坐标转换游戏区域坐标 索引到坐标表示法需互换坐标
                goto_blockxy(_y + x, _x + y)
                _fill_map_point(_y + x, _x + y, b_color)
                # 打印行数超过终端窗口高度 可能会提前折行导致方块错乱
                print('{}{}\033[0m'.format(b_color, GAME_SQUARE))


def rotate_block():
    """
    逆时针旋转方块 即求NxM到MxN的转置矩阵
    :return: None
    """
    b_length, b_height = BLOCK_BITMAP[-2][-2][0], BLOCK_BITMAP[-2][-2][1]
    # b_lengthXb_height 方块索引表示法即 b_heightXb_length
    b_target = [[0 for _y in range(b_height)] for _x in range(b_length)]
    for _y in range(b_length):
        for _x in range(b_height):
            # 逆时针旋转90度
            offset = len(BLOCK_BITMAP[_x]) - b_length
            b_target[_y][_x] = BLOCK_BITMAP[_x][-_y - 1 - offset]
    # 生成旋转后方块
    for _x in range(4):
        for _y in range(4):
            if _x < b_length and _y < b_height:
                BLOCK_BITMAP[_x][_y] = b_target[_x][_y]
            elif _x == _y and _x == 2:
                BLOCK_BITMAP[_x][_y] = BLOCK_BITMAP[_x][_y][::-1]
            elif _x == _y and _x == 3:
                continue
            else:
                BLOCK_BITMAP[_x][_y] = 0


def _edge_detect(x, y):
    """
    方块是否超出游戏地图检测
    :param x: 方块左上角坐标x
    :param y: 方块左上角坐标y
    :return: 布尔型
    """
    b_l, b_h = BLOCK_BITMAP[-2][-2][0], BLOCK_BITMAP[-2][-2][1]
    if x < GAME_AREA_X or y < GAME_AREA_Y or \
            x + b_l - 1 >= GAME_AREA_X + GAME_AREA_L or \
            y + b_h - 1 >= GAME_AREA_Y + GAME_AREA_H:
        return False
    else:
        return True


def _clear_block(x, y, ln, h):
    """
    清除指定方块
    :param x: 起始x坐标
    :param y: 起始y坐标
    :param ln: 区域长度
    :param h: 区域高度
    :return: None
    """
    for _x in range(x, x + ln):
        for _y in range(y, y + h):
            if BLOCK_BITMAP[_y - y][_x - x] == 1:
                goto_blockxy(_x, _y)
                # 因为标准输出缓冲区的原因 不要传参end='' 否则打印内容可能不会立刻显示
                print('{}{}\033[0m'.format(GAME_BKGCOLOR, GAME_CLEAR))


def move_block(x, y, direction, distance=1):
    """
    移动方块
    :param x: 当前位置x
    :param y: 当前位置y
    :param direction: 移动方向 'l'向左 'r'向右 'd'向下
    :param distance: 移动距离
    :return: None
    """
    b_l, b_h = BLOCK_BITMAP[-2][-2][0], BLOCK_BITMAP[-2][-2][1]
    if direction == 'l' and _edge_detect(x - distance, y):
        _clear_block(x, y, b_l, b_h)
        print_block(x - distance, y)
        BLOCK_COORD['x'], BLOCK_COORD['y'] = x - distance, y
    elif direction == 'r' and _edge_detect(x + distance, y):
        _clear_block(x, y, b_l, b_h)
        print_block(x + distance, y)
        BLOCK_COORD['x'], BLOCK_COORD['y'] = x + distance, y
    elif direction == 'd' and _edge_detect(x, y + distance):
        _clear_block(x, y, b_l, b_h)
        print_block(x, y + distance)
        BLOCK_COORD['x'], BLOCK_COORD['y'] = x, y + distance


def spawn_newblock():
    """新方块生成
    """
    # 方块挑选
    b_type = 'IJLOSTZ'
    _pick_block(random.choice(b_type))
    # 新方块出生点初始化
    BLOCK_COORD['x'], BLOCK_COORD['y'] = BLOCK_SX, BLOCK_SY


# 后台计算
# 负责计算图形的消除 计分等
# 图形
# 交互函数
# 负责处理键盘输入
if __name__ == '__main__':
    tetris_init()

    for i in 'IJLOTZSX':
        spawn_newblock()
        print_block(BLOCK_COORD['x'], BLOCK_COORD['y'])
        time.sleep(0.1)
        for j in range(24):
            move_block(BLOCK_COORD['x'], BLOCK_COORD['y'], 'd')
            time.sleep(0.09)

    time.sleep(1)
    print('\n')
    print('DONEEEEEEEEEE')
    restore_cursor()
