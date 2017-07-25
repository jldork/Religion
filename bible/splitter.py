import subprocess
import re


def run_and_get_stdout(cmd):
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return stdout


def get_lines(text, book):
    cmd = ["awk", "/{}/{{print NR;}}".format(text), book]
    a = run_and_get_stdout(cmd)
    lines = a.decode().strip('\n').split('\n')
    return [int(line) for line in lines]


def clean_text(text, escape=True, linebreak=True, spaces=False):
    if escape:
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\xff]', '', text)
        text = text.replace('\xc2\xb7', '')
    if linebreak:
        text = re.sub(r"(?<=[a-z])\r?\n", " ", text)
    if not spaces:
        text = text.replace(" ", "_")
    return text.strip()
