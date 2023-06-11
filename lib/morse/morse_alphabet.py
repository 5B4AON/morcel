
DIT = '.'
DAH = '-'
END_OF_WORD = ' '

morse = {
    'A': '.-',
    'B': '-...',
    'C': '-.-.',
    'D': '-..',
    'E': '.',
    'F': '..-.',
    'G': '--.',
    'H': '....',
    'I': '..',
    'J': '.---',
    'K': '-.-',  # Prosign for 'invitation to transmit'
    'L': '.-..',
    'M': '--',
    'N': '-.',
    'O': '---',
    'P': '.--.',
    'Q': '--.-',
    'R': '.-.',
    'S': '...',
    'T': '-',
    'U': '..-',
    'V': '...-',
    'W': '.--',
    'X': '-..-',
    'Y': '-.--',
    'Z': '--..',
    '1': '.----',
    '2': '..---',
    '3': '...--',
    '4': '....-',
    '5': '.....',
    '6': '-....',
    '7': '--...',
    '8': '---..',
    '9': '----.',
    '0': '-----',
    '.': '.-.-.-', # Period
    ',': '--..--', # Comma
    '?': '..--..', # Question mark
    "'": '.----.', # Apostrophe
    '!': '-.-.--', # Exclamation point, digraph <KW>
    '/': '-..-.',  # Slash
    '(': '-.--.',  # Open parenthesis, digraph <KN>, Abbreviation for 'over to you'
    ')': '-.--.-', # Close parenthesis
    '&': '.-...',  # Ampersand, digraph <AS>, Prosign for 'wait'
    ':': '---...', # Colon
    ';': '-.-.-.', # Semicolon
    '=': '-...-',  # Double dash, digraph <BT>, Prosign for 'new paragraph'
    '+': '.-.-.',  # Plus sign, digraph <AR>, Prosign for 'end of message'
    '-': '-....-', # Minus sign, Hyphen
    '_': '..--.-', # Underscore
    '"': '.-..-.', # Quotation mark
    '$': '...-..-',# Dollar sign, digraph <SX>
    '@': '.--.-.', # At sign, digraph <AC>
    '<SK>': '...-.-',# Prosign for 'end of work'
    '<Error>': '........',# Prosign for 'error'
    '<BK>': '-...-.-',# Prosign for 'break-in'
    '<KA>': '-.-.-',# Prosign for 'attention', new message
    '<VE>': '...-.',# Prosign for 'verified'
    '<SOS>': '...---...' # Start of distress signal, only used by original sender for imminent danger to life or property
}

def symbolToChar(s):
    for key, value in morse.items():
        if value == s:
            return key
    return '#'

# TODO symbolsToText(s)

def charToSymbol(c):
    return morse.get(c)

# TODO textToSymbols(t)
