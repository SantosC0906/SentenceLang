import re

def interpret(filename):
    with open(filename) as file:
        global variables, methods
        variables = {}
        methods = {}  # Store methods and their parameters
        lines = file.readlines()
        index = 0
        
        while index < len(lines):
            line = lines[index].strip()
            
            # Skip empty lines
            if not line:
                index += 1
                continue

            # Handle rewrite command
            if line == "rewrite.":
                print("\nBack to Python:")
                print("-" * 20)
                python_code = translate_to_python(filename)
                print(python_code)
                index += 1
                continue
            
            # Method declaration with parameters
            method_with_params = re.match(r"The essay (\w+) needs (.*?)$", line)
            if method_with_params:
                method_name = method_with_params.group(1)
                params = [p.strip() for p in method_with_params.group(2).split(',')]
                index = handle_method_declaration(methods, lines, index, method_name, params)
                continue

            # Method declaration without parameters
            method_decl = re.match(r"The essay (\w+)$", line)
            if method_decl:
                method_name = method_decl.group(1)
                index = handle_method_declaration(methods, lines, index, method_name, [])
                continue

            # Method call with parameters
            method_call_params = re.match(r"Read (\w+) with (.*?)\.", line)
            if method_call_params:
                method_name = method_call_params.group(1)
                args = [arg.strip() for arg in method_call_params.group(2).split(',')]
                handle_method_call(variables, methods, method_name, args)
                index += 1
                continue

            # Method call without parameters
            method_call = re.match(r"Read (\w+)\.", line)
            if method_call:
                method_name = method_call.group(1)
                handle_method_call(variables, methods, method_name, [])
                index += 1
                continue
            
            # Simple assignment (like "x is 1")
            simple_assign = re.match(r"(\w+) is (\d+)", line)
            if simple_assign:
                var_name, value = simple_assign.groups()
                variables[var_name] = int(value)
                index += 1
                continue
                
            # Variable declaration
            var_decl = re.match(r"(\w+) is (a \w+)\.", line)
            if var_decl:
                var_name, var_type = var_decl.groups()
                handle_variable_declaration(variables, var_name, var_type)
                index += 1
                continue
            
            # Until loop (new syntax)
            until_loop = re.match(r"Until (\w+) is (\w+) repeat this paragraph", line)
            if until_loop:
                var_name, max_var = until_loop.groups()
                index = handle_until_loop(variables, lines, index, var_name, max_var)
                continue
            
            # For loop (original syntax)
            for_loop = re.match(r"Starting at (\w+) is (\d+) repeat this paragraph (\d+) times\.", line)
            if for_loop:
                var_name, start_val, times = for_loop.groups()
                index = handle_for_loop(variables, lines, index, var_name, int(start_val), int(times))
                continue
            
            # If statement with module operation
            if_module = re.match(r"when module (\w+) by (\d+) is (\d+)( and module (\w+) by (\d+) is (\d+))? enter this paragraph", line, re.IGNORECASE)
            if if_module:
                index = handle_module_if(variables, lines, index, if_module)
                continue
            
            # Unless statement (new syntax)
            unless_stmt = re.match(r"unless module (\w+) by (\d+) is (\d+) enter this paragraph", line)
            if unless_stmt:
                index = handle_unless_statement(variables, lines, index, unless_stmt)
                continue
            
            # Regular if statement
            if_stmt = re.match(r"When (.*?) enter this paragraph", line)
            if if_stmt:
                condition = if_stmt.group(1)
                index = handle_if_statement(variables, lines, index, condition)
                continue
            
            # Arithmetic operations
            if handle_arithmetic(variables, line):
                index += 1
                continue
            
            # Print statement
            if handle_print(variables, line):
                index += 1
                continue
            
            index += 1

