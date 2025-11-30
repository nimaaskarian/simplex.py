#!/usr/bin/python3
from string import whitespace, digits, ascii_letters
from enum import Enum, auto
from fractions import Fraction
import numpy as np
from tabulate import tabulate
import sys

class ReadExpressionState(Enum):
    Coefficient = auto(),
    Name = auto()

def read_expression(s: str):
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
                    denominator=1
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
    return (names, coefficients)

def simplex_data(s: str):
    lines = s.splitlines()
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
                for j,item in enumerate(constraints[i][0][0]):
                    if variable_name < item:
                        insert_index=j
                    else:
                        break
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

def print_table(function, constraints_c, names):
    constraints_show = [[str(item) for item in constraint]  for constraint in constraints_c ]
    function_show = list(map(str, function))
    print(tabulate([function_show]+constraints_show, headers=names, tablefmt="simple_grid", floatfmt="#"))

def solve_simplex_and_print_tables(data):
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
        print_table(function, constraints_c, names)
        in_variable = in_variable_function(function)
        try:
            out_variable, _ = min(((i,constraint) for i,constraint in enumerate(constraints_c) if constraint[in_variable] > 0), key=choose_out(in_variable))
        except ValueError:
            print(f"Function {function_name} is unbounded ({function_name} -> {'+' if kind == 'max' else '-'}∞)")
            return 
        print(f"Selected col {in_variable} ({names[in_variable]}) to be entered")
        print(f"Selected row {out_variable+1} to be exited")
        divide_value = [constraints_c[out_variable][in_variable]][0]
        if divide_value != 1:
            constraints_c[out_variable]=constraints_c[out_variable]/divide_value
            print(f"Used basic row operation R{out_variable+1} = R{out_variable+1}/{divide_value}")
        print_row_operation(function[in_variable], out_variable, 0)
        function = function - (constraints_c[out_variable] * function[in_variable])
        for i,constraint in enumerate(constraints_c):
            if i != out_variable:
                print_row_operation(constraint[in_variable], out_variable, i+1)
                constraints_c[i] = constraint - (constraints_c[out_variable] * constraint[in_variable])
    print_table(function, constraints_c, names)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        import fileinput
        stdin_string = ""
        for line in fileinput.input():
            stdin_string+=line
        solve_simplex_and_print_tables(simplex_data(stdin_string))
    else:
        has_multiple_files = len(sys.argv) > 2
        for i,arg in enumerate(sys.argv[1:]):
            if has_multiple_files:
                if i != 0:
                    print()
                print(f"Solving {arg}:")
            with open(arg) as fp:
                solve_simplex_and_print_tables(simplex_data(fp.read()))
