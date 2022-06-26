# Research Project Q4 2021-2022

## Generating δ-NFGs
Using the Python scripts in `./deltaNFG`, one can easily compute their δ-NFGs.
Example:
```python
from deltaNFG.generate_deltaNFG import NFG
NFG("Example")
```
This will generate a δ-NFG for each commit, saved in the folder `./data/delta-NFGs/Example`. The code is taken from `./subjects/Example`.
<br>
Most of the code to generate δ-NFGs is from https://github.com/PPPI/Flexeme/tree/0.2.
## Detecting and eliminating dead code
To detect dead code, one can use the Python scripts in `./deadCode`.
Example:
```python
from deadCode.dead_code_detection import revived_code
from deadCode.dead_code_elimination import elimination

revived_variables, dead_variables = revived_code("Example", 1)  # Find revived or dead variables
revived_code, dead_code = revived_code("Example", 2)  # Find revived or dead pieces of code
elimination("Example", dead_variables)  # Eliminate dead variables
```

## Getting started
In the `main.py` file, one can find a ready-to-run script.
