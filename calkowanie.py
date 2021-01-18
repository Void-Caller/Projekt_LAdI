import copy

def parse(a):
    '''Tworzy listę znaków z przesłanego łańcucha znakowego (usuwa spacje).
    
    a-równanie w postaci ciągu znaków'''

    tab = []
    j = 0
    #rozdziela znaki na składowe tak aby zachować wieloznakowe stałe
    for i in range(len(a)):
        if a[i] in "+-/*()^":
            tab.append(a[j:i])
            tab.append(a[i])
            j = i+1
    tab.append(a[j:])
    #usuwa puste znaki i spacje
    for i in tab:
        if i == '' or i == ' ':
            tab.remove(i)

    return tab

def preoperation(a):
    '''Tworzy struktury list zagnieżdżonych dla nawiasów.
    
    a-lista składowych'''

    new = [] #nowa lista
    par = [] #lista tego co znajduje sie w nawiasach
    found = 0 #określa ile otwarć nawiasów znaleziono
    for i in range(len(a)):
        if found == 0:
            if a[i] == '(':
                found = 1
                par = [] #czyści listę kiedy znajdzie nowe niepowiązane otwarcie nawiasu
            else:
                new.append(a[i]) #kiedy nie ma otwarcia nawiasu kopiuje listę bez zmian
        else:
            if a[i] == '(':
                found = found + 1 
                par.append(a[i])
            elif a[i] == ')':
                found = found - 1
                if found > 0: #kiedy found zmiejszy się do zera oznacza to, że został zamknięty ostatni nawias
                    par.append(a[i])
                else:
                    new.append(['(', preoperation(par)]) #na zawartości nawiasu funkcja jest wywoływana ponownie
            else:
                par.append(a[i])
    return new

def operation(a, operations):
    '''Tworzy listy zagnieżdżone z których składa sie graf.
    
    a-lista składowych,
    operations-operatory'''

    for i in range(len(a)):
        if isinstance(a[i], list):
            pass #nie robi nic ponieważ ma do czynienia z listą oznaczającą nawias lub podwójnie zapakowaną listą
        elif a[i] in operations:
            #następujące instrukcje warunkowe mają na celu zapewnienie, że żadna lista nie zostanie zapakowana ponownie
            if isinstance(a[i-1], list):
                #tworzy s-wyrażenie, z których składa sie graf
                return [a[i], a[i-1], operation(a[i+1:], operations)] 
            else:
                #najpierw operator, następnie to co przed nim a potem to co po nim zamienane jest dalej
                return [a[i], a[0:i], operation(a[i+1:], operations)] 
    #kiedy nie znaleziono symbolu oznacza to, że jakaś lista została zapakowana w listę ponownie, tu jest wypakowywana    
    else: 
        if len(a) == 1 and isinstance(a[0], list):
            return a[0]

        return a

def graph(a, operations):
    '''Tworzy graf w postaci list zagnieżdżonych.
    
    a-równanie w postaci listy zagnieżdżonej
    operations-operatory'''

    #przeszukuje listy w poszukiwaniu fragmentów jeszcze nie zamienionych w s-wyrażenia
    if isinstance(a[0], list):
        #jeśli jest listą to oznacza, że jeszcze nie zostało zamienione
        a = operation(a, operations)
    elif a[0] in "+-*":
        #jeśli pierwszy element jest operatorem to znaczy, że już została dokonana zamiana i trzeba przeszukiwać dalej
        a[1] = graph(a[1], operations)
        a[2] = graph(a[2], operations)
    else:
        #tu mamy do czynienia z niezmienioną listą
        a = operation(a, operations)

    return a

def deep_graph(a):
    '''Zamienia zawartość nawiasów na grafy.
    
    a-równanie w postaci listy zagnieżdżonej'''

    #przeszukuje graf w poszukiwaniu nawiasów a następnie zamienia ich zawartość w grafy
    #kiedy tego dokona wykonuje się ponownie na nowym grafie w poszukieaniu nawiasów zagnieżdżonych
    if a[0] == '(':
        a[1] = make_a_graph(a[1])
        a[1] = deep_graph(a[1])
    elif a[0] in "+-*/^":
        a[1] = deep_graph(a[1])
        a[2] = deep_graph(a[2])
    
    return a

def delistifier(a):
    '''Wyciąga znaki z list na najniższym poziomie drzewa.
    
    a-równanie w postaci listy zagnieżdżonej'''

    #kiedy długość listy wynosi 1 to znaczy, że jest tam tylko stała albo zmienna, nie operator
    #ekstrakcja jest potrzebna aby inne funkcje mogły działać na takim grafie
    if len(a) > 2:
        a[1] = delistifier(a[1])
        a[2] = delistifier(a[2])
    elif len(a) > 1:
        a[1] = delistifier(a[1])
    else:
        a = a[0]
    
    return a

def make_a_graph(a):
    '''Tworzy graf zgodne z kolejnością wykonywania działań.

    a-lista składowych'''

    step1 = operation(a, "+")
    step2 = graph(step1, "-")
    step3 = graph(step2, "*")
    step4 = graph(step3, "/")
    step5 = graph(step4, "^")

    return step5

def assemble(a):
    '''Składa graf do formy ciągu znaków.
    
    a-równanie w postaci listy zagnieżdżonej'''

    if a[0] == '(':
        return '(' + assemble(a[1]) + ')'
    elif a[0] not in "+-/*^":
        return a
    else:
        return assemble(a[1]) + a[0] + assemble(a[2])

def found(a, v):
    '''Sprawdza czy w podanym grafie znajduje się konkretna zmienna.
    
    a-równanie w postaci listy zagnieżdżonej,
    v-szukana zmienna'''

    if a[0] in "+-*/^":
        f1 = found(a[1], v)
        f2 = found(a[2], v)
    elif a[0] == v:
        return True
    else:
        return False

    return f1 or f2