def translate_to_python(filename):
    """Translate the program code to Python"""
    with open(filename) as file:
        lines = file.readlines()
        python_code = []
        indent_level = 0
        index = 0
        
        while index < len(lines):
            line = lines[index].strip()
            if line == "rewrite.":  # Skip the rewrite command
                index += 1
                continue
                
            indentation = "    " * indent_level
            
            if not line:
                index += 1
                continue
            
            # Method declaration with parameters
            method_with_params = re.match(r"The essay (\w+) needs (.*?)$", line)
            if method_with_params:
                method_name = method_with_params.group(1)
                params = [p.strip() for p in method_with_params.group(2).split(',')]
                python_code.append(f"{indentation}def {method_name}({', '.join(params)}):")
                indent_level += 1
                index += 1
                continue

            # Method declaration without parameters
            method_decl = re.match(r"The essay (\w+)$", line)
            if method_decl:
                method_name = method_decl.group(1)
                python_code.append(f"{indentation}def {method_name}():")
                indent_level += 1
                index += 1
                continue

            # Method call with parameters
            method_call_params = re.match(r"Read (\w+) with (.*?)\.", line)
            if method_call_params:
                method_name = method_call_params.group(1)
                args = [arg.strip() for arg in method_call_params.group(2).split(',')]
                python_code.append(f"{indentation}{method_name}({', '.join(args)})")
                index += 1
                continue

            # Method call without parameters
            method_call = re.match(r"Read (\w+)\.", line)
            if method_call:
                method_name = method_call.group(1)
                python_code.append(f"{indentation}{method_name}()")
                index += 1
                continue
            
            # Variable declaration
            var_decl = re.match(r"(\w+) is (a \w+)\.", line)
            if var_decl:
                var_name, var_type = var_decl.groups()
                if var_type == "a number":
                    python_code.append(f"{indentation}{var_name} = 0")
                elif var_type == "a bool":
                    python_code.append(f"{indentation}{var_name} = False")
                elif var_type == "a string":
                    python_code.append(f"{indentation}{var_name} = \"\"")
                index += 1
                continue
            
            # Simple assignment
            simple_assign = re.match(r"(\w+) is (\d+)", line)
            if simple_assign:
                var_name, value = simple_assign.groups()
                python_code.append(f"{indentation}{var_name} = {value}")
                index += 1
                continue
            
            # Until loop
            until_loop = re.match(r"Until (\w+) is (\w+) repeat this paragraph", line)
            if until_loop:
                var_name, max_var = until_loop.groups()
                python_code.append(f"{indentation}while {var_name} <= {max_var}:")
                indent_level += 1
                index += 1
                continue
            
            # Print statement
            print_stmt = re.match(r'say "(.*?)"\.|say (\w+)\.', line)
            if print_stmt:
                if print_stmt.group(1):  # String literal
                    python_code.append(f'{indentation}print("{print_stmt.group(1)}")')
                else:  # Variable
                    var_name = print_stmt.group(2)
                    python_code.append(f'{indentation}print({var_name})')
                index += 1
                continue
            
            # Arithmetic operations
            add_op = re.match(r"add (\d+) to (\w+)\.", line)
            if add_op:
                value, var = add_op.groups()
                python_code.append(f"{indentation}{var} += {value}")
                index += 1
                continue
            
            subtract_op = re.match(r"subtract (\d+) from (\w+)\.", line)
            if subtract_op:
                value, var = subtract_op.groups()
                python_code.append(f"{indentation}{var} -= {value}")
                index += 1
                continue
            
            # If statement with module operation
            if_module = re.match(r"when module (\w+) by (\d+) is (\d+)( and module (\w+) by (\d+) is (\d+))? enter this paragraph", line, re.IGNORECASE)
            if if_module:
                var1, mod1, res1 = if_module.group(1), if_module.group(2), if_module.group(3)
                condition = f"{var1} % {mod1} == {res1}"
                if if_module.group(4):  # If there's a second condition
                    var2, mod2, res2 = if_module.group(5), if_module.group(6), if_module.group(7)
                    condition += f" and {var2} % {mod2} == {res2}"
                python_code.append(f"{indentation}if {condition}:")
                indent_level += 1
                index += 1
                continue
            
            # Unless statement
            unless_stmt = re.match(r"unless module (\w+) by (\d+) is (\d+) enter this paragraph", line)
            if unless_stmt:
                var, mod, res = unless_stmt.group(1), unless_stmt.group(2), unless_stmt.group(3)
                python_code.append(f"{indentation}if not ({var} % {mod} == {res}):")
                indent_level += 1
                index += 1
                continue
            
            # Regular if statement
            if_stmt = re.match(r"When (.*?) enter this paragraph", line)
            if if_stmt:
                condition = if_stmt.group(1)
                # Convert condition to Python syntax
                condition = condition.replace(" greater than ", " > ")
                condition = condition.replace(" less than ", " < ")
                condition = condition.replace(" is not ", " != ")
                condition = condition.replace(" is ", " == ")
                python_code.append(f"{indentation}if {condition}:")
                indent_level += 1
                index += 1
                continue
            
            # Otherwise (else) statement
            if "otherwise enter this paragraph" in line:
                indent_level -= 1
                python_code.append(f"{indentation}else:")
                indent_level += 1
                index += 1
                continue
            
            # Decrease indent level when leaving a block
            if index > 0 and len(lines[index-1].strip()) > 0 and len(line) <= len(lines[index-1]) - len(lines[index-1].lstrip()):
                indent_level = max(0, indent_level - 1)
            
            index += 1
        
        return "\n".join(python_code)

