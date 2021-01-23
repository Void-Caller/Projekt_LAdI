import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import networkx as nx
import ast

# parsuje przesłany ciąg znaków
def parse(a):
    '''Tworzy listę znaków z przesłanego łańcucha znakowego (usuwa spacje).

    a-równanie w postaci ciągu znaków'''

    tab = []
    j = 0
    # rozdziela znaki na składowe tak aby zachować wieloznakowe stałe
    for i in range(len(a)):
        if a[i] in "+-/*()^":
            tab.append(a[j:i])
            tab.append(a[i])
            j = i + 1
    tab.append(a[j:])
    # usuwa puste znaki i spacje
    for i in tab:
        if i == '' or i == ' ':
            tab.remove(i)

    return tab


def preoperation(a):
    '''Tworzy struktury list zagnieżdżonych dla nawiasów.

    a-lista składowych'''

    new = []  # nowa lista
    par = []  # lista tego co znajduje sie w nawiasach
    found = 0  # określa ile otwarć nawiasów znaleziono
    for i in range(len(a)):
        if found == 0:
            if a[i] == '(':
                found = 1
                par = []  # czyści listę kiedy znajdzie nowe niepowiązane otwarcie nawiasu
            else:
                new.append(a[i])  # kiedy nie ma otwarcia nawiasu kopiuje listę bez zmian
        else:
            if a[i] == '(':
                found = found + 1
                par.append(a[i])
            elif a[i] == ')':
                found = found - 1
                if found > 0:  # kiedy found zmiejszy się do zera oznacza to, że został zamknięty ostatni nawias
                    par.append(a[i])
                else:
                    new.append(['(', preoperation(par)])  # na zawartości nawiasu funkcja jest wywoływana ponownie
            else:
                par.append(a[i])
    return new


def operation(a, operations):
    '''Tworzy listy zagnieżdżone z których składa sie graf.

    a-lista składowych,
    operations-operatory'''

    for i in range(len(a)):
        if isinstance(a[i], list):
            pass  # nie robi nic ponieważ ma do czynienia z listą oznaczającą nawias lub podwójnie zapakowaną listą
        elif a[i] in operations:
            # następujące instrukcje warunkowe mają na celu zapewnienie, że żadna lista nie zostanie zapakowana ponownie
            if isinstance(a[i - 1], list):
                # tworzy s-wyrażenie, z których składa sie graf
                return [a[i], a[i - 1], operation(a[i + 1:], operations)]
            else:
                # najpierw operator, następnie to co przed nim a potem to co po nim zamienane jest dalej
                return [a[i], a[0:i], operation(a[i + 1:], operations)]
                # kiedy nie znaleziono symbolu oznacza to, że jakaś lista została zapakowana w listę ponownie, tu jest wypakowywana
    else:
        if len(a) == 1 and isinstance(a[0], list):
            return a[0]

        return a


def graph(a, operations):
    '''Tworzy graf w postaci list zagnieżdżonych.

    a-równanie w postaci listy zagnieżdżonej
    operations-operatory'''

    # przeszukuje listy w poszukiwaniu fragmentów jeszcze nie zamienionych w s-wyrażenia
    if isinstance(a[0], list):
        # jeśli jest listą to oznacza, że jeszcze nie zostało zamienione
        a = operation(a, operations)
    elif a[0] in "+-*":
        # jeśli pierwszy element jest operatorem to znaczy, że już została dokonana zamiana i trzeba przeszukiwać dalej
        a[1] = graph(a[1], operations)
        a[2] = graph(a[2], operations)
    else:
        # tu mamy do czynienia z niezmienioną listą
        a = operation(a, operations)

    return a


