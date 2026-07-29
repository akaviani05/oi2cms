# oi2cms

`oi2cms` is a command-line helper for turning an Olympiad problem package into
a CMS (Contest Management System) import archive. It discovers input/output
files in COCI, USACO, or user-defined layouts, assigns them to subtasks, copies
the checker, and creates a timestamped ZIP archive ready to import into CMS.

## Features

- Export COCI-style test packages to the CMS directory format.
- Export USACO-style numbered test packages, assigning test numbers to
  subtasks interactively.
- Export packages with custom filename templates using subtask and test-ID
  placeholders.
- Include a custom checker or use the included line-by-line default checker.
- Generate `problem.json`, test input/output pairs, per-subtask JSON files,
  and a `checker/` directory.
- Package every export as a ZIP archive without removing the unpacked export
  directory.
- Provide shell-completion support through Typer.

## Requirements

- Python 3.8 or newer
- [Poetry](https://python-poetry.org/)
- A CMS-compatible C++ checker and `testlib.h`

## Installation

Clone the repository and install its locked dependencies:

```bash
poetry install
```

Run the CLI through Poetry while working from the clone:

```bash
poetry run oi2cms --help
```

To install the CLI into Poetry's environment instead, use:

```bash
poetry install
poetry shell
oi2cms --help
```

The available problem exporters are:

```text
oi2cms problem coci-problem PATH [--checker CHECKER]
oi2cms problem usaco-problem PATH [--checker CHECKER]
oi2cms problem pattern-problem PATH [--checker CHECKER]
```

For shell completion, see `oi2cms --help`; Typer exposes
`--install-completion` for Bash, Zsh, Fish, and PowerShell.

## Checker setup

Unless `--checker` is supplied, the exporter expects these files:

```text
~/.oi2cms/default.cpp
~/.oi2cms/testlib.h
```

The repository includes a default checker and `testlib.h` under `testlib/`.
Install them once with:

```bash
mkdir -p ~/.oi2cms
cp testlib/default.cpp ~/.oi2cms/default.cpp
cp testlib/testlib.h ~/.oi2cms/testlib.h
```

The default checker accepts output only when the remaining lines match exactly.
For special judges, provide the path to your checker:

```bash
poetry run oi2cms problem coci-problem ./sum --checker ./checkers/sum.cpp
```

`~` is supported in the checker argument, for example
`--checker ~/.oi2cms/my-checker.cpp`.

## COCI-style export

For a problem directory named `sum`, the exporter recognizes the following
filenames directly inside that directory:

```text
sum.in.<subtask><test>
sum.out.<subtask><test>
sum.dummy.in.<test>
sum.dummy.out.<test>
```

`<subtask>` must be numeric. The rest of each test identifier may contain word
characters. Dummy tests become subtask `0` (typically samples).

For example:

```text
sum/
├── sum.dummy.in.1
├── sum.dummy.out.1
├── sum.in.1a
├── sum.out.1a
├── sum.in.1b
├── sum.out.1b
├── sum.in.2a
└── sum.out.2a
```

Export it with:

```bash
poetry run oi2cms problem coci-problem ./sum
```

The tool prints the test cases it found, then asks for the time limit, memory
limit, and configuration for every discovered subtask. Enter time in seconds
and memory in MiB. For each subtask, enter its score and the comma-separated
subtask IDs whose tests it should include. For example, a subtask `2` that
includes tests from subtasks `1` and `2` should receive `1,2`.

## USACO-style export

The USACO exporter expects numbered input/output pairs:

```text
problem/
├── 1.in
├── 1.out
├── 2.in
├── 2.out
├── 3.in
└── 3.out
```

Run:

```bash
poetry run oi2cms problem usaco-problem ./problem
```

First enter the number of scored subtasks. The exporter then asks for a test
range for each subtask from `0` through that number, where `0` is useful for
samples. Enter individual tests or inclusive ranges separated by commas:

```text
Enter number of subtasks: 2
Enter testcases in subtask 0: 1
Enter testcases in subtask 1: 2-5,8
Enter testcases in subtask 2: 6-7,9-10
```

It next asks for the shared CMS metadata and each subtask's score and included
subtasks, just as in the COCI flow.

## Pattern-based export

Use `pattern-problem` when the input and output names encode both the subtask
and the test index but do not follow the COCI or USACO conventions:

```bash
poetry run oi2cms problem pattern-problem ./trap
```

Enter an input filename pattern and an output filename pattern. Use `$s` for
the subtask and `$i` for the test index; each placeholder must occur exactly
once in each pattern. Everything else is treated as literal filename text.
For example, for files such as `trap.01.02.in` and `trap.01.02.out`, enter:

```text
Enter input filename pattern ($s=subtask, $i=index): trap.$s.$i.in
Enter output filename pattern ($s=subtask, $i=index): trap.$s.$i.out
```

This discovers the pair as subtask `01`, test `02`, then prompts for the time
and memory limits plus the score and included-subtask relation for every
discovered subtask, like the other exporters.

## Generated archive

An export of problem `sum` creates a directory and ZIP file named like:

```text
sum-CMS-26-07-28-14-30-00/
sum-CMS-26-07-28-14-30-00.zip
```

The directory contains:

```text
sum-CMS-.../
├── problem.json
├── checker/
│   ├── checker.cpp
│   └── testlib.h
├── subtasks/
│   ├── 0.json
│   ├── 1.json
│   └── ...
└── tests/
    ├── 0-1.in
    ├── 0-1.out
    ├── 1-a.in
    └── 1-a.out
```

`problem.json` contains the code and name (both derived from the directory
name), time and memory limits, batch-task settings, and a score precision of
two decimal places. Tests are ordered by subtask and then test ID. Each
subtask JSON file contains its numeric score and the CMS test names selected
at the interactive prompt.

Import the unpacked export into CMS with the TPS task loader:

```bash
cmsImportTask -L tps_task -S sum-CMS-26-07-28-14-30-00/
```

To attach the task to an existing contest, add its numeric CMS contest ID:

```bash
cmsImportTask -L tps_task -S -c CONTEST_ID sum-CMS-26-07-28-14-30-00/
```

## Current command status

`contest create`, `team create`, and `team add` are registered commands but
are placeholders; they do not currently create CMS contests, teams, or users.
The `hello` commands are simple smoke-test commands. The production workflow
in this version is the three `problem` exporters described above.

## Notes and limitations

- Every discovered test needs both an `.in` and a matching `.out` file; verify
  the printed discovery list before completing the prompts.
- The exporter creates output in the current working directory. Avoid running
  it in a location that already contains a same-second export name.
- The generated archive copies checker source; CMS still needs its normal
  checker build/import process.
- There is currently no automated test suite beyond the CLI smoke checks.