def handle_method_declaration(methods, lines, current_line, method_name, parameters):
    """Handle method declaration and store the method body"""
    body_lines = []
    next_line = current_line + 1
    current_indent = len(lines[current_line]) - len(lines[current_line].lstrip())
    
    # Collect method body
    while (next_line < len(lines) and 
           len(lines[next_line]) - len(lines[next_line].lstrip()) > current_indent):
        body_lines.append(lines[next_line])
        next_line += 1
    
    methods[method_name] = {
        'parameters': parameters,
        'body': body_lines
    }
    
    return next_line

def handle_method_call(variables, methods, method_name, arguments):
    """Handle method calls with arguments"""
    if method_name not in methods:
        raise Exception(f"Method {method_name} not found")
    
    method = methods[method_name]
    if len(arguments) != len(method['parameters']):
        raise Exception(f"Method {method_name} expects {len(method['parameters'])} arguments, got {len(arguments)}")
    
    # Create a new scope for the method
    method_scope = variables.copy()
    
    # Bind parameters to arguments
    for param, arg in zip(method['parameters'], arguments):
        # Try to get the value from variables if it's a variable name
        if arg in variables:
            method_scope[param] = variables[arg]
        else:
            # Otherwise treat it as a literal value
            try:
                method_scope[param] = int(arg)
            except ValueError:
                method_scope[param] = arg
    
    # Execute method body
    for line in method['body']:
        line = line.strip()
        if line:  # Skip empty lines
            if handle_arithmetic(method_scope, line):
                continue
            if handle_print(method_scope, line):
                continue
    
    # Copy any modified variables back to the main scope
    for var in variables:
        if var in method_scope:
            variables[var] = method_scope[var]

def handle_variable_declaration(variables, var_name, var_type):
    if var_type == "a number":
        variables[var_name] = 0
    elif var_type == "a bool":
        variables[var_name] = False
    elif var_type == "a string":
        variables[var_name] = ""

