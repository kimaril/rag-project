import re
import json
import pymupdf
from tqdm.auto import tqdm


class PDFParser:
    def __init__(self):
        self.raw_text = ""
        self.structured = []
        self.current_section = None

    def load_text(self, pdf_path):
        self.doc = pymupdf.open(pdf_path, filetype="pdf")

    def parse(self):
        for page_num, page in tqdm(enumerate(self.doc, start=1), total=len(self.doc)):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                if block['type'] != 0:  # type 0 = text
                    continue
                block_text = ""
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip().replace('-\n', '')
                        if not text:
                            continue

                        font_size = span["size"]
                        is_bold = "Bold" in span["font"]

                        # Примитивная эвристика для заголовков
                        if font_size > 12 or is_bold:
                            if text.lower().startswith("abstract"):
                                block_text += "\n## Abstract\n"
                            elif text.lower().startswith("introduction"):
                                block_text += "\n## Introduction\n"
                            elif text.lower().startswith("conclusion") or text.lower().startswith("discussion"):
                                block_text += f"\n## {text.strip()}\n"
                            elif text.lower().startswith("references"):
                                block_text += f"\n## References\n"
                            elif font_size > 13:
                                block_text += f"\n### {text.strip()}\n"
                            else:
                                block_text += f"\n{text.strip()}\n"
                        elif text.lower().startswith("figure") or text.lower().startswith("fig."):
                            block_text += f"\n[FIGURE] {text.strip()}\n"
                        elif text.lower().startswith("table"):
                            block_text += f"\n[TABLE] {text.strip()}\n"
                        else:
                            block_text += f"{text} "

                if block_text.strip():
                    self.structured.append(block_text.strip())

    def get_structured_blocks(self):
        return self.structured
