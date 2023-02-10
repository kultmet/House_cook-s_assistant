from pathlib import Path
from datetime import date
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF
from cuisine.models import Recipe, Tag, BaseIngredientWithUnits, Favorite, Order, IngredientRecipe

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



# def pdf_generator(values, user):
#     pdf = Document()
#     page = Page(width=240)
#     pdf.add_page(page=page)
#     layout = SingleColumnLayout(page)
#     for value in values:
#         layout.add(Paragraph(value, font='Courier-Bold',))
#     # print(Path('hallo_word.pdf'))
#     with open(Path(f'{user}_{datetime.now()}.pdf'), 'w') as pdf_file_handle:
#         print(Path('hallo_word.pdf'))
#         PDF.dumps(pdf_file_handle, pdf)

user = 'admin'
ingredients = ['пиво', 'Водка', 'рЫба']
# pdf_generator(ingredients, user)
if __name__ == '__main__':
    txt_generator(ingredients, user)