def deep_graph(a):
    '''Zamienia zawartość nawiasów na grafy.

    a-równanie w postaci listy zagnieżdżonej'''

    # przeszukuje graf w poszukiwaniu nawiasów a następnie zamienia ich zawartość w grafy
    # kiedy tego dokona wykonuje się ponownie na nowym grafie w poszukieaniu nawiasów zagnieżdżonych
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

    # kiedy długość listy wynosi 1 to znaczy, że jest tam tylko stała albo zmienna, nie operator
    # ekstrakcja jest potrzebna aby inne funkcje mogły działać na takim grafie
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
        a = ["*", a, v]  # do stałej dołączana jest zmienna
    elif a[0] in "+-":
        # iteruje po kolejnych składowych równania
        a[1] = extension(a[1], v)
        a[2] = extension(a[2], v)
    elif a[0] in "*":
        # sprawdza czy w podanej składowej nie ma zmiennej, po której całkujemy
        if found(a, v):
            if isinstance(a[1], list) and found(a[1], v):
                # jeśli w sprawdzanej liście jest szukana zmienna przeszukujemy w tę stronę
                a[1] = extension(a[1], v)
            elif isinstance(a[2], list):
                a[2] = extension(a[2], v)
            elif a[2] == v:
                # jeśli znaleziono zmienną całkujemy po niej
                a[2] = ["*", ['(', ["/", "1", "2"]], ["^", v, "2"]]
            elif a[1] == v:
                a[1] = ["*", ['(', ["/", "1", "2"]], ["^", v, "2"]]
        else:
            a = ['*', a, v]
    elif a[0] in "^":
        if a[1] == v:
            # jeśli znaleziono potęgę zmiennej całkujemy po niej
            a = ["*", ['(', ["/", "1", str(int(a[2]) + 1)]], ["^", v, str(int(a[2]) + 1)]]

    return a


def integration(a, var):
    '''Całkuje przekazany graf zgodnie z listą zmiennych.

    a-równanie w postaci listy zagnieżdżonej,
    var-lista zmiennych'''

    extended = a
    for i in var:
        extended = extension(extended, i)

    # dodaje stałą
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

    # tworzy graf
    final = prepareFunction(function)
    # całkuje graf
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

    # oddziela zmienne od równania
    function, variables = a.split(" ")

    # rozdziela zmienne
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

    # tworzy graf
    final = prepareFunction(function)
    # całkuje graf
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

    # oddziela zmienne od równania
    function, restraints, var = a.split(" ")

    # rozdziela początek i koniec przedzialu całkowania
    res = restraints.split(',')

    result = definitiveIntegration(function, res[0], res[1], var[1])

    with open(output, "a") as f:
        f.write(str(result))
        f.write('\n')

    if r:
        return result

#rozszerzenie funkcjonalności o macierze sąsiedztwa

def integrate_to_graph(function, variables):
    '''Całkuje podany wielomian przez podane zmienne.
    Zwraca scałkowane równanie w postaci tabeli grafu.

    equation-wielomian,
    variables-lista zmiennych'''

    # tworzy graf
    final = prepareFunction(function)
    # całkuje graf
    result = integration(final, variables)

    return result

def integrate_from_File(input="input.txt"):
    '''Odczytuje podane równanie w postaci wielomianu
    a następnie przetwarza je i zwraca graf w formie tablicy.

    input-plik wejściowy(domyślnie input.txt),
    '''

    with open(input, "r") as f:
        a = f.read()
        a = a.strip('\n')

    # oddziela zmienne od równania
    function, variables = a.split(" ")

    # rozdziela zmienne
    var = variables.split("d")
    var.remove('')

    result = integrate_to_graph(function, var)
    return result


#zliczanie wierzchołków grafu
def count_vertices(graph):
    '''Zwraca liczbę wierzchołków grafu.

        graph - graf, którego wierzchołki zliczamy.
    '''
    i = 0
    for vertice in graph:
        if isinstance(vertice, list):
            i += count_vertices(vertice)
        else:
            i += 1
    return i

#wypełnia macierz sąsiedztwa nad przekątną
def map_graph(matrix, graph, row, col):
    '''Rekurencyjne uzupełnianie macierzy sąsiedztwa grafu nad przekątną

        matrix - macierz do uzupełnienia
        graph - graf w postaci tablicy tablic
        row - wiersz
        col - kolumna
    '''
    if isinstance(graph[1], list):
        col += 1
        matrix[row][col] = 1
        tmp_row = col
        tmp = map_graph(matrix, graph[1], tmp_row, col)
        col += count_vertices(graph[1])-1
    else:
        col += 1
        matrix[row][col] = 1

    if len(graph) >= 3:
       if isinstance(graph[2], list):
           col += 1
           matrix[row][col] = 1
           tmp_row = col
           tmp = map_graph(matrix, graph[2], tmp_row, col)
           col += count_vertices(graph[1])-1
       else:
           col += 1
           matrix[row][col] = 1

    return 0

