from backend.services.output_filter import OutputFilter


class TestOutputFilter:
    def test_strip_thinking_tags(self):
        text = "公开内容<thinking>隐藏思维链</thinking>更多内容"
        result = OutputFilter.strip_hidden_cot(text)
        assert "<thinking>" not in result
        assert "隐藏思维链" not in result
        assert "公开内容" in result
        assert "更多内容" in result

    def test_strip_json_block(self):
        text = '正常发言\n```json\n{"key":"value"}\n```\n后续内容'
        result = OutputFilter.strip_json_block(text)
        assert "```json" not in result
        assert '"key":"value"' not in result
        assert "正常发言" in result
        assert "后续内容" in result

    def test_sanitize_full_pipeline(self):
        text = '观点<thinking>内部推理</thinking>```json\n{"a":1}\n```结尾'
        result = OutputFilter.sanitize(text)
        assert "内部推理" not in result
        assert "```json" not in result
        assert "观点" in result
        assert "结尾" in result

    def test_clean_text_passes_through(self):
        text = "这是一段正常的发言内容"
        result = OutputFilter.sanitize(text)
        assert result.strip() == text
