def txt_generator(values, filename) -> str:
    """Генерирует txt файл и возвращает подготовленую строку обратно."""
    prepared_string = ''
    with open(filename, 'w', encoding='UTF-8') as file:
        for result in values:
            prepared_string += result[
                'base_ingredient__name'
            ].title() + ' - ' + str(result[
                'amount__sum'
            ]) + ' ' + result[
                'base_ingredient__measurement_unit'
            ] +'\n'
        file.write(prepared_string)
    return prepared_string


if __name__ == '__main__':
    user = 'admin'
    ingredients = ['пиво', 'Водка', 'рЫба']
    txt_generator(ingredients, user)
