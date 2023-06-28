from django import template

register = template.Library()


FWORDS_VACSET = {
    'д': ['дебил', 'дрянь',],
    'и': ['идиот', 'извращенец',],
    'м': ['мудак',],
    'р': ['редиска'],
}

# Регистрируем наш фильтр под именем censor, чтоб Django понимал,
# что это именно фильтр для шаблонов, а не простая функция.

# в этом фильтре делается предположение что так называемое плохое слово начинается с буквы - то есть оно не закавычено
# можно усложнить функцию чтобы и это отслеживалось - но в другой раз
# проверка сначала проходит по букве что сократить время поиска


@register.filter()
def censor(textnews):
    word_list = textnews.split(' ')
    # print(word_list)
    for idx, value in enumerate(word_list):
        if value:
            if value[0].lower() in FWORDS_VACSET.keys():
                for el in FWORDS_VACSET[value[0].lower()]:
                    if el in value.lower():
                        # print(el, value, idx)
                        corrected = value[0] + '*' * (len(el)-1) + value[len(el):]
                        # print(corrected)
                        word_list[idx] = corrected
                        # word_list[idx][1:len(el)] = "*" * (len(el)-1)
                        # print(word_list[idx])

    return ' '.join(word_list)
