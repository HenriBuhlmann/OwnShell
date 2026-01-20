import sys
import os 
import subprocess


def main():
    running = True
    while running:
        sys.stdout.write("$ ") 
        tokens = tokenize_input(input())
        if not tokens:
            continue
        else:
            running = handle_command(tokens)


def tokenize_input(input_line):
    modes = {"normal":normal_mode,
             "inside_single_quote":single_quote_mode,
             "inside_double_quote":double_quote_mode,
             "escaped_in_double_quote":escaped_in_double_quote_mode,
             "escaped":escaped_mode
    }

    current_token = ""
    current_mode = "normal"
    token_list = []

    for char in input_line:
        func = modes[current_mode]
        current_token, current_mode, token_finished = func(char, current_token)
        if token_finished:
            if current_token:
                token_list.append(current_token)
                current_token = ""
    if current_token:
        token_list.append(current_token)
    
    return token_list
  
    
def normal_mode(char, current_token):
    token_finished = False
    new_mode = "normal"
    new_token = current_token
    if char == " ":
        token_finished = True
    elif char == "\\":
        new_mode = "escaped"
    elif char == "'":
        new_mode = "inside_single_quote"
    elif char == '"':
        new_mode = "inside_double_quote"
    else:
        new_token += char

    return new_token, new_mode, token_finished 


def single_quote_mode(char, current_token):
    new_mode = "inside_single_quote"
    new_token = current_token
    token_finished = False
    if char == "'":
        new_mode = "normal"
    else:
        new_token += char

    return new_token, new_mode, token_finished


def double_quote_mode(char, current_token):
    new_mode = "inside_double_quote"
    new_token = current_token
    token_finished = False
    if char == '"':
        new_mode = "normal"
    elif char == "\\":
        new_mode = "escaped_in_double_quote"
    else:
        new_token += char
    
    return new_token, new_mode, token_finished


def escaped_in_double_quote_mode(char, current_token):
    new_mode = "inside_double_quote"
    new_token = current_token
    token_finished = False

    if char == '"' or char == "\\":
        new_token += char
    else:
        new_token += "\\" + char
        
    return new_token, new_mode, token_finished


def escaped_mode(char, current_token):
    new_mode = "normal"
    new_token = current_token
    token_finished = False

    new_token += char

    return new_token, new_mode, token_finished


def handle_command(tokens):
    command, arguments, redirect, operation = parse_input(tokens)
    
    if command in shell_builtins:
        return execute_builtin(command, arguments, redirect, operation)
    else:
        return execute_external(command, arguments, redirect, operation)
    

def parse_input(tokens):
    redirect = None

    for position, current_item in enumerate(tokens):
        if current_item == ">" or current_item =="1>" or current_item =="2>":
            redirect = tokens[position + 1]
            command = tokens[0]
            arguments = tokens[1:position]
            operation = tokens[position]
            return command, arguments, redirect, operation

    command = tokens[0]
    arguments = tokens[1:]

    return command, arguments, None, None


def execute_builtin(command, arguments, redirect, operation):
        func = shell_builtins[command]
        return func(arguments, redirect, operation)
    

def execute_external(command, arguments, redirect, operation):
    for directory in os.environ["PATH"].split(os.pathsep):
        absolute_path = os.path.join(directory, command)
        if os.path.exists(absolute_path) and os.access(absolute_path, os.X_OK):
            if redirect:
                if operation == ">" or operation =="1>":
                    os.makedirs(os.path.dirname(redirect), exist_ok=True)
                    with open(redirect, "w") as f:
                        subprocess.run([absolute_path] + arguments, stdout=f)
                    return True
                else:
                    os.makedirs(os.path.dirname(redirect), exist_ok=True)
                    with open(redirect, "w") as f:
                        subprocess.run([absolute_path] + arguments, stderr=f)
                    return True
            else:
                subprocess.run([command] + arguments, executable=absolute_path)                
                return True
            
    print(f"{command}: command not found")
    return True

    
def echo_cmd(arguments, redirect, operation):
    output = " ".join(arguments)

    if redirect:
        directory = os.path.dirname(redirect)
        if directory:
            os.makedirs(directory, exist_ok=True)

    if operation == ">" or operation == "1>":
        with open(redirect, "w") as f:
            print(output, file=f)

        return True
    
    elif operation =="2>":
        open(redirect, "w").close()
        print(output)
        return True
    
    else:
        print(output)
        return True


def exit_cmd(arguments=None, redirect=None, operation = None):
    return False
     

def type_cmd(arguments, redirect, operation=None):
    if not arguments:
        return True
    
    target = arguments[0]

    if target in shell_builtins:
        if redirect:
            with open(redirect, 'w') as f:
                print(f"{target} is a shell builtin", file=f)
                return True
        else:
            print( f"{target} is a shell builtin")
            return True
        
    for directory in os.environ["PATH"].split(os.pathsep):
            absolute_path = os.path.join(directory, target)
            if os.path.exists(absolute_path) and os.access(absolute_path, os.X_OK):
                    if redirect:
                        with open(redirect, 'w') as f:
                            print(f"{target} is {absolute_path}", file=f)
                            return True
                    else:
                        print(f"{target} is {absolute_path}") 
                        return True
    if redirect:
        with open(redirect, 'w') as f:
            print(f"{target}: not found", file=f)
            return True 
    else:
        print(f"{target}: not found") 
        return True


def pwd_cmd(arguments, redirect, operation=None):
    if redirect:
         with open(redirect, 'w') as f:
            print(os.getcwd(), file=f)
            return True
    else:
        print(os.getcwd())
        return True 


def cd_cmd(arguments, redirect, operation = None):
    if not arguments:
        return True

    if len(arguments) >= 2:
        print("cd: too many arguments")
        return True
    
    path = arguments[0]

    if path == "~":
        os.chdir(os.environ["HOME"])
    elif os.path.exists(path):
        os.chdir(path)
    else: 
        print(f"cd: {path}: No such file or directory")
    return True


shell_builtins = {"echo": echo_cmd,
                  "exit": exit_cmd,
                  "type": type_cmd,
                  "pwd": pwd_cmd, 
                  "cd": cd_cmd
                  }


if __name__ == "__main__":
    main()

