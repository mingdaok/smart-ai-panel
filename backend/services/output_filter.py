import re


class OutputFilter:
    """保障前端永远不会收到 LLM 原始/不安全输出"""

    @staticmethod
    def strip_hidden_cot(text: str) -> str:
        text = re.sub(r'<thinking>.*?</thinking>', '', text, flags=re.DOTALL)
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        text = re.sub(r'\[COT\].*?\[/COT\]', '', text, flags=re.DOTALL)
        return text

    @staticmethod
    def strip_json_block(text: str) -> str:
        text = re.sub(r'```json\s*\n.*?\n```', '', text, flags=re.DOTALL)
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        return text

    @staticmethod
    def sanitize(text: str) -> str:
        text = OutputFilter.strip_hidden_cot(text)
        text = OutputFilter.strip_json_block(text)
        return text.strip()
