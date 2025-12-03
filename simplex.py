#!/usr/bin/python3
from enum import Enum, auto
from fractions import Fraction

class ReadExpressionState(Enum):
    Coefficient = auto(),
    Name = auto()

def read_expression(s: str):
    from string import whitespace, digits, ascii_letters
    state = ReadExpressionState.Coefficient
    numerator = 1
    denominator = 1
    coefficients = []
    names = []
    i = 0
    while i < len(s):
        if s[i] in whitespace:
            i+=1
            continue
        match state:
            case ReadExpressionState.Coefficient:
                if s[i] == '-':
                    numerator=-1
                elif s[i] == '+':
                    numerator=1
                else:
                    numerator_str = ""
                    denominator_str = ""
                    while i < len(s) and s[i] in digits:
                        numerator_str+=s[i]
                        i+=1
                    if s[i] == "/":
                        i+=1
                        while i < len(s) and s[i] in digits:
                            denominator_str+=s[i]
                            i+=1
                    if numerator_str:
                        numerator *= int(numerator_str)
                    if denominator_str:
                        denominator *= int(denominator_str)
                    if s[i] in ascii_letters:
                        state = ReadExpressionState.Name
                    continue
            case ReadExpressionState.Name:
                name = ""
                while i < len(s) and s[i] not in ["+", "-"]:
                    if s[i] in whitespace:
                        i+=1
                        continue
                    name+=s[i]
                    i+=1
                if name:
                    coefficients.append(Fraction(numerator, denominator))
                    names.append(name)
                    numerator=1
                    denominator=1
                    state = ReadExpressionState.Coefficient
                continue
        i+=1
    names_coefficients = sorted(zip(names, coefficients))
    sorted_names = [name for name,_ in names_coefficients]
    sorted_coefficients = [coefficient for _,coefficient in names_coefficients]

    return (sorted_names, sorted_coefficients)

def simplex_data(s: str):
    lines = list(filter(lambda line: not line.strip().startswith("#"), s.splitlines()))
    kind, function = lines[0].split(" ",1)
    kind = kind[:3].lower()
    if kind not in ["max", "min"]:
        raise Exception(f"Invalid kind {kind}")
    try:
        function_name, function = function.split("=",1)
        function_name = function_name.strip()
    except ValueError:
        function_name = "z"
    function = read_expression(function)
    constraints = [[item.strip() for item in constraint.split("<=")] for constraint in lines[1:]]
    constraints = [(read_expression(expression), Fraction(value)) for expression, value in constraints]
    for variable_name in function[0]:
        for i,constraint in enumerate(constraints):
            if variable_name not in constraint[0][0]:
                insert_index=len(constraints[i][0][0])
                for j in range(len(constraints[i][0][0])-1, -1, -1):
                    item = constraints[i][0][0][j]
                    if variable_name < item:
                        insert_index=j
                constraints[i][0][0].insert(insert_index, variable_name)
                constraints[i][0][1].insert(insert_index, 0)
    for i in range(len(constraints)):
        slack_name=f"s{i+1}"
        function[0].append(slack_name)
        function[1].append(Fraction(0))
        constraints[i][0][0].append(slack_name)
        constraints[i][0][1].append(Fraction(1))
        for j in range(len(constraints)):
            if j != i:
                constraints[j][0][0].append(slack_name)
                constraints[j][0][1].append(0)
                
    return kind, function_name, function, constraints

def choose_out(in_variable):
    def choose(data):
        key = data[1][-1]/data[1][in_variable]
        return key
    return choose

def print_row_operation(coefficient, out_i, current_i):
    if coefficient == 0:
        return
    if coefficient < 0:
        coefficient = f"+ {coefficient*-1}" 
    else:
        coefficient = f"- {coefficient}" 
    print(f"Used basic row operation R{current_i} = R{current_i} {coefficient}R{out_i+1}")

def print_table(function, constraints_c, names, tablefmt):
    from tabulate import tabulate
    constraints_show = [[str(item) for item in constraint]  for constraint in constraints_c ]
    function_show = list(map(str, function))
    print(tabulate([function_show]+constraints_show, headers=names, tablefmt=tablefmt, floatfmt="#"))

def solve_simplex_and_print_tables(data, args):
    import numpy as np
    kind, function_name, function, constraints = data
    if kind == "max":
        hasnt_ended = lambda f: min(f) < 0
        in_variable_function = np.argmin
    else:
        hasnt_ended = lambda f: max(f) > 0
        in_variable_function = np.argmax

    constraints_c = []
    names = function[0]+["RHS"]
    for i, constraint in enumerate(constraints):
        constraints_c.append(np.array(constraint[0][1]+[constraint[1]]))
    function = np.array(function[1]+[0])

    function = function*-1
    while hasnt_ended(function):
        print_table(function, constraints_c, names, args.tablefmt)
        in_variable = in_variable_function(function)
        try:
            out_variable, _ = min(((i,constraint) for i,constraint in enumerate(constraints_c) if constraint[in_variable] > 0), key=choose_out(in_variable))
        except ValueError:
            if not args.table_only:
                print(f"Function {function_name} is unbounded ({function_name} -> {'+' if kind == 'max' else '-'}∞)")
            return 
        if not args.table_only:
            print(f"Selected col {in_variable} ({names[in_variable]}) to be entered")
            print(f"Selected row {out_variable+1} to be exited")
        divide_value = constraints_c[out_variable][in_variable]
        if divide_value != 1:
            constraints_c[out_variable]=constraints_c[out_variable]/divide_value
            if not args.table_only:
                print(f"Used basic row operation R{out_variable+1} = R{out_variable+1}/{divide_value}")
        if not args.table_only:
            print_row_operation(function[in_variable], out_variable, 0)
        function = function - (constraints_c[out_variable] * function[in_variable])
        for i,constraint in enumerate(constraints_c):
            if i != out_variable:
                if not args.table_only:
                    print_row_operation(constraint[in_variable], out_variable, i+1)
                constraints_c[i] = constraint - (constraints_c[out_variable] * constraint[in_variable])
    print_table(function, constraints_c, names, args.tablefmt)
    for i,z in enumerate(function):
        if z == 0:
            if sum(constraint[i] for constraint in constraints_c) != 1:
                try:
                    out_variable, _ = min(((j,constraint) for j,constraint in enumerate(constraints_c) if constraint[i] > 0), key=choose_out(i))
                    print(f"Col {i} ({names[i]}) can be entered as well, to produce the same output.")
                    print(f"That way row {out_variable+1} would exit")
                except ValueError:
                    break
    return function[-1]

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(prog="simplex.py", description="a simple simplex solver for unix nerds")
    parser.add_argument("filenames", nargs="*", help="files to process simplex from. each file is considered a simplex")
    parser.add_argument("--table-only", action="store_true", help="only print tables. don't be verbose about operations, selections and failures")
    parser.add_argument("--tablefmt", default="simple_outline", help="table format. for all possible formats check https://pypi.org/project/tabulate")
    args = parser.parse_args()
    if len(args.filenames) == 0:
        import fileinput
        stdin_string = ""
        for line in fileinput.input():
            stdin_string+=line
        solve_simplex_and_print_tables(simplex_data(stdin_string), args)
    else:
        has_multiple_files = len(args.filenames) > 1
        for i,arg in enumerate(args.filenames):
            if has_multiple_files:
                if i != 0:
                    print()
                print(f"Solving {arg}:")
            with open(arg) as fp:
                solve_simplex_and_print_tables(simplex_data(fp.read()), args)
