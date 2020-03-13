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
import sys
import select
import copy
import termios


# #################
# 全局变量定义
# #################


# 地图相关变量

# 下面的方块指7种基本方块 小方块指构成基本方块的最小单位
# 终端使用等宽字体时 小方块正好是个小正方形 1个小方块由2个英文字符组成
# 游戏区域即游戏地图的长与高
GAME_AREA_L, GAME_AREA_H = 16, 24
# 游戏区域内左上角坐标为坐标原点 X为横坐标 Y为纵坐标
GAME_AREA_X, GAME_AREA_Y = 2, 2
# 游戏边框图形 基本方块的小方块渲染图形 清除小方块图形
GAME_EDGE, GAME_SQUARE, GAME_CLEAR = '##', 'xx', '  '
# 游戏区域背景色
GAME_BKGCOLOR = '\033[40;30m'
# 游戏区域位图 即游戏地图
GAME_BITMAP = [[[0, GAME_BKGCOLOR] for y in range(GAME_AREA_L)] for x in range(GAME_AREA_H)]

# 方块相关变量

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
# 方块临时存储位图
BLOCK_BITMAP = [[0, 0, [0, 0], 0] if i == 2 else [0, 0, 0, 0] for i in range(4)]
# 定义方块出生点的方块左上角的地图坐标
BLOCK_SX, BLOCK_SY = GAME_AREA_X + GAME_AREA_L // 2 - 2, GAME_AREA_Y
# 方块左上角地图坐标
BLOCK_COORD = {'x': BLOCK_SX, 'y': BLOCK_SY}
# 生成方块计数 得分 方块类型
BLOCK_COUNT, GAME_SCORE, BLOCK_TYPE = 0, 0, '_'

# 按键和信息相关变量

# 按键变量 按键检测间隔 方块打印间隔
KEY_DEFAULT, KEY_PAUSE = '_', ' '
KEY, KEY_INTERVAL, PNT_INTERVAL = KEY_DEFAULT, 0.01, 0.2
# 计分板左上角坐标
INFO_AREA_X, INFO_AREA_Y = GAME_AREA_X + GAME_AREA_L + 2, GAME_AREA_Y + 1
# 计分板区域长与高
INFO_AREA_L, INFO_AREA_H = 8, GAME_AREA_H


# #################
# 函数定义
# #################


# 初始化与通用函数
# 包括坐标定位 绘制地图边框 填充地图背景色等函数


def exit_clear(txt, e_code=0):
    """
    退出时做一些清理工作
    :param txt: 文本
    :param e_code: 退出码
    :return:
    """
    print(txt)
    exit(e_code)


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


def _gotoxy_print(x=1, y=1, *args, **kwargs):
    """打印调试信息"""
    goto_blockxy(x, y)
    print(*args, **kwargs)


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


def draw_edge(x=1, y=1):
    """
    绘制游戏边框
    """
    ln1 = GAME_AREA_L + INFO_AREA_L + 3
    ln2 = GAME_AREA_L + 1
    ln3 = GAME_AREA_L + INFO_AREA_L + 2
    h = GAME_AREA_H
    _edge_block(x, y, ln1, 1)
    _edge_block(x, y + 1, 1, h)
    _edge_block(x + ln2, y + 1, 1, h)
    _edge_block(x + ln3, y + 1, 1, h)
    _edge_block(x, y + h + 1, ln1, 1)


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


def _print_map_bits():
    """
    打印地图点 用于调试
    :return: None
    """
    a, b = GAME_AREA_X + GAME_AREA_L + INFO_AREA_L + 3, GAME_AREA_Y
    for x in range(len(GAME_BITMAP)):
        goto_blockxy(a, b)
        for y in range(len(GAME_BITMAP[0])):
            if GAME_BITMAP[x][y][0] == 1:
                print('\033[31m{}\033[0m,'.format(GAME_BITMAP[x][y][0]), end='')
            else:
                print('{},'.format(GAME_BITMAP[x][y][0]), end='')
        b += 1


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


