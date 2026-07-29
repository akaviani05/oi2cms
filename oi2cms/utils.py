import os
import re

from oi2cms.model import Problem, Testcase

def add_testcase(testcases, subtask, test, input_path, output_path):
    flag = False
    for testcase in testcases:
        if(testcase.subtask == subtask and testcase.test == test):
            if(input_path != None):
                testcase.input_path = input_path
            if(output_path != None):
                testcase.output_path = output_path
            flag = True
    if(not flag):
        testcases.append(Testcase(subtask, test, input_path, output_path))

def find_testcases(path, in_pattern, out_pattern):
    testcases = []
    in_prog = re.compile(in_pattern)
    out_prog = re.compile(out_pattern)
    for dir, folders, files in os.walk(path):
        for filename in files:
            path = os.path.join(dir, filename)
            in_result = in_prog.match(path)
            out_result = out_prog.match(path)
            if(in_result != None):
                subtask = in_result.group("subtask")
                test = in_result.group("test")
                add_testcase(testcases, subtask, test, path, None)
            if(out_result != None):
                subtask = out_result.group("subtask")
                test = out_result.group("test")
                add_testcase(testcases, subtask, test, None, path)
    for testcase in testcases:
        print(testcase.subtask, testcase.test, testcase.input_path, testcase.output_path)
    return testcases

def find_testcases_from_templates(path, input_template, output_template):
    """Find testcase pairs using filename templates with $s and $i markers.

    ``$s`` is the subtask identifier and ``$i`` is the test identifier.  The
    rest of a template is matched literally, so a period in a filename does
    not need to be escaped by the user.
    """
    def compile_template(template, label):
        required_markers = ("$s", "$i")
        missing_markers = [marker for marker in required_markers
                           if marker not in template]
        if missing_markers:
            raise ValueError(
                f"{label} pattern must contain {', '.join(missing_markers)}."
            )
        if template.count("$s") != 1 or template.count("$i") != 1:
            raise ValueError(f"{label} pattern must contain $s and $i once each.")

        escaped = re.escape(template)
        escaped = escaped.replace(r"\$s", r"(?P<subtask>.+?)")
        escaped = escaped.replace(r"\$i", r"(?P<test>.+?)")
        return re.compile(escaped)

    input_pattern = compile_template(input_template, "Input")
    output_pattern = compile_template(output_template, "Output")
    testcases = []

    for directory, folders, files in os.walk(path):
        for filename in files:
            input_result = input_pattern.fullmatch(filename)
            output_result = output_pattern.fullmatch(filename)
            file_path = os.path.join(directory, filename)
            if input_result is not None:
                add_testcase(testcases, input_result.group("subtask"),
                             input_result.group("test"), file_path, None)
            if output_result is not None:
                add_testcase(testcases, output_result.group("subtask"),
                             output_result.group("test"), None, file_path)

    for testcase in testcases:
        print(testcase.subtask, testcase.test,
              testcase.input_path, testcase.output_path)
    return testcases

def find_specific_subtask(path, subtask, in_pattern, out_pattern):
    testcases = []
    in_prog = re.compile(in_pattern)
    out_prog = re.compile(out_pattern)
    for dir, folders, files in os.walk(path):
        for filename in files:
            path = os.path.join(dir, filename)
            in_result = in_prog.match(path)
            out_result = out_prog.match(path)
            if(in_result != None):
                test = in_result.group("test")
                add_testcase(testcases, subtask, test, path, None)
            if(out_result != None):
                test = out_result.group("test")
                add_testcase(testcases, subtask, test, None, path)
    for testcase in testcases:
        print(testcase.subtask, testcase.test, testcase.input_path, testcase.output_path)
    return testcases
