import re
from typing import Type

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


@deconstructible
class ASCIIUsernameValidator(validators.RegexValidator):
    regex = r'^[\w.@+-]+\Z'
    message = _(
        'Enter a valid username. This value may contain only English letters, '
        'numbers, and @/./+/-/_ characters.'
    )
    flags = re.ASCII


@deconstructible
class UnicodeUsernameValidator(validators.RegexValidator):
    regex = r'^[\w.@+-]+\Z'
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and @/./+/-/_ characters.'
    )
    flags = 0

@deconstructible
class NonNegativeValidator(validators.MinValueValidator):
    '''Checks whether value is not negative
    Parameters
    ---
    input_type : str - What kind of value cannot be negative
    it is used here: Value of {input_type} cannot be negative
    '''
    def __init__(self, input_type):

        super().__init__(limit_value = 0, message='')
        self.limiting_type = input_type
        self.message =_( f'Value of {input_type} cannot be negative')


    limit_value = 0


@deconstructible
class InRangeValidator(validators.BaseValidator):
    '''this validator accepts only int and float, any other value will be converted into 0'''
    
    def clean_compare_list(self, compare_list):
        try:
            val_1 = compare_list[0]
        except IndexError:
            val_1 = 1
            val_2 = 0
        else:
            try:
                val_2 = compare_list[1]
            except IndexError:
                val_2 = 0

        if not isinstance(val_1,(float, int)):
            val_1 = 0
        if not isinstance(val_2,(float, int)):
            val_2 = 0
        
        return (val_1, val_2)

    def __init__(self, limit_value, message='') -> None:
        low = min(limit_value)
        high = max(limit_value)
        message = _(f'Value should be between {low} and {high}. Please correct.')
        super().__init__(limit_value, message=message)
        
    def compare(self, value, compare_with):
        list_2_compare = self.clean_compare_list(compare_with)

        return (
            value < min(list_2_compare) or
            value > max(list_2_compare)
        )

        


    
@deconstructible
class ListedValueValidator(validators.BaseValidator):
    def compare(self, value, compare_with):
        return not value in compare_with

    def __init__(self, limit_value, type_to_sum = '', message = None) -> None:
        limits_readable = ''
        for value in limit_value:
            limits_readable = limits_readable + str(value) + ', '
        limits_readable = limits_readable[:-2]
        if message == None:
            message = _(f'Value should be one of the following: {limits_readable}. Please correct.')
        super().__init__(limit_value, message=message)

@deconstructible
class SumValidator(validators.BaseValidator):

    def clean_compare_list(self, compare_list):
        try:
            compare_list = list(compare_list)
            for value in compare_list:
                if not isinstance(value,(float, int)):
                    value = 0
        except TypeError:
            compare_list = [compare_list]

    def compare(self, value, compare_with):
        list_2_compare = self.clean_compare_list(compare_with)
        return not value == sum(compare_with)
        
    def __init__(self, limit_value, type_to_sum = 'parts', message=None) -> None:
        if message == None:   
            message = _(f'Given number doesnt match the sum of {type_to_sum}. Please correct.')
        super().__init__(limit_value, message=message)

@deconstructible
class WeaponsValidator(validators.BaseValidator):
    '''This validator checks that you have not taken 3+3 weapons and unsupported ammo'''
    pass