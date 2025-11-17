import winreg
import pyautogui
import ctypes
import re

from decimal import *

FILES = 'data'
DAY = 60 * 60 * 24

getcontext().prec = 1402
def zeros(x):
    return Decimal('.' + x * '0') if x > 0 else Decimal(f'1e{abs(x)}')

def rond(num, rounding_accuracy):
    return num.quantize(rounds[rounding_accuracy], ROUND_HALF_UP)

invisible_win_title = 'невидимое окно'
temp_scopes, temp_scopes_with_smth = r'(?:\(-?\)|U-?u)', r'(?:\(.*?\)|U.*?u)'
calc_geometry_state_change_expression = r'Максимум \d+ символ(?:|а|ов)|Калькулятор теперь (?:вверху|в центре|внизу)'
pattern_checking_on_empty_scopes = fr'(?:[+\-/•:^√]|mod|div)*(?:(?:sin|cos|tg|ctg|lg|ln){temp_scopes}|log{temp_scopes}by{temp_scopes_with_smth}|log{temp_scopes_with_smth}by{temp_scopes}|{temp_scopes})'

united_symbols = ('log', 'div', 'mod', 'sin', 'cos', 'ctg') + ('ln', 'lg', 'tg', 'by')
united_symbols_with_scopes = ('log(', 'sin(', 'cos(', 'ctg(', ')by(') + ('ln(', 'lg(', 'tg(') + ('log|', 'sin|', 'cos|', 'ctg|', '|by|', '|by(', ')by|') + ('ln|', 'lg|', 'tg|')
united_symbols_without_scopes = ('sin', 'cos', 'tg', 'ctg', 'ln', 'lg')
full_funcs_with_Uu = tuple((f'{i}{j}' for i in ('sin', 'cos', 'tg', 'ctg', 'lg', 'ln') for j in ('()', 'Uu'))) + tuple((f'log{i}by{j}' for i in ('()', 'Uu') for j in ('()', 'Uu')))

special_keys = ('Up', 'Down', 'Left', 'Right', 'Control_L', 'Return', 'grave', 'Tab', 'changed text', 'Win_L'
                'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Escape', 'Caps_Lock', 'apostrophe', 'quotedbl', 'braceleft', 'braceright')
ghost_keys = ('Up', 'Down', 'Left', 'Right', 'Control_L', 'Control_R', 'Shift_L', 'Shift_R', 'Alt_L', 'Alt_R', 'Caps_Lock')
keys_after_dot = ('minus', 'equal', 'slash', 'semicolon', 'backslash', 'bracketleft', 'bracketright')
last_key = None

rounds = [zeros(_) for _ in (400, 380, 360, 305, 100)]
ending_symbols = list('+-•:^,%@k.') + list(united_symbols)
correct_answer_num_symbols = '0123456789Ee-+.•^() '
last_time_main_win_geometry_change = 0
last_val_before_geometry_change = 'если это вставится, значение использовали до его определения !!!техническая ошибка разработчиков!!!'
last_time_round_change = 0

max_denominator = 10000

max_history_length, min_history_length = 10000, 100
word_ends1 = ('е', 'я', 'й')
word_ends2 = ('', 'а', 'ов')


def clear_q_with_content(example, cursor_place):
    return re.sub(r'(?:q.*|q?)$', '', example[:cursor_place]) + example[cursor_place:]


def clear_space_and_bracks_with_content(example):
    return re.sub(r' ?\[.*\]', '', example)


def get_correct_ending(num, word_endings):
    if num % 10 in [0, 5, 6, 7, 8, 9] or num % 100 in [11, 12, 13, 14]:
        return word_endings[2]
    elif num % 10 == 1:
        return word_endings[0]
    else:
        return word_endings[1]
    

