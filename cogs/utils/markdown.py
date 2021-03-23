## markdown特殊表記
def bold(string):
    return '**' + string + '**'

def italic(string):
    return '*' + string + '*'

def code(string):
    return '`' + string + '`'

def code_block(string, language = ''):
    return '```'+ language + '\n' + string + '```'

def mask(string):
    return '||' + string + '||'