import re
import typing

import PyPDF2

# output = pypandoc.convert_file('somefile.txt', 'rst', format='md')


def text_extractor(path):
    max_pages = 50
    outfile = "./output.md"
    with open(outfile, mode='wb') as out:
        print("Writing to", outfile)
        with open(path, mode='rb') as f:
            reader = PyPDF2.PdfReader(f)
            # num_pages = reader.getNumPages()
            num_pages = len(reader.pages)
            for i in range(num_pages):
                page = reader.pages[i]
                # data.append(page.extract_text())
                # print(page.extract_text())
                visit_text(page, out)
                if i >= max_pages:
                    print("Exiting")
                    return i


def visit_text(page, out: typing.IO):
    parts = []

    def visitor_body(text, cm, tm, fontDict, fontSize):
        # TODO unicode translation error
        prepend = None
        if fontDict is not None and re.match(r'/.*Bold.*', fontDict['/BaseFont']):
            # print(fontDict)
            if fontSize < 10:
                prepend = '#####'
            else:
                prepend = '###'

        # print(text, end='')

        y = tm[5]
        if 54 < y < 585:
            if prepend is not None:
                parts.append(prepend)
            parts.append(text)

    page.extract_text(visitor_text=visitor_body)
    text_body = "".join(parts)

    # print(text_body)
    out.write(text_body.encode('utf-8'))


if __name__ == "__main__":
    path = (r'C:\Users\benny\Calibre Library\Unknown\The Alchemy of Finance (by George So (22)'
            r'\The Alchemy of Finance (by Geor - Unknown.pdf')
    num_page = text_extractor(path)
    print('The pdf has {} pages'.format(num_page))

# python md2epub.py <markdown_directory> <output_file.epub>
# (venv) ocr-python>move output.md md\chapter1.md
# Overwrite C:\Users\benny\PyCharmProjects\ocr-python\md\chapter1.md? (Yes/No/All): yes
#         1 file(s) moved.
# (venv) C:\Users\benny\PyCharmProjects\ocr-python> python mark2epub-master\mark2epub.py md\ out.epub
# eBook creation complete
