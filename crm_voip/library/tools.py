# -*- coding: utf-8 -*-
import random
import string

from odoo import _


def getRandomString(prefix='', length=10):
    prefix = prefix or ''
    letters_and_digits = string.ascii_letters + string.digits
    return prefix + ''.join(random.choice(letters_and_digits) for i in range(length-len(prefix)))


def to_2d_float(val):
    return int(float(val) * 100) / 100


def luhn(card_number):
    sum = 0
    alt = 0
    i = len(card_number) - 1
    while i >= 0:
        num = int(card_number[i])
        if alt:
            num = num * 2
            if num > 9:
                num = (num % 10) + 1
        sum = sum + num
        alt = not alt
        i -= 1
    return sum % 10 == 0


def format_phone(number):
    number = number or ''
    number = number.replace(' ', '')
    if number.startswith('+'):
        number = number.replace('+', '00')

    return number


def minute_to_hr(duration):
    dur = ''
    if duration != '':
        h, m = divmod(duration, 60)
        if h > 0:
            dur = str(h) + _(" hr. ")
            if m > 0:
                dur = dur + str(m) + _(" min.")
        else:
            dur = str(m) + _(" min.")

    return dur