def _copy_block(rotated_block, origin_block):
    """
    方块拷贝函数
    :param rotated_block: 旋转后的方块位图
    :param origin_block: 原始方块位图 必须是4x4方块
    :return: None
    """
    b_length, b_height = origin_block[-2][-2][0], origin_block[-2][-2][1]
    for _x in range(4):
        for _y in range(4):
            if _x < b_length and _y < b_height:
                # 原始方块长x高 => 位图[高][长] => 旋转后方块的 位图[长][高]
                # 所以这里_x是b_length _y是b_height
                origin_block[_x][_y] = rotated_block[_x][_y]
            elif _x == _y and _x == 2:
                # 长x高变换
                origin_block[_x][_y] = origin_block[_x][_y][::-1]
            elif _x == _y and _x == 3:
                # 颜色值不改变
                continue
            else:
                origin_block[_x][_y] = 0


def _rotate_block(flag=True):
    """
    逆时针旋转方块 即求NxM到MxN的转置矩阵
    :param flag: True生成旋转后的方块 False只旋转不生成旋转后方块
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
    # flag为真 生成旋转后方块
    if flag:
        _copy_block(b_target, BLOCK_BITMAP)
    # 生成临时旋转后方块用于检测
    else:
        # 拷贝未旋转的方块为模板
        tmp_bitmap = copy.deepcopy(BLOCK_BITMAP)
        # 生成为临时方块
        _copy_block(b_target, tmp_bitmap)
        return tmp_bitmap


def _edge_detect(x, y, b_bitmap):
    """
    方块是否超出游戏地图检测
    :param x: 方块左上角坐标x
    :param y: 方块左上角坐标y
    :param b_bitmap: 方块位图
    :return: 布尔型
    """
    b_l, b_h = b_bitmap[-2][-2][0], b_bitmap[-2][-2][1]
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
                # 清除地图点
                _clear_map_area(_x, _y, 1, 1)


def move_block(x, y, direction, distance=1):
    """
    移动方块或旋转方块
    :param x: 当前位置x
    :param y: 当前位置y
    :param direction: 移动方向 'to_l'向左 'to_r'向右 'to_d'向下 'to_u'原地旋转
    :param distance: 移动距离
    :return: 布尔型
    """
    global KEY
    respawn_flag = False
    b_l, b_h = BLOCK_BITMAP[-2][-2][0], BLOCK_BITMAP[-2][-2][1]
    if direction == 'to_l' and _edge_detect(x - distance, y, BLOCK_BITMAP) and \
            _collision_detect(x - distance, y, 'to_l'):
        _clear_block(x, y, b_l, b_h)
        print_block(x - distance, y)
        BLOCK_COORD['x'], BLOCK_COORD['y'] = x - distance, y
    elif direction == 'to_r' and _edge_detect(x + distance, y, BLOCK_BITMAP) and \
            _collision_detect(x + distance, y, 'to_r'):
        _clear_block(x, y, b_l, b_h)
        print_block(x + distance, y)
        BLOCK_COORD['x'], BLOCK_COORD['y'] = x + distance, y
    elif direction == 'to_d' and _edge_detect(x, y + distance, BLOCK_BITMAP) and \
            _collision_detect(x, y + distance, 'to_d'):
        _clear_block(x, y, b_l, b_h)
        print_block(x, y + distance)
        BLOCK_COORD['x'], BLOCK_COORD['y'] = x, y + distance
    elif direction == 'to_d' and (not _edge_detect(x, y + distance, BLOCK_BITMAP)
                                  or not _collision_detect(x, y + distance, 'to_d')):
        respawn_flag = True
    elif direction == 'to_u' and _edge_detect(x, y, _rotate_block(False)) and \
            _collision_detect_r(x, y, _rotate_block(False)):
        _clear_block(x, y, b_l, b_h)
        _rotate_block()
        print_block(x, y)
    # 恢复向下移动 区别于get_keys获取的's'
    KEY = KEY_DEFAULT
    return respawn_flag


def spawn_newblock(t=None):
    """新方块生成
    """
    global BLOCK_COUNT, BLOCK_TYPE
    # 方块挑选
    b_type = 'IJLOSTZ'
    if t is None:
        BLOCK_TYPE = random.choice(b_type)
    else:
        BLOCK_TYPE = t
    _pick_block(BLOCK_TYPE)
    # 新方块出生点初始化
    BLOCK_COORD['x'], BLOCK_COORD['y'] = BLOCK_SX, BLOCK_SY
    BLOCK_COUNT += 1


# 按键处理函数
# 包括获取按键 按键转换方向等


def get_keys(delay=None):
    """
    按键获取函数 p键退出 不支持方向键
    :param delay: 传递额外延迟
    :return: None
    """
    global KEY
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    new = termios.tcgetattr(fd)
    # 关闭回显和回车
    new[3] = new[3] & ~termios.ECHO & ~termios.ICANON
    # 在一个方块打印间隔时间内检测times次按键输入
    # get_keys函数充当sleep函数等待PNT_INTERVAL秒的过程中获取按键
    count, times = 0, PNT_INTERVAL // KEY_INTERVAL
    try:
        termios.tcsetattr(fd, termios.TCSADRAIN, new)
        while count < times:
            if delay is not None:
                time.sleep(delay)
            time.sleep(KEY_INTERVAL)
            # support non-blocking input
            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                KEY = sys.stdin.read(1)
                if KEY in 'wad':  # 2倍加速移动或旋转
                    times //= 2
                if KEY == 's':  # 4倍加速下降
                    times //= 4
                # 暂停
                if KEY == KEY_PAUSE:
                    break
            count += 1
    except KeyboardInterrupt:
        exit_clear('Get: Ctrl-C to EXIT', 1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def get_direction():
    """
    按键转换为方向 'to_l'向左 'to_r'向右 'to_d'向下 'to_u'原地旋转
    :return: 方向
    """
    if KEY == 'a':
        return 'to_l'
    elif KEY == 'd':
        return 'to_r'
    elif KEY == 's':
        return 'to_d'
    elif KEY == 'w':
        return 'to_u'
    elif KEY == KEY_DEFAULT:
        return 'to_d'


# 碰撞检测与计分函数
# 包括方块向下运动碰撞检测 地图中方块的消除 消除后计分等


def _collision_detect(x, y, direction):
    """
    方块与方块之间碰撞检测
    :param x: 方块左上角坐标x
    :param y: 方块左上角坐标y
    :param direction: 移动方向 'to_l'向左 'to_r'向右 'to_d'向下
    :return: 布尔型
    """
    b_l, b_h = BLOCK_BITMAP[-2][-2][0], BLOCK_BITMAP[-2][-2][1]
    distance = 1000000
    if direction == 'to_l':
        for _y in range(y, y + b_h):
            block_y = _y - y
            map_y = _y - GAME_AREA_Y
            for block_x in range(b_l):  # 0->b_l-1
                if BLOCK_BITMAP[block_y][block_x] == 1:
                    sx = x - GAME_AREA_X + block_x
                    for map_x in range(sx, -1, -1):
                        if GAME_BITMAP[map_y][map_x][0] == 1:
                            if abs(sx - map_x) < distance:
                                distance = abs(sx - map_x)
                                break
                    break
    elif direction == 'to_r':
        for _y in range(y, y + b_h):
            block_y = _y - y
            map_y = _y - GAME_AREA_Y
            for block_x in range(b_l - 1, -1, -1):
                if BLOCK_BITMAP[block_y][block_x] == 1:
                    sx = x - GAME_AREA_X + block_x
                    for map_x in range(sx, len(GAME_BITMAP[0])):
                        if GAME_BITMAP[map_y][map_x][0] == 1:
                            if abs(map_x - sx) < distance:
                                distance = abs(map_x - sx)
                                break
                    break
    elif direction == 'to_d':
        for _x in range(x, x + b_l):
            block_x = _x - x
            map_x = _x - GAME_AREA_X
            for block_y in range(b_h - 1, -1, -1):
                # 从左往右从下往上 寻找方块上第一个值为1的点 纵坐标为block_y
                if BLOCK_BITMAP[block_y][block_x] == 1:
                    # 从block_y映射到地图对应的点的下一个点 此点为方块下次将到达的点 纵坐标起点为sy
                    # 传递y的实参为y + distance 已包含移动方向distance
                    sy = y - GAME_AREA_Y + block_y
                    # 从sy开始竖直向下到地图纵坐标最大值len(GAME_BITMAP) 查找值为1的地图点
                    for map_y in range(sy, len(GAME_BITMAP)):
                        if GAME_BITMAP[map_y][map_x][0] == 1:
                            # 计算地图点map_y到方块下次将到达的点sy之间距离
                            if abs(map_y - sy) < distance:
                                distance = abs(map_y - sy)
                                break
                    # 只需要查找一次地图上的点
                    break
    # 距离为0 则为假 表示点有重叠 不能移动
    return distance


def _collision_detect_r(x, y, b_bitmap):
    """
    旋转后碰撞检测
    :param x: 方块左上角坐标x
    :param y: 方块左上角坐标y
    :param b_bitmap: 临时方块位图
    :return: 布尔型
    """
    # 迭代临时方块与对应地图上的点
    for _x in range(4):
        for _y in range(4):
            # 原始方块和旋转后方块有重叠
            if b_bitmap[_x][_y] == 1 and BLOCK_BITMAP[_x][_y] == 1:
                # 排除重叠的点
                b_bitmap[_x][_y] = 0
            # 旋转后方块与地图是否有重叠点
            map_x, map_y = y - GAME_AREA_Y + _x, x - GAME_AREA_X + _y
            if b_bitmap[_x][_y] == 1 and GAME_BITMAP[map_x][map_y][0] == 1:
                return False
    return True


def print_info():
    x, y = INFO_AREA_X, INFO_AREA_Y
    str_len = INFO_AREA_L - GAME_AREA_X + 1
    goto_blockxy(x, y)
    # '按键：'占3个小方块宽度 2个英文字符占一个小方块宽度
    print('按键：{:<{}}'.format(str(KEY), (str_len - 3) * 2))
    goto_blockxy(x, y + 2)
    print('方块数：{:<{}}'.format(str(BLOCK_COUNT), (str_len - 4) * 2))
    goto_blockxy(x, y + 4)
    print('方块：{:<{}}'.format(str(BLOCK_TYPE), (str_len - 3) * 2))
    goto_blockxy(x, y + 6)
    print('得分：{:<{}}'.format(str(GAME_SCORE), (str_len - 3) * 2))
    goto_blockxy(x, y + 9)
    print('按 {}'.format('空格' if KEY_PAUSE == ' ' else KEY_PAUSE))
    goto_blockxy(x, y + 10)
    print('暂停/开始')


def eliminate_blocks():
    # TODO 消除函数 未完成
    # TODO 计分功能 未完成
    pass


if __name__ == '__main__':
    tetris_init()
    while True:
        # 生成新方块
        spawn_newblock()
        print_block(BLOCK_COORD['x'], BLOCK_COORD['y'])
        down_move_count = 0
        while True:
            get_keys()
            # 暂停
            if KEY == KEY_PAUSE:
                KEY = KEY_DEFAULT
                while KEY != ' ':
                    try:
                        get_keys(0.2)
                    except KeyboardInterrupt:
                        exit_clear('Get: Ctrl-C to EXIT', 1)
            # 打印信息
            print_info()
            reborn_flag = move_block(BLOCK_COORD['x'], BLOCK_COORD['y'], get_direction())
            if down_move_count == 0 and reborn_flag:
                restore_cursor()
                exit_clear('Gam Over!!!', 0)
            if reborn_flag:
                break
            # _print_map_bits()
            down_move_count += 1
