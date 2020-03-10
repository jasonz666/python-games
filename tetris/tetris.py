#!/usr/bin/env python
# encoding:utf-8
# file: practice17.py
# date: 2020-03-08
# author: Jason

# ##########################
# 终端俄罗斯方块Tetris
# ##########################

import time

# #################
# 全局变量定义
# #################

# 游戏区域长度高度 1个方块2个英文字符 实际长度要x2
GAME_AREA_L, GAME_AREA_H = 20, 24
# 游戏区域左上角起始点坐标 假设此点为坐标原点 X为横坐标 Y为纵坐标
GAME_AREA_X, GAME_AREA_Y = 2, 2
# 游戏边框图形 方块渲染图形
GAME_EDGE, GAME_SQUARE = '##', 'xx'
# 游戏区域背景色
GAME_BACKGROUND = '\033[40;30m'

# 7方块初始状态位图 全部定义4x4
# 2,2位置存储方块实际长度高度 3,3位置存储颜色序列
BLOCK_DICT = {
    # 天蓝色
    'I': [[1, 1, 1, 1],
          [0, 0, 0, 0],
          [0, 0, [4, 1], 0],
          [0, 0, 0, '\033[46;36m']],
    # 蓝色
    'J': [[1, 0, 0, 0],
          [1, 1, 1, 0],
          # [3,2]表示此方块长=3高=2 索引正好相反 x=2为两行y=3为三列
          # 即 3,2为游戏区域的坐标表示法的长度与高度 2,3为二维列表的索引表示法的列表长度
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

# 游戏区域 即地图位图
GAME_BITMAP = [[0 for y in range(GAME_AREA_H)] for x in range(GAME_AREA_L)]

# 单方块临时存储位图
BLOCK_BITMAP = [[0, 0, [0, 0], 0] if i == 2 else [0, 0, 0, 0] for i in range(4)]

# #################
# 函数定义
# #################

# TODO 俄罗斯方块未完成。。。。。。。。。。
# TODO 函数测试
# tetris_init       OK
# goto_blockxy      OK
# clear_blockline   OK
# clear_area        OK
# edge_block        OK
# draw_edge         OK
# pick_block        OK
# print_block       OK
# draw_background   OK
# restore_cursor    OK
# rotate_block      OK
# move_block        ...

# TODO 未完成函数。。。。
# get_keypress
#


# 初始化与通用函数
# 包括坐标定位 绘制地图边框 填充地图背景色等函数

def goto_blockxy(x=1, y=1):
    """
    将终端光标移动到方块的起始位置
    :param x: 方块的坐标x
    :param y: 方块的坐标y
    :return: None
    """
    # 1个方块占2个英文字符宽度
    # 实际坐标_x与方块坐标x的转换
    _x = (x - 1) * 2 + 1
    print('\033[{};{}H'.format(y, _x), end='', sep='')


def edge_block(x=1, y=1, ln=1, h=1, b=GAME_EDGE):
    """
    绘制边框方块
    :param x: 起点x
    :param y: 起点y
    :param ln: 边框方块长
    :param h: 边框方块高
    :param b: 边框方块字符
    """
    for _y in range(y, y + h):
        goto_blockxy(x, _y)
        print('{}'.format(b * ln))


def draw_edge(x=1, y=1, ln=GAME_AREA_L, h=GAME_AREA_H):
    """
    绘制游戏边框
    """
    edge_block(x, y, ln + 2, 1)
    edge_block(x, y + 1, 1, h)
    edge_block(x + ln + 1, y + 1, 1, h)
    edge_block(x, y + h + 1, ln + 2, 1)


def clear_blockline(lenght=1, block=GAME_SQUARE, bkg=GAME_BACKGROUND):
    """
    填充指定长度方块为背景色 即清除方块
    :param lenght: 方块长度 每个方块占2英文字符宽度
    :param block: 填充的方块
    :param bkg: 填充的背景色
    :return: None
    """
    # 因为标准输出缓冲区的原因 不要传参end='' 否则打印内容可能不会立刻显示
    print('{}{}\033[0m'.format(bkg, block * lenght))


def clear_area(x=GAME_AREA_X, y=GAME_AREA_Y, ln=GAME_AREA_L, h=GAME_AREA_H):
    """
    清除指定矩形区域 清除的最小单位是方块 即2个英文字符
    假定游戏区域为黑色背景
    :param x: 起始x坐标
    :param y: 起始y坐标
    :param ln: 区域长度
    :param h: 区域高度
    :return: None
    """
    for _y in range(y, y + h):
        goto_blockxy(x, _y)
        clear_blockline(ln)


def draw_background():
    """
    游戏区域背景色填充
    """
    clear_area()


def restore_cursor():
    """清屏并恢复隐藏的光标
    """
    print('\033[2J\033[?25h')


def tetris_init():
    """
    初始化工作
    """
    # 清屏与隐藏光标
    print('\033[2J\033[?25l')
    # 绘制游戏区域边框
    draw_edge()
    # 地图填充背景色
    draw_background()


# 方块处理函数
# 包括选取方块 打印方块 方块旋转 方块平移等函数

def pick_block(b_type, b_dict=BLOCK_DICT, b_bitmap=BLOCK_BITMAP):
    """
    选取特定类型的方块
    :param b_type: 方块类型
    :param b_dict: 7方块存储位图
    :param b_bitmap: 单方块存储位图 4x4二维列表
    :return: 单方块存储位图
    """
    for x in range(4):
        for y in range(4):
            b_bitmap[x][y] = b_dict[b_type][x][y]
    return b_bitmap


def print_block(x, y, b_bitmap=BLOCK_BITMAP):
    """
    打印一种方块
    :param x: 起始点x
    :param y: 起始点y
    :param b_bitmap: 已生成好的方块位图 是二维列表
    :return: None
    """
    b_l, b_h = BLOCK_BITMAP[-2][-2][0], BLOCK_BITMAP[-2][-2][1]
    # 这里的_x,_y为索引表示法 参数x,y为坐标表示法
    for _y in range(b_l):
        for _x in range(b_h):
            # 必须判断是否等于1 不要用True/False判断
            # b_bitmap坐标互换 让位图中所有1呈现的图像与实际打印的图像一致
            # 即b_bitmap中纵向扫描 print也纵向打印
            if b_bitmap[_x][_y] == 1:
                # 方块位图坐标转换游戏区域坐标 索引到坐标表示法需互换坐标
                goto_blockxy(_y + x, _x + y)
                # 打印行数超过终端窗口高度 可能会提前折行导致方块错乱
                print('{}{}\033[0m'.format(BLOCK_BITMAP[-1][-1], GAME_SQUARE))


def rotate_block(b_bitmap=BLOCK_BITMAP):
    """
    逆时针旋转方块 求NxM到MxN的转置矩阵
    :param b_bitmap: 方块存储位图 二位列表
    :return: 旋转后的方块位图
    """
    b_length, b_height = b_bitmap[-2][-2][0], b_bitmap[-2][-2][1]
    # b_lengthXb_height 方块索引表示法即 b_heightXb_length
    b_target = [[0 for _y in range(b_height)] for _x in range(b_length)]
    for _y in range(b_length):
        for _x in range(b_height):
            # 逆时针旋转90度
            offset = len(b_bitmap[_x]) - b_length
            b_target[_y][_x] = b_bitmap[_x][-_y - 1 - offset]
    # 生成旋转后方块
    for _x in range(4):
        for _y in range(4):
            if _x < b_length and _y < b_height:
                b_bitmap[_x][_y] = b_target[_x][_y]
            elif _x == _y and _x == 2:
                b_bitmap[_x][_y] = b_bitmap[_x][_y][::-1]
            elif _x == _y and _x == 3:
                continue
            else:
                b_bitmap[_x][_y] = 0
    return b_bitmap


def move_block(to_x, to_y, b_bitmap=BLOCK_BITMAP):
    pass


# 后台计算
# 负责计算图形的消除 计分等
# 图形
# 交互函数
# 负责处理键盘输入
if __name__ == '__main__':
    tetris_init()
    time.sleep(1)

    x, y = GAME_AREA_X, GAME_AREA_Y
    for i in 'IJLOTZS':
        x = GAME_AREA_X
        pick_block(i)
        for j in range(5):
            print_block(x, y)
            x += BLOCK_BITMAP[-2][-2][0] + 1
            rotate_block()
        y += BLOCK_BITMAP[-2][-2][1] + 2
        time.sleep(0.1)

    print('\n')
    print('DONEEEEEEEEEE')
    time.sleep(2)
    # restore_cursor()
