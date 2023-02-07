from pathlib import Path
from datetime import date
from borb.pdf import Document, Page, SingleColumnLayout, Paragraph, PDF
from cuisine.models import Recipe, Tag, BaseIngredientWithUnits, Favorite, Order, IngredientRecipe

def txt_generator(values, user):
    with open(Path(f'{user}_{date.today()}.txt'), 'w', encoding='UTF-8') as file:
        for value in values:
            value += '\n'
            file.write(value)


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
