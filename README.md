# TransCAD_bin
A data conversion tool to help user parse "bin" TransCAD file without installing TransCAD

*   [![][001colab]](https://colab.research.google.com/github/jinsanity07git/TransCAD_bin/blob/main/notebooks/bin2df.ipynb ) 
*   [![][002colab]](https://colab.research.google.com/github/jinsanity07git/TransCAD_bin/blob/main/notebooks/bin2df_widget.ipynb ) 

## Guidance

```
├── bin2df.py 				## execution script
├── input    					## sample input file
│   ├── BOSTON.DCB
│   ├── BOSTON.bin
├── output						## corresponding output file
│   ├── BOSTON.csv 
└── transcad 				  ## supporting parsing pacakge
```

User-specified parameter: 

* `fname` : input the name of the `DCB` and `bin` file without suffix eg. "BOSTON"

```python
convert(fname = "BOSTON" )
```

Note: 

* Use Python 3 as the runtime environment 
* Use pandas version later than 1.0.1

[001colab]: https://img.shields.io/badge/colab-gold "Small"
[002colab]: https://img.shields.io/badge/colab-widget-gold "Small"
