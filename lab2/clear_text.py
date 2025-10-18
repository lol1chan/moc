import re

input_txt = f"lab2/franko_zbirka.txt"
output_txt = f"lab2/franko_zbirka_cleared.txt"


with open(input_txt, "r", encoding="utf-8") as f:
    text = f.read()

cleared_text = re.sub(r"[^А-ЩЬЮЯҐЄІЇа-щьюяґєії]", "", text)
cleared_text = re.sub(r"[А-ЩЬЮЯҐЄІЇ]", r"а-щьюяґєії", cleared_text)

with open(output_txt, "w", encoding="utf-8") as f:
    f.write(cleared_text)