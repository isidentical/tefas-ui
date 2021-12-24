# Tefas UI

A simple terminal UI for viewing fund P/L analysis through TEFAS.

Features (that my own bank's UI lack):
- Daily and weekly P/L
- FX comparisons

## Installation

You can simply install it through `pip`:

```
pip install tefas-ui
```

> Note: if you need forex support, please install `tefas-ui[forex]`.

## Usage

Use it with `tefas-ui`, and target it to the data file that contains the
export you took from your bank. Tefas UI only supports TEB at the moment,
but feel free to make new PRs for other banks as well.

```
tefas-ui <input file> <fund format: {teb}>
```

[![asciicast](https://asciinema.org/a/3rPBpZWufrcnYMVxk3SmSMC2J.svg)](https://asciinema.org/a/3rPBpZWufrcnYMVxk3SmSMC2J)
