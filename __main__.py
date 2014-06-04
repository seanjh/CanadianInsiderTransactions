"""Canadian Insider Transactions.

Usage:
    sedi_transactions <issuer_num>...

Options:
    -h --help     Show this screen.
    --version     Show version.
"""


import os
from docopt import docopt
from sedi_transactions.transactions import SEDIView

OUTPUT_PATH = os.path.abspath(
    os.path.join(os.path.abspath(__file__), '..', 'output')
)
if not os.path.exists(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)


def write_html(html_text, encoding, filename):
    with open(filename, 'w', encoding=encoding) as outfile:
        outfile.write(html_text)

def main():
    arguments = docopt(__doc__, version='Canadian Insider Transactions 0.1')
    sedar_issuers = arguments.get('<issuer_num>')

    with SEDIView() as sv:
        i = 0
        while i < len(sedar_issuers):
            html = sv.get_transactions_view(sedar_issuers[i])
            filename = os.path.join(OUTPUT_PATH,
                                    ('{0}.html').format(sedar_issuers[i]))
            if html:
                print("Downloading HTML to {0}".format(filename))
                write_html(html, sv.encoding, filename)
            i += 1

if __name__ == '__main__':
    main()