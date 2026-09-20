#!/usr/bin/env python3
"""Reproduce the Cyphral Distich decode against the 1834 Maitland Club text."""

from pathlib import Path
import csv
import re
from urllib.request import urlopen

SOURCE_URL = "https://archive.org/download/worksofsirthomas00mait/worksofsirthomas00mait_djvu.txt"

CIPHER_1 = [5,3,27,38,32,14,21,8,66,8,70,39,5,9,12,18,2,3,56,5,1,7,3,2,13,19,3,25,9,3,16,6]
# Maitland Club 1834 p. 417. Vals' blog displays 33 at position 24; the scan prints 38.
CIPHER_2 = [25,15,13,6,11,20,5,1,2,12,1,20,20,49,20,20,35,33,4,6,8,35,5,38,5,5,18,10,3,11,32,42]
EXPECTED_1 = "OGODUPHOLDKINGCHARLSTHESECONDAND"
EXPECTED_2 = "MAKEHIMTHESUPREMERULEROFTHISLAND"


def load_source() -> str:
    """Use a local OCR dump when present; otherwise fetch the public Internet Archive text."""
    path = Path("1834.txt")
    if path.exists():
        return path.read_text(errors="replace")
    with urlopen(SOURCE_URL) as response:
        return response.read().decode(errors="replace")


def sections_1834(text: str) -> dict[int, str]:
    """Extract the 32 Proquiritations from the 1834 OCR."""
    chunk = text[text.index("1.  Seeing,  from  the  creation"):text.index("THE  CYPHRAL  DISTICH")]
    chunk = re.sub(r"\n\s*(?:PROQUIRITATIONS\.\s*\d+|\d+\s+PROQUIRITATIONS\.)\s*\n", "\n", chunk)
    chunk = re.sub(r"\n\s*\d{3}\s*\n", "\n", chunk)
    chunk = chunk.replace("3 1 .  That", "31.  That")
    # This printed compound must count as two words for coordinate 2:15.
    chunk = re.sub(r"parol-\s*\n\s*breaking", "parol breaking", chunk)
    # Join ordinary words split only because they wrap across a printed line.
    chunk = re.sub(r"-\s*\n\s*", "", chunk)
    chunk = re.sub(r"\s+", " ", chunk)
    parts = re.split(r"(?<!\w)(\d{1,2})\s*\.\s+", chunk)
    return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts), 2)}


def words(section: str) -> list[str]:
    """Tokenize using the two counting conventions needed by the proposed cipher."""
    section = section.replace("hinc hide", "hinc_inde").replace("hinc inde", "hinc_inde")
    return re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?(?:_[A-Za-z]+)?", section)


def decode(cipher: list[int], expected: str, sections: dict[int, str], line: int):
    rows = []
    letters = []
    for position, (index, want) in enumerate(zip(cipher, expected), 1):
        token = words(sections[position])[index - 1]
        got = token[0].upper()
        rows.append((line, position, index, token.replace("_", " "), got, want, got == want))
        letters.append(got)
    return "".join(letters), rows


def main():
    sections = sections_1834(load_source())
    assert len(sections) == 32

    out1, rows1 = decode(CIPHER_1, EXPECTED_1, sections, 1)
    out2, rows2 = decode(CIPHER_2, EXPECTED_2, sections, 2)

    with Path("coordinates.csv").open("w", newline="") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["line", "position", "word_index", "word", "decoded", "expected", "match"])
        writer.writerows(rows1 + rows2)

    print(out1)
    print(out2)
    print("matches:", sum(row[-1] for row in rows1 + rows2), "/64")
    assert out1 == EXPECTED_1 and out2 == EXPECTED_2

    vals_cipher_2 = CIPHER_2.copy()
    vals_cipher_2[23] = 33
    vals_out, vals_rows = decode(vals_cipher_2, EXPECTED_2, sections, 2)
    print("Vals transcription:")
    print(vals_out)
    print("matches:", sum(row[-1] for row in vals_rows), "/32")


if __name__ == "__main__":
    main()