def handle_for_loop(variables, lines, current_line, var_name, start_val, times):
    variables[var_name] = start_val
    
    # Collect loop body
    body_lines = []
    next_line = current_line + 1
    current_indent = len(lines[current_line]) - len(lines[current_line].lstrip())
    
    while next_line < len(lines):
        line = lines[next_line].rstrip()
        if not line:  # Skip empty lines
            next_line += 1
            continue
            
        line_indent = len(line) - len(line.lstrip())
        if line_indent <= current_indent:
            break
            
        body_lines.append(line)
        next_line += 1
    
    # Execute loop
    for _ in range(times):
        i = 0
        while i < len(body_lines):
            line = body_lines[i].strip()
            if not line:
                i += 1
                continue
                
            # Handle if statements
            if_match = re.match(r"When (.*?) enter this paragraph", line)
            if if_match:
                condition = if_match.group(1)
                if_block = []
                else_block = []
                j = i + 1
                in_else = False
                
                while j < len(body_lines):
                    curr_line = body_lines[j].strip()
                    if not curr_line:
                        j += 1
                        continue
                        
                    if "otherwise enter this paragraph" in curr_line:
                        in_else = True
                        j += 1
                        continue
                        
                    if len(body_lines[j]) - len(body_lines[j].lstrip()) <= len(body_lines[i]) - len(body_lines[i].lstrip()):
                        break
                        
                    if in_else:
                        else_block.append(curr_line)
                    else:
                        if_block.append(curr_line)
                    j += 1
                
                if evaluate_condition(variables, condition):
                    for stmt in if_block:
                        execute_statement(variables, stmt)
                else:
                    for stmt in else_block:
                        execute_statement(variables, stmt)
                        
                i = j
                continue
            
            # Handle other statements
            if handle_arithmetic(variables, line):
                i += 1
                continue
            if handle_print(variables, line):
                i += 1
                continue
            
            i += 1
    
    return next_line

def execute_statement(variables, line):
    """Helper function to execute a single statement"""
    if handle_arithmetic(variables, line):
        return
    if handle_print(variables, line):
        return

def handle_until_loop(variables, lines, current_line, var_name, max_var):
    """Handle until loop with natural condition"""
    # Get the maximum value from variables
    max_value = variables.get(max_var, 0)
    
    # Collect loop body
    body_lines = []
    next_line = current_line + 1
    current_indent = len(lines[current_line]) - len(lines[current_line].lstrip())
    
    while (next_line < len(lines) and 
           len(lines[next_line]) - len(lines[next_line].lstrip()) > current_indent):
        body_lines.append(lines[next_line])
        next_line += 1
    
    # Execute loop
    current_value = variables.get(var_name, 0)
    while current_value <= max_value:
        for line in body_lines:
            line = line.strip()
            if line:  # Skip empty lines
                if handle_arithmetic(variables, line):
                    continue
                if handle_print(variables, line):
                    continue
        current_value = variables.get(var_name, 0)
    
    return next_line

def handle_if_statement(variables, lines, current_line, condition):
    # Collect if body and else body
    if_body = []
    else_body = []
    next_line = current_line + 1
    current_indent = len(lines[current_line]) - len(lines[current_line].lstrip())
    in_else = False
    
    while next_line < len(lines):
        line = lines[next_line]
        line_indent = len(line) - len(line.lstrip())
        
        if line_indent <= current_indent:
            break
            
        if "otherwise enter this paragraph" in line.strip():
            in_else = True
        else:
            if in_else:
                else_body.append(line)
            else:
                if_body.append(line)
        next_line += 1
    
    # Execute appropriate block
    if evaluate_condition(variables, condition):
        for line in if_body:
            line = line.strip()
            if line:  # Skip empty lines
                if handle_arithmetic(variables, line):
                    continue
                if handle_print(variables, line):
                    continue
    else:
        for line in else_body:
            line = line.strip()
            if line:  # Skip empty lines
                if handle_arithmetic(variables, line):
                    continue
                if handle_print(variables, line):
                    continue
    
    return next_line

def evaluate_condition(variables, condition):
    # Handle different condition types
    greater_than = re.match(r"(\w+) greater than (\d+)", condition)
    if greater_than:
        var_name, value = greater_than.groups()
        return variables.get(var_name, 0) > int(value)
    
    equals = re.match(r"(\w+) is (\d+)", condition)
    if equals:
        var_name, value = equals.groups()
        return variables.get(var_name, 0) == int(value)
    
    not_equals = re.match(r"(\w+) is not (\d+)", condition)
    if not_equals:
        var_name, value = not_equals.groups()
        return variables.get(var_name, 0) != int(value)
    
    less_than = re.match(r"(\w+) less than (\d+)", condition)
    if less_than:
        var_name, value = less_than.groups()
        return variables.get(var_name, 0) < int(value)
    
    return False

