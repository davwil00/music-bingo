import re


numbers = {'one': '1',
           'two': '2',
           'three': '3',
           'four': '4',
           'five': '5',
           'six': '6',
           'seven': '7',
           'eight': '8',
           'nine': '9',
           'ten': '10',
           'eleven': '11',
           'twelve': '12',
           'thirteen': '13',
           'fourteen': '14',
           'fifteen': '15',
           'sixteen': '16',
           'seventeen': '17',
           'eighteen': '18',
           'nineteen': '19',
           'thousand': '1000'}
ordinals = {'first': '1',
            'second': '2',
            'third': '3',
            'fourth': '4',
            'fifth': '5',
            'sixth': '6',
            'seventh': '7',
            'eighth': '8',
            'ninth': '9',
            'tenth': '10'}
tens = {
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90
}

special_matches = {
    '9 to 5': '925',
    'Number of the Beast': '666'
}

remix = re.compile(' \(?(\(|- )([\d]{4} |[\w\" ]+)?(remix|remastered|remaster|mix|radio edit)( \d{4})?\)?', re.I)
feat = re.compile(' \(feat\.[\w ]+\)', re.I)
version = re.compile(' - (single|album) version', re.I)


def convert_to_number(string: str) -> str:
    decoded = ''
    string = replace_number_words(string)
    for char in string:
        if char.isdigit():
            decoded += char

    return decoded


def replace_number_words(string: str) -> str:
    for special_match in special_matches:
        if string.find(special_match) >= 0:
            return special_matches[special_match]
    words = string.split(' ')
    for i, word in enumerate(words):
        if word.lower() in tens:
            next_word = words[i + 1]
            next_number_word = replace_number_words(next_word)
            if next_number_word.isdigit():
                string = re.sub(f'\\b{word} {next_word}\\b', f'{str(tens[word.lower()])[0]}{next_number_word}', string, flags=re.I)
        if word.lower() in numbers:
            string = re.sub(f'\\b{word}\\b', numbers[word.lower()], string, flags=re.I)
        if word.lower() in ordinals:
            string = re.sub(f'\\b{word}\\b', ordinals[word.lower()], string, flags=re.I)

    return string


def strip_additional_info(string: str) -> str:
    result = remix.sub('', string)
    result = feat.sub('', result)
    result = version.sub('', result)
    return result

