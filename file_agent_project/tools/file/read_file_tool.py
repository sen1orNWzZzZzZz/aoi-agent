from tools.specs import ToolSpec, FieldIssue
from tools.errors import ToolError, ToolErrorCode, PlatErrorCategory
from core.schemas import Action, ToolResult
from tools.file.read_file import read_file


class ReadFileTool:
      def __init__(self):
          self.spec = ToolSpec(name="read_file", required_fields=["file_name"], repair_slots={"file_name":"tool_args.file_name"}, default_user_messages={"file_name":"请提供正确的文件路径名"})

      def get_name(self):
          return "read_file"

      def get_spec(self):
          return self.spec

      def validate(self, tool_args:dict):
          if len(self.build_field_issues(tool_args=tool_args)) !=0:
              return False
          else:
              return True

      def build_field_issues(self, tool_args:dict):
          if not tool_args.get("file_name", ""):
              return [FieldIssue(field_name="file_name",target_path=self.spec.repair_slots["file_name"],reason = "missing", required=True)]
          else:
              return []
# {
#     "patch_type": "action_patch",
#     "fields": {
#       "file_name": "tool_args.file_name"
#     },
#     "missing_fields": ["file_name"]
#   }
      def apply_patch(self, action:Action, resolved_fields:dict, resume_patch:dict):
          for key in resume_patch["fields"].keys():
              if key is not None:
                if self.spec.repair_slots[key] == resume_patch["fields"][key]:
                    action.tool_args[key] = resolved_fields[key]
          return action

      def execute(self, tool_args:dict):
          if self.validate(tool_args):
              tool_result = read_file(tool_args["file_name"])
              return tool_result
          else:
              return ToolResult(content= tool_args,tool_name="read_file",success=False,error_message="tool args missing", error=ToolError(code=ToolErrorCode.TOOL_ARGUMENT_MISSING,category=PlatErrorCategory.USER_FIXABLE,field_issues=self.build_field_issues(tool_args),message=self.get_spec().default_user_messages["file_name"]))