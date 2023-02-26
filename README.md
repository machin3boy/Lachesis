# Simple-Lachesis

A simplified implementation of Lachesis in Go and in Python (the latter of which is still in the works) in order to simulate/mechanize runs of the protocol and examine its properties of Liveness, Safety, etc. 

## GoLachesis:

-  this is an implementation of Lachesis in Go
-  run `main.go`
-  reading files and setting the validators is currently done through `main.go`
-  some sample DAGs and the script to generate them are available in `Simple-Lachesis/GoLachesis/inputs`

## PyLachesis:

-  this is an implementation of Lachesis in Python
-  Another port/implementation of Lachesis 

### Why Both?

-  Go is (far) more performant, but Python is easier to add changes to ad-hoc
-  The idea is to leverage the benefits of both languages
-  Python has more libraries for graphing and data science
