import os
import sys

from gptscript.exec_utils import exec_cmd, stream_exec_cmd, stream_exec_cmd_with_events
from gptscript.tool import FreeForm, Tool

opt_to_arg = {
    "cache": "--disable-cache=",
    "cacheDir": "--cache-dir=",
    "quiet": "--quiet=",
    "chdir": "--chdir=",
    "subTool": "--sub-tool=",
}


def _get_command():
    if os.getenv("GPTSCRIPT_BIN") is not None:
        return os.getenv("GPTSCRIPT_BIN")

    python_bin_dir = os.path.dirname(sys.executable)
    return os.path.join(python_bin_dir, "gptscript")


def version():
    cmd = _get_command()
    out, _ = exec_cmd(cmd, ["--version"])
    return out


def list_tools():
    cmd = _get_command()
    out, _ = exec_cmd(cmd, ["--list-tools"])
    return out


def list_models():
    cmd = _get_command()
    try:
        models, _ = exec_cmd(cmd, ["--list-models"])
        return models.strip().split("\n")
    except Exception as e:
        raise e


def exec(tool, opts={}):
    cmd = _get_command()
    args = to_args(opts)
    args.append("-")
    try:
        tool_str = process_tools(tool)
        out, err = exec_cmd(cmd, args, input=tool_str)
        return out, err
    except Exception as e:
        raise e


def stream_exec(tool, opts={}):
    cmd = _get_command()
    args = to_args(opts)
    args.append("-")
    try:
        tool_str = process_tools(tool)
        process = stream_exec_cmd(cmd, args, input=tool_str)
        return process.stdout, process.stderr, process.wait
    except Exception as e:
        raise e


def stream_exec_with_events(tool, opts={}):
    cmd = _get_command()
    args = to_args(opts)
    args.append("-")
    try:
        tool_str = process_tools(tool)
        process, events = stream_exec_cmd_with_events(cmd, args, input=tool_str)
        return process.stdout, process.stderr, events, process.wait
    except Exception as e:
        raise e


def exec_file(tool_path, input="", opts={}):
    cmd = _get_command()
    args = to_args(opts)

    args.append(tool_path)

    if input != "":
        args.append(input)
    try:
        out, err = exec_cmd(cmd, args)
        return out, err
    except Exception as e:
        raise e


def stream_exec_file(tool_path, input="", opts={}):
    cmd = _get_command()
    args = to_args(opts)

    args.append(tool_path)

    if input != "":
        args.append(input)
    try:
        process = stream_exec_cmd(cmd, args)

        return process.stdout, process.stderr, process.wait
    except Exception as e:
        raise e


def stream_exec_file_with_events(tool_path, input="", opts={}):
    cmd = _get_command()
    args = to_args(opts)

    args.append(tool_path)

    if input != "":
        args.append(input)
    try:
        process, events = stream_exec_cmd_with_events(cmd, args)

        return process.stdout, process.stderr, events, process.wait
    except Exception as e:
        raise e


def to_args(opts):
    args = []
    for opt, val in opts.items():
        opt_arg = opt_to_arg.get(opt, None)
        if opt_arg is not None:
            if opt == "cache":
                args.append(opt_arg + str(not val))
            else:
                args.append(opt_arg + val)
    return args


def process_tools(tools):
    if isinstance(tools, Tool):
        return str(tools)

    if isinstance(tools, list):
        if len(tools) > 0:
            if isinstance(tools[0], Tool):
                return tool_concat(tools)
            else:
                raise Exception("Invalid tool type must be [Tool] or FreeForm")
    elif isinstance(tools, FreeForm):
        return str(tools)
    else:
        raise Exception("Invalid tool type must be [Tool] or FreeForm")


def tool_concat(tools=[]):
    resp = ""
    if len(tools) == 1:
        return str(tools[0])
    if tools:
        resp = "\n---\n".join([str(tool) for tool in tools])

    return resp
