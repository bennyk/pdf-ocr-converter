import re
import sys
import typing
import subprocess

import PyPDF2

# output = pypandoc.convert_file('somefile.txt', 'rst', format='md')

# type: typing.IO
out = None
chapters = []
markdown_dir = "markdown_dir"


def text_extractor(path):
    print("stdout encoding", sys.stdout.encoding)
    max_pages = 50
    with open(path, mode='rb') as f:
        reader = PyPDF2.PdfReader(f)
        # page = reader.pages[25]
        # visit_text(page, out)
        # return 1
        num_pages = len(reader.pages)
        for i in range(num_pages):
            page = reader.pages[i]
            visit_text(page)
            if i >= max_pages:
                print("Exiting")
                return i


def visit_text(page):
    global out, markdown_dir
    parts = []
    dup_int = 1

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
        if 0 < y < 585:
            if prepend is not None:
                parts.append(prepend)
            parts.append(text)

    page.extract_text(visitor_text=visitor_body)
    text_body = "".join(parts)

    # print(text_body)

    text_para = text_body.split('\n')
    m = re.match(r'###(.+)$', text_para[0].lower())
    if m is not None:
        s = re.sub(r'#+', '', m.group(1))
        s = re.sub(r'\*', '', s)
        s = re.sub(r'\s+', '_', s)
        if s != '':
            if s in chapters:
                dup_int += 1
                s += str(dup_int)
            chapters.append(s)
            print("Adding chapter '{}'".format(s))
            outfile = "{}/{}.md".format(markdown_dir, s)
            out = open(outfile, mode='wb')

    if out is not None:
        stream_out(text_para)


def stream_out(text_para: list):
    global out
    body = ''
    flag = False
    suppress = True

    for i, x in enumerate(text_para):
        m = re.search(r'(#+)(.+?)$', x)
        if m is not None:
            s = re.sub(r'#+', '', m.group(2))
            body += '{}{}\n'.format(m.group(1), s)
            if not suppress:
                print("{}{}".format(m.group(1), s))
        else:
            m = re.search(r'(.+?)(#+)$', x)
            if m is not None:
                body += '{}\n{} '.format(m.group(1), m.group(2))
                if not suppress:
                    print("{}\n{} ".format(m.group(1), m.group(2)), end='')
                flag = True
            else:
                if flag:
                    flag = False
                    s = re.sub(r'#+', '', x)
                    s = re.sub(r'\s+', ' ', s)
                    body += s
                    body += '\n'
                    if not suppress:
                        print(s, '\n')
                else:
                    body += x + '\n'
                    if not suppress:
                        print(x)

    # Alternative 'utf-8', and Windows 'cp1252' or 'ansi'
    # https://www.ibm.com/docs/en/cognos-analytics/11.0.0?topic=performance-pdf-file-settings
    if out is not None:
        out.write(body.encode('utf-8'))


def write_template(chaps):
    global markdown_dir

    template = '''{
    "metadata": {
        "dc:title": "Mark2Epub Sample",
        "dc:creator": "Mark2Epub",
        "dc:language": "en-US",
        "dc:identifier": "mark2epub-sample",
        "dc:source": "",
        "meta": "",
        "dc:date": "2023-01-01",
        "dc:publisher": "",
        "dc:contributor": "",
        "dc:rights": "",
        "dc:description": "",
        "dc:subject": ""
    },
    "cover_image": "cover.jpg",
    "default_css": ["code_styles.css", "general.css"],
    "chapters": [
%markdown%
    ]
}
'''
    mark = ''
    for i, chap in enumerate(chaps):
        mark += "        "
        mark += '''{{"markdown": "{}.md", "css": ""}}'''.format(chap)
        if (1+i) != len(chaps):
            mark += ',\n'

    outfile = "{}/description.json".format(markdown_dir)
    with open(outfile, mode='w') as f:
        replaced = template.replace('%markdown%', mark)
        f.write(replaced)
        print("Wrote markdown in {}".format(outfile))
        # TODO import markdown not found error
        # print("Execute mark2epub")
        # subprocess.run(['python', 'mark2epub-master/mark2epub.py', 'markdown_dir', 'out.epub'])


if __name__ == "__main__":
    path = (r'C:\Users\benny\Calibre Library\Unknown\The Alchemy of Finance (by George So (22)'
            r'\The Alchemy of Finance (by Geor - Unknown.pdf')
    num_page = text_extractor(path)
    print('The pdf has {} pages'.format(num_page))
    write_template(chapters)

# python md2epub.py <markdown_directory> <output_file.epub>
# (venv) ocr-python>move output.md md\chapter1.md
# Overwrite C:\Users\benny\PyCharmProjects\ocr-python\md\chapter1.md? (Yes/No/All): yes
#         1 file(s) moved.
# (venv) C:\Users\benny\PyCharmProjects\ocr-python> python mark2epub-master\mark2epub.py md\ out.epub
# eBook creation complete

# TODO Join pagination
# TODO Need to build ebook e.g. Makefile
# TODO Fixing the bold font.
# TODO Incomplete sentence: " spirit of that evening was well characterized when one" cut
# TODO Need to join 0xad or hyphen '-' in ANSI mode (non-printable) to join two partial word
# TODO Missing character "*s*o" e.g. "waves ― o it is with the human uncertainty"
