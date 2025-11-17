import time
from tkinter import *
from tkinter import font, ttk, SEL_FIRST, SEL_LAST
from math import log
import re
import random
from decimal import *

import json
import datetime
import pyperclip
import keyboard
import ctypes
import pyautogui
from maths import *
from info import *

user32 = ctypes.WinDLL("user32", use_last_error=True)

calculator_greeting = 'нажми [?] или ctrl+[/], чтобы узнать как использовать калькулятор'
i_last_example = i_history = 'future'
has_left_main_win_flag = True


def clean_pattern_empty_scopes(example_to_clean):
    while re.search(pattern_checking_on_empty_scopes, example_to_clean):
        # if re.search(rf'{pattern_checking_on_empty_scopes}', )
        example_to_clean = re.sub(pattern_checking_on_empty_scopes, '', example_to_clean)
    return example_to_clean


def get_text_length(text, entry):
    font_obj = font.Font(font=entry.cget("font"))
    return font_obj.measure(text)


def setting_y(coord):
    settings['y'] = coord
    try:
        change_width_of_entry(entry_box.get(), entry_box, result)
    except NameError:
        pass


def change_width_of_entry(text, entry1, entry2):
    entry_text_length = get_text_length(text, entry1)
    if main_win.focus_get() in (main_win, entry_box, result):
        entry1.place(x=1, y=1, width=entry_text_length + 4, height=HEIGHT - (2, 1)[settings['y'] == MAX_COORD])
        entry2.place(x=entry_text_length + 2, y=1, width=(WIDTH - 2) - (entry_text_length + 1), height=HEIGHT - (2, 1)[settings['y'] == MAX_COORD])
    else:
        entry1.place(x=1, y=0, width=entry_text_length + 4, height=HEIGHT)
        entry2.place(x=entry_text_length + 2, y=0, width=(WIDTH - 2) - (entry_text_length + 1), height=HEIGHT)
    
    