text_help_calc = ("  строка-калькулятор | быстрый ввод • мгновенное вычисление • точный ответ\n\n"
                  "Приоритет операций, быстрые клавиши для их вызова (чтобы лишний раз не нажимать shift) и ассоциации к запоминанию\n"
                  " .0. Константы: π≈3.14 [p] (pi), e≈2.718 [e], φ≈1.618 [f] (fi); десятичная дробь [.] [,]\n"
                  " .1. Скобки: () [[] или o] (скобки – 'o', разбитое пополам); модуль: | [\\] [a] (от англ. abs – модуль)\n"
                  " .2. Факториал от числа x: x! [i] (факториал – перевернутый i)\n"
                  " .3. Корень: √ [r] (root – корень), N√M=N^(1/M), не путать с N•√M\n"
                  " .4. Логарифмы: logAbyB [l], ln [n], lg [g], by [b]. Тригонометрия: sin [s]; cos [c]; tg [t]; ctg [k] ('k' созвучна 'c')\n"
                  " .5. Степень: ^ [w] [xx] ('^' (/\\) – 'w' (\\/\\/) без краёв)\n"
                  " .6. Умножение: • [x]; деление: [/]; остаток от деления: mod [m] [%]; деление нацело: div [d] [//]\n"
                  " .7. Сложение: + [=]; вычитание: [-]\n"
                  "\nУправление окнами и копированием\n"
                  " ● '?' или ctrl+/ — инструкция (помощь), ctrl+h — последние примеры (история)\n"
                  " ● ctrl+пробел переключает фокус между калькулятором-строкой и окном, которое у тебя перед глазами\n"
                  " ● [esc], ctrl+w закрывают окно в фокусе приложения.\n"
                  " ● [`] (где [ё]) очищает поле ввода, ['] копирует пример в буфер обмена, [\"] копирует ответ\n"
                  " ● [enter] заменяет пример в поле ввода на ответ\n"
                  " ● enter, ['], [\"], ctrl+s, либо первое удаление числа после ввода примера добавляет пример в историю\n"
                  " ● ctrl+↑, ctrl+↓, ctrl+alt+↑, ctrl+alt+↓ прокручивают историю\n"
                  " ● ctrl+shift+z перемещает на один пример в прошлое, ctrl+shift+y — в будущее\n"
                  " ● ctrl+z перемещает на одно действие назад, ctrl+y — вперёд\n"
                  " ● При вставке текста из истории или других источников, он форматируется под строку или другое окно на уровне символов\n"
                  "\nРедактирование поля ввода (условимся, что 'I' — это курсор, или каретка)\n"
                  " ⬥ При стирании '•√I' через [⌫] после нажатия [r] останется '√I'\n"
                  " ⬥ '/100' [P] (percent — процент), '•10^' [E] (2•10^5 кратко 2e5), [;] пишет '(1/I)' и [.] пишет '0.', если перед курсором не цифра\n"
                  " ⬥ '^2' [u] (похожа на график x^2), '^3' [j] (на клавиатуре похожа на x^3), '^4' [U] (x^4), '^(-I)' [y]\n"
                  " ⬥ поставит 3 нуля [z] (zeros — нули), 6 [M] (million), 9 [B] (billion), 12 [T] (trillion), 15 [Q] (quadrillion)\n"
                  " ⬥ при [цифра] после '0' введётся '.' с цифрой, при [z M B T Q] после '.' введётся на одну '0' меньше, после '0' тоже самое с '.' впереди\n"
                  " ⬥ [v] вводит длиннейшую повторяющуюся последовательность без чисел или констант на концах; [V] — 2-ю по количеству символов\n"
                  " ⬥ '•' ставится автоматически. При 'I' после 'π' или '1', '(' после '!' появится '/' (удобно вводить радианы 'k•π/m' и сочетание 'n!/(k!•(n-k)!)')\n"
                  " ⬥ '•' не ставится при [|], только с [a], так как пример можно понять по-разному ('|5+5|7+8|2+2|', как '|5+5|•7+8•|2+2|' или '|5+5•|7+8|•2+2|')\n"
                  " ⬥ После любого знака или в начале строки [•] введёт '2•', [/] — '1/' (кроме случаев: после '•' — '/2', после '√' — '/3')\n"
                  " ⬥ если [+] после '•', '/', '^', '√', то он будет вводиться с '2', иначе заменится на '1'; после '.' поставить любой знак, кроме [.] и появится '5'\n"
                  "\nЛайфхаки и преимущества!\n"
                  " ★ Быстрый ввод примера, точные тригонометрические и логарифмические вычисления\n"
                  " ★ Считает даже выражения вида (-32)^(3/5), (-5.2)!, (-11)mod(-3), log(4)by(-2)\n"
                  " ★ Учёт недостающих символов '2+2)•3•|1+1' → '(2+2)•3•|1+1|', очищенный пример от лишних скобок в истории '(|(2+2)|•3' → '|2+2|•3'\n"
                  " ★ Автоматичское добавление необходимых знаков при вводе примера\n"
                  " ★ Раскладка меняется на английскую на время фокусировки на приложении, потом возвращается на предыдущую\n"
                  " ★ Много подсказок: калькулятор, не считавший примеры 2 недели, подскажет, как открыть инструкцию применения\n"
                  " ★ Открой строку за 15 секунд после закрытия и пример останется. Иначе перейдёт в историю, если в ответе не число — удалится\n"
                  "\nНастройки и вид\n"
                  " ⚙ Размещение. Перетаскивай калькулятор мышкой, комбинациями ctrl+shift+↑↓ или написанием 'y#', '-y#' (y — отступ сверху, -y снизу)\n"
                  " ⚙ Низ экрана: '1-#' или '-#', при 'y' от 0 до 1 не включительно, это число высот экрана, а не пикселей, 'y' можно писать примерами: '4^2/7#'\n"
                  " ⚙ Округление. По умолчанию: пиши где угодно в примере q, до нужного знака: qA (A от -23 до 17) и оно подействует через секунду\n"
                  " ⚙ Настрой размер памяти истории, вводя hx#, где x — максимальное число примеров\n"
                  " ⚙ Меняй тему со светлой на тёмную, с тёмной на светлую через ctrl+t (theme)\n"
                  " ⚙ Увеличивай и уменьшай текст комбинациями [ctrl]+[±], разворачивай и сворачивай строку комбинациями ctrl+↑↓\n"
                  "\nПредупреждения и ограничения\n"
                  f" ❗ Для тригонометрических функций сокращения рациональных дробей со знаменателем менее {max_denominator} — градусы, остальное — радианы\n"
                  " ❗ Если модуль ответа не находится в диапазоне от 10^(-285) до 10^995 и при этом не равен нулю, вычисление не точно\n"
                  " ❗ Если калькулятор закрылся на более, чем 15 секунд, округляется всё снова по умолчанию\n"
                  " ❗ Приложение не даст вам открыть более 1 дополнительного окна во избежание бардака\n"
                  " ❗ 2^2^2^2=2^2^4=2^16=65536, 3k3k19683=3k27=3, -A^(-B)≠(-A)^(-B), √A!=√(A!)\n"
                  " ❗ Знак умножить писать обязательно: нельзя 5sin90, можно 5•sin90\n"
                  " ❗ Округлять можно от 23 знаков перед запятой до 17 знаков после")


