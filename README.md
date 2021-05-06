# TransCAD_bin
A data conversion tool to help user parse "bin" TransCAD file without installing TransCAD

## Guidance

```
├── bin2df.py 				## excution script
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

