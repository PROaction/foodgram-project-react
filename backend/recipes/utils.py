from fpdf import FPDF


FONT_SIZE = 12
WIDTH = 0
HEIGHT = 10
IS_BORDER = False
MOVE_TO_NEXT_LINE = 1  # если 1 - переместить курсор на следующую строку

ALIGN_HEADER = 'C'  # выравнивание по центру
ALIGN_BODY = 'L'  # выравнивание по левому краю

HEIGHT_EMPTY_STRING_FOR_TITLE = 10


class PDF(FPDF):

    def header(self):
        self.set_font('FreeSans', '', FONT_SIZE)
        self.cell(
            WIDTH, HEIGHT, 'Список покупок', IS_BORDER, MOVE_TO_NEXT_LINE,
            ALIGN_HEADER
        )

    def chapter_title(self, title):
        self.set_font('FreeSans', '', FONT_SIZE)
        self.cell(
            WIDTH, HEIGHT, title, IS_BORDER, MOVE_TO_NEXT_LINE, ALIGN_BODY
        )
        self.ln(HEIGHT_EMPTY_STRING_FOR_TITLE)

    def chapter_body(self, body):
        self.set_font('FreeSans', '', FONT_SIZE)
        self.multi_cell(WIDTH, HEIGHT, body)
        self.ln()

    def print_chapter(self, title, body):
        self.add_page()
        self.chapter_title(title)
        self.chapter_body(body)