def is_dark_theme():
    # Путь к ключу реестра, где хранятся настройки темы
    registry_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    value_name = "AppsUseLightTheme"  # Значение, которое определяет светлую или тёмную тему

    try:
        # Открываем ключ реестра
        registry_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, registry_path)
        
        # Читаем значение
        value, _ = winreg.QueryValueEx(registry_key, value_name)
        
        # Закрываем ключ
        winreg.CloseKey(registry_key)
        
        # Если значение 0, то тема тёмная, иначе светлая
        return value == 0
    except FileNotFoundError:
        # Если ключ или значение не найдены, предполагаем светлую тему (или обработайте ошибку по-другому)
        return False

# --------------------
screen_width, screen_height = pyautogui.size()

# Получить высоту панели задач
def get_taskbar_height():
    SPI_GETWORKAREA = 48
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    taskbar_height = screen_height - (rect.bottom - rect.top)
    return taskbar_height


class FakeWindow():
    def focus_get(self):
        return
    
    def focus_set(self):
        pass
    
    def destroy(self):
        pass
    
    def winfo_viewable(self):
        return False
    
    def title(self):
        return invisible_win_title
    
    def wm_state(self):
        return 'iconic'


def is_russian_layout() -> bool:
    """
    Проверяет, активна ли русская раскладка клавиатуры в текущем окне.
    Возвращает True для русской раскладки, False для остальных случаев.
    """
    user32 = ctypes.windll.user32
    
    # Получаем дескриптор активного окна и его поток
    hwnd = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(hwnd, None)
    
    # Получаем идентификатор раскладки клавиатуры
    keyboard_layout = user32.GetKeyboardLayout(thread_id)
    language_id = keyboard_layout & 0xFFFF  # Извлекаем младшие 16 бит
    
    # Русская раскладка имеет код 0x0419
    return language_id == 0x0419


keyboard_layout_memory = ('en', 'ru')[is_russian_layout()]