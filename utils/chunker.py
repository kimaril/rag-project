import re
import json
import settings

class TextChunker:
    def __init__(self, structured_blocks):
        self.structured_blocks = structured_blocks
        self.max_chunk_size = settings.MAX_CHUNK_SIZE
        self.chunks = []
        self.section_filter = {'Аннотация', 'Оглавление', 'Литература'}
        self.content_filter_pattern = r"^\d+(\.\d+)*\.\s+.+$"

    def split_into_chunks(self, text):
        sentences = re.split(r'(?<=[.!?]) +', text)
        current_chunk = ""
        chunks = []

        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= self.max_chunk_size:
                current_chunk += sentence + " "
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def chunk(self):
        current_section = None

        for section in self.structured_blocks:
            if section.startswith("##"):
                current_section = section.replace("#", "").strip()
                continue
            elif section.startswith("###"):
                current_section = section.replace("#", "").strip()
                continue
            elif section.startswith("[FIGURE]") or section.startswith("[TABLE]"):
                self.chunks.append({
                    "section": current_section,
                    "type": "caption",
                    "content": section
                })
            else:
                # Это обычный текст — делим его на чанки
                content_chunks = self.split_into_chunks(section)
                for chunk in content_chunks:
                    self.chunks.append({
                        "section": current_section,
                        "type": "text",
                        "content": chunk
                    })

    def filter_chunks(self):
        self.section_filter = self.section_filter | {self.chunks[0]['section']}
        self.chunks = [chunk for chunk in self.chunks if (chunk['section'] not in self.section_filter and\
                                                          re.match(pattern=self.content_filter_pattern,
                                                                   string=chunk['content']) is None)]
        
    def save(self, output_path):
        with open(output_path, "w", encoding="utf-8") as f:
            for chunk in self.chunks:
                json.dump(chunk, f, ensure_ascii=False)
                f.write("\n")