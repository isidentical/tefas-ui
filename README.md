# Tefas UI

A simple terminal UI for viewing fund P/L analysis through TEFAS.

Features (that my own bank's UI lack):
- Daily and weekly P/L
- FX comparisons

## Installation

You can simply install it through `pip`:

```
pip install git+https://github.com/isidentical/tefas-ui
```

> Note: please install forex-python for currency support

## Usage

Use it with `tefas-ui`, and target it to the data file that contains the
export you took from your bank. Tefas UI only supports TEB at the moment,
but feel free to make new PRs for other banks as well.

```
tefas-ui <input file> <fund format: {teb}>
```

```
 $ tefas-ui examples/teb.txt teb
                                                                        TEFAS Index                                                                         
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Name ┃ Title                                          ┃ Purchase Date ┃ Total Shares ┃   Total Worth ┃    P/L (today) ┃ P/L (this week) ┃ P/L (all time) ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ TYH  │ TEB ASSET MANAGEMENT EQUITY FUND               │ 2021-09-14    │         3000 │  581.4570 TRY │   -52.4100 TRY │    -64.9530 TRY │   -37.8351 TRY │
│      │ (EQUITY-INTENSIVE FUND)                        │               │              │               │                │                 │                │
│ TPL  │ TEB ASSET MANAGEMENT EUROBOND (FX) DEBT        │ 2021-12-14    │         1000 │ 4351.4720 TRY │ -1432.3900 TRY │   -538.0710 TRY │  1461.9290 TRY │
│      │ INSTRUMENTS FUND                               │               │              │               │                │                 │                │
│ TMG  │ İŞ ASSET MANAGEMENT FOREIGN EQUITY FUND        │ 2021-12-10    │         6000 │ 1404.4740 TRY │  -444.7320 TRY │   -157.6200 TRY │   388.7620 TRY │
│ N/A  │ Total Portfolio                                │ N/A           │          N/A │ 6337.4030 TRY │ -1929.5320 TRY │   -760.6440 TRY │  1812.8559 TRY │
└──────┴────────────────────────────────────────────────┴───────────────┴──────────────┴───────────────┴────────────────┴─────────────────┴────────────────┘
```


```
 $ tefas-ui examples/teb.txt teb --currency usd
                                                                        TEFAS Index                                                                         
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Name ┃ Title                                            ┃ Purchase Date ┃ Total Shares ┃  Total Worth ┃   P/L (today) ┃ P/L (this week) ┃ P/L (all time) ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ TYH  │ TEB ASSET MANAGEMENT EQUITY FUND                 │ 2021-09-14    │         3000 │  44.6372 USD │   -4.0234 USD │     -0.4622 USD │    -0.5533 USD │
│      │ (EQUITY-INTENSIVE FUND)                          │               │              │              │               │                 │                │
│ TPL  │ TEB ASSET MANAGEMENT EUROBOND (FX) DEBT          │ 2021-12-14    │         1000 │ 334.0529 USD │ -109.9614 USD │     -7.0857 USD │   132.4524 USD │
│      │ INSTRUMENTS FUND                                 │               │              │              │               │                 │                │
│ TMG  │ İŞ ASSET MANAGEMENT FOREIGN EQUITY FUND          │ 2021-12-10    │         6000 │ 107.8184 USD │  -34.1411 USD │     -1.1674 USD │    43.8357 USD │
│ N/A  │ Total Portfolio                                  │ N/A           │          N/A │ 486.5085 USD │ -148.1259 USD │     -8.7153 USD │   175.7348 USD │
└──────┴──────────────────────────────────────────────────┴───────────────┴──────────────┴──────────────┴───────────────┴─────────────────┴────────────────┘
```
