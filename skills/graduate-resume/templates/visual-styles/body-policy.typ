// One fixed body size per render; the Python driver permits at most one retry.
#let body-size(default: 10.5pt) = float(sys.inputs.at("body-font-pt", default: str(default / 1pt))) * 1pt
