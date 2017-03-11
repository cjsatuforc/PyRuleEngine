'''Library to implement hashcat style rule engine.'''
import re
# based on hashcat rules from
# https://hashcat.net/wiki/doku.php?id=rule_based_attack


def i36(string):
    '''Shorter way of converting base 36 string to integer'''
    return int(string, 36)


def rule_regex_gen():
    ''''Generates regex to parse rules'''
    __rules__ = [
        ':', 'l', 'u', 'c', 'C', 't', r'T\w', 'r', 'd', r'p\w', 'f', '{',
        '}', '$.', '^.', '[', ']', r'D\w', r'x\w\w', r'O\w\w', r'i\w.',
        r'o\w.', r"'\w", 's..', '@.', r'z\w', r'Z\w', 'q',
        ]
    for i, func in enumerate(__rules__):
        __rules__[i] = func[0]+func[1:].replace(r'\w', '[a-zA-Z0-9]')
    ruleregex = '|'.join(['%s%s' % (re.escape(a[0]), a[1:]) for a in __rules__])
    return re.compile(ruleregex)
__ruleregex__ = rule_regex_gen()

FUNCTS = {}
FUNCTS[':'] = lambda x, i: x
FUNCTS['l'] = lambda x, i: x.lower()
FUNCTS['u'] = lambda x, i: x.upper()
FUNCTS['c'] = lambda x, i: x.capitalize()
FUNCTS['C'] = lambda x, i: x.capitalize().swapcase()
FUNCTS['t'] = lambda x, i: x.swapcase()
FUNCTS['T'] = lambda x, i: x[0:i36(i)]+x[i36(i)].swapcase()+x[i36(i)+1:]
FUNCTS['r'] = lambda x, i: x[::-1]
FUNCTS['d'] = lambda x, i: x+x
FUNCTS['p'] = lambda x, i: x*(i36(i)+1)
FUNCTS['f'] = lambda x, i: x+x[::-1]
FUNCTS['{'] = lambda x, i: x[1:]+x[0]
FUNCTS['}'] = lambda x, i: x[-1]+x[:-1]
FUNCTS['$'] = lambda x, i: x+i
FUNCTS['^'] = lambda x, i: i+x
FUNCTS['['] = lambda x, i: x[1:]
FUNCTS[']'] = lambda x, i: x[:-1]
FUNCTS['D'] = lambda x, i: x[:i36(i)-1]+x[i36(i):]
FUNCTS['x'] = lambda x, i: x[i36(i[0]):i36(i[1])]
FUNCTS['O'] = lambda x, i: x[:i36(i[0])]+x[i36(i[1])+1:]
FUNCTS['i'] = lambda x, i: x[:i36(i[0])]+i[1]+x[i36(i[0]):]
FUNCTS['o'] = lambda x, i: x[:i36(i[0])]+i[1]+x[i36(i[0])+1:]
FUNCTS["'"] = lambda x, i: x[:i36(i)]
FUNCTS['s'] = lambda x, i: x.replace(i[0], i[1])
FUNCTS['@'] = lambda x, i: x.replace(i, '')
FUNCTS['z'] = lambda x, i: x[0]*i36(i)+x
FUNCTS['Z'] = lambda x, i: x+x[-1]*i36(i)
FUNCTS['q'] = lambda x, i: ''.join([a*2 for a in x])


class RuleEngine(object):
    '''
    Initiate with the rules you want to apply and then call .apply for each
    string you want to apply the rules to.
    >>> engine=RuleEngine([':', '$1', 'ss$'])
    >>> for i in engine.apply('password'):
    ...        print(i)
    password
    password1
    pa$$word
    >>> for i in engine.apply('princess'):
    ...        print(i)
    princess
    princess1
    prince$$
    '''
    def __init__(self, rules):
        self.rules = tuple(map(__ruleregex__.findall, rules))

    def apply(self, string):
        '''Apply saved rules to given string.'''
        for rule in self.rules:
            word = string
            for function in rule:
                try:
                    word = FUNCTS[function[0]](word, function[1:])
                except IndexError:
                    pass
            yield word

    def change_rules(self, new_rules):
        '''Replace current rules with new_rules'''
        self.rules = tuple(map(__ruleregex__.findall, new_rules))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