def extension(a, v):
    '''Rozszeża graf zgodnie z zasadami całkkowania.

    a-równanie w postaci listy zagnieżdżonej,
    v-zmienna po której całkujemy'''

    if a[0] == '(':
        pass
    elif a[0] not in "+-/*^":
        a = ["*", a, v] #do stałej dołączana jest zmienna
    elif a[0] in "+-":
        #iteruje po kolejnych składowych równania
        a[1] = extension(a[1], v)
        a[2] = extension(a[2], v)
    elif a[0] in "*":
        #sprawdza czy w podanej składowej nie ma zmiennej, po której całkujemy
        if found(a, v):
            if isinstance(a[1], list) and found(a[1], v):
                #jeśli w sprawdzanej liście jest szukana zmienna przeszukujemy w tę stronę
                a[1] = extension(a[1], v)
            elif isinstance(a[2], list) :
                a[2] = extension(a[2], v)
            elif a[2] == v:
                #jeśli znaleziono zmienną całkujemy po niej
                a[2] = ["*", ['(', ["/", "1", "2"]], ["^", v, "2"]]
            elif a[1] == v:
                a[1] = ["*", ['(', ["/", "1", "2"]], ["^", v, "2"]]
        else:
            a = ['*', a, v]
    elif a[0] in "^":
        if a[1] == v:
            #jeśli znaleziono potęgę zmiennej całkujemy po niej
            a = ["*", ['(', ["/", "1", str(int(a[2]) + 1)]], ["^", v, str(int(a[2]) + 1)]]

    return a

def integration(a, var):
    '''Całkuje przekazany graf zgodnie z listą zmiennych.
    
    a-równanie w postaci listy zagnieżdżonej,
    var-lista zmiennych'''

    extended = a
    for i in var:
        extended = extension(extended, i)

    #dodaje stałą
    return ["+", "C", extended]

def calculate(a, variable, value):
    '''Oblicza wartość wielomianu.
    
    a-graf w postaci listy zagnieżdżonej,
    values-słownik zawierający wszystkie zmienne wraz z ich wartościami'''

    if a[0] == "(":
        return calculate(a[1], variable, value)
    elif a[0] == "+":
        return float(calculate(a[1], variable, value)) + float(calculate(a[2], variable, value))
    elif a[0] == "-":
        return float(calculate(a[1], variable, value)) - float(calculate(a[2], variable, value))
    elif a[0] == "*":
        return float(calculate(a[1], variable, value)) * float(calculate(a[2], variable, value))
    elif a[0] == "/":
        return float(calculate(a[1], variable, value)) / float(calculate(a[2], variable, value))
    elif a[0] == "^":
        return float(calculate(a[1], variable, value)) ** float(calculate(a[2], variable, value))
    elif a == variable:
        return value
    else:
        return float(a)

def prepareFunction(a):
    '''Parsuje a potem zamienia podany ciąg znaków w graf.
    
    a-ciąg znaków'''

    parsed = parse(a)
    prepared = preoperation(parsed)
    graph1 = make_a_graph(prepared)
    ready = deep_graph(graph1)
    final = delistifier(ready)

    return final

def integrate(function, variables):
    '''Całkuje podany wielomian przez podane zmienne.
    Zwraca zcałkowane równanie w postaci ciągu znaków.
    
    equation-wielomian,
    variables-lista zmiennych'''

    #tworzy graf
    final = prepareFunction(function)
    #całkuje graf
    result = integration(final, variables)

    return assemble(result)


def integrateFile(input="input.txt", output="output.txt", r=False):
    '''Odczytuje podane równanie w postaci wielomianu 
    a następnie przetważa je i zapisuje do pliku wyjściowego.

    input-plik wejściowy(domyślnie input.txt),
    output-plik wyjściowy(domyślnie output.txt),
    r-zmienna informująca czy funkcja ma zwracać graf w postaci ciągu znaków'''
    
    with open(input, "r") as f:
        a = f.read()
        a = a.strip('\n')
    
    #oddziela zmienne od równania
    function, variables = a.split(" ")

    #rozdziela zmienne
    var = variables.split("d")
    var.remove('')

    result = integrate(function, var)
    
    with open(output, "a") as f:
        f.write(result)
        f.write('\n')

    if r:
        return result

def definitiveIntegration(function, start, end, variable):
    '''Całkje w sposób oznaczony podany wielomian przez podaną zmienną.
    Zwraca zcałkowane równanie w postaci ciągu znaków.
    Działa tylko na wielomian jednej zmiennej.
    
    equation-wielomian,
    start-początek przedziału całkowania,
    end-koniec przedziału całkowania,
    variables-zmienne'''

    #tworzy graf
    final = prepareFunction(function)
    #całkuje graf
    result = extension(final, variable)

    return calculate(result, variable, end) - calculate(result, variable, start)


def definitiveIntegrationFile(input="input.txt", output="output.txt", r=False):
    '''Odczytuje podane równanie w postaci wielomianu 
    a następnie przetważa je i zapisuje do pliku wyjściowego.

    input-plik wejściowy(domyślnie input.txt),
    output-plik wyjściowy(domyślnie output.txt)'''
    
    with open(input, "r") as f:
        a = f.read()
        a = a.strip('\n')
    
    #oddziela zmienne od równania
    function, restraints, var = a.split(" ")

    #rozdziela początek i koniec przedzialu całkowania
    res = restraints.split(',')

    result = definitiveIntegration(function,res[0], res[1], var[1])
    
    with open(output, "a") as f:
        f.write(str(result))
        f.write('\n')

    if r:
        return result