def map_graph_labels(labels, graph, row, col):
    '''Rekurencyjne przypisywanie oznaczeń do wierzchołków grafu na rysunku.

            labels - słownik etykiet
            graph - graf w postaci tablicy tablic
            row - wiersz
            col - kolumna
        '''

    if not (row in labels.keys()):
        labels[row] = graph[0]

    if isinstance(graph[1], list):
        col += 1
        tmp_row = col
        tmp = map_graph_labels(labels, graph[1], tmp_row, col)
        col += count_vertices(graph[1])-1
    else:
        col += 1
        if not (col in labels.keys()):
            labels[col] = graph[1]

    if len(graph) >= 3:
       if isinstance(graph[2], list):
           col += 1
           tmp_row = col
           tmp = map_graph_labels(labels, graph[2], tmp_row, col)
           col += count_vertices(graph[1])-1
       else:
           col += 1
           if not (col in labels.keys()):
               labels[col] = graph[2]

    return 0


def map_full(graph):
    '''Funkcja tworząca macierz sąsiedztwa podanego grafu. Zwraca macierz sąsiedztwa.

        graph - graf w postaci tablicy tablic
    '''
    graph_count = count_vertices(graph)

    graph_matrix = np.zeros([graph_count, graph_count], dtype=int)

    map_graph(graph_matrix, graph, 0, 0)

    tmp = graph_matrix.transpose()
    # złożenie górnej i dolnej macierzy w wypełnioną macierz sąsiedzttwa.
    graph_matrix += tmp

    return graph_matrix


def print_graph(graph, output='test.pdf'):
    '''Funkcja rysująca graf i zapisująca go w pliku.

    graph - rysowany graf
    output - string z nazwą pliku zapisu

    '''

    labels = {}

    graph_matrix = map_full(graph)

    map_graph_labels(labels, graph, 0, 0)
    pp = PdfPages(output)
    G = nx.from_numpy_matrix(np.array(graph_matrix))
    pos = nx.spring_layout(G)

    node_colors = ['r']
    for i in range(count_vertices(graph)-1):
        node_colors.append('#1f77b4')

    g = nx.draw(G, with_labels=True, labels=labels, pos=pos, node_color=node_colors)
    # zapisuję graf do pliku
    pp.savefig(g)
    # czyszcze rysowaną figurę przed następnym rysunkiem.
    plt.clf()
    pp.close()

def save_matrix(matrix, labels, output='matrix.txt'):
    '''Zapisuje macierz sąsiedztwa w pliku tekstowym.

        matrix - macierz do zapisu
        labels - etykiety wierzchołków
        output - nazwa pliku zapisu
    '''
    with open(output, "w") as o:
        o.write(str(labels)+'\n')
        o.write(np.array2string(matrix)[1:-1])

def load_matrix(input='matrix.txt'):
    '''Wczytuje macierz sąsiedztwa z pliku i zwraca ją oraz jej etykiety.

        input - plik zapisu
    '''
    adj_matrix = []
    label = ''

    with open(input, 'r') as myfile:
        label = myfile.readline()
        for line in myfile:
            l = line.replace(' ', '').replace('[', '').replace(']', '').replace('\n', '')

            matrix = list(l)

            mat = [int(x) for x in matrix]

            adj_matrix.append(mat)
    return (np.array(adj_matrix), ast.literal_eval(label))



if __name__ == '__main__':

    graph = integrate_from_File()

    graph_matrix = map_full(graph)

    labels = {}
    map_graph_labels(labels, graph, 0, 0)

    #print(graph)

    print(graph_matrix)
    save_matrix(graph_matrix, labels)

    matrix_test = load_matrix()

    print(matrix_test[0])
    print(matrix_test[1])

    print_graph(graph)