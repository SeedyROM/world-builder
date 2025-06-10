from world_builder.parser import CodeChanges, ParserErrorType, parse_markup

TEST_MARKUP = """
<code-change>
    <summary>
        [Brief overview of all changes being made]
    </summary>

    <files-to-change>
        <file name="path/to/file1.ext" />
        <file name="path/to/file2.ext" />
        <file name="path/to/file3.ext" />
    </files-to-change>

    <changes>
        <change file-name="path/to/file1.ext">
            <modify start-line="10" end-line="15">
                [replacement code for lines 10-15]
            </modify>
            <add>
                [new code to append to file]
            </add>
        </change>

        <change file-name="path/to/file2.ext">
            <add>
                [complete new file content]
            </add>
        </change>

        <change file-name="path/to/file3.ext">
            <delete />
        </change>
    </changes>

    <additional-steps>
        <step>npm install new-package</step>
        <step>Update configuration file</step>
    </additional-steps>

    <verification>
        <step>Run tests to verify login functionality</step>
        <step>Check database connections are pooled</step>
    </verification>
</code-change>
"""


class TestParser:
    def test_parse_code_change(self):
        """Test parsing a complete code change XML structure."""
        # Parse the XML markup
        code_change = CodeChanges.from_xml(TEST_MARKUP)

        # Check the summary
        assert code_change.summary == "[Brief overview of all changes being made]"

        # Check files to change
        assert len(code_change.files_to_change) == 3
        assert code_change.files_to_change[0].name == "path/to/file1.ext"
        assert code_change.files_to_change[1].name == "path/to/file2.ext"
        assert code_change.files_to_change[2].name == "path/to/file3.ext"

        # Check changes
        assert len(code_change.changes) == 3
        assert code_change.changes[0].file_name == "path/to/file1.ext"
        assert len(code_change.changes[0].modifications) == 1
        assert code_change.changes[0].modifications[0].start_line == 10
        assert code_change.changes[0].modifications[0].end_line == 15
        assert (
            code_change.changes[0].modifications[0].content
            == "[replacement code for lines 10-15]"
        )

        assert len(code_change.changes[0].additions) == 1
        assert (
            code_change.changes[0].additions[0].content
            == "[new code to append to file]"
        )

        assert code_change.changes[1].file_name == "path/to/file2.ext"
        assert len(code_change.changes[1].additions) == 1
        assert (
            code_change.changes[1].additions[0].content == "[complete new file content]"
        )

        assert code_change.changes[2].file_name == "path/to/file3.ext"
        assert len(code_change.changes[2].deletions) == 1

        # Check additional steps
        assert len(code_change.additional_steps) == 2
        assert code_change.additional_steps[0] == "npm install new-package"
        assert code_change.additional_steps[1] == "Update configuration file"

        # Check verification steps
        assert len(code_change.verification_steps) == 2
        assert (
            code_change.verification_steps[0]
            == "Run tests to verify login functionality"
        )
        assert (
            code_change.verification_steps[1] == "Check database connections are pooled"
        )

    def test_parse_minimal_markup(self):
        """Test parsing minimal valid XML with only required fields."""
        minimal_markup = """
        <code-change>
            <summary>Simple change</summary>
        </code-change>
        """

        code_change = CodeChanges.from_xml(minimal_markup)

        assert code_change.summary == "Simple change"
        assert len(code_change.files_to_change) == 0
        assert len(code_change.changes) == 0
        assert len(code_change.additional_steps) == 0
        assert len(code_change.verification_steps) == 0

    def test_parse_only_modifications(self):
        """Test parsing XML with only modification changes."""
        modify_only_markup = """
        <code-change>
            <summary>Only modifications</summary>
            <changes>
                <change file-name="test.py">
                    <modify start-line="5" end-line="10">
                        Updated function
                    </modify>
                </change>
            </changes>
        </code-change>
        """

        code_change = CodeChanges.from_xml(modify_only_markup)

        assert code_change.summary == "Only modifications"
        assert len(code_change.changes) == 1
        assert code_change.changes[0].file_name == "test.py"
        assert len(code_change.changes[0].modifications) == 1
        assert len(code_change.changes[0].additions) == 0
        assert len(code_change.changes[0].deletions) == 0
        assert code_change.changes[0].modifications[0].start_line == 5
        assert code_change.changes[0].modifications[0].end_line == 10
        assert code_change.changes[0].modifications[0].content == "Updated function"

    def test_parse_optional_modify_attributes(self):
        """Test parsing modifications without line numbers."""
        modify_no_lines = """
        <code-change>
            <summary>Modify without lines</summary>
            <changes>
                <change file-name="test.py">
                    <modify>
                        Full file replacement
                    </modify>
                </change>
            </changes>
        </code-change>
        """

        code_change = CodeChanges.from_xml(modify_no_lines)

        assert len(code_change.changes) == 1
        modify = code_change.changes[0].modifications[0]
        assert modify.start_line is None
        assert modify.end_line is None
        assert modify.content == "Full file replacement"

    def test_parse_multiple_operations_same_file(self):
        """Test parsing multiple operations on the same file."""
        multiple_ops = """
        <code-change>
            <summary>Multiple operations</summary>
            <changes>
                <change file-name="complex.py">
                    <modify start-line="1" end-line="5">
                        Updated imports
                    </modify>
                    <modify start-line="20" end-line="25">
                        Updated function
                    </modify>
                    <add>
                        New function at end
                    </add>
                    <add>
                        Another new function
                    </add>
                </change>
            </changes>
        </code-change>
        """

        code_change = CodeChanges.from_xml(multiple_ops)

        change = code_change.changes[0]
        assert change.file_name == "complex.py"
        assert len(change.modifications) == 2
        assert len(change.additions) == 2
        assert len(change.deletions) == 0

        # Check first modification
        assert change.modifications[0].start_line == 1
        assert change.modifications[0].end_line == 5
        assert change.modifications[0].content == "Updated imports"

        # Check second modification
        assert change.modifications[1].start_line == 20
        assert change.modifications[1].end_line == 25
        assert change.modifications[1].content == "Updated function"

        # Check additions
        assert change.additions[0].content == "New function at end"
        assert change.additions[1].content == "Another new function"

    def test_parse_whitespace_handling(self):
        """Test that whitespace is properly stripped from content."""
        whitespace_markup = """
        <code-change>
            <summary>

                    Whitespace test

            </summary>
            <changes>
                <change file-name="test.py">
                    <add>

                        Content with whitespace

                    </add>
                </change>
            </changes>
        </code-change>
        """

        code_change = CodeChanges.from_xml(whitespace_markup)

        assert code_change.summary == "Whitespace test"
        assert code_change.changes[0].additions[0].content == "Content with whitespace"

    def test_parse_empty_sections(self):
        """Test parsing with empty optional sections."""
        empty_sections = """
        <code-change>
            <summary>Empty sections test</summary>
            <files-to-change>
            </files-to-change>
            <changes>
            </changes>
            <additional-steps>
            </additional-steps>
            <verification>
            </verification>
        </code-change>
        """

        code_change = CodeChanges.from_xml(empty_sections)

        assert code_change.summary == "Empty sections test"
        assert len(code_change.files_to_change) == 0
        assert len(code_change.changes) == 0
        assert len(code_change.additional_steps) == 0
        assert len(code_change.verification_steps) == 0

    def test_parse_markup_function_success(self):
        """Test the parse_markup function with valid input."""
        result = parse_markup(TEST_MARKUP)

        assert result.is_ok()
        code_change = result.unwrap()
        assert code_change.summary == "[Brief overview of all changes being made]"
        assert len(code_change.files_to_change) == 3

    def test_parse_markup_empty_input(self):
        """Test parse_markup function with empty input."""
        result = parse_markup("")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.INVALID_XML
        assert "Empty or whitespace-only markup" in error.source

    def test_parse_markup_whitespace_only(self):
        """Test parse_markup function with whitespace-only input."""
        result = parse_markup("   \n\t   ")

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.INVALID_XML
        assert "Empty or whitespace-only markup" in error.source

    def test_parse_markup_malformed_xml(self):
        """Test parse_markup function with malformed XML."""
        malformed_xml = """
        <code-change>
            <summary>Test</summary>
            <unclosed-tag>
        </code-change>
        """

        result = parse_markup(malformed_xml)

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

    def test_parse_markup_wrong_root_element(self):
        """Test parse_markup function with wrong root element."""
        wrong_root = """
        <wrong-element>
            <summary>Test</summary>
        </wrong-element>
        """

        result = parse_markup(wrong_root)

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.MISSING_ELEMENT

    def test_parse_markup_missing_required_fields(self):
        """Test parse_markup function with missing required fields."""
        missing_summary = """
        <code-change>
            <files-to-change>
                <file name="test.py" />
            </files-to-change>
        </code-change>
        """

        result = parse_markup(missing_summary)

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.PARSING_ERROR
        assert "Validation failed" in error.source

    def test_parse_markup_invalid_attribute_types(self):
        """Test parse_markup function with invalid attribute types."""
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

        result = parse_markup(invalid_types)

        assert result.is_err()
        error = result.unwrap_err()
        assert error.type == ParserErrorType.PARSING_ERROR

    def test_serialization_roundtrip(self):
        """Test that parsing and serializing produces equivalent results."""
        # Parse the original markup
        original_code_change = CodeChanges.from_xml(TEST_MARKUP)

        # Serialize back to XML
        serialized_xml = original_code_change.to_xml(pretty_print=True)

        # Parse the serialized XML
        reparsed_code_change = CodeChanges.from_xml(serialized_xml)

        # Compare key fields
        assert original_code_change.summary == reparsed_code_change.summary
        assert len(original_code_change.files_to_change) == len(
            reparsed_code_change.files_to_change
        )
        assert len(original_code_change.changes) == len(reparsed_code_change.changes)
        assert len(original_code_change.additional_steps) == len(
            reparsed_code_change.additional_steps
        )
        assert len(original_code_change.verification_steps) == len(
            reparsed_code_change.verification_steps
        )

    def test_edge_cases_special_characters(self):
        """Test parsing with special characters and CDATA."""
        special_chars = """
        <code-change>
            <summary>Special chars: &lt;>&amp;"'</summary>
            <changes>
                <change file-name="test.py">
                    <add><![CDATA[
                        def function():
                            return "Hello <world> & universe!"
                    ]]></add>
                </change>
            </changes>
        </code-change>
        """

        code_change = CodeChanges.from_xml(special_chars)

        assert "Special chars: <>&\"'" in code_change.summary
        assert (
            'return "Hello <world> & universe!"'
            in code_change.changes[0].additions[0].content
        )

    def test_large_content_handling(self):
        """Test parsing with large content blocks."""
        large_content = "x" * 10000  # 10KB of content
        large_markup = f"""
        <code-change>
            <summary>Large content test</summary>
            <changes>
                <change file-name="large.py">
                    <add>{large_content}</add>
                </change>
            </changes>
        </code-change>
        """

        code_change = CodeChanges.from_xml(large_markup)

        assert code_change.summary == "Large content test"
        assert len(code_change.changes[0].additions[0].content) == 10000
        assert code_change.changes[0].additions[0].content == large_content

    def test_unicode_content(self):
        """Test parsing with Unicode content."""
        unicode_markup = """
        <code-change>
            <summary>Unicode test: 你好世界 🌍 ñoño</summary>
            <changes>
                <change file-name="unicode.py">
                    <add>
                        # Comment with emoji: 🚀
                        def hello():
                            return "Hello 世界!"
                    </add>
                </change>
            </changes>
        </code-change>
        """

        code_change = CodeChanges.from_xml(unicode_markup)

        assert "你好世界 🌍 ñoño" in code_change.summary
        assert "🚀" in code_change.changes[0].additions[0].content
        assert "世界" in code_change.changes[0].additions[0].content
