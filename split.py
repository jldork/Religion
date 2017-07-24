import subprocess
import re


def run_and_get_stdout(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return stdout

def get_lines(text):
    cmd = ["awk","/{}/{{print NR;}}".format(text),"bible.txt"]
    a = run_and_get_stdout(cmd)
    lines = a.decode().strip('\n').split('\n')
    return [int(line) for line in lines]

def clean_text(text, escape=True, linebreak=True, spaces=False):
    if escape:
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
    if linebreak:
        text = re.sub(r"(?<=[a-z])\r?\n"," ", text)
    if not spaces:
        text = text.replace(" ","_")
    return text.strip()

book_separations = get_lines("Book")

for i in range(len(book_separations)-1):
    index = (book_separations[i], book_separations[i+1])
    
    title = run_and_get_stdout(["sed","{}!d".format(index[0]), "bible.txt"]) 
    title = clean_text(title.decode())
    prefix = str(i) if i > 9 else "0{}".format(i) 
    fname = prefix+"_"+title.split(":")[0] + ".txt"

    cmd = ["sed","-n","{},{}p".format(index[0],index[1]-1), "bible.txt"]
    chapter = run_and_get_stdout(cmd)

    with open(fname, 'wb') as f:
        f.write(chapter)

