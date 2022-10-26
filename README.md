# Tefas UI

A simple terminal UI for viewing fund P/L analysis through TEFAS.

Features (that my own bank's UI lack):
- Daily and weekly P/L
- FX comparisons

## Installation

Install it through `pip`:

```
pip install tefas-ui
```

> Note: if you need forex support, please install `tefas-ui[forex]`.

## Usage

The P/L sheets and the other information can be simply generated by pointing `tefas-ui`
CLI command to your input file (something that you export from your bank). It will try
to parse it (if it is one of the supported formats) and render it.

```
tefas-ui <input file> <fund format: {teb}>
```

[![asciicast](https://asciinema.org/a/3rPBpZWufrcnYMVxk3SmSMC2J.svg)](https://asciinema.org/a/3rPBpZWufrcnYMVxk3SmSMC2J)
