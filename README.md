# Updated Version of an old Chess Implementation

Basic Chess implementation in python.

## Overview

A quick and dirty implementation of a chess engine using only pygame to display the board.

![Screenshot](Images/example.png)

All chess rules are implemented.
No real title or endscreen, but replaybility is implemented (it's just not very pretty).



### Installing

Clone or download the repo install the requirements and run the main

```
>> pip install -r requirements.txt
>> python main.py
```

As a default you will be playing against a MinMax algorithm of depth 3. To play against a human (or as white and black) switch 

```
>> playerAgainstAi = True
```

to 

```
>> playerAgainstAi = False
```


