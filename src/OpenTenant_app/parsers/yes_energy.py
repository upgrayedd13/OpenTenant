import pdfplumber
import re

def getStatementDate(text: str) -> str:
    pattern = r''
    r = re.compile(pattern)


def parseYesEnergy(fname: str) -> None:
    with pdfplumber.open(fname) as pdf:
        page1 = pdf.pages[0]
        page2 = pdf.pages[1]

        page1Table = page1.extract_tables()
        page2Table = page2.extract_tables()

        page1Text = page1.extract_text()
        page2Text = page2.extract_text()

    print(page1Table)
    print()
    print(page1Text)
    print()
    
    if 'GAS PROFILE' in page1Text:
        print('Found gas profile')



# Test main function
def main() -> None:
    import argparse
    
    parser = argparse.ArgumentParser(description='Extracts data from a YES ENERGY management statement.')
    parser.add_argument('-f', '--file', type=str, required=True, help='File to parse.')
    args = parser.parse_args()

    parseYesEnergy(args.file)


if __name__ == "__main__":
    main()