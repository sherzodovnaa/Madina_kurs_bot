from openpyxl import Workbook

from utils.helper.user_helper import all_quizzes


def write_xl():
    wb = Workbook()
    ws = wb.active
    ws.title = 'savollar'
    ws.append(['Category', 'Subcategory', 'Quiz', 'A', 'B', 'C', 'D'])
    for quiz in all_quizzes():
        category_name = quiz.subcategory.category.name
        subcategory_name = quiz.subcategory.name
        text = quiz.text
        a, b, c, d = [op.text for op in quiz.options]
        ws.append([category_name, subcategory_name, text, a, b, c, d])
    wb.save('savollar.xlsx')


if __name__ == '__main__':
    write_xl()
