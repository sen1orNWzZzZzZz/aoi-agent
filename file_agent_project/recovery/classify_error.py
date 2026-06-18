

"""  分类错误"""

from tool_layer.base import ToolResult


def classify_error(tool_result: ToolResult) -> str:
    error_msg = tool_result.error_message or ""
    user_fixable = ["不存在", "路径", "目录", "不是文件", "超出工作区范围"]
    fatal = ["UTF-8", "utf-8", "编码", "encode", "Permission denied"]

    if any(k in error_msg for k in user_fixable):
        return "user_fixable"
    if any(k in error_msg for k in fatal):
        return "fatal"
    return "retryable"