def change_size_of_everything(scale, scale_was_zero=False, change_result=True):
    global max_character_amount, place_coords, last_time_main_win_geometry_change, val_before_last_main_win_geometry_change
    global WIDTH, HEIGHT, X_COORD, MAX_COORD
    max_character_amount = (174, 174, 152, 120, 99, 71)[scale]
    
    HEIGHT = screen_width // (201, 81, 71, 61, 51, 41)[scale]
    X_COORD = screen_width // 12

    WIDTH = screen_width - 2 * X_COORD
    MAX_COORD = screen_height - get_taskbar_height() - HEIGHT
    if abs(settings['y'] - recents['mid']) <= HEIGHT and (settings['scale'] != scale or scale_was_zero):
        setting_y(MAX_COORD // 2)
    if abs(settings['y'] - recents['low']) <= HEIGHT and (settings['scale'] != scale or scale_was_zero):
        setting_y(MAX_COORD)

    recents['low'], recents['mid'], recents['top'] = MAX_COORD, MAX_COORD // 2, 0
    place_coords = (recents['low'], recents['mid'], recents['top'])
    
    entry_box.config(font=('Arial', HEIGHT // 2))
    result.config(font=('Arial', HEIGHT // 2))
    change_width_of_entry(entry_box.get(), entry_box, result)
    main_win.geometry(f'{WIDTH}x{HEIGHT}+{X_COORD}+{settings['y']}')
    
    if change_result:
        if not re.search(calc_geometry_state_change_expression, result.get()):
            val_before_last_main_win_geometry_change = result.get()
        result.delete(0, END)
        result.insert(END, f'{' ' * bool(example_value)}Максимум {max_character_amount} символ{get_correct_ending(max_character_amount, word_ends2)}')
        last_time_main_win_geometry_change = time.time()
    if scale:
        settings['scale'] = scale


history_of_calculations, recents, settings = None, None, None
def rewrite_json(file):
    with open(f'{FILES}/{file}.json', 'w') as json_file:
        json.dump({'history': history_of_calculations, 'settings': settings, 'recents': recents}[file], json_file)
            
            
def create_greeting():
    global calculator_greeting
    with open(f'{FILES}/greetings.json', 'r', encoding='utf-8') as greetings_file:
        calculator_greeting = random.choice(json.load(greetings_file))
        

MAX_COORD = screen_height - get_taskbar_height() - screen_width // 61
with open(f'{FILES}/history.json', 'r') as history_file:
    try:
        history_of_calculations = json.load(history_file)
    except json.decoder.JSONDecodeError:
        history_of_calculations = 'Пример\nРезультат вычислений\nПервое использование программы: ' + str(datetime.datetime.today())[:-7].replace('-', '.')
        rewrite_json('history')
with open(f'{FILES}/recents.json', 'r') as recents_file:
    try:
        recents = json.load(recents_file)
    except json.decoder.JSONDecodeError:
        recents = {'closing time': [0 for _ in range(3)], 'example before closing': '', 'cursor before closing': 0, 'cursor before moving calc': 0,
                   'recent examples': [['', '', '', ''] for _ in range(20)], 'last examples': [['', '', '', '', '', ''],],
                   'low': MAX_COORD, 'mid': MAX_COORD // 2, 'top': 0, 'mouse coords': {'x': 0, 'y': 0}, 'win theme alike calc': True, 'rounding info longer': 3}
        rewrite_json('recents')
with open(f'{FILES}/settings.json', 'r') as settings_file:
    try:
        settings = json.load(settings_file)
    except json.decoder.JSONDecodeError:
        settings = {'y': MAX_COORD, 'history length': 4000, 'theme': ('dark', 'light')[not is_dark_theme()], 'scale': 3, 'round': 'по умолчанию'}
        rewrite_json('settings')
if recents['rounding info longer'] == 0:
    recents['rounding info longer'] = (time.time() - recents['closing time'][-1] > 14 * DAY) * 3
if time.time() - recents['closing time'][-3] < 14 * DAY:
    create_greeting()
    
ROUND_ANSWER_TO_MANUALLY = settings['round']


getcontext().prec = 1402
# Временная штука для программы работы без ошибки
max_character_amount = (174, 174, 152, 120, 99, 71)[settings['scale']]

HEIGHT = screen_width // (201, 81, 71, 61, 51, 41)[settings['scale']]
X_COORD = screen_width // 24

WIDTH = screen_width - 2 * X_COORD
MAX_COORD = screen_height - get_taskbar_height() - HEIGHT

if recents['low'] != MAX_COORD:
    if abs(settings['y'] - recents['mid']) <= HEIGHT * 4:
        setting_y(MAX_COORD // 2)
    elif settings['y'] - recents['mid'] > HEIGHT * 4:
        setting_y(MAX_COORD)
    else:
        setting_y(0)
    setting_y(min(MAX_COORD, settings['y']))

recents['low'], recents['mid'], recents['top'] = MAX_COORD, MAX_COORD // 2, 0
place_coords = (recents['low'], recents['mid'], recents['top'])


def is_num(symbols, num_symbs=list('0123456789.-Ee+')):
    return all((i in num_symbs for i in symbols))


def change_scopes_to_modules():
    global example_value
    example_value = delete_in_example(example_value, 1)
    example_value = delete_in_example(example_value, -1)
    example_value = insert_in_example(example_value, '|')
    example_value = insert_in_example(example_value, '|', right=True)
    
    
def find_the_most_useful_symbol_to_paste(example, last_is_digit, first=True):
    often_meeting_parts = []
    for i in range(len(example) - 2):
        if (example[i] in '0123456789πφe.' and last_is_digit or example[i] not in '0123456789πφe.' and (not last_is_digit)):
            continue
        for j in range(i + 2, len(example) + 1):
            if example.count(example[i:j]) < 2 or example[j - 1] in '0123456789πφe.' or not re.search(r'[0-9πφe]', example[i:j]):
                continue
            often_meeting_parts.append(example[i:j])
    for i in range(len(often_meeting_parts)):
        for j in range(len(often_meeting_parts)):
            if often_meeting_parts[i] in often_meeting_parts[j] and i != j and example.replace(often_meeting_parts[j], '').count(often_meeting_parts[i]) < 2:
                often_meeting_parts[i] = ''
    often_meeting_parts = sorted(often_meeting_parts, key=lambda x: len(x), reverse=True)
    if often_meeting_parts:
        return often_meeting_parts[0 if len(often_meeting_parts) < 2 or first else 1]
    else:
        number_expression = r'-?(?:[0-9]+(?:\.[0-9]+)?|[πφe])'
        example_numbers = list(re.finditer(fr'{number_expression}|\({number_expression}\)|\|{number_expression}\|', example))
        if len(example_numbers) > 1:
            the_often_meeting_part = example[example_numbers[0].end():example_numbers[-1].start()]
            for right_index in range(len(the_often_meeting_part)):
                part_of_the_often_meeting_part = the_often_meeting_part[:right_index]
                if part_of_the_often_meeting_part.count('(') < part_of_the_often_meeting_part.count(')'):
                    the_often_meeting_part = '#' * right_index + the_often_meeting_part[right_index:]
            the_often_meeting_part = the_often_meeting_part.replace('#', '')
            if the_often_meeting_part[:1] not in '0123456789πφe.' and not last_is_digit:
                the_often_meeting_part = the_often_meeting_part[list(re.finditer(r'[0-9πφe.]', the_often_meeting_part))[0].start():]
            if re.search(r'[0-9πφe]', the_often_meeting_part):
                return the_often_meeting_part
            else:
                return ''
        else:
            return ''
        

def create_perfect_example(non_perfect_example):    
    non_perfect_example = rescope_example(non_perfect_example)
    
    if not non_perfect_example:
        return
    non_perfect_example = non_perfect_example.replace(' ', '')
    non_perfect_example = non_perfect_example.replace('by', ')by').replace('log', 'log(')
    non_perfect_example = f'({non_perfect_example})'.replace('-)', ')')[1:-1]
    non_perfect_example = re.sub(r'(?:[\+\-•/^,\.]|mod|div)(?=\))', r'', f'({non_perfect_example})')
    
    for i in range(len(non_perfect_example) - 2):
        if non_perfect_example[i + 1] == '|':
            non_perfect_example = non_perfect_example[:i + 1] + 'Uu'[non_perfect_example[i] in '0123456789!)uπφe' or bool(re.match(r'[+•:^!\)]|mod|div', non_perfect_example[i + 2:]))] + non_perfect_example[i + 2:]
    
    non_perfect_example = clean_pattern_empty_scopes(non_perfect_example)
           
    non_perfect_example = f'({non_perfect_example})'
    
    split_non_perfect_example = []
    for no_brack, brack in zip(re.split(r'[()Uu]', non_perfect_example), re.findall(r'[()Uu]', non_perfect_example)):
        split_non_perfect_example.append(no_brack)
        split_non_perfect_example.append(brack)
    split_non_perfect_example = ['R'] + [i for i in split_non_perfect_example if i] + ['R']
    
    while '(' in split_non_perfect_example or 'U' in split_non_perfect_example:
        for i in range(1, len(split_non_perfect_example) - 3):
            if split_non_perfect_example[i] + split_non_perfect_example[i + 2] not in ('()', 'Uu'):
                continue
            try:
                while split_non_perfect_example[i - 1] + split_non_perfect_example[i + 3] in ('()', 'Uu'):
                    brack1, brack2 = 'Uu' if 'U' in split_non_perfect_example[i - 1:i + 1] else '()'
                    split_non_perfect_example[i - 1:i + 4] = [brack1] + [split_non_perfect_example[i + 1]] + [brack2]
                    split_non_perfect_example = ['R'] + split_non_perfect_example + ['R']
                split_non_perfect_example[i:i + 3] = [split_non_perfect_example[i] + split_non_perfect_example[i + 1] + split_non_perfect_example[i + 2]]
                split_non_perfect_example = ['R'] + split_non_perfect_example + ['R']
            except IndexError:
                pass
            try:
                while split_non_perfect_example[i + 2] not in '()UuR':
                    split_non_perfect_example[i + 1:i + 3] = [split_non_perfect_example[i + 1] + split_non_perfect_example[i + 2]]
                    split_non_perfect_example = split_non_perfect_example + ['R']
            except IndexError:
                pass
            try:
                while split_non_perfect_example[i] not in '()UuR':
                    split_non_perfect_example[i:i + 2] = [split_non_perfect_example[i] + split_non_perfect_example[i + 1]]
                    split_non_perfect_example = ['R'] + split_non_perfect_example
            except IndexError:
                pass
            break
        
    non_perfect_example = ''.join([i for i in split_non_perfect_example if i != 'R'])
    if re.fullmatch(r'\((?:-(?:[φπe]|[0-9]+(?:\.[0-9]+)?))\)', non_perfect_example):
        non_perfect_example = re.sub(r'\((-(?:[φπe]|[0-9]+(?:\.[0-9]+)?))\)', r'\1', non_perfect_example)
    non_perfect_example = re.sub(r'\(([φπe]|[0-9]+(?:\.[0-9]+)?)\)', r'\1', non_perfect_example)
    
    non_perfect_example = re.sub(r'(sin|cos|tg|ctg|ln|lg|by)(\d+(?:\.\d+)?|\.\d+|e)', r'\1(\2)', non_perfect_example)
    non_perfect_example = re.sub(r'(ln|lg)([φπe])', r'\1(\2)', non_perfect_example)
    non_perfect_example = re.sub(r'(mod|div)([φπe])', r'\1(\2)', non_perfect_example)
    non_perfect_example = re.sub(r'([φπe])(mod|div)', r'(\1)\2', non_perfect_example)
    non_perfect_example = re.sub(r'log([φπe]|\d+(?:\.\d+)?|\.\d+)by', r'log(\1)by', non_perfect_example)
    non_perfect_example = re.sub(r'(sin|cos|tg|ctg|ln|lg|log|by)\((\d{1,4}|\d\.\d{1,3}|\d{2}\.\d{1,2}|\d{3}\.\d)\)', r'\1\2', non_perfect_example)
    
    non_perfect_example = non_perfect_example.replace('U', '|').replace('u', '|').strip('R')
    if non_perfect_example[:1] == '(' and non_perfect_example[-1:] == ')':
        non_perfect_example = non_perfect_example[1:-1]
    
    non_perfect_example = re.sub(r'(?<![a-z])\(((?:sin|cos|tg|ctg|ln|lg|by)(?:\|.*?\||\(.*?\)))\)', r'\1', non_perfect_example)
    non_perfect_example = re.sub(r'(?<![a-z])\((log(?:\|.*?\||\(.*?\))by(?:\|.*?\||\(.*?\)))\)', r'\1', non_perfect_example)
    
    return non_perfect_example


def rescope_example(unscoped_example):
    unscoped_example = clear_q_with_content(unscoped_example, cursor_index)
    brackets = ''.join([i for i in unscoped_example if i in '()Uu'])
    
    scope_counter = 0
    while unscoped_example[:1] == '(' and unscoped_example[-1:] == ')':
        brackets = brackets[1:-1]
        unscoped_example = unscoped_example[1:-1]
        scope_counter += 1
        
    while '()' in brackets or 'Uu' in brackets:
        brackets = brackets.replace('()', '').replace('Uu', '')
    basic_for_start_brackets = ''.join(re.findall(r'[)u]+', brackets))
    basic_for_end_brackets = ''.join(re.findall(r'[U(]+', brackets))
    unscoped_example = basic_for_start_brackets[::-1].replace(')', '(').replace('u', 'U') + unscoped_example + basic_for_end_brackets[::-1].replace('(', ')').replace('U', 'u')
    check_example_scoping = unscoped_example
    
    while '()' in check_example_scoping or 'Uu' in check_example_scoping:
        check_example_scoping = check_example_scoping.replace('()', '').replace('Uu', '')
        
    if not check_example_scoping:
        return
    
    scopes_of_example = ''.join(re.findall(r'[()Uu]', unscoped_example))
    while '()' in scopes_of_example or 'Uu' in scopes_of_example:
        scopes_of_example = scopes_of_example.replace('()', '').replace('Uu', '')
    if scopes_of_example:
        return
    
    return '(' * scope_counter + unscoped_example + ')' * scope_counter
            

def modify_info(example):
    a = '– '
    when_rad_when_deg = '(в радианах, если угол иррациональный, иначе в градусах)'
    if not example:
        return calculator_greeting
    if example == calculator_greeting.lower():
        a += 'приветствие'
    if example in ('ထ', '+ထ', '-ထ'):
        a += {'ထ': 'Бесконечность', '+ထ': 'положительная Бесконечность', '-ထ': 'отрицательная Бесконечность'}[example]
    if example in ('log()by()', 'ln()', 'lg()'):
        a += {'log()by()': 'log(число)by(основание)', 'ln()': 'логарифм по основанию e=2,718…', 'lg()': 'логарифм по основанию 10'}[example]
    if example in ('!', '||'):
        a += {'!': 'факториал (n!=1·2·…·n)', '||': 'модуль (делает значения неотрицательными)', '()': 'скобки'}[example]
    if example in ('√', '3√', '4√'):
        a += {'√': 'квадратный корень', '3√': 'кубический корень', '4√': 'биквадратный корень', }[example]
    if example[:-2] in ('√', '3√', '4√') and example[-2:] == '()':
        a += {'√': 'квадратный корень', '3√': 'кубический корень', '4√': 'биквадратный корень', }[example[:-2]]
    if example in ('mod', 'div'):
        a += {'mod': 'остаток от деления', 'div': 'целочисленное деление'}[example]
    if example in ('sin()', 'cos()', 'tg()', 'ctg()'):
        a += {'sin()': f'синус{when_rad_when_deg}', 'cos()': f'косинус{when_rad_when_deg}', 'tg()': f'тангенс{when_rad_when_deg}', 'ctg()': f'котангенс{when_rad_when_deg}'}[example]
    if example in ('^2', '^3', '^4'):
        a += {'^2': 'квадрат', '^3': 'куб', '^4': 'гиперкуб'}[example]
    if example in ('10^100', '10^303', '10^3003', '10^10^100'):
        a += {'10^100': 'гугол', '10^303': 'центиллион', '10^3003': 'миллиллион', '10^10^100': 'гуголплекс'}[example]
    if re.fullmatch(r'1(?: 000){2,8}', example):
        z3 = ' 000'
        a += {f'1{2 * z3}': '10^6, миллион', f'1{3 * z3}': '10^9, миллиард', f'1{4 * z3}': '10^12, триллион', f'1{5 * z3}': '10^15, квадриллион',
              f'1{6 * z3}': '10^18, квинтиллион', f'1{7 * z3}': '10^21, секстиллион', f'1{8 * z3}': '10^24, септиллион'}[example]
    return a if a != '– ' else None


def q_solve_example(example):
    return solve_example(clear_q_with_content(example, cursor_index))
    

def solve_example(example=None):
    global perfect_example, ROUND_ANSWER_TO_MANUALLY, last_time_round_change
    perfect_example = ''
    example = (entry_box.get() if example is None else example).lower()
    modified_info = modify_info(example)
    
    if modified_info is not None:
        return modified_info
    cursor_or_selected_end_index = max(indexes_of_selection.values()) if indexes_of_selection else cursor_index
    if example.count('q') == 1 and cursor_or_selected_end_index >= example.index('q') + 1:
        last_time_round_change = time.time()
        bind_left_button()
        mn, mx = min_rounding, max_rounding
        if cursor_or_selected_end_index == example.index('q') + 1:
            ROUND_ANSWER_TO_MANUALLY = settings['round'] = 'по умолчанию'
            return f'{q_solve_example(example)} [округление по умолчанию (можешь дописать число округления: от {mn} знаков (перед запятой) до {mx} знаков (после запятой))]'
        rounding_num = re.fullmatch(r'-?\d+', example[example.index('q') + 1:cursor_or_selected_end_index])
        if not rounding_num:
            return 'Неверная запись округления! Между q и кареткой должно быть целое число'
        rounding_num = int(rounding_num[0])
        if rounding_num > mx or rounding_num < mn:
            return f'{q_solve_example(example)} [Необходимо задать количество знаков после запятой не более {mx}, но и не менее {mn}!]'
        ROUND_ANSWER_TO_MANUALLY = settings['round'] = rounding_num
        manual_round_abs = abs(ROUND_ANSWER_TO_MANUALLY)
        num_of_ending_symbols = (0 < manual_round_abs % 10 < 5 and manual_round_abs // 10 != 1) + (manual_round_abs % 10 == 1 and manual_round_abs != 11)
        return f'{q_solve_example(example)} [{manual_round_abs} знак{('ов', 'а', '')[num_of_ending_symbols]} {('перед', 'после')[ROUND_ANSWER_TO_MANUALLY > 0]} запятой]'
    
    for i in range(2):
        for j in range(-3, 0):
            if example[j:] in ending_symbols:
                example = example[:j]
                break
            
    for j in range(-3, 0):
        if example[j:] in ending_symbols:
            return 'Ошибка в конце примера!'
        
    if ' ' in example and len(set(example)) == 1:
        return 'Зачем тебе пробелы?'
    elif ')(' in example:
        return 'Сочетание символов ")(" может быть неправильно растолковано. Возможно, ты имеешь ввиду ")•("?'
    elif example == 'h':
        return f'Задай размер памяти истории (от {min_history_length} до {max_history_length})'
    elif example[:1] == 'h' and example[-1:] == '#':
        if not example[1:-1].isdigit():
            return 'Ошибка! Длина истории вычислений должна быть числом!'
        num = int(example[1:-1])
        if min_history_length <= num <= max_history_length:
            settings['history length'] = 4 * num
            return f'С следующего открытия калькулятора: длина истории вычислений — {num} примеров.'
        return f'Необходимо задать количество примеров в истории не более {max_history_length}, но и не менее {min_history_length}!'
    elif re.fullmatch(r'-?[^#]*#', example.replace(' ', '')):
        unit_of_distance = False
        if example.replace(' ', '') == '-#':
            example = '-0#'
            unit_of_distance = True
        if re.fullmatch(r'-?1-#', example.replace(' ', '')):
            y_coord = (-1, 1)[example.replace(' ', '') == '1-#'] * MAX_COORD
            unit_of_distance = True
        else:
            if not re.fullmatch(r'-?(?:[0-9]+(?:\.[0-9]+)?)#', example):
                example = solve_example(example[:-1]).replace(' ', '') + '#'
            if not re.fullmatch(r'-?(?:[0-9]+(?:\.[0-9]+)?)#', example):
                return 'Координата должна быть числом!'
            y_coord = float(example[:-1])
            if -1 < y_coord < 1:
                y_coord *= MAX_COORD
                unit_of_distance = True
            y_coord = int(str(Decimal(y_coord).quantize(Decimal('.0'), ROUND_HALF_UP))[:-2])
        if abs(y_coord) > MAX_COORD:
            return f'Либо сделай координату в диапазоне от -{MAX_COORD} до {MAX_COORD}, либо нажми на "Ctrl+Shift" и стрелку "Вверх" или "Вниз" на клавиатуре!'
        setting_y(y_coord + (0, MAX_COORD)[example[0] == '-'])
        main_win.geometry(f'{WIDTH}x{HEIGHT}+{X_COORD}+{settings['y']}')
        return 'место калькулятора в ' + ('пикселях', 'расстояниях от края калькулятора вверху до его края внизу')[unit_of_distance]
    if '$' in example:
        return 'Почему символ "$" есть в примере?'
    pi_replaced, e_replaced, fi_replaced = f'({C.pi}+0)', f'({C.e}+0)', f'({C.fi}+0)'

    pre_example = f'({example})'
    for i in range(len(pre_example) - 2):
        if pre_example[i + 1] == '|':
            pre_example = pre_example[:i + 1] + 'Uu'[pre_example[i] in '0123456789!)ueπφ' or bool(re.match(r'[+•:^!\)]|mod|div', pre_example[i + 2:]))] + pre_example[i + 2:]
            
    example = pre_example[1:-1]
    example = clean_pattern_empty_scopes(example)
    example = re.sub(r'[Uu]', '|', example)
    if re.search(r'[eπφ][eπφ(]|[eπφ)][eπφ]', example):
        return 'Рядом с константой не может быть ни скобки, ни константы!'
    example = example.replace('π', pi_replaced).replace('φ', fi_replaced).replace('e', e_replaced)
    example = example.replace('.', ',').replace(' ', '').replace('/', ':')
    example = example.replace('√', '$').replace('k', '$').replace('r', '$')
    example = example.replace('by', ')by').replace('log', 'log(')
    example = f'({example})'.replace('-)', ')')[1:-1]
    example = re.sub(r'(?:(?<=mod|div|sin|cos|ctg|log)|(?<=[+\-•/^(])|(?<=ln|lg|by)),', r'0,', example)
    example = re.sub(r'(?:[\+\-•:^,]|mod|div)(?=\))', r'', f'({example})')
    
    for i in range(len(example) - 2):
        if example[i + 1] == '|':
            example = example[:i + 1] + 'Uu'[example[i] in '0123456789!)ueπφ' or bool(re.match(r'[+•:^!\)]|mod|div', example[i + 2:]))] + example[i + 2:]
    those_symbols_cannot_be_near = re.findall(r'(?:(?:[+\-•:^,]|mod|div)(?:[+•:^,]|mod|div)|,-)', example)
    if those_symbols_cannot_be_near:
        those_symbols_cannot_be_near[0] = those_symbols_cannot_be_near[0].replace(',', '.').replace(':', '/')
        return f'Сочетание "{those_symbols_cannot_be_near[0]}" в примере недопустимо!'
    pre_example_brackets = ''.join([i for i in example if i in '()Uu'])
    example_brackets = ''.join([i for i in example.replace('log', '<').replace('by', '>') if i in '()Uu<>'])
    e_replaced, pi_replaced, fi_replaced = [i.replace('(', '\\(').replace(')', '\\)').replace('.', ',').replace('+', '\\+') for i in (e_replaced, pi_replaced, fi_replaced)]
    consts_expression = fr'(?:{e_replaced}|{pi_replaced}|{fi_replaced})'
    if re.search(fr'{consts_expression}U|u{consts_expression}', example):
        return 'Рядом с константой не может быть модуля!'
    while example_brackets[:1] == '(' and example_brackets[-1:] == ')':
        example_brackets = example_brackets[1:-1]
    while any([i in example_brackets for i in ('()', 'Uu', '<>')]):
        example_brackets = example_brackets.replace('()', '').replace('Uu', '').replace('<>', '')
    if re.fullmatch(r'(?:U|u|\(|\))+', example):
        return '0'
    if re.search(r'\(\)', example):
        return f'В примере есть скобки без чисел внутри'
    if re.search(r'Uu', example):
        return 'В примере есть модули без чисел внутри'
    if not re.fullmatch(r'[\)u]*[U\(]*', example_brackets):
        return 'Что-то не так со скобками, модулем или логарифмом!'

    example = rescope_example(example)
    if not example:
        return 'Что-то не так со скобками, модулем или логарифмом!'
    while '$' in example:
        for i in range(len(example) - 1):
            if example[i + 1] == '$':
                example = f'{example[:i + 1]}{('2', '')[example[i] in '0123456789,)u!']}k{example[i + 2:]}'
    if example and example[1] in '+•' and example[2:3] != '-':
        example = example[:1] + example[2:]
    example = example.replace('+-', '-').replace('--', '+').replace('•-', '•(0-1)•').replace(':-', ':(0-1):')
    saved_example = example
    example = example.replace('sin', '1+1-').replace('cos', '1+1-').replace('ctg', '1+1-').replace('tg', '1+1-')
    example = example.replace('lg', '1+1-').replace('ln', '1+1-').replace('by', '+')
    example = example.replace('k', '+1-').replace('log', '1+1-').replace('2.718281828459045', '1+1')
    example = example.replace('^-', '+').replace('+-', '-').replace('--', '+')
    if re.search(r'(?:sin|cos|tg|ctg|k)(?:[+•:^,)!u]|mod|div)', saved_example):
        return 'В примере после одной из функций стоит не тот символ, либо отстутствует что-либо!'
    for i in (list('+•:^,)-0!u') + ['mod', 'div']):
        for j in ('lg', 'ln', 'log'):
            if j + '-' in saved_example:
                return 'Число, находящееся после функции, со знаком минус берётся в скобки!'
            if ((j + i) in saved_example) and ((j + '0,') not in saved_example):
                return 'В примере после одной из функций ошибка!'
    if re.search(r'[0-9,\.](?:sin|cos|tg|ctg|lg|ln|log)', saved_example):
        return "В примере перед одной из функций стоит не тот символ! (возможно перед этой функцией нужно поставить '•')"
    example = example.replace('mod', '%').replace('div', '@')

    if 'ထ' in example:
        return 'К сожалению, строка не поддерживает бесконечности'
    bad_symbols = re.findall(r'[^0-9+\-•:^,@%!()Uu]', example)
    if bad_symbols:
        return f'Почему символ "{bad_symbols[0] if bad_symbols[0] not in ('@', '%') else ('mod', 'div')[bad_symbols[0] == '@']}" есть в примере?'
    if example and example[1] in '+•:^,@%!':
        if example[1] == ',':
            example = f'(0{example[1:]}'
        else:
            return 'Ошибка в начале примера!'
    example = example.replace('%', 'mod').replace('@', 'div')
    if re.search(r'[(U](?:[+•:^),u]|mod|div)|(?:[+•:^(,U-]|mod|div)[u)!]|[0-9,][(U]|[u)!][0-9,]', example):
        return 'Около скобки, модуля, факториала или числа e, π или φ — ошибка!'
    
    if re.search(r',\d+,', example):
        return 'Почему в одном числе две запятые или точки?'
    elif len(example) >= 3:
        for i in range(len(example) - 2):
            if (example[i] in '(+-•:^' or example[i - 2:i + 1] in ('mod', 'div')) and (example[i + 1] == '0') and example[i + 2].isdigit():
                return f'Почему в примере введено "{example[i + 1:i + 3]}"?'
    example = saved_example
    
    if re.search(r'(?:k|sin|cos|tg|ctg|by)-', example):
        return 'Нельзя число или выражение со знаком минус брать без скобок!'
    
    for i in range(len(example) - 2):
        if example[i + 1] == '|':
            example = example[:i + 1] + 'Uu'[example[i] in '0123456789!)ueπφ' or bool(re.match(r'[+•:^!\)]|mod|div', example[i + 2:]))] + example[i + 2:]
            
    example = rescope_example(example)
    if not example:
        return 'Что-то не так со скобками, модулем или логарифмом!'
    
    while '()' in example_brackets or 'Uu' in example_brackets:
        example_brackets = example_brackets.replace('()', '').replace('Uu', '')
    
    example = f'({example})'.replace('^-', "&").replace(',', '.').replace('(-', '(0-').replace('U-', 'U0-')
    example = re.sub(r'(\+|!|div|mod|U|u|•|:|\^|-|\(|\)|sin|cos|tg|ctg|ln|lg|k|log|by)', r' \1 ', example)
    example_for_calculations = [i for i in example.replace("&", ' ^- ').split() if i]
    
    perfect_example = create_perfect_example(pre_example)
    
    if not perfect_example:
        return 'Что-то не так со скобками, модулем или логарифмом!'
    
    try:
        i_stop, i_start = 0, -1
        while '(' in example_for_calculations or 'U' in example_for_calculations:
            for i in range(len(example_for_calculations)):
                if example_for_calculations[i] in ('(', 'U'):
                    i_start = i
                if example_for_calculations[i_start] + example_for_calculations[i] in ('()', 'Uu'):
                    i_stop = i
                    break
            inner_example = example_for_calculations[i_start + 1:i_stop]
            while any((element in inner_example for element in 'sin cos tg ctg ln lg k ! log'.split())):
                for i in range(len(inner_example) - 1):
                    if not (inner_example[i + 1] == '!' and is_num(inner_example[i])):
                        continue
                    inner_example[i:i + 2] = ['R', C.factorial(num=inner_example[i])]
                    if type(inner_example[i + 1]) is str:
                        return inner_example[i + 1]
                    inner_example[i + 1] = str(inner_example[i + 1])
                inner_example = [i for i in inner_example if i != 'R']
                for i in range(len(inner_example) - 3, -1, -1):
                    if not (inner_example[i + 1] == 'k' and is_num(inner_example[i + 2])):
                        continue
                    inner_example[i:i + 3] = [C.radical(num=inner_example[i + 2], power=inner_example[i]), 'R', 'R']
                    if type(inner_example[i]) is str:
                        return inner_example[i]
                    inner_example[i] = str(inner_example[i])
                inner_example = [i for i in inner_example if i != 'R']
                for i in range(len(inner_example) - 4, -1, -1):
                    if inner_example[i] == 'log' and inner_example[i + 2] == 'by' and is_num(inner_example[i + 1]) and is_num(inner_example[i + 3]):
                        inner_example[i:i + 4] = [C.log(inner_example[i + 1], inner_example[i + 3]), 'R', 'R', 'R']
                        if type(inner_example[i]) is str:
                            return inner_example[i]
                        inner_example[i] = str(inner_example[i])
                inner_example = [i for i in inner_example if i != 'R']
                for i in range(len(inner_example) - 1):
                    if inner_example[i] in ('sin', 'cos', 'tg', 'ctg', 'ln', 'lg') and is_num(inner_example[i + 1]):
                        if inner_example[i] in ('sin', 'cos', 'tg', 'ctg'):
                            inner_example[i] = C.trig(inner_example[i], C.rad_to_deg(inner_example[i + 1]), C.is_deg(inner_example[i + 1]))
                        elif inner_example[i] in ('ln', 'lg'):
                            inner_example[i] = C.log(inner_example[i + 1], (10, C.e)[inner_example[i] == 'ln'])
                        if type(inner_example[i]) is str:
                            return inner_example[i]
                        inner_example[i] = str(inner_example[i])
                        inner_example[i + 1] = 'R'
                inner_example = [i for i in inner_example if i != 'R']
            while '^' in inner_example or '^-' in inner_example:
                for i in range(len(inner_example) - 3, -1, -1):
                    if not (is_num(inner_example[i]) and is_num(inner_example[i + 2]) and inner_example[i + 1] in ('^-', '^')):
                        continue
                    inner_example[i:i + 3] = [C.pow(num=inner_example[i], power=inner_example[i + 2], power_type=inner_example[i + 1]), 'R', 'R']
                    if type(inner_example[i]) is str:
                        return inner_example[i]
                    inner_example[i] = str(inner_example[i])
                inner_example = [i for i in inner_example if i != 'R']
            while '•' in inner_example or ':' in inner_example or 'mod' in inner_example or 'div' in inner_example:
                for i in range(len(inner_example) - 2):
                    if is_num(inner_example[i]) and is_num(inner_example[i + 2]) and inner_example[i + 1] in ('•', ':', 'mod', 'div'):
                        num1, num2 = Decimal(inner_example[i]), Decimal(inner_example[i + 2])
                        if inner_example[i + 1] in ('•', ':'):
                            if num1 == num2 == 0 and inner_example[i + 1] == ':':
                                return 'Неопределённость 0/0'
                            inner_example[i:i + 3] = ['R', 'R', str(rond((num1 * num2 if inner_example[i + 1] != ':' else num1 / num2), 0))]
                        if inner_example[i + 1] in ('mod', 'div'):
                            if rond(num2, 1) == 0:
                                return 'Остаток от деления, либо целочисленное деление на ноль невозможно!'
                            k_div = 1
                            if rond(num2, 1) <= 0:
                                num2 = abs(num2)
                                k_div = -1
                            num1, num2 = rond(num1, 2), rond(num2, 2)
                            div, mod = rond(num1 // num2, 3), rond(num1 % num2, 3)
                            res = (mod, div * k_div)[inner_example[i + 1] == 'div']
                            if mod < 0:
                                res = rond((mod + num2, (div - 1) * k_div)[inner_example[i + 1] == 'div'], 3)
                            inner_example[i:i + 3] = ['R', 'R', str(res)]
                inner_example = [i for i in inner_example if i != 'R']
            while '+' in inner_example or '-' in inner_example:
                for i in range(len(inner_example) - 2):
                    if is_num(inner_example[i]) and is_num(inner_example[i + 2]) and inner_example[i + 1] in ('+', '-'):
                        num1, num2 = Decimal(inner_example[i]), Decimal(inner_example[i + 2])
                        inner_example[i:i + 3] = ['R', 'R', str(rond(num1 + (-1, 1)[inner_example[i + 1] == '+'] * num2, 0))]
                inner_example = [i for i in inner_example if i != 'R']
            inner_example = inner_example[0]
            if example_for_calculations[i_start] == 'U':
                inner_example = str(abs(Decimal(inner_example)))
            example_for_calculations[i_start:i_stop + 1] = [inner_example]
        
        if len(example_for_calculations) != 1:
            return 'Где-то ошибка!'
        example_for_calculations = Decimal(example_for_calculations[0])
        if ROUND_ANSWER_TO_MANUALLY != 'по умолчанию':
            example_for_calculations = example_for_calculations.quantize(zeros(ROUND_ANSWER_TO_MANUALLY), ROUND_HALF_UP)
        if abs(example_for_calculations) > Decimal(10) ** -(ROUND_ANSWER_TO - ROUND_ANSWER_TO_IF_POW) or abs(example_for_calculations) < Decimal(10) ** -300:
            example_for_calculations = example_for_calculations.quantize(Decimal('.' + ROUND_ANSWER_TO * '0'), ROUND_HALF_UP)
        else:
            log_num = log(abs(example_for_calculations), 10)
            example_for_calculations = example_for_calculations.quantize(Decimal('.' + (int(-log_num) + ROUND_ANSWER_TO_IF_POW + 1 if type(log_num) in (Decimal, int, float) else ROUND_ANSWER_TO) * '0'), ROUND_HALF_UP)
        if example_for_calculations == 0:
            return '0'
        raw_res = str(example_for_calculations.quantize(Decimal('.0'), ROUND_HALF_UP))[:-2] if example_for_calculations % 1 == 0 else str(example_for_calculations)
        if (Decimal(raw_res) > Decimal(10) ** 24 or 0 < Decimal(raw_res) < Decimal(10) ** -6) or (Decimal(raw_res) < -Decimal(10) ** 24 or 0 > Decimal(raw_res) > -Decimal(10) ** -6):
            fly_exp = 0
            while abs(Decimal(raw_res)) >= Decimal(10) ** 300:
                raw_res = str(Decimal(raw_res) / Decimal(10) ** 100)
                fly_exp += 100
            raw_res_exp1 = Decimal(log(abs(Decimal(raw_res)), 10)).quantize(Decimal('.' + 5 * '0'), ROUND_HALF_UP)
            raw_res_exp1 = raw_res_exp1.quantize(Decimal('0'), ROUND_FLOOR)
            raw_res_exp2 = Decimal(Decimal(raw_res) / Decimal(Decimal(10) ** raw_res_exp1))
            raw_res_exp2 = raw_res_exp2.quantize(Decimal('.' + '0' * (ROUND_ANSWER_TO + 2 if -(ROUND_ANSWER_TO - ROUND_ANSWER_TO_IF_POW) <= raw_res_exp1 <= 0 else ROUND_ANSWER_TO_IF_POW)), ROUND_HALF_UP)
            raw_res = f'{raw_res_exp2}E{'' if abs(Decimal(raw_res)) < 10 ** (-6) else '+'}{raw_res_exp1 + fly_exp}'
        if ('E' in raw_res or 'e' in raw_res) and '.' in raw_res:
            while '0e' in raw_res or '0E' in raw_res:
                raw_res = raw_res.replace('0E', 'E').replace('0e', 'e')
            while '.e' in raw_res or '.E' in raw_res:
                raw_res = raw_res.replace('.E', 'E').replace('.e', 'e')
        else:
            while (raw_res[-1] == '0' or raw_res[-1] == '.') and '.' in raw_res:
                raw_res = raw_res[:-1]
        if raw_res.count('e') == 1 or raw_res.count('E') == 1:
            if 'e+' in raw_res or 'E+' in raw_res or 'e' in raw_res or 'E' in raw_res:
                raw_res = raw_res.replace('e+', '•10^').replace('E+', '•10^')
            if 'e-' in raw_res or 'E-' in raw_res:
                raw_res = raw_res.replace('e-', '•10^(-').replace('E-', '•10^(-') + ')'
            if '^(-' in raw_res and (raw_res[-3] == '-' and int(raw_res[-3:-1]) in range(7, ROUND_ANSWER_TO - ROUND_ANSWER_TO_IF_POW + 1)):
                shift_or_not_first_pow_index = not raw_res[-3:-2].isdigit()
                if raw_res[0] == '-':
                    raw_res = '-0.' + (int(raw_res[-3 + shift_or_not_first_pow_index:-1]) - 1) * '0' + raw_res[:-9 + shift_or_not_first_pow_index].replace('.', '').replace('-', '')
                else:
                    raw_res = '0.' + (int(raw_res[-3 + shift_or_not_first_pow_index:-1]) - 1) * '0' + raw_res[:-9 + shift_or_not_first_pow_index].replace('.', '')
            if raw_res[:2] == '1•':
                raw_res = raw_res[2:]
            if raw_res[:3] == '-1•':
                raw_res = '-' + raw_res[3:]
        if '10^' not in raw_res:
            if '.' not in raw_res:
                lenta_split0 = ''
                for i in range(len(raw_res) - 1, -1, -1):
                    lenta_split0 = raw_res[i] + lenta_split0
                    if len(lenta_split0.replace(' ', '')) % 3 == 0 and len(lenta_split0) >= 3:
                        lenta_split0 = ' ' + lenta_split0
                if lenta_split0[0] == ' ':
                    lenta_split0 = lenta_split0[1:]
                if lenta_split0[:2] == '- ':
                    lenta_split0 = '-' + lenta_split0[2:]
                raw_res = lenta_split0
            else:
                lenta_split1 = lenta_split2 = ''
                splitted_raw_res = raw_res.split('.')
                for i in range(len(splitted_raw_res[0]) - 1, -1, -1):
                    lenta_split1 = splitted_raw_res[0][i] + lenta_split1
                    if len(lenta_split1.replace(' ', '')) % 3 == 0 and len(lenta_split1) >= 3:
                        lenta_split1 = ' ' + lenta_split1
                if lenta_split1[0] == ' ':
                    lenta_split1 = lenta_split1[1:]
                if lenta_split1[:2] == '- ':
                    lenta_split1 = '-' + lenta_split1[2:]
                for i in range(len(splitted_raw_res[1])):
                    lenta_split2 += splitted_raw_res[1][i]
                    if len(lenta_split2.replace(' ', '')) % 3 == 0 and len(lenta_split2) >= 3:
                        lenta_split2 += ' '
                if lenta_split2[-1] == ' ':
                    lenta_split2 = lenta_split2[:-1]
                raw_res = lenta_split1 + '.' + lenta_split2
        return raw_res
    except ZeroDivisionError:
        return 'На ноль или малое число делить нельзя! (±ထ)'
    except (OverflowError, Overflow, InvalidOperation):
        return 'Слишком длинные числа! Или возможно где-то ошибка!'
    except ValueError:
        return 'Где-то ошибка!'
    
    
def get_writing_form(the_example):
    return '=' if is_num(clear_space_and_bracks_with_content(the_example), correct_answer_num_symbols) and the_example else ' ' if the_example != calculator_greeting and the_example and the_example[:1] != ' ' else ''


def calculate_result():
    global example_value, cursor_index
    result.delete(0, END)
    if len(entry_box.get()) > max_character_amount:
        entry_box.delete(max_character_amount, END)
        cursor_index = entry_box.index('insert')

    example_value = entry_box.get().lower()
    example_res = solve_example()
    result.insert(END, f'{get_writing_form(example_res)}{example_res}')
    
    if add_to_recents(example_value):
        recents['recent examples'].append([example_value, result.get().strip('='), perfect_example, cursor_index])
    if len(recents['recent examples']) > 20:
        recents['recent examples'].pop(0)
        
    config_fg_and_insertbackground()
    
        
def insert_in_example(example, insert_arg, right=False):
    global cursor_index
    new_example = f'{example[:cursor_index]}{insert_arg}{example[cursor_index:]}'
    if not right:
        cursor_index += len(new_example) - len(example)
    return new_example


def delete_in_example(example, index_limit_steps):
    global cursor_index
    new_example = f'{example[:cursor_index + index_limit_steps]}{example[cursor_index:]}' if index_limit_steps < 0 else f'{example[:cursor_index]}{example[cursor_index + index_limit_steps:]}'
    if index_limit_steps < 0:
        cursor_index += len(new_example) - len(example)
    return new_example


def disable_editing_added_win_text(key):
    # Разрешаем Control-C (копирование) и Control-A (выделение всего)
    if (key.state & 0x0004) and (key.keysym.lower() in ('c', 'a')):
        return  # Не блокируем эти события
    # Блокируем остальные клавиши редактирования
    if key.keysym in ('BackSpace', 'Delete'):
        return "break"
    elif key.char != '':  # Блокируем ввод символов
        return "break"
    
    
def disable_left_mouse_button_clicking(key):
    return "break"
    
    
def scroll_text(string_shift):
    added_win.focus_set()
    text_entry['state'] = DISABLED
    if abs(string_shift) == 1:
        text_entry.yview_scroll(string_shift, 'pages')
    elif abs(string_shift) == 4:
        text_entry.yview_scroll(string_shift, 'units')
    else:
        text_entry.yview((1.0, END)[string_shift > 0])
    text_entry['state'] = NORMAL
    
    
def added_win_control_keypress(event):
    if event.state & 0x0004 and event.keycode == 32:
        entry_box.focus_set()
    elif event.state & 0x0004 and event.keycode == 87:
        manage_not_main_window_close()
    elif event.state & 0x0004 and event.keycode == 65:
        text_entry.tag_add(SEL, '1.0', 'end-1c')
        
def create_added_win(win_type):
    global added_win, text_entry, cursor_index, example_value
    theme_is_light = settings['theme'] == 'light'
    
    if win_type is None:
        added_win = FakeWindow()
        return
    
    is_help = win_type == '?'
    
    try:
        added_win.destroy()
    except NameError:
        pass
    added_win = Toplevel()
    added_win.iconbitmap(f'icons/{('history', 'help')[is_help]}.ico')
    added_win.title(('история', 'инструкция')[is_help])
    
    added_win.geometry(f'{WIDTH - 10}x{MAX_COORD - 100}+{X_COORD}+0')
    added_win.resizable(width=False, height=False)
    
    added_win.focus_set()
    added_win.protocol('WM_DELETE_WINDOW', lambda: manage_not_main_window_close())
    added_win.attributes('-alpha', '0.975')
    
    text_entry = Text(added_win, bg=('#' + '10' * 3, '#' + 'e9' * 3)[settings['theme'] == 'light'], fg=entry_box.cget('fg'), font=(('Arial', 12, 'bold'), ('Arial', 16, 'bold'))[is_help])
    text_entry.place(x=2, y=2, width=WIDTH - 30, height=MAX_COORD - 104)
    
    scrollbar_history_calc = ttk.Scrollbar(added_win, orient='vertical', command=text_entry.yview)
    scrollbar_history_calc.pack(side=RIGHT, fill=Y)
    text_entry['yscrollcommand'] = scrollbar_history_calc.set
    
    text_entry.config(insertbackground=entry_box.cget('insertbackground'), selectbackground=('#' + '38' * 3, '#' + 'b7' * 3)[settings['theme'] == 'light'], insertwidth=1)
    
    text_entry.bind('<Key>', disable_editing_added_win_text)
    
    added_win['bg'] = ('#' + '20' * 3, '#' + 'e8' * 3)[settings['theme'] == 'light']
    
    added_win.bind('<Control-Shift-Up>', lambda key: None)  # не удалять! поддерживает автономию перед <Control-Up>
    added_win.bind('<Control-Shift-Down>', lambda key: None)  # не удалять! поддерживает автономию перед <Control-Down>
    added_win.bind('<Control-Up>', lambda key: scroll_text(-4))
    added_win.bind('<Control-Down>', lambda key: scroll_text(4))
    
    added_win.bind('<Control-t>', change_theme)
    added_win.bind('<Control-T>', change_theme)
    
    if cursor_index and example_value[cursor_index - 1:cursor_index].lower() == '?':
        example_value = delete_in_example(example_value, -1)
        cursor_index -= 1
    entry_box.delete(0, END)
    entry_box.insert(END, example_value)
    entry_box.icursor(cursor_index)
    if type(indexes_of_selection) is dict:
        entry_box.selection_range(*indexes_of_selection.values())
        
    added_win.bind('<Control-Key>', added_win_control_keypress)
    text_entry.bind('<Control-Key>', added_win_control_keypress)
    
    added_win.bind('<Escape>', lambda key: manage_not_main_window_close())
    text_entry.bind('<Escape>', lambda key: manage_not_main_window_close())
    
    (finish_to_history_win, finish_to_help_win)[is_help]()


def finish_to_help_win():
    theme_is_light = settings['theme'] == 'light'
    title, text = ('Arial', 16, 'bold'), ('Arial', 14)
    
    black = ("#bbbbbb", 'black')[theme_is_light]
    green = ("#429442", 'green')[theme_is_light]
    purple = ("#9659aa", 'purple')[theme_is_light]
    gray = ("#9C9C9C", 'gray40')[theme_is_light]
    red = ("#b42020", 'red4')[theme_is_light]
    colors = (black, green, purple, gray, red)
    [text_entry.tag_config(f'help_{color}_{(14, 16)[flag]}', font=(text, title)[flag], foreground=color) for color in colors for flag in (True, False)]
    
    splitted_text_entry = text_help_calc.split('\n')
    text_entry.delete(1.0, END)
    for i in range(len(splitted_text_entry)):
        val = splitted_text_entry[i] + '\n'
        tag_rows = (12, 22, 11, 9, 9)
        a, b, c, d, e = (sum(tag_rows[:i + 1]) for i in range(5))
        size = (14, 16)[i in (2, a, b, c, d, e)]
        color = (black, purple, green, gray, red, red)[(i >= a) + (i >= b) + (i >= c) + (i >= d) + (i >= e)]
        text_entry.insert(END, val, f'help_{color}_{size}')


def finish_to_history_win():
    theme_is_light = settings['theme'] == 'light'
    
    added_win.bind('<Control-Alt-Up>', lambda key: scroll_text(-1))
    added_win.bind('<Control-Alt-Down>', lambda key: scroll_text(1))
    
    color1 = ('#' + 'b0' * 3, '#' + '2f' * 3)[theme_is_light]
    color2 = ('#' + '90' * 3, '#' + '5f' * 3)[theme_is_light]
    [text_entry.tag_config(f'history_{color1}', foreground=color1), text_entry.tag_config(f'history_{color2}', foreground=color2)]
    tags = (None, f'history_{color1}', f'history_{color1}', f'history_{color2}')
    [text_entry.insert(END, val + '\n', tags[(i + 1) % 4]) for i, val in enumerate(history_of_calculations.split('\n'))]
    
    
def manage_not_main_window_close():
    added_win.withdraw()
    added_win.title(invisible_win_title)
    entry_box.focus_set()
        

ROUND_ANSWER_TO = 18
ROUND_ANSWER_TO_IF_POW = 12
max_rounding = ROUND_ANSWER_TO - 1
min_rounding = -(24 - 1)

white_or_black = ('white', 'black')[settings['theme'] == 'light']
main_win = Tk()

main_win.overrideredirect(True) # Убрать заголовок окна
main_win.wm_attributes('-topmost', 1)  # Сделать окно несворачиваемым при нажатии на другие окна
main_win.attributes('-alpha', '0.975')
main_win.resizable(width=False, height=False)

main_win.title('Калькулятор.')
main_win['bg'] = white_or_black

entry_box = Entry(main_win, font=('Arial', HEIGHT // 2), fg=white_or_black, bg=white_or_black, borderwidth=0, insertwidth=1, insertontime=700, insertofftime=500)
entry_box.insert(END, recents['example before closing'])
entry_box.icursor(recents['cursor before closing'])
entry_box.focus_set()
cursor_index = entry_box.index('insert')
indexes_of_selection = None
can_backspace = entry_box.index('insert') != 0

result = Entry(main_win, font=('Arial', HEIGHT // 2), fg=white_or_black, bg=white_or_black, borderwidth=0, insertwidth=1, insertontime=700, insertofftime=500)
change_width_of_entry(recents['example before closing'], entry_box, result)
example_value = entry_box.get()

create_added_win(None)
change_size_of_everything(scale=settings['scale'])

main_win.geometry(f'{WIDTH}x{HEIGHT}+{X_COORD}+{settings['y']}')


def set_focus_from_not_my_application():
    if not main_win.focus_get():
        change_size_of_everything(scale=settings['scale'], scale_was_zero=True, change_result=False)
        length = get_text_length(entry_box.get()[:cursor_index], entry_box) + 3
        width_plus_x_coord = WIDTH + X_COORD
        length_plus_x_coord = length + X_COORD
        last_pos = pyautogui.position()
        x = length_plus_x_coord if length_plus_x_coord < width_plus_x_coord - 5 else width_plus_x_coord - 5
        y = settings['y'] + HEIGHT // 2
        pyautogui.moveTo(x, y)
        pyautogui.click()
        pyautogui.moveTo(*last_pos)
        
        
def set_keyboard_layout_memory():
    global keyboard_layout_memory
    keyboard_layout_memory = ('en', 'ru')[not is_russian_layout()]


keyboard.add_hotkey('ctrl+space', set_focus_from_not_my_application)
keyboard.add_hotkey('shift+alt', set_keyboard_layout_memory)
keyboard.add_hotkey('win+space', set_keyboard_layout_memory)



def delete_to_the(k):
    global example_value, cursor_index
    for i in range(4, 2, -1):
        if example_value[cursor_index - i:cursor_index - 1] in united_symbols_without_scopes and example_value[cursor_index - 1:cursor_index + 1] in ('||', '()') and k == -1:
            example_value = delete_in_example(example_value, 1)
            example_value = delete_in_example(example_value, -i)
            break
    else:
        if example_value[cursor_index - 4:cursor_index + 5] in ('log()by()', 'log||by||', 'log()by||', 'log||by()'):
            example_value = delete_in_example(example_value, 5)
            example_value = delete_in_example(example_value, -4)
        elif example_value[cursor_index - 8:cursor_index + 1] in ('log()by()', 'log||by||', 'log()by||', 'log||by()') and k == -1:
            example_value = delete_in_example(example_value, 1)
            example_value = delete_in_example(example_value, -8)
        elif example_value[cursor_index - 1:cursor_index + 1] in ('()', '||'):
            example_value = delete_in_example(example_value, 1)
            example_value = delete_in_example(example_value, -1)
        elif example_value[cursor_index - 2:cursor_index] == '•√':
            example_value = delete_in_example(example_value, -2)
            example_value = insert_in_example(example_value, '√')
        elif cursor_index > 0 and k == -1 or cursor_index < len(example_value) and k == 1:
            example_value = delete_in_example(example_value, k)


def get_selection(the_entry=entry_box):
    try:
        return {'start': the_entry.index(SEL_FIRST), 'end': the_entry.index(SEL_LAST)}
    except TclError:
        return
    
    
def add_to_recents(value):
    return value != recents['recent examples'][-1][0]


def clean_from_scopes_with_emptyness(value):
    value = f'({value})'
    for i in range(len(value) - 2):
        if value[i + 1] == '|':
            value = value[:i + 1] + 'Uu'[value[i] in '0123456789!)ueπφ' or bool(re.match(r'[+•:^!\)]|mod|div', value[i + 2:]))] + value[i + 2:]
            
    value = value[1:-1]
    
    value = clean_pattern_empty_scopes(value)
    value = re.sub(r'[Uu]', '|', value)
    value = re.sub(r'(?:[\+\-•:^,]|mod|div)(?=\))', r'', f'({value})')[1:-1]
    return value


def make_it_future(example_after_q=False):
    global i_last_example
    entry_box.delete(0, END)
    entry_box.insert(END, example_value)
    entry_box.icursor(cursor_index)
    calculate_result()
    change_width_of_entry(entry_box.get(), entry_box, result)
    i_last_example = 'future'
    
    
def get_difference(old, new):
    if old:
        for i in range(len(new)):
            if old[:1] == new[:1]:
                old = old[1:]
                new = new[1:]
            else:
                break
        for i in range(len(new) - 1, -1, -1):
            if old[-1:] == new[i]:
                old = old[:-1]
            else:
                break
    return old


def insertion_if_division_of_one(left_symbol, arg, example):
    if re.fullmatch(r'(?:[^0-9\.]|^)1', example[max(cursor_index - 2, 0):cursor_index]):
        return insert_in_example(example, f'/{arg}')
    else:
        return insert_in_example(example, f'{'•' if left_symbol in '0123456789φπeထ)!' else ''}{arg}')


def key_calc(key):
    global history_of_calculations, i_history, i_last_example, added_win, settings, example_value, cursor_index, can_backspace, indexes_of_selection, keyboard_layout_memory
    bypass = bypass2 = False
        
    if i_last_example != 'future' and hasattr(key, 'keysym') and key.keysym not in ('Control_L', 'Control_R'):
        add_to_last_examples_if_selection_or_cursor_change()
        make_it_future()
        bypass2 = True
    
    if type(key) is tuple:
        cursor_index = key[0]
        start, end = key
        keysym = 'changed text'
        bypass = True
        entry_box.delete(0, END)
        entry_box.insert(END, example_value)       
        calculate_result()
        entry_box.icursor(cursor_index)
        change_width_of_entry(entry_box.get(), entry_box, result)
        add_to_last_examples_if_selection_or_cursor_change()
    
    if not bypass:
        keysym = key.keysym if len(key.keysym) > 1 or key.keysym in 'MBTQIVPEU' else key.keysym.lower()
            
        if keysym in ('Tab', 'Up', 'Down', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Caps_Lock', 'Win_L'):
            return
        
        if not bypass2:
            if type(indexes_of_selection) is dict:
                pass
            elif keysym in ('BackSpace', 'Left'):
                cursor_index = entry_box.index('insert') + (1 if can_backspace else 0)
            elif keysym not in special_keys and keysym != 'Delete' or keysym in ('Right', 'apostrophe', 'quotedbl'):
                cursor_index = entry_box.index('insert') - 1
            else:
                cursor_index = entry_box.index('insert')
        
        entry_box.delete(0, END)
        example_value = recents['recent examples'][-1][0]
        
        if type(indexes_of_selection) is dict and keysym not in ('Return', 'grave', 'Escape', 'Tab'):
            start, end = indexes_of_selection.values()
            if keysym in ('Left', 'Right'):
                cursor_index = start if keysym == 'Left' else end
                entry_box.insert(END, example_value)
                entry_box.icursor(cursor_index)
                indexes_of_selection = None
                bypass = True
            elif keysym not in special_keys:
                example_value = example_value[:start] + example_value[end:]
                cursor_index = start
                indexes_of_selection = None
                if keysym in ('Delete', 'BackSpace'):
                    entry_box.insert(END, example_value)
                    entry_box.icursor(cursor_index)
                    calculate_result()
                    change_width_of_entry(entry_box.get(), entry_box, result)
                    bypass = True
    
    if not bypass:
        symbol_that_is_left_from_cursor = example_value[cursor_index - 1:cursor_index]
        symbol_that_is_right_from_cursor = example_value[cursor_index:cursor_index + 1]
        if not symbol_that_is_left_from_cursor:
            symbol_that_is_left_from_cursor = '#'
        if not symbol_that_is_right_from_cursor:
            symbol_that_is_right_from_cursor = '#'
        if (symbol_that_is_left_from_cursor == '.' and (len(keysym) == 1 and keysym in 'sctklngpefraodmxbivVyujwzPEU' or keysym in keys_after_dot)):
            example_value = insert_in_example(example_value, '5')
            symbol_that_is_left_from_cursor = example_value[cursor_index - 1:cursor_index]
        if keysym == 'BackSpace':
            for i in range(3, 1, -1):
                if example_value[cursor_index - i:cursor_index] in united_symbols:
                    example_value = delete_in_example(example_value, -i)
                    break
            else:
                delete_to_the(k=-1)
        elif keysym == 'Delete':
            for i in range(3, 1, -1):
                if example_value[cursor_index:cursor_index + i] in united_symbols:
                    example_value = delete_in_example(example_value, i)
                    break
            else:
                delete_to_the(k=1)
        elif keysym == 'grave':
            example_value = ''
        elif keysym == 'v':
            example_value = insert_in_example(example_value, f'{find_the_most_useful_symbol_to_paste(example_value, symbol_that_is_left_from_cursor in '0123456789πφe.)!ထ')}')
            example_value = example_value[:max_character_amount]
        elif keysym == 'V':
            example_value = insert_in_example(example_value, f'{find_the_most_useful_symbol_to_paste(example_value, symbol_that_is_left_from_cursor in '0123456789πφe.)!ထ', first=False)}')
            example_value = example_value[:max_character_amount]
        elif keysym == 'h':
            example_value = insert_in_example(example_value, 'h' if not example_value else '')
        elif keysym == 'space':
            example_value = insert_in_example(example_value, ' ')
        elif keysym == 'I':
            example_value = insert_in_example(example_value, 'ထ')
        elif keysym == 'b':
            right_find = list(re.finditer(r'(?:log\(|log\|)', example_value[:cursor_index]))
            right_find = right_find[-1] if right_find else None
            insert_by = 'by'
            if right_find:
                example_in_future_log_part = example_value[right_find.end():cursor_index]
                if example_in_future_log_part.count('(') == example_in_future_log_part.count(')') and example_in_future_log_part.count('|') % 2 == 0:
                    insert_by = ')by' if right_find.group() == 'log(' else '|by' if right_find.group() == 'log|' else 'by'
            match_after_by_module = re.match(r'[^()]*?\|', example_value[cursor_index:])
            match_after_by_scope = re.match(r'[^(|]*?\)', example_value[cursor_index:])
            if match_after_by_module:
                insert_by += '|'
            if match_after_by_scope:
                insert_by += '('
            example_value = insert_in_example(example_value, insert_by)
        elif keysym == 'dollar':
            pass  # Этот символ можно использовать для пустого нажатия, удалять запрещено!
        elif keysym in ('ampersand', 'greater', 'less', 'braceleft', 'braceright', 'underscore'):
            pass
        elif keysym in ('apostrophe', 'quotedbl'):
            indexes_of_selection = None
            pyperclip.copy(result.get().replace('•', '*').replace('ထ', 'inf').replace('=', '') if keysym == 'quotedbl' else example_value.replace('•', '*').replace('ထ', 'inf'))
        elif len(keysym) == 1 and keysym in 'zMBTQPEU':
            if keysym == 'U':
                example_value = insert_in_example(example_value, '^4')
            elif keysym in 'zMBTQ':
                zers = '0' * (('zMBTQ'.index(keysym) + 1) * 3)
                example_value = insert_in_example(example_value, zers if symbol_that_is_left_from_cursor in '0123456789.' else f'•1{zers}' if symbol_that_is_left_from_cursor in 'φπeထ)!' else f'1{zers}')
            elif keysym == 'P':
                example_value = insert_in_example(example_value, f'{'/100' if symbol_that_is_left_from_cursor in '0123456789φπeထ)!' else '1/100'}')
            elif keysym == 'E':
                example_value = insert_in_example(example_value, '•10^' if symbol_that_is_left_from_cursor in '0123456789φπeထ)!' else '1•10^' if symbol_that_is_left_from_cursor in '^√' else '10^')
        elif keysym in ('period', 'comma'):
            if symbol_that_is_left_from_cursor != '.':
                example_value = insert_in_example(example_value, '/' if symbol_that_is_left_from_cursor == 'π' else '•' if symbol_that_is_left_from_cursor in 'φe)!' else '')
                example_value = insert_in_example(example_value, '.' if symbol_that_is_left_from_cursor.isdigit() else '0.')
            else:
                example_value = delete_in_example(example_value, -1)
                example_value = insert_in_example(example_value, '•0.')
        elif keysym in ('s', 'c', 't', 'k'):
            example_value = insertion_if_division_of_one(symbol_that_is_left_from_cursor, {'s': 'sin', 'c': 'cos', 't': 'tg', 'k': 'ctg'}[keysym], example_value)
            if symbol_that_is_right_from_cursor != '(':
                example_value = insert_in_example(example_value, '(')
                example_value = insert_in_example(example_value, ')', right=True)
        elif keysym in ('d', 'm'):
            example_value = insert_in_example(example_value, f'{({'m': 'mod', 'd': 'div'}[keysym])}')
        elif keysym == 'l':
            example_value = insertion_if_division_of_one(symbol_that_is_left_from_cursor, 'log(', example_value)
            example_value = insert_in_example(example_value, ')by' if symbol_that_is_right_from_cursor == '(' else ')by()', right=True)
        elif keysym in ('n', 'g'):
            example_value = insertion_if_division_of_one(symbol_that_is_left_from_cursor, {'n': 'ln', 'g': 'lg'}[keysym], example_value)
            if symbol_that_is_right_from_cursor != '(':
                example_value = insert_in_example(example_value, '(')
                example_value = insert_in_example(example_value, ')', right=True)
        elif keysym == 'p':
            example_value = insertion_if_division_of_one(symbol_that_is_left_from_cursor, 'π', example_value)
        elif keysym == 'r':
            example_value = insertion_if_division_of_one(symbol_that_is_left_from_cursor, '√', example_value)
        elif keysym in ('bar', 'backslash'):
            example_value = insert_in_example(example_value, '|')
        elif keysym == 'a':
            for i in range(4, 2, -1):
                if example_value[cursor_index - i:cursor_index - 1] in united_symbols_without_scopes and example_value[cursor_index - 1:cursor_index + 1] == '()':
                    change_scopes_to_modules()
                    break
            else:
                if example_value[cursor_index - 4:cursor_index + 3] == 'log()by' or example_value[cursor_index - 3:cursor_index + 1] == 'by()':
                    change_scopes_to_modules()
                else:
                    example_value = insertion_if_division_of_one(symbol_that_is_left_from_cursor, '|', example_value)
                    example_value = insert_in_example(example_value, '|', right=True)
        elif keysym in ('exclam', 'i'):
            example_value = insert_in_example(example_value, '!')
        elif keysym == 'percent':
            example_value = insert_in_example(example_value, 'mod')
        elif keysym == 'at':
            example_value = insert_in_example(example_value, 'div')
        elif keysym in ('asciicircum', 'w'):
            if symbol_that_is_left_from_cursor not in '0123456789φπeထ)|!' and keysym != 'asciicircum':
                example_value = insert_in_example(example_value, '2')
            example_value = insert_in_example(example_value, '^')
        elif keysym == 'y':
            if symbol_that_is_left_from_cursor not in '0123456789φπeထ)|!' and keysym != 'asciicircum':
                example_value = insert_in_example(example_value, '10')
            example_value = insert_in_example(example_value, '^(-')
            example_value = insert_in_example(example_value, ')', right=True)
        elif keysym == 'u':
            example_value = insert_in_example(example_value, '^2')
        elif keysym == 'j':
            example_value = insert_in_example(example_value, '^3')
        elif keysym in ('x', 'asterisk'):
            if symbol_that_is_left_from_cursor == '•' and keysym != 'asterisk':
                example_value = delete_in_example(example_value, -1)
                example_value = insert_in_example(example_value, '^')
            elif symbol_that_is_left_from_cursor not in '0123456789φπeထ)|!' and keysym != 'asterisk':
                example_value = insert_in_example(example_value, '2•')
            else:
                example_value = insert_in_example(example_value, '•')
        elif keysym == 'minus':
            for i in range(3, 1, -1):
                if example_value[cursor_index - i:cursor_index] in united_symbols:
                    example_value = insert_in_example(example_value, '(-')
                    example_value = insert_in_example(example_value, ')', right=True)
                    break
            else:
                if symbol_that_is_left_from_cursor not in '^+-•/√':
                    example_value = insert_in_example(example_value, '-')
                else:
                    example_value = insert_in_example(example_value, '(-')
                    example_value = insert_in_example(example_value, ')', right=True)
        elif keysym in ('equal', 'plus'):
            if symbol_that_is_left_from_cursor in '•/^√':
                example_value = insert_in_example(example_value, '2')
                example_value = insert_in_example(example_value, '+')
            elif symbol_that_is_left_from_cursor not in '0123456789φπeထ)|!' and keysym != 'plus':
                example_value = insert_in_example(example_value, '1')
            else:
                example_value = insert_in_example(example_value, '+')
        elif keysym in ('slash', 'colon', 'semicolon'):
            if symbol_that_is_left_from_cursor == '/' and keysym == 'slash':
                example_value = delete_in_example(example_value, -1)
                example_value = insert_in_example(example_value, 'div')
            elif symbol_that_is_left_from_cursor not in '0123456789φπeထ)|!' and keysym in ('semicolon', 'slash'):
                if (symbol_that_is_left_from_cursor not in '(' or example_value[cursor_index:cursor_index  + 1] not in ')') and keysym == 'semicolon':
                    example_value = insert_in_example(example_value, '(1/')
                    example_value = insert_in_example(example_value, ')', right=True)
                elif symbol_that_is_left_from_cursor == '√':
                    example_value = insert_in_example(example_value, '3/')
                elif symbol_that_is_left_from_cursor in '•^':
                    example_value = insert_in_example(example_value, f'({('', '-')[symbol_that_is_left_from_cursor == '•']}1/')
                    example_value = insert_in_example(example_value, ')', right=True)
                else:
                    example_value = insert_in_example(example_value, '1/')
            else:
                example_value = insert_in_example(example_value, '/')
        elif keysym == 'e':
            example_value = insertion_if_division_of_one(symbol_that_is_left_from_cursor, 'e', example_value)
        elif keysym == 'f':
            example_value = insertion_if_division_of_one(symbol_that_is_left_from_cursor, 'φ', example_value)
        elif keysym in ('parenleft', 'bracketleft'):
            example_value = insertion_if_division_of_one(symbol_that_is_left_from_cursor, '(', example_value)
        elif keysym == 'o':
            example_value = insert_in_example(example_value, f'{'/' if re.search(r'(?:(?:[^0-9\.]|^)1|!)$', example_value[:cursor_index]) else '•' if symbol_that_is_left_from_cursor in '0123456789φπeထ)' else ''}(')
            example_value = insert_in_example(example_value, ')', right=True)
        elif keysym in ('parenright', 'bracketright'):
            example_value = insert_in_example(example_value, ')')
        elif keysym == 'numbersign':
            example_value = insert_in_example(example_value, '#')
        elif keysym.isdigit():
            if re.fullmatch(r'(?:[^0-9\.]|^)0', example_value[max(cursor_index - 2, 0):cursor_index]):
                example_value = insert_in_example(example_value, '•0')
            else:
                example_value = insert_in_example(example_value, f'{'/' if symbol_that_is_left_from_cursor in 'π' else '•' if symbol_that_is_left_from_cursor in 'φe)!' else ''}{keysym}')
        elif keysym in ('Left', 'Right'):
            for i in range(4, 1, -1):
                if (example_value[cursor_index:cursor_index + i], example_value[cursor_index - i:cursor_index])[keysym == 'Left'] in (united_symbols + united_symbols_with_scopes):
                    cursor_index += (i, -i)[keysym == 'Left']
                    break
            else:
                cursor_index += (1, -1)[keysym == 'Left']
            add_to_last_examples_if_selection_or_cursor_change()
        elif keysym not in special_keys:
            example_value = insert_in_example(example_value, f'{keysym}')
        if not (keysym.isdigit() or keysym in ('minus', 'BackSpace', 'Delete')) and ('q' in example_value and keysym != 'q' or example_value.count('q') ==  2):
            example_value, _, _, cursor_index, indexes_of_selection, _ = recents['last examples'][-1]
        entry_box.insert(END, example_value)
        calculate_result()
        if keysym not in ('grave', 'Return', 'Escape'):
            add_to_last_examples_if_selection_or_cursor_change()
    
    recent_examples = recents['recent examples']
    peak = ''
    for i in range(-2, -len(recent_examples), -1):
        if ((len(recent_examples[-i][0]) >= len(recent_examples[-(i + 1)][0]) or 'q' in recent_examples[-(i + 1)][0] and 'q' not in recent_examples[-i][0]) 
            and not ('q' in recent_examples[-(i + 1)][0] and 'q' in recent_examples[-i][0])):
            peak = recent_examples[-i][0]
    difference1, difference2 = (get_difference(old=peak, new=recent_examples[-i][0]) for i in (1, 2))
    
    num_is_part_of_deleted = re.search(r'[0-9φπe]', difference1) and not re.search(r'[0-9φπe]', difference2)
    
    if keysym in ('grave', 'Return', 'BackSpace', 'Delete', 'apostrophe', 'quotedbl') or num_is_part_of_deleted:
        indexes_of_selection = None
        perfect_ex_for_ans = ''
        if num_is_part_of_deleted and keysym in ('Delete', 'BackSpace', 'grave', 'changed text'):
            perfect_ex_for_ans = recent_examples[-2][2]
        elif keysym in ('apostrophe', 'quotedbl', 'Return'):
            perfect_ex_for_ans = recent_examples[-1][2]
        for i in range(2):
            for j in range(-3, 0):
                if perfect_ex_for_ans[j:] in ending_symbols:
                    perfect_ex_for_ans = perfect_ex_for_ans[:j]
                    break
        
        perfect_ex_for_ans = clean_from_scopes_with_emptyness(perfect_ex_for_ans)
        
        split_old_history_of_calculations = history_of_calculations.split('\n')
        history_res = solve_example(perfect_ex_for_ans)
        rounding_in_history = ''
        if str(ROUND_ANSWER_TO_MANUALLY).strip('-').isdigit():
            manual_round_abs = abs(ROUND_ANSWER_TO_MANUALLY)
            num_of_ending_symbols = (0 < manual_round_abs % 10 < 5 and manual_round_abs // 10 != 1) + (manual_round_abs % 10 == 1 and manual_round_abs != 11)
            rounding_in_history = f' ({manual_round_abs} знак{('ов', 'а', '')[num_of_ending_symbols]} {('перед', 'после')[ROUND_ANSWER_TO_MANUALLY > 0]} запятой)'
        
        temporary_data_and_rounding = split_old_history_of_calculations[2]
        
        if perfect_ex_for_ans and (perfect_ex_for_ans != split_old_history_of_calculations[0] or (rounding_in_history not in temporary_data_and_rounding or '(' in temporary_data_and_rounding and rounding_in_history == '')):
            history_input = perfect_ex_for_ans
            if is_num(history_res, correct_answer_num_symbols) and history_res != history_input.replace(' ', ''):
                if keysym in ('Return', 'grave'):
                    entry_box.delete(0, END)
                    entry_box.insert(END, str(history_res) if keysym == 'Return' else example_value)
                    example_value = entry_box.get()
                    cursor_index = entry_box.index('insert')
                value_to_add = [example_value, result.get().strip('='), perfect_example, cursor_index]
                value_to_add_plus = [example_value, clear_space_and_bracks_with_content(result.get().strip('=')) if example_value else '', '', cursor_index, indexes_of_selection if indexes_of_selection else None, settings['round']]
                if add_to_recents(example_value):
                    recents['recent examples'].append(value_to_add)
                if value_to_add_plus != recents['last examples'][-1]:
                    recents['last examples'].append(value_to_add_plus)
                if len(recents['last examples']) > 500:
                    recents['last examples'].pop(0)
                if len(recents['recent examples']) > 20:
                    recents['recent examples'].pop(0)
                
                if history_input and added_win.title() in ('история', invisible_win_title):
                    i_last_example = 'future'
                    i_history = 'future'
                    date_time = str(datetime.datetime.today())[:-7].replace('-', '.')
                    date_time_rounding = f'{date_time}{rounding_in_history}'
                    new_history = f'{perfect_example}\n{history_res}\n{date_time_rounding}\n\n{history_of_calculations}'
                    split0_history_of_calculations = new_history.split('\n')
                    
                    too_much_history_data = len(split0_history_of_calculations) > settings['history length']
                    history_of_calculations = '\n'.join(split0_history_of_calculations if not too_much_history_data else split0_history_of_calculations[:settings['history length']])
                    if added_win.title() != invisible_win_title:
                        try:
                            theme_is_light = settings['theme'] == 'light'
                            color1 = ('#' + 'b0' * 3, '#' + '2f' * 3)[theme_is_light]
                            color2 = ('#' + '90' * 3, '#' + '5f' * 3)[theme_is_light]
                            text_entry.insert(0.0, date_time_rounding + '\n' + '\n', f'history_{color2}')
                            text_entry.insert(0.0, history_res + '\n', f'history_{color1}')
                            text_entry.insert(0.0, perfect_example + '\n', f'history_{color1}')
                            if too_much_history_data:
                                text_entry.delete(1.0, END)
                                tags = (None, f'history_{color1}', f'history_{color1}', f'history_{color2}')
                                [text_entry.insert(END, val + '\n', tags[(i + 1) % 4]) for i, val in enumerate(history_of_calculations.split('\n'))]
                        except NameError:
                            pass
        elif keysym == 'Return':
            solve_res = solve_example(perfect_ex_for_ans)
            if is_num(solve_res, correct_answer_num_symbols):
                entry_box.delete(0, END)
                entry_box.insert(END, solve_res)
                example_value = entry_box.get()
                cursor_index = entry_box.index('insert')
            value_to_add = [example_value, result.get().strip('='), perfect_example, cursor_index]
            value_to_add_plus = [example_value, clear_space_and_bracks_with_content(result.get().strip('=')) if example_value else '', '', cursor_index, indexes_of_selection if indexes_of_selection else None], settings['round']
            if add_to_recents(example_value):
                recents['recent examples'].append(value_to_add)
            if value_to_add_plus != recents['last examples'][-1]:
                recents['last examples'].append(value_to_add_plus)
            if len(recents['last examples']) > 500:
                recents['last examples'].pop(0)
            if len(recents['recent examples']) > 20:
                recents['recent examples'].pop(0)
    
    entry_box.icursor(cursor_index)
    if modify_info(example_value) is not None:
        calculate_result()
    can_backspace = entry_box.index('insert') != 0
    
    
    change_width_of_entry(entry_box.get(), entry_box, result)

    
    if keysym == 'Escape':
        close_main_win()
        if not is_russian_layout() and keyboard_layout_memory == 'ru':
            hwnd = user32.GetForegroundWindow()
            user32.PostMessageW(hwnd, 0x50, 0, user32.LoadKeyboardLayoutW("00000419", 0x1))
        
        
def real_key_calc(key):
    key_calc(key)
    if hasattr(key, 'keysym') and key.keysym not in ('Escape', 'Tab', 'Up', 'Down', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Caps_Lock', 'Win_L' 'y', 'z', 'Y', 'Z'):
        add_to_last_examples_if_selection_or_cursor_change()
        
        
def save_example_to_history(key):
    global history_of_calculations, i_history, i_last_example, added_win, settings, example_value, cursor_index, can_backspace, indexes_of_selection, keyboard_layout_memory
    indexes_of_selection = None
    perfect_ex_for_ans = recents['recent examples'][-1][2]
    for i in range(2):
        for j in range(-3, 0):
            if perfect_ex_for_ans[j:] in ending_symbols:
                perfect_ex_for_ans = perfect_ex_for_ans[:j]
                break

    perfect_ex_for_ans = clean_from_scopes_with_emptyness(perfect_ex_for_ans)

    split_old_history_of_calculations = history_of_calculations.split('\n')
    history_res = solve_example(perfect_ex_for_ans)
    rounding_in_history = ''
    if str(ROUND_ANSWER_TO_MANUALLY).strip('-').isdigit():
        manual_round_abs = abs(ROUND_ANSWER_TO_MANUALLY)
        num_of_ending_symbols = (0 < manual_round_abs % 10 < 5 and manual_round_abs // 10 != 1) + (manual_round_abs % 10 == 1 and manual_round_abs != 11)
        rounding_in_history = f' ({manual_round_abs} знак{('ов', 'а', '')[num_of_ending_symbols]} {('перед', 'после')[ROUND_ANSWER_TO_MANUALLY > 0]} запятой)'

    temporary_data_and_rounding = split_old_history_of_calculations[2]

    if perfect_ex_for_ans and (perfect_ex_for_ans != split_old_history_of_calculations[0] or (rounding_in_history not in temporary_data_and_rounding or '(' in temporary_data_and_rounding and rounding_in_history == '')):
        history_input = perfect_ex_for_ans
        if is_num(history_res, correct_answer_num_symbols) and history_res != history_input.replace(' ', ''):
            value_to_add = [example_value, result.get().strip('='), perfect_example, cursor_index]
            value_to_add_plus = [example_value, clear_space_and_bracks_with_content(result.get().strip('=')) if example_value else '', '', cursor_index, indexes_of_selection if indexes_of_selection else None, settings['round']]
            if add_to_recents(example_value):
                recents['recent examples'].append(value_to_add)
            if value_to_add_plus != recents['last examples'][-1]:
                recents['last examples'].append(value_to_add_plus)
            if len(recents['last examples']) > 500:
                recents['last examples'].pop(0)
            if len(recents['recent examples']) > 20:
                recents['recent examples'].pop(0)
            
            if history_input and added_win.title() in ('история', invisible_win_title):
                i_last_example = 'future'
                i_history = 'future'
                date_time = str(datetime.datetime.today())[:-7].replace('-', '.')
                date_time_rounding = f'{date_time}{rounding_in_history}'
                new_history = f'{perfect_example}\n{history_res}\n{date_time_rounding}\n\n{history_of_calculations}'
                split0_history_of_calculations = new_history.split('\n')
                
                too_much_history_data = len(split0_history_of_calculations) > settings['history length']
                history_of_calculations = '\n'.join(split0_history_of_calculations if not too_much_history_data else split0_history_of_calculations[:settings['history length']])
                if added_win.title() != invisible_win_title:
                    try:
                        theme_is_light = settings['theme'] == 'light'
                        color1 = ('#' + 'b0' * 3, '#' + '2f' * 3)[theme_is_light]
                        color2 = ('#' + '90' * 3, '#' + '5f' * 3)[theme_is_light]
                        text_entry.insert(0.0, date_time_rounding + '\n' + '\n', f'history_{color2}')
                        text_entry.insert(0.0, history_res + '\n', f'history_{color1}')
                        text_entry.insert(0.0, perfect_example + '\n', f'history_{color1}')
                        if too_much_history_data:
                            text_entry.delete(1.0, END)
                            tags = (None, f'history_{color1}', f'history_{color1}', f'history_{color2}')
                            [text_entry.insert(END, val + '\n', tags[(i + 1) % 4]) for i, val in enumerate(history_of_calculations.split('\n'))]
                    except NameError:
                        pass


def insert_values_in_inputs_without_date(new_entry_box_value, new_result_value, date_time_rounding, symbol, new_cursor_index, new_indexes_of_selection, rounding_to='по умолчанию'):
    global example_value, cursor_index, can_backspace, indexes_of_selection
    entry_box.insert(END, new_entry_box_value)
    subbed_new_result_value = re.sub(r' ?\[.+\]', r'', new_result_value)
    
    rounding_in_history = ''
    if str(rounding_to).strip('-').isdigit():
        manual_round_abs = abs(rounding_to)
        num_of_ending_symbols = (0 < manual_round_abs % 10 < 5 and manual_round_abs // 10 != 1) + (manual_round_abs % 10 == 1 and manual_round_abs != 11)
        rounding_in_history = f' ({manual_round_abs} знак{('ов', 'а', '')[num_of_ending_symbols]} {('перед', 'после')[rounding_to > 0]} запятой)'
    
    result.insert(END, f'{symbol}{subbed_new_result_value}{' ' * bool(subbed_new_result_value)}[{date_time_rounding}{rounding_in_history}]')
    
    example_value = entry_box.get().lower()
    cursor_index = entry_box.index('insert')
    indexes_of_selection = new_indexes_of_selection
    if type(new_cursor_index) is int:
        cursor_index = new_cursor_index
        entry_box.icursor(cursor_index)
    if type(indexes_of_selection) is dict:
        entry_box.select_range(*indexes_of_selection.values())
    can_backspace = cursor_index != 0
    
    
def insert_values_in_inputs(new_entry_box_value, new_result_value, date_time_rounding, symbol, new_cursor_index=None):
    global example_value, cursor_index, can_backspace, indexes_of_selection
    entry_box.insert(END, new_entry_box_value)
    date_time_rounding = re.sub(r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})', r'\3.\2.\1-\4:\5:\6', date_time_rounding)
    result.insert(END, f'{symbol}{re.sub(r' ?\[.+\]', r'', new_result_value)} [{date_time_rounding}]')
    
    example_value = entry_box.get().lower()
    cursor_index = entry_box.index('insert')
    if type(new_cursor_index) is int:
        cursor_index = new_cursor_index
        entry_box.icursor(cursor_index)
    can_backspace = cursor_index != 0
    indexes_of_selection = None
    
    value_to_add = [example_value, result.get().strip('='), perfect_example, cursor_index]
    value_to_add_plus = [example_value, clear_space_and_bracks_with_content(result.get().strip('=')) if example_value else '', '', cursor_index, indexes_of_selection if indexes_of_selection else None, settings['round']]
    if add_to_recents(example_value):
        recents['recent examples'].append(['', calculator_greeting, '', 0, '', 'по умолчанию'])
        recents['recent examples'].append(value_to_add)
    if value_to_add_plus != recents['last examples'][-1]:
        recents['last examples'].append(value_to_add_plus)
    if len(recents['last examples']) > 500:
        recents['last examples'].pop(0)
    while len(recents['recent examples']) > 20:
        recents['recent examples'].pop(0)
        
        
def ctrl_y(self):
    global i_history, i_last_example, last_example_value
    last_examples = recents['last examples']
    if i_last_example == 'future':
        return
    i_history = 'future'
    entry_box.delete(0, END)
    result.delete(0, END)
    if i_last_example == 'past':
        i_last_example = 0
        insert_values_in_inputs_without_date(*last_examples[i_last_example][:2], f'{len(last_examples) - (i_last_example + 1)} действи{get_correct_ending(len(last_examples) - (i_last_example + 1), word_ends1)} назад',
                                             get_writing_form(re.sub(r' ?\[.+\]', r'', last_examples[i_last_example][1])), *last_examples[i_last_example][3:6])
    elif i_last_example < len(last_examples) - 2:
        i_last_example += 1
        insert_values_in_inputs_without_date(*last_examples[i_last_example][:2], f'{len(last_examples) - (i_last_example + 1)} действи{get_correct_ending(len(last_examples) - (i_last_example + 1), word_ends1)} назад',
                                             get_writing_form(re.sub(r' ?\[.+\]', r'', last_examples[i_last_example][1])), *last_examples[i_last_example][3:6])
    else:
        i_last_example = 'future'
        solved_example = solve_example(last_example_value)
        insert_values_in_inputs_without_date(last_example_value, solved_example, 'Последний введённый пример', '=' if is_num(solved_example, correct_answer_num_symbols) else ' ' * bool(last_example_value), last_example_cursor, last_example_selection, ROUND_ANSWER_TO_MANUALLY)
    change_width_of_entry(entry_box.get(), entry_box, result)
    config_fg_and_insertbackground()
        
        
def ctrl_z(self):
    global i_history, i_last_example, last_example_value, last_example_cursor, last_example_selection
    last_examples = recents['last examples']
    if i_last_example == 'past':
        return
    i_history = 'future'
    if i_last_example == 'future':
        last_example_cursor = cursor_index
        last_example_selection = indexes_of_selection
    entry_box.delete(0, END)
    result.delete(0, END)
    if i_last_example == 'future':
        last_example_value = example_value
        i_last_example = len(last_examples) - 2
        insert_values_in_inputs_without_date(*last_examples[i_last_example][:2], f'{len(last_examples) - (i_last_example + 1)} действи{get_correct_ending(len(last_examples) - (i_last_example + 1), word_ends1)} назад',
                                             get_writing_form(re.sub(r' ?\[.+\]', r'', last_examples[i_last_example][1])), *last_examples[i_last_example][3:6])
    elif i_last_example > 0:
        i_last_example -= 1
        insert_values_in_inputs_without_date(*last_examples[i_last_example][:2], f'{len(last_examples) - (i_last_example + 1)} действи{get_correct_ending(len(last_examples) - (i_last_example + 1), word_ends1)} назад',
                                             get_writing_form(re.sub(r' ?\[.+\]', r'', last_examples[i_last_example][1])), *last_examples[i_last_example][3:6])
    else:
        i_last_example = 'past'
        insert_values_in_inputs_without_date('Более ранняя история ваших действий не сохранилась!', 'Неизвестно, что было', 'Много действий назад', ' ', None, 'по умолчанию')
    change_width_of_entry(entry_box.get(), entry_box, result)
    config_fg_and_insertbackground()


def ctrl_shift_z(self):
    global i_last_example, i_history, last_example_value
    if i_history == 'past':
        return
    i_last_example = 'future'
    entry_box.delete(0, END)
    result.delete(0, END)
    split_history_of_calculations = history_of_calculations.split('\n')
    if i_history == 'future':
        last_example_value = example_value
        i_history = 0
        insert_values_in_inputs(*split_history_of_calculations[i_history:i_history + 3], '=')
    elif i_history < len(history_of_calculations.split('\n')) - 4:
        i_history += 4
        insert_values_in_inputs(*split_history_of_calculations[i_history:i_history + 3], '=')
    else:
        i_history = 'past'
        insert_values_in_inputs('В этом промежутке времени история вычислений была пустой!', 'Доисторический период', 'Время до первого запуска калькулятора', ' ')
    change_width_of_entry(entry_box.get(), entry_box, result)
    config_fg_and_insertbackground()


def ctrl_shift_y(self):
    global i_last_example, i_history, last_example_value
    if i_history == 'future':
        return
    i_last_example = 'future'
    entry_box.delete(0, END)
    result.delete(0, END)
    split_history_of_calculations = history_of_calculations.split('\n')
    if i_history == 'past':
        i_history = len(split_history_of_calculations) - 4
        if not split_history_of_calculations[i_history]:
            i_history += 1
        insert_values_in_inputs(*split_history_of_calculations[i_history:i_history + 3], '=')
    elif i_history > 3:
        i_history -= 4
        insert_values_in_inputs(*split_history_of_calculations[i_history:i_history + 3], '=')
    else:
        i_history = 'future'
        solved_example = solve_example(last_example_value)
        insert_values_in_inputs(last_example_value, solved_example, 'Последний введённый пример', '=' if is_num(solved_example, correct_answer_num_symbols) else ' ' * bool(last_example_value))
    change_width_of_entry(entry_box.get(), entry_box, result)
    config_fg_and_insertbackground()
    
    
def move_calculator_to_standard_positions():
    global main_win, entry_box, result, last_time_main_win_geometry_change, val_before_last_main_win_geometry_change
    main_win.geometry(f'{WIDTH}x{HEIGHT}+{X_COORD}+{settings['y']}')
    if not re.search(calc_geometry_state_change_expression, result.get()):
        val_before_last_main_win_geometry_change = result.get()
    result.delete(0, END)
    result.insert(END, f'{' ' * bool(example_value)}Калькулятор теперь {('внизу', 'в центре', 'вверху')[place_coords.index(settings['y'])]}')
    last_time_main_win_geometry_change = time.time()
    

def move_up(key):
    setting_y(recents['mid'] if recents['mid'] < settings['y'] else recents['top'])
    move_calculator_to_standard_positions()


def move_down(key):
    setting_y(recents['mid'] if recents['mid'] > settings['y'] else recents['low'])
    move_calculator_to_standard_positions()
    
    
def add_to_last_examples_if_selection_or_cursor_change():
    if 'q' in example_value:
        return
    value_to_add_plus = [example_value, clear_space_and_bracks_with_content(result.get().strip('=')) if example_value else '', '', cursor_index, indexes_of_selection if indexes_of_selection else None, settings['round']]
    if value_to_add_plus != recents['last examples'][-1]:
        recents['last examples'].append(value_to_add_plus)
    if len(recents['last examples']) > 500:
        recents['last examples'].pop(0)
    
    
def set_main_focus(event):
    global can_backspace, indexes_of_selection, cursor_index
    indexes_of_selection = get_selection()
    if main_win.focus_get() == result:
        result_selection = get_selection(result)
        if type(result_selection) is dict and result_selection['start'] != result_selection['end']:
            pyperclip.copy(result.get()[result_selection['start']:result_selection['end']].replace('•', '*').replace('ထ', 'inf').replace('=', ''))
        entry_box.select_range(END, END)
        indexes_of_selection = None
        entry_box.icursor(END)
    entry_box.focus_set()
    cursor_index = entry_box.index('insert') 
    can_backspace = cursor_index != 0
    
    add_to_last_examples_if_selection_or_cursor_change()
    
    
def define_future_of_cursor(side, right_without_ctrls_and_shifts=False):
    replaced_abs_value = replace_abs_signs(example_value)
    temp_cursor_index = max(0, cursor_index)
    if side == 'right':
        i = len(re.match(r'q.*#|q*', replaced_abs_value[temp_cursor_index:])[0])
        if i:
            temp_cursor_index += i
            return temp_cursor_index
        temp_cursor_index += len(re.match(r'(?:[+\-•/:^√= ]|mod|div)*', replaced_abs_value[temp_cursor_index:])[0])
        i = len(re.match(r'(?:\)|u|\])*', replaced_abs_value[temp_cursor_index:])[0])
        temp_cursor_index += i
        if i < 2:
            temp_cursor_index += len(re.match(r'(?:[+\-•/:^√= ]|mod|div)*', replaced_abs_value[temp_cursor_index:])[0])
        if re.match(r'log', replaced_abs_value[temp_cursor_index:]):
            for i in range(3, len(replaced_abs_value[temp_cursor_index:]) + 1):
                if replaced_abs_value[temp_cursor_index:temp_cursor_index + i].count('log') == replaced_abs_value[temp_cursor_index:temp_cursor_index + i].count('by'):
                    break
            temp_cursor_index += i
        temp_cursor_index += len(re.match(r'sin|cos|tg|ctg|ln|lg|by|', replaced_abs_value[temp_cursor_index:])[0])
        if replaced_abs_value[temp_cursor_index:temp_cursor_index + 1] in list('U(['):
            nxt_scope = replaced_abs_value[temp_cursor_index:temp_cursor_index + 1]
            open_brack, closed_brack = nxt_scope, 'u)]'[(nxt_scope == '(') + 2 * (nxt_scope == '[')]
            for i in range(1, len(replaced_abs_value[temp_cursor_index:]) + 1):
                if replaced_abs_value[temp_cursor_index:temp_cursor_index + i].count(open_brack) == replaced_abs_value[temp_cursor_index:temp_cursor_index + i].count(closed_brack):
                    break
            temp_cursor_index += i
            return temp_cursor_index
        temp_cursor_index += len(re.match(r'(?:[φπe]|\d*\.?\d*)?!*', replaced_abs_value[temp_cursor_index:])[0])
        return temp_cursor_index
    
    elif side == 'left':
        i = len(re.search(r'(?:q.*|q?)$', replaced_abs_value[:temp_cursor_index])[0])
        if i:
            temp_cursor_index -= i
            return temp_cursor_index
        temp_cursor_index -= len(re.search(r'(?:[+\-•/:^!= ]|mod|div)*$', replaced_abs_value[:temp_cursor_index])[0])
        i = len(re.search(r'(?:\(|U|\[)*$', replaced_abs_value[:temp_cursor_index])[0])
        temp_cursor_index -= i
        if i < 2:
            temp_cursor_index -= len(re.search(r'(?:[+\-•/:^!= ]|mod|div)*$', replaced_abs_value[:temp_cursor_index])[0])
        if replaced_abs_value[temp_cursor_index - 1:temp_cursor_index] in list('u)]'):
            prv_scope = replaced_abs_value[temp_cursor_index - 1:temp_cursor_index]
            open_brack, closed_brack = 'U(['[(prv_scope == ')') + 2 * (prv_scope == ']')], prv_scope
            for i in range(len(replaced_abs_value[:temp_cursor_index]) - 1, -1, -1):
                if replaced_abs_value[i:temp_cursor_index].count(open_brack) == replaced_abs_value[i:temp_cursor_index].count(closed_brack):
                    break
            temp_cursor_index = i

        else:
            temp_cursor_index -= len(re.search(r'√*(?:[φπe]|\d*\.?\d*)?$', replaced_abs_value[:temp_cursor_index])[0])
            if re.search(r'(?:\(|U|\[|^)-$', replaced_abs_value[:temp_cursor_index]):
                temp_cursor_index -= 1
        temp_cursor_index -= len(re.search(r'(?:sin|cos|tg|ctg|ln|lg|)$', replaced_abs_value[:temp_cursor_index])[0])
        if re.search(r'by$', replaced_abs_value[:temp_cursor_index]):
            for i in range(len(replaced_abs_value[:temp_cursor_index]) - 2, -1, -1):
                if replaced_abs_value[i:temp_cursor_index].count('log') == replaced_abs_value[i:temp_cursor_index].count('by'):
                    break
            temp_cursor_index = i
        if re.search(r'log$', replaced_abs_value[:temp_cursor_index]):
            temp_cursor_index -= 3
        return temp_cursor_index
    
    
def set_cursor_to_the(key, start_or_end_or_num):
    global can_backspace, indexes_of_selection, cursor_index
    if 'q' in example_value:
        return
    make_it_future()
    if type(start_or_end_or_num) is str:
        entry_box.icursor((0, END)[start_or_end_or_num == 'end'])
    else:
        entry_box.icursor(start_or_end_or_num)
    indexes_of_selection = None
    cursor_index = entry_box.index('insert')
    can_backspace = cursor_index != 0
    
    add_to_last_examples_if_selection_or_cursor_change()
    
    
def set_cursor_shift_to_the(key, side_or_num, text_will_be_changed=False):
    global indexes_of_selection, cursor_index
    if 'q' in example_value:
        return
    make_it_future()
    
    if type(side_or_num) is str:
        for i in range(3, 1, -1):
            if entry_box.get()[slice(*((cursor_index - i, cursor_index), (cursor_index, cursor_index + i))[side_or_num == 'right'])] in united_symbols:
                break
        else:
            i = 1
        i = (-i, i)[side_or_num == 'right']
        new_cursor_index = cursor_index + i
    else:
        new_cursor_index = side_or_num
    if new_cursor_index not in range(len(entry_box.get()) + 2):
        new_cursor_index = (cursor_index, 0)[new_cursor_index < 0]
    if type(indexes_of_selection) is not dict:
        entry_box.select_range(*((new_cursor_index, cursor_index) if new_cursor_index < cursor_index else (cursor_index, new_cursor_index)))
    else:
        if new_cursor_index < indexes_of_selection['start']:
            entry_box.select_range(new_cursor_index, indexes_of_selection['end'])
        elif new_cursor_index > indexes_of_selection['end']:
            entry_box.select_range(indexes_of_selection['start'], new_cursor_index)
        else:
            entry_box.select_range(*((indexes_of_selection['start'], new_cursor_index) if new_cursor_index < cursor_index else (new_cursor_index, indexes_of_selection['end'])))
    entry_box.icursor(new_cursor_index)
    cursor_index = entry_box.index('insert')
    indexes_of_selection = get_selection()
    
    if not text_will_be_changed:
        add_to_last_examples_if_selection_or_cursor_change()
    

def set_cursor_shift_to_the_edge(key, start_or_end):
    global indexes_of_selection, cursor_index
    if type(start_or_end) is str:
        new_cursor_index = (0, len(entry_box.get()))[start_or_end == 'end']
    else:
        new_cursor_index = start_or_end
    if type(indexes_of_selection) is not dict:
        indexes_of_selection = {'start': cursor_index, 'end': cursor_index}
    has_edges = indexes_of_selection['start'] == 0 or indexes_of_selection['end'] == len(entry_box.get())
    entry_box.select_range(*((new_cursor_index, indexes_of_selection[('end', 'start')[has_edges]]) if start_or_end == 'start' or new_cursor_index < cursor_index else (indexes_of_selection[('start', 'end')[has_edges]], new_cursor_index)))
    entry_box.icursor(new_cursor_index)
    cursor_index = entry_box.index('insert')
    indexes_of_selection = get_selection()
    
    add_to_last_examples_if_selection_or_cursor_change()
    

def select_all(key):
    global indexes_of_selection, cursor_index
    cursor_index = len(entry_box.get())
    entry_box.select_range(0, cursor_index)
    entry_box.icursor(cursor_index)
    indexes_of_selection = get_selection()
    
    add_to_last_examples_if_selection_or_cursor_change()
 

def copy_text(key):
    global indexes_of_selection, cursor_index, example_value, i_last_example
    if type(indexes_of_selection) is dict:
        if indexes_of_selection['start'] == indexes_of_selection['end']:
            indexes_of_selection = None
        else:
            pyperclip.copy(example_value[indexes_of_selection['start']:indexes_of_selection['end']].replace('•', '*').replace('ထ', 'inf'))
        
        
def cut_text(key):
    global indexes_of_selection, example_value, can_backspace
    if type(indexes_of_selection) is dict and indexes_of_selection['start'] == indexes_of_selection['end']:
        indexes_of_selection = None
    if type(indexes_of_selection) is not dict:
        return
    pyperclip.copy(example_value[indexes_of_selection['start']:indexes_of_selection['end']].replace('•', '*').replace('ထ', 'inf'))
    change_text('')


def paste_text(key):
    global indexes_of_selection, cursor_index, can_backspace, example_value
    if indexes_of_selection is None:
        indexes_of_selection = {'start': cursor_index, 'end': cursor_index}
    
    replaced_paste = pyperclip.paste()
    
    if re.search(r'2\d\d\d\.(?:0\d|11|12)\.(?:[0-3]\d|31) (?:[01]\d|2[0-3])(?::[0-5]\d){2}', replaced_paste):
        # Алгоритм замены для истории
        replaced_paste = re.sub(r'\n', '&', replaced_paste)
        replaced_paste = re.sub(r' ', '#', replaced_paste)
        replaced_paste = re.sub(r'\s', '', replaced_paste)
        replaced_paste = re.sub(r'&&', ', ', replaced_paste)
        
        replaced_paste = re.sub(r'&(2\d\d\d\.(?:0\d|11|12)\.(?:[0-3]\d|31))#((?:[01]\d|2[0-3])(?::[0-5]\d){2})(?:#(\(\d{1,2})#(знак(?:|а|ов))#(перед|после)#(запятой\)))?', r' [\1 \2 \3 \4 \5 \6]', replaced_paste).replace(4 * ' ', '')
        replaced_paste = ', '.join((i.replace('&', '=', 1) for i in replaced_paste.split(', ')))
        replaced_paste = replaced_paste.replace('&', ' ')
        replaced_paste = re.sub(r'#', '', replaced_paste)
    else:
        replaced_paste = re.sub(r' ', '#', replaced_paste)
        replaced_paste = re.sub(r'\s', '', replaced_paste)
        replaced_paste = re.sub(r'#', ' ', replaced_paste)
        if not re.search(r'[а-яА-ЯЁё]', replaced_paste):
            replaced_paste = re.sub(r' {2,}', r' ', replaced_paste.replace('÷', '/').replace(':', '/').replace('//', 'div').replace('%', 'mod'))
        replaced_paste = re.sub(r'(\d)√', r'\1•√', replaced_paste)
    
    if not re.search(r'[а-яА-ЯЁё]', replaced_paste):
        replaced_paste = replaced_paste.replace('x', '•').replace('*', '•').replace('inf', 'ထ').replace('∞', 'ထ').replace('–', '-').replace('–', '-').replace('×', '•').replace(' ', ' ')
    
    change_text(replaced_paste)
    
def change_text(pasted, start=None, end=None):
    global indexes_of_selection, cursor_index, can_backspace, example_value
    
    make_it_future()
    if start is None:
        start = indexes_of_selection['start']
    if end is None:
        end = indexes_of_selection['end']
    example_value = example_value[:start] + pasted + example_value[end:]
    cursor_index = start + len(pasted)
    indexes_of_selection = None
    can_backspace = cursor_index != 0
    key_calc((cursor_index, end))
    
    add_to_last_examples_if_selection_or_cursor_change()
    
    
def change_selection_colors_to_normal(theme_is_light):
    entry_box.config(insertbackground=('#e0e0e0', '#1f1f1f')[theme_is_light])
    result.config(insertbackground=entry_box.cget('insertbackground'))
    entry_box.config(selectforeground=entry_box.cget('fg'), selectbackground=('#' + '50' * 3, '#' + 'ab' * 3)[theme_is_light])
    result.config(selectforeground=entry_box.cget('fg'), selectbackground=entry_box.cget('selectbackground'))
    
    
def change_selection_colors_to_invisible():
    fg, bg = entry_box.cget('fg'), entry_box.cget('bg')
    entry_box.config(insertbackground=bg)
    result.config(insertbackground=bg)
    entry_box.config(selectforeground=fg, selectbackground=bg)
    result.config(selectforeground=fg, selectbackground=bg)
    
    
def save_index(event):
    if not ((event.state & 0x0001) or (event.state & 0x0002) or (event.state & 0x0003)):  # не (левая кнопка (Button1) или средняя кнопка (Button2) или правая кнопка (Button3) мыши зажата)
        recents['cursor before moving calc'] = entry_box.index('insert')
    
    
def on_pushing_left_button(event):
    recents['mouse coords'] = {'x': event.x_root, 'y': event.y_root}
    
    
def on_freeing_left_button(event):
    global indexes_of_selection, cursor_index
    if recents['mouse coords']['x'] == -2:
        indexes_of_selection, cursor_index = None, recents['cursor before moving calc']
        entry_box.select_range(*[cursor_index for _ in range(2)])
        entry_box.icursor(cursor_index)
        pyautogui.hotkey('shift', '4')
        change_selection_colors_to_normal(settings['theme'] == 'light')
    set_main_focus(event)
    recents['cursor before moving calc'] = entry_box.index('insert')
    
    
def move_main_win(event):
    global indexes_of_selection, cursor_index
    x, y, pre_x, pre_y = event.x_root, event.y_root, *recents['mouse coords'].values()
    if pre_x not in (-1, -2):
        if (pre_y - y) ** 2 + (pre_x - x) ** 2 < (HEIGHT // 2) ** 2:
            return
        recents['mouse coords'] = {'x': -1, 'y': -1} if x != pre_x and abs((y - pre_y) / (x - pre_x)) < 2.7 else {'x': -2, 'y': -2}
        pre_x, pre_y = recents['mouse coords'].values()
    if pre_x == -1:
        return
    y_coord = event.y_root - HEIGHT // 2
    if y_coord < 0:
        y_coord = 0
    if y_coord > MAX_COORD:
        y_coord = MAX_COORD
    setting_y(y_coord)
    main_win.geometry(f'{WIDTH}x{HEIGHT}+{X_COORD}+{y_coord}')
    change_selection_colors_to_invisible()
    entry_box.focus_set()
    result.delete(0, END)
    result.insert(END, f'{' ' * bool(entry_box.get())}y={y_coord}')
    
    
def has_selection():
    return indexes_of_selection and indexes_of_selection['start'] != indexes_of_selection['end']
    

main_win.bind('<Control-a>', select_all)
main_win.bind('<Control-A>', select_all)
main_win.bind('<Control-c>', copy_text)
main_win.bind('<Control-C>', copy_text)
main_win.bind('<Control-x>', cut_text)
main_win.bind('<Control-X>', cut_text)
main_win.bind('<Control-v>', paste_text)
main_win.bind('<Control-V>', paste_text)
main_win.bind('<Shift-Up>', lambda key: set_cursor_shift_to_the_edge(key, 'start'))
main_win.bind('<Shift-Down>', lambda key: set_cursor_shift_to_the_edge(key, 'end'))
main_win.bind('<Control-Shift-Left>', lambda key: set_cursor_shift_to_the(key, define_future_of_cursor('left')))
main_win.bind('<Control-Shift-Right>', lambda key: set_cursor_shift_to_the(key, define_future_of_cursor('right')))
main_win.bind('<Shift-Left>', lambda key: set_cursor_shift_to_the(key, 'left'))
main_win.bind('<Shift-Right>', lambda key: set_cursor_shift_to_the(key, 'right'))
main_win.bind('<Up>', lambda key: set_cursor_to_the(key, 'start'))
main_win.bind('<Down>', lambda key: set_cursor_to_the(key, 'end'))
main_win.bind('<Control-Left>', lambda key: set_cursor_to_the(key, define_future_of_cursor('left')))
main_win.bind('<Control-Right>', lambda key: set_cursor_to_the(key, define_future_of_cursor('right')))
main_win.bind('<Control-BackSpace>', lambda key: change_text('', define_future_of_cursor('left'), cursor_index) if not has_selection() else cut_text(key))
main_win.bind('<Control-Delete>', lambda key: change_text('', cursor_index, define_future_of_cursor('right')) if not has_selection() else cut_text(key))
main_win.bind('<Control-Shift-y>', ctrl_shift_y)
main_win.bind('<Control-Shift-z>', ctrl_shift_z)
main_win.bind('<Control-Shift-Y>', ctrl_shift_y)
main_win.bind('<Control-Shift-Z>', ctrl_shift_z)
main_win.bind('<Control-y>', ctrl_y)
main_win.bind('<Control-z>', ctrl_z)
main_win.bind('<Control-Y>', ctrl_y)
main_win.bind('<Control-Z>', ctrl_z)
main_win.bind('?', lambda key: create_added_win('?'))
main_win.bind('<Control-slash>', lambda key: create_added_win('?'))
main_win.bind('<Control-h>', lambda key: create_added_win('h'))
main_win.bind('<Control-H>', lambda key: create_added_win('h'))
main_win.bind('<Control-space>', lambda key: (pyautogui.hotkey('Alt', 'Tab'), time.sleep(0.05), pyautogui.press('Enter')))
main_win.bind('<Control-s>', save_example_to_history)
main_win.bind('<Control-S>', save_example_to_history)

main_win.bind('<Motion>', save_index)

main_win.bind('<ButtonRelease-1>', on_freeing_left_button)
main_win.bind('<ButtonRelease-2>', set_main_focus)
main_win.bind('<ButtonRelease-3>', set_main_focus)

main_win.bind('<ButtonPress-1>', on_pushing_left_button)
main_win.bind("<B1-Motion>", move_main_win)

main_win.bind('<Control-Shift-Up>', move_up)
main_win.bind('<Control-Shift-Down>', move_down)

main_win.bind('<Control-Key>', lambda key: None)  # не удалять! поддерживает автономию перед <Key>
main_win.bind('<Alt-Key>', lambda key: None)  # не удалять! поддерживает автономию перед <Key>
main_win.bind('<Key>', real_key_calc)

main_win.bind('<Control-equal>', lambda key: change_size_of_everything(scale=min(settings['scale'] + 1, 5), scale_was_zero=HEIGHT <= screen_width // 180))
main_win.bind('<Control-minus>', lambda key: change_size_of_everything(scale=max(settings['scale'] - 1, 1), scale_was_zero=HEIGHT <= screen_width // 180))
main_win.bind('<Control-Up>', lambda key: change_size_of_everything(**(({'scale': 0} if HEIGHT > screen_width // 180 else {'scale': settings['scale'], 'scale_was_zero': True}) | {'change_result': False})))
main_win.bind('<Control-Down>', lambda key: change_size_of_everything(**(({'scale': 0} if HEIGHT > screen_width // 180 else {'scale': settings['scale'], 'scale_was_zero': True}) | {'change_result': False})))


def on_enter(event):
    global keyboard_layout_memory
    keyboard_layout_memory = ('en', 'ru')[is_russian_layout()]
    entry_box.config(bg=('#' + '27' * 3, '#' + 'e2' * 3)[settings['theme'] == 'light'])
    result.config(bg=entry_box.cget('bg'))
    change_width_of_entry(entry_box.get(), entry_box, result)
    
    
def on_leave(event):
    if main_win.focus_get() not in (main_win, entry_box, result):
        entry_box.config(bg=('#' + '1f' * 3, '#' + 'ea' * 3)[settings['theme'] == 'light'])
        result.config(bg=entry_box.cget('bg'))
    
    
def focus_in(event):
    if is_russian_layout():
        hwnd = user32.GetForegroundWindow()
        user32.PostMessageW(hwnd, 0x50, 0, user32.LoadKeyboardLayoutW("00000409", 0x1))
    main_win['bg'] = ('#' + '4f' * 3, '#' + 'a0' * 3)[settings['theme'] == 'light']
    entry_box.config(bg=('#' + '27' * 3, '#' + 'e2' * 3)[settings['theme'] == 'light'])
    result.config(bg=entry_box.cget('bg'))
    change_size_of_everything(scale=settings['scale'], scale_was_zero=True, change_result=False)
    config_fg_and_insertbackground()
    
    
def focus_out(event):
    global keyboard_layout_memory
    if not is_russian_layout() and keyboard_layout_memory == 'ru':
        hwnd = user32.GetForegroundWindow()
        user32.PostMessageW(hwnd, 0x50, 0, user32.LoadKeyboardLayoutW("00000419", 0x1))
    entry_box.config(bg=('#' + '1f' * 3, '#' + 'ea' * 3)[settings['theme'] == 'light'])   
    result.config(bg=entry_box.cget('bg'))
    change_width_of_entry(entry_box.get(), entry_box, result)


main_win.bind('<FocusOut>', focus_out)
main_win.bind('<FocusIn>', focus_in)
main_win.bind('<Enter>', on_enter)
main_win.bind('<Leave>', on_leave)


def close_main_win():
    global added_win
    if added_win.winfo_viewable() and added_win.title() == 'инструкция':
        create_added_win('h')
        manage_not_main_window_close()
    elif added_win.winfo_viewable():
        manage_not_main_window_close()
    else:
        recents['win theme alike calc'] = is_dark_theme() == (settings['theme'] == 'dark')
        recents['example before closing'] = example_value   
        recents['cursor before closing'] = cursor_index
        recents['closing time'].append(time.time())
        recents['closing time'].pop(0)
        rewrite_json('history')
        rewrite_json('settings')
        rewrite_json('recents')
        main_win.destroy()
        

def config_fg_and_insertbackground():
    theme_is_light = settings['theme'] == 'light'
    entry_box.config(fg=('#' + 'd0' * 3, '#' + '0f' * 3)[theme_is_light] if example_value not in ('ထ', '+ထ', '-ထ') else ('#b0b054', '#3f3f8b')[theme_is_light])
    result.config(fg=('#' + 'b0' * 3, '#' + '2f' * 3)[theme_is_light] if example_value not in ('ထ', '+ထ', '-ထ') else ('#909054', '#5f5f9b')[theme_is_light])
    
    if result.get() == calculator_greeting or modify_info(entry_box.get()) is not None:
        result.config(fg=('#' + '70' * 3, '#' + '6f' * 3)[theme_is_light])
    elif not is_num(result.get().replace('=', ''), correct_answer_num_symbols) and example_value not in ('ထ', '+ထ', '-ထ'):
        result.config(fg=('#' + 'a8' * 3, '#' + '37' * 3)[theme_is_light])
    change_selection_colors_to_normal(theme_is_light)
        

def change_theme(event):
    theme_is_light = settings['theme'] == 'light'
    settings['theme'] = ('light', 'dark')[theme_is_light]
    
    added_win_in_focus, text_entry_in_focus = False, False
    if added_win.title() != invisible_win_title:
        scroll_pos = text_entry.yview()[0]
        cursor_pos = text_entry.index(INSERT)
        start_sel, end_sel = (text_entry.index(SEL_FIRST), text_entry.index(SEL_LAST)) if text_entry.tag_ranges(SEL) else (cursor_pos, cursor_pos)
        
        added_win_in_focus, text_entry_in_focus = main_win.focus_get() == added_win, main_win.focus_get() == text_entry
    
    selected = recents['last examples'][-1][4]
    focus_in(event)
    create_added_win((None, 'h', '?')[(added_win.title() == 'история') + (added_win.title() == 'инструкция') * 2])
    
    # Важно для не смены курсора и самого примера
    entry_box.delete(0, END)
    entry_box.insert(END, example_value)
    entry_box.icursor(cursor_index)
    # конец коммента важности
    
    if selected:
        entry_box.select_range(*selected.values())
    
    if not (added_win_in_focus or text_entry_in_focus):
        entry_box.focus_set()
    else:
        text_entry.yview_moveto(scroll_pos)
        if added_win_in_focus or text_entry_in_focus:
            added_win.focus_force()
        if text_entry_in_focus:
            text_entry.focus_force()
        text_entry.mark_set(INSERT, cursor_pos)
        text_entry.tag_add(SEL, start_sel, end_sel)
        
        
def unbind_left_button():
    entry_box.unbind('<ButtonPress-1>')
    entry_box.unbind('<B1-Motion>')
    entry_box.bind('<ButtonPress-1>', on_pushing_left_button)
    entry_box.bind('<B1-Motion>', move_main_win)
    
    
def bind_left_button():
    entry_box.unbind('<ButtonPress-1>')
    entry_box.unbind('<B1-Motion>')
    entry_box.bind('<ButtonPress-1>', disable_left_mouse_button_clicking)
    entry_box.bind("<B1-Motion>", disable_left_mouse_button_clicking)
        

def check_theme_or_geometry_change():
    global last_theme, example_value, indexes_of_selection
    current = is_dark_theme()
    if current != last_theme:
        last_theme = current
        if (settings['theme'] == 'dark'):
            set_focus_from_not_my_application()
            change_theme(None)
            pyautogui.hotkey('ctrl', 'space')
    res_val, entry_val = result.get(), entry_box.get()
    if time.time() - last_time_main_win_geometry_change > 1.6 and re.search(calc_geometry_state_change_expression, res_val):
        result.delete(0, END)
        result.insert(END, val_before_last_main_win_geometry_change)
    elif time.time() - last_time_round_change > (10 if recents['rounding info longer'] > 0 else 0.8) and 'q' in entry_val:
        if recents['rounding info longer'] > 0:
            recents['rounding info longer'] -= 1
        if has_selection():
            pyautogui.press('right' if cursor_index == get_selection()['start'] else 'left')
        if 'q' in entry_val and main_win.focus_get() == entry_box:
            pyautogui.hotkey('ctrl', 'backspace')
            main_win.after(20, unbind_left_button)
            example_value = entry_box.get()
    main_win.after(100, check_theme_or_geometry_change)  # проверять каждую десятую секунды
last_theme = is_dark_theme()
check_theme_or_geometry_change()
        
        
if recents['win theme alike calc'] and is_dark_theme() != (settings['theme'] == 'dark'):
    change_theme(None)
    

main_win.bind('<Control-t>', change_theme)
main_win.bind('<Control-T>', change_theme)

calculate_result()

if time.time() - recents['closing time'][-1] > 15:
    change_text('', 0, len(entry_box.get()))
    ROUND_ANSWER_TO_MANUALLY = settings['round'] = 'по умолчанию'

main_win.mainloop()
