from tools.file import list_files, read_file
TOOL_SPECS = {"list_files": list_files.list_files_spec,
              "read_file":read_file.read_file_spec}

TOOL_HANDLER = {"list_files": list_files.list_files,
              "read_file":read_file.read_file}