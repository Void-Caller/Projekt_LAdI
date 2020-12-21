# parsuje przesłany ciąg znaków
def parse(a, operations):
    for i in range(len(a)):
        if a[i] in operations:
            return [a[i], a[0:i], parse(a[i+1:], operations)] 
    else:
        return a

# przeszukuje graf w poszukiwaniu niesparsowanych elementów
def graph(a, operations):
    if a[1][0] in "+-*":
        a[1] = graph(a[1], operations)
    else:
        a[1] = parse(a[1], operations)

    if a[2][0] in "+-*":
        a[2] = graph(a[2], operations)
    else:
        a[2] = parse(a[2], operations)

    return a

# składa graf z powrotem w ciąg znaków
def assemble(a):
    if a[0] not in "+-/*^":
        return a
    else:
        return assemble(a[1]) + a[0] + assemble(a[2])

# rozszeża graf zgodnie z zasadami całkowania
def extension(a):
    if a[0] not in "+-/*^":
        a = ["*", a, "x"]
    elif a[0] in "+-":
        a[1] = extension(a[1])
        a[2] = extension(a[2])
    elif a[0] in "*":
        if a[2] == "x":
            a[2] = ["*", ["/", "1", "2"], ["^", "x", "2"]]
        else:
            a[2] = extension(a[2])
    elif a[0] in "^":
        a = ["*", ["/", "1", str(int(a[2]) + 1)], ["^", "x", str(int(a[2]) + 1)]]

    return a

# całkuje graf
def integration(a):
    extended = extension(a)
    return ["+", "C", extended]

# zmniejsza graf zgodnie z zasadami różniczkowania
def retraction(a):
    if a[0] in "+-":
        a[1] = retraction(a[1])
        a[2] = retraction(a[2])
    elif a[0] in "*":
        if a[2] == "x":
            a = a[1]
        else:
            a[2] = retraction(a[2])
    elif a[0] in "^":
        a = ["*", a[2], ["^", "x", str(int(a[2]) - 1)]]

    return a

# różniczkuje graf
def differentiation(a):
    retracted = retraction(a)
    return retracted[2]

# oblicza wartość funkcji reprezentowanej przez graf
def calculate(a, value):
    if a[0] == "+":
        return float(calculate(a[1], value)) + float(calculate(a[2], value))
    elif a[0] == "-":
        return float(calculate(a[1], value)) - float(calculate(a[2], value))
    elif a[0] == "*":
        return float(calculate(a[1], value)) * float(calculate(a[2], value))
    elif a[0] == "/":
        return float(calculate(a[1], value)) / float(calculate(a[2], value))
    elif a[0] == "^":
        return float(calculate(a[1], value)) ** float(calculate(a[2], value))
    elif a == "x":
        return value
    else:
        return float(a)

# obliczanie wartości całki za pomocą metody prostokątów
def rectangular(a, x0, xn, dx):
    x = x0 + dx
    field = 0
    while x <= xn:
        field = field + (dx * abs(calculate(a, x)))
        x = x + dx

    return field

# obliczanie wartości pochodnej za pomocą centralnrj metody Eulera
def central(a, x0, dx):
    x1 = x0 - dx
    x2 = x0 + dx
    return (calculate(a, x2) - calculate(a, x1)) / (x2 - x1) 

if __name__ == '__main__':
    import copy

    with open("input.txt", "r") as f:
        a = f.read()
        a = a.strip('\n')

# kilka etapów parsowania dla zapewnienia poprawności wykonywania dziłań
    stack = parse(a, "+")
    parsed = graph(stack, "-")
    pregraph = graph(parsed, "*")
    graph = graph(pregraph, "/^")

    print(rectangular(graph, 2, 6, 0.5))
    print(central(graph, 2, 0.5))

    integral = integration(copy.deepcopy(graph))

    derivative = differentiation(copy.deepcopy(graph))

    with open("output.txt", "a") as f:
        f.write(assemble(integral))
        f.write('\n')
        f.write(assemble(derivative))
