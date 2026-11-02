import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.mcp_client import format_call_result, make_tool_schema


class MCPToolAdapterTests(unittest.TestCase):
    def test_schema_has_server_prefix_and_input_schema(self):
        tool = SimpleNamespace(
            name="list_pets",
            description="List pets",
            input_schema={
                "type": "object",
                "properties": {"page": {"type": "integer"}},
                "required": ["page"],
            },
        )

        schema = make_tool_schema("pet-hospital", tool)

        self.assertEqual(schema["function"]["name"], "mcp_pet_hospital_list_pets")
        self.assertEqual(schema["function"]["description"], "List pets")
        self.assertEqual(schema["function"]["parameters"], tool.input_schema)

    def test_schema_resolves_name_collisions(self):
        tool = SimpleNamespace(name="list_pets", description="", inputSchema={})

        schema = make_tool_schema("pet-hospital", tool, {"mcp_pet_hospital_list_pets"})

        self.assertNotEqual(schema["function"]["name"], "mcp_pet_hospital_list_pets")
        self.assertLessEqual(len(schema["function"]["name"]), 64)

    def test_result_preserves_text_and_structured_content(self):
        result = SimpleNamespace(
            content=[SimpleNamespace(text="Found pets")],
            structuredContent={"pets": [{"name": "Mimi"}]},
            isError=False,
        )

        formatted = format_call_result(result)

        self.assertIn('"text": "Found pets"', formatted)
        self.assertIn('"name": "Mimi"', formatted)

    def test_result_marks_mcp_errors(self):
        result = SimpleNamespace(
            content=[SimpleNamespace(text="Backend unavailable")],
            structuredContent=None,
            isError=True,
        )

        self.assertEqual(
            format_call_result(result), "MCP 工具返回错误：Backend unavailable"
        )


if __name__ == "__main__":
    unittest.main()