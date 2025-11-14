from info import rond, max_denominator
import re
from decimal import *
from functools import lru_cache, wraps
from mpmath import mp
getcontext().prec = 1402
mp.dps = 402


def classmethod_with_cache(func):
    func = lru_cache()(func)
    
    @wraps(func)    
    def wrapper(cls, *args, **kwargs):
        return func(cls, *args, **kwargs)
    
    return classmethod(wrapper)


@lru_cache
def replace_abs_signs(val):
    val = f'({val})'
    for i in range(len(val) - 1):
        if val[i + 1] == '|':
            val = val[:i + 1] + 'Uu'[val[i] in '0123456789!)uπφe'] + val[i + 2:]
    return val[1:-1]


class C:
    e = Decimal('2.7182818284590452353602874713526624977572470936999595749669676277240766303535475945713821785251664274274663919320030599218'
                '1741359662904357290033429526059563073813232862794349076323382988075319525101901157383418793070215408914993488416750924476146'
                '06680822648001684774118537423454424371075390777449920695517027618386062613313845830007520449338265602976067371132007093287091'
                '27443747047230696977209310141692836819025515108657463772111252389784425056953696770785449969967946864454905987931636889230098')
    
    pi = Decimal('3.141592653589793238462643383279502884197169399375105820974944592307816406286208998628034825342117067982148086513282306647'
                 '093844609550582231725359408128481117450284102701938521105559644622948954930381964428810975665933446128475648233786783165'
                 '271201909145648566923460348610454326648213393607260249141273724587006606315588174881520920962829254091715364367892590360'
                 '011330530548820466521384146951941511609433057270365759591953092186117381932611793105118548074462379962749567351885752724')
    
    fi = Decimal('1.6180339887498948482045868343656381177203091798057628621354486227052604628189024497072072041893911374'
                 '847540880753868917521266338622235369317931800607667263544333890865959395829056383226613199282902678806752'
                 '087668925017116962070322210432162695486262963136144381497587012203408058879544547492461856953648644492410')
    
    @classmethod_with_cache
    def factorial(cls, num):
        num = Decimal(num)
        if num < 0 and rond(num, 3) % 1 == 0:
            return f'Факториал целого отрицательного числа смысла не имеет! (±ထ)'
        return Decimal(str(mp.factorial(num)))
        
    @classmethod_with_cache
    def pow(cls, num, power, power_type):
        num, power = Decimal(num), Decimal(power)
        if power_type == '^-':
            power = -power
        if power < 0:
            if type(power_result := cls.pow(num, -power, power_type[0])) is str:
                return power_result
            return rond(1 / power_result, 2)
        if power_type == 'k':
            power = rond(1 / Decimal(power), 0)
        if num >= 0 or rond(power, 1) % 1 == 0:
            return rond(Decimal(str(mp.power(num, power))), 0)
        for odd_num in range(4999, 10000, 2):
            reversed_pow = 1 / Decimal(odd_num)
            rounded_reversed_pow = rond(reversed_pow, 1)
            maybe_num_about_zero = rond(power, 1) % rounded_reversed_pow
            if rond(maybe_num_about_zero, 2) == 0:
                num = rond(Decimal(-(abs(num) ** reversed_pow)), 1)
                power = (power / rounded_reversed_pow).quantize(Decimal('0'), ROUND_HALF_UP)
                res = num ** power
                return f'Результат вычисления {'степени' if power_type != 'k' else 'корня'} крайне неточен, поскольку результат числа слишком небольшой!' if res == 0 and num != 0 else res
        else:
            return 'Чётный, дробный или слишком большой знаменатель у степени числа!' if power_type != 'k' else 'Нет решения среди действительных чисел, либо слишком большой числитель или степень у корня числа!'
        
    @classmethod_with_cache
    def radical(cls, num, power):
        num, power = Decimal(num), Decimal(power)
        if num >= 0:
            return Decimal(str(mp.power(num, 1 / power)))
        elif rond(abs(power), 1) % 2 == 1 and num < 0:
            return rond(-Decimal(str(mp.root(abs(num), power))), 0)
        else:
            return C.pow(num, power, power_type='k')
    
    @classmethod_with_cache
    def log(cls, num_by_log, base):
        num_by_log, base = Decimal(num_by_log), Decimal(base)
        
        base_rond1, num_by_log_rond1 = rond(base, 1), rond(num_by_log, 1)
        if base_rond1 in (-1, 0, 1):
            return f'Не существует логарифма по основанию {int(rond(base, 1))} (бесконечное, либо пустое множество)!'
        if abs(abs(base_rond1) - 1) < 10 ** -20:
            return 'Поскольку основание логарифма слишком близко к единице ответ сильно неточный!'
        if num_by_log_rond1 == 0:
            return 'Не существует логарифма, если логарифмируемое число – ноль!'
        if abs(num_by_log) > 10 ** 1001 or abs(num_by_log) < 10 ** -305:
            return 'Слишком большое или маленькое логарифмируемое число логарифма!'
        if abs(base) > 10 ** 1001 or abs(base) < 10 ** -305:
            return 'Слишком большое или маленькое основание логарифма!'
        if base_rond1 > 0 and num_by_log_rond1 < 0:
            return 'Логарифм отрицательного числа по положительному основанию невозможен!'
        log_result_if_both_args_positive = Decimal(str(mp.log(abs(num_by_log)) / mp.log(abs(base))))
        log_result_if_both_args_positive_rond4 = rond(log_result_if_both_args_positive, 4)
        if base_rond1 < 0 and num_by_log_rond1 < 0 and abs(log_result_if_both_args_positive_rond4 % 2) != 1:
            return 'Логарифм числа меньше нуля по основанию меньше нуля может вернуть только нечётное число!'
        if base_rond1 < 0 and num_by_log_rond1 > 0 and log_result_if_both_args_positive_rond4 % 2 != 0:
            return 'Логарифм числа больше нуля по основанию меньше нуля может вернуть только чётное число!'
        return log_result_if_both_args_positive if base_rond1 > 0 and num_by_log_rond1 > 0 else log_result_if_both_args_positive_rond4
    
    @classmethod
    def is_deg(cls, angle):
        return '.' not in angle or len(angle.split('.')[-1]) < 10 or bool(re.findall(r'(\d+)\1{7}', angle.split('.')[-1][:100]))
    
    @classmethod_with_cache
    def rad_to_deg(cls, angle):
        if cls.is_deg(angle):
            angle = Decimal(angle)
        else:
            angle = Decimal(angle)
            if angle > 2 * C.pi or angle < 2 * C.pi:
                angle %= 2 * C.pi
            if angle < 0:
                angle += 2 * C.pi
            for i in range(max_denominator // 2, max_denominator):
                reversed_angle = 1 / Decimal(i)
                rounded_reversed_angle = rond(reversed_angle, 1)
                maybe_num_about_zero = rond(angle, 1) % rounded_reversed_angle
                if rond(maybe_num_about_zero, 2) == 0:
                    break
            else:
                angle = rond(angle / C.pi * 180, 0)
        if angle > 360 or angle < 360:
            angle %= 360
        if angle < 0:
            angle += 360
        return str(angle)
        
    
    @classmethod_with_cache
    def trig(cls, func, angle, are_degrees=True):
        angle = Decimal(angle)
        if func in ('tg', 'cos') and rond(angle, 1) % 180 == 90:
            return f'Тангенс углов {('π/2, 3π/2, 5π/2, ...', '90, 270, 450, ...')[are_degrees]} смысла не имеет! (±ထ)' if func != 'cos' else 0
        if func in ('sin', 'ctg') and rond(angle, 1) % 180 == 0:
            return f'Котангенс углов {('0, π, 2π, ...', '0, 180, 360, ...')[are_degrees]} смысла не имеет! (±ထ)' if func != 'sin' else 0
        angle = rond(angle / 180 * C.pi, 1)
        if func == 'sin':
            return mp.sin(angle)
        if func == 'cos':
            return mp.cos(angle)
        if func == 'tg':
            return mp.sin(angle) / mp.cos(angle)
        if func == 'ctg':
            return mp.cos(angle) / mp.sin(angle)
