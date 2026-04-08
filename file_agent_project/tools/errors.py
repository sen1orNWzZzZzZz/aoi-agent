from enum import Enum
from dataclasses import dataclass,field
from specs import FieldIssue

class ToolErrorCode(Enum):
    TOOL_ARGUMENT_MISSING = "tool_argument_missing"# = "工具参数缺失"
    TOOL_ARGUMENT_INVALID = "tool_argument_invalid"#"工具参数违法"
    PATH_OUT_OF_WORKSPACE = "path_out_of_workspace"#"路径超出合法范围"
    FILE_NOT_FOUND = "file_not_found"#"文件没有找到"
    DIR_NOT_FOUND = "dir_not_found" #"文件夹不存在"
    PATH_IS_FILE = "path_is_file" #"该路径是文件"
    PATH_IS_DIRECTORY = "path_is_directory"# "该路径是文件夹"
    ENCODING_UNSUPPORTED = "encoding_unsupport" #"解码方式不支持"
    IO_TEMPORARY_FAILURE = "io_temporary_failure"#"io错误"
    UNKNOWN_TOOL_ERROR = "unknown_tool_error"#"未知的工具错误"

class PlatErrorCategory(Enum):
    USER_FIXABLE = "user_fixable"#"用户可修复"
    RETRYABLE = "retryable"#"可重试"
    FATAL = "fatal"#"需终止"
    SECURITY = "security"#"安全问题"
    PROTOCOL = "protocol"#"协议问题"


@dataclass
class ToolError:
    code:ToolErrorCode
    category:PlatErrorCategory
    message:str
    field_issues: list[FieldIssue] = field(default_factory=list)
    missing_info:str | None = None
    repair_target:str | None = None
    retryable:bool | None = None
    raw_error:str | None = None