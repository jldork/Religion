import os
from splitter.functions import *

book = "texts/bible.txt"
book_dir = "texts/bible/"
book_separations = get_lines("Book", book)

if not os.path.exists(book_dir):
    os.makedirs(book_dir)

for i in range(len(book_separations) - 1):
    index = (book_separations[i], book_separations[i + 1])

    title = run_and_get_stdout(["sed", "{}!d".format(index[0]), book])
    title = clean_text(title.decode())
    prefix = str(i) if i > 9 else "0{}".format(i)
    fname = title.split(":")[0].strip().strip("_")
    fname = prefix + "_" + fname + ".txt"

    cmd = ["sed", "-n", "{},{}p".format(index[0], index[1] - 1), book]
    chapter = run_and_get_stdout(cmd)

    with open(book_dir + fname, 'wb') as f:
        f.write(chapter)
