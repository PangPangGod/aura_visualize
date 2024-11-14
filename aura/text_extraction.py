from abc import ABC, abstractmethod
from pydantic import BaseModel, validate_call
from typing import List
from pypdf import PdfReader

class BaseTextExtraction(ABC, BaseModel):
    @abstractmethod
    def get_text():
        pass

class PyPDFTextExtraction(BaseTextExtraction):
    """
    Get Text Extraction with pypdf

    Args:
        file_path (str): basic file path. wrap with Path object later.
    """
    file_path: str
    
    def get_text(self, prettify_with_index: bool = True) -> str:
        """ 
        Main method (Extract text from pdf file with pypdf)

        Args:
            prettify_with_index (bool): If True, text will be prettified with index, seperator.
            EX : =============================== Page 1
            Defaults to True.
        """
        reader = PdfReader(self.file_path)

        if prettify_with_index:
            return self._prettify_text(reader)
        else :
            return '\n\n'.join([page.extract_text() for page in reader.pages])
    
    def _prettify_text(self, reader:PdfReader) -> List[str]:
        all_pages_text = []

        for index, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            formatted_page_text = f"{'='*80}\nPage {index}\n\n{page_text}\n"
            all_pages_text.append(formatted_page_text)

        return ''.join(all_pages_text)