def handle_arithmetic(variables, line):
    add_op = re.match(r"add (\d+) to (\w+)\.", line)
    if add_op:
        value, var = add_op.groups()
        variables[var] = variables.get(var, 0) + int(value)
        return True
    
    subtract_op = re.match(r"subtract (\d+) from (\w+)\.", line)
    if subtract_op:
        value, var = subtract_op.groups()
        variables[var] = variables.get(var, 0) - int(value)
        return True
    
    return False

def handle_print(variables, line):
    print_stmt = re.match(r'say "(.*?)"\.|say (\w+)\.', line)
    if print_stmt:
        if print_stmt.group(1):  # String literal
            print(print_stmt.group(1))
        else:  # Variable
            var_name = print_stmt.group(2)
            print(variables.get(var_name, 'undefined'))
        return True
    return False

def handle_module_if(variables, lines, current_line, match_obj):
    var1, mod1, res1 = match_obj.group(1), int(match_obj.group(2)), int(match_obj.group(3))
    
    # Check if there's an "and" condition
    if match_obj.group(4):  # If there's a second condition
        var2, mod2, res2 = match_obj.group(5), int(match_obj.group(6)), int(match_obj.group(7))
        condition_met = (variables.get(var1, 0) % mod1 == res1 and 
                        variables.get(var2, 0) % mod2 == res2)
    else:
        condition_met = variables.get(var1, 0) % mod1 == res1
    
    if_body = []
    else_body = []
    next_line = current_line + 1
    current_indent = len(lines[current_line]) - len(lines[current_line].lstrip())
    in_else = False
    
    while next_line < len(lines):
        line = lines[next_line]
        line_indent = len(line) - len(line.lstrip())
        
        if line_indent <= current_indent:
            break
            
        if "otherwise enter this paragraph" in line.strip():
            in_else = True
        else:
            if in_else:
                else_body.append(line)
            else:
                if_body.append(line)
        next_line += 1
    
    if condition_met:
        for line in if_body:
            line = line.strip()
            if line:  # Skip empty lines
                if handle_arithmetic(variables, line):
                    continue
                if handle_print(variables, line):
                    continue
    else:
        for line in else_body:
            line = line.strip()
            if line:  # Skip empty lines
                if handle_arithmetic(variables, line):
                    continue
                if handle_print(variables, line):
                    continue
    
    return next_line

def handle_unless_statement(variables, lines, current_line, match_obj):
    var, mod, res = match_obj.group(1), int(match_obj.group(2)), int(match_obj.group(3))
    condition_met = not (variables.get(var, 0) % mod == res)
    
    if_body = []
    else_body = []
    next_line = current_line + 1
    current_indent = len(lines[current_line]) - len(lines[current_line].lstrip())
    in_else = False
    
    while next_line < len(lines):
        line = lines[next_line]
        line_indent = len(line) - len(line.lstrip())
        
        if line_indent <= current_indent:
            break
            
        if "otherwise enter this paragraph" in line.strip():
            in_else = True
        else:
            if in_else:
                else_body.append(line)
            else:
                if_body.append(line)
        next_line += 1
    
    if condition_met:
        for line in if_body:
            line = line.strip()
            if line:  # Skip empty lines
                if handle_arithmetic(variables, line):
                    continue
                if handle_print(variables, line):
                    continue
    else:
        for line in else_body:
            line = line.strip()
            if line:  # Skip empty lines
                if handle_arithmetic(variables, line):
                    continue
                if handle_print(variables, line):
                    continue
    
    return next_line

# Example usage
if __name__ == "__main__":
    try:
        interpret("program.sentence")
    except Exception as e:
        print(f"Error executing program: {e}")
