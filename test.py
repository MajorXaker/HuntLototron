def aaa(arg1 = None, arg2 = None):
    values = (arg1, arg2)
    if None in values:
        print('None was given')
    else:
        print('Good values were given')

aaa(arg1='kek')