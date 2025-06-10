from world_builder.prompts import ParserErrorType, parse_prompt_result


class TestPromptParsing:
    def test_parse_prompt_result_function_success(self):
        """Test the parse_prompt_result function with valid input."""
        result = parse_prompt_result(
            """
            <code-change>
                <summary>Test summary</summary>
                <files-to-change>
                    <file name="test1.py" />
                    <file name="test2.py" />
                    <file name="test3.py" />
                </files-to-change>
                <changes>
                    <change file-name="test1.py">
                        <modify start-line="1" end-line="5">Modified content</modify>
                    </change>
                    <change file-name="test2.py">
                        <add>New content</add>
                    </change>
                    <change file-name="test3.py">
                        <delete />
                    </change>
                </changes>
                <additional-steps>
                    <step>Run migration</step>
                    <step>Update documentation</step>
                </additional-steps>
                <verification>
                    <step>Run tests</step>
                    <step>Check logs</step>
                </verification>
            </code-change>
            """
        )

        assert result.is_ok()
        code_change = result.unwrap()
        assert code_change.summary == "Test summary"
        assert len(code_change.files_to_change) == 3

    def test_parse_prompt_result_empty_input(self):
        """Test parse_prompt_result function with empty input."""
        result = parse_prompt_result("")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.INVALID_XML
        assert "Empty or whitespace-only markup" in error.source

    def test_parse_prompt_result_whitespace_only(self):
        """Test parse_prompt_result function with whitespace-only input."""
        result = parse_prompt_result("   \n\t   ")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.INVALID_XML
        assert "Empty or whitespace-only markup" in error.source

    def test_parse_prompt_result_malformed_xml(self):
        """Test parse_prompt_result function with malformed XML."""
        malformed_xml = """
        <code-change>
            <summary>Test</summary>
            <unclosed-tag>
        </code-change>
        """

        result = parse_prompt_result(malformed_xml)

        assert result.is_err()
        error = result.unwrap_err()
        # Should be INVALID_XML for malformed XML, but some parsers
        # might categorize differently
        assert error.type in [
            ParserErrorType.INVALID_XML,
            ParserErrorType.PARSING_ERROR,
        ]
        assert (
            "Malformed XML" in error.source
            or "XMLSyntax" in error.source
            or "parsing" in error.source.lower()
        )

    def test_parse_prompt_result_wrong_root_element(self):
        """Test parse_prompt_result function with wrong root element."""
        wrong_root = """
        <wrong-element>
            <summary>Test</summary>
        </wrong-element>
        """

        result = parse_prompt_result(wrong_root)

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.MISSING_ELEMENT

    def test_parse_prompt_result_missing_required_fields(self):
        """Test parse_prompt_result function with missing required fields."""
        missing_summary = """
        <code-change>
            <files-to-change>
                <file name="test.py" />
            </files-to-change>
        </code-change>
        """

        result = parse_prompt_result(missing_summary)

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.PARSING_ERROR
        assert "Validation failed" in error.source

    def test_parse_prompt_result_invalid_attribute_types(self):
        """Test parse_prompt_result function with invalid attribute types."""
        invalid_types = """
        <code-change>
            <summary>Test</summary>
            <changes>
                <change file-name="test.py">
                    <modify start-line="not-a-number" end-line="15">
                        Content
                    </modify>
                </change>
            </changes>
        </code-change>
        """

        result = parse_prompt_result(invalid_types)

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.PARSING_ERROR
