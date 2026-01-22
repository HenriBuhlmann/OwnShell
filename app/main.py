import sys
import os
import subprocess
import readline

symbols = {">":["w", "stdout"],
           "1>":["w", "stdout"],
           "2>":["w", "stderr"],
           ">>":["a", "stdout"],
           "1>>":["a", "stdout"],
           "2>>":["a", "stderr"]}


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


def parse_input(tokens):
    redirect = None
    
    for position, current_item in enumerate(tokens):
        if current_item in symbols:
            redirect = tokens[position + 1]
            command = tokens[0]
            arguments = tokens[1:position]
            operation = symbols[tokens[position]]
            return command, arguments, redirect, operation

    command = tokens[0]
    arguments = tokens[1:]

    return command, arguments, None, None


def handle_command(tokens):
    command, arguments, redirect, operation = parse_input(tokens)
    
    if command in shell_builtins:
        return execute_builtin(command, arguments, redirect, operation)
    else:
        return execute_external(command, arguments, redirect, operation)
    

def execute_builtin(command, arguments, redirect, operation):
        func = shell_builtins[command]
        return func(arguments, redirect, operation)
    

def execute_external(command, arguments, redirect, operation):
    for directory in os.environ["PATH"].split(os.pathsep):
        absolute_path = os.path.join(directory, command)
        if os.path.exists(absolute_path) and os.access(absolute_path, os.X_OK):
            if redirect:
                f, flag = handle_redirect(redirect, operation)
                subprocess.run([absolute_path] + arguments, **{flag: f})
                f.close()
                return True
            else:
                subprocess.run([command] + arguments, executable=absolute_path)                
                return True
            
    print(f"{command}: command not found")
    return True


def handle_redirect(redirect, operation):
    directory = os.path.dirname(redirect)
    if directory:
        os.makedirs(directory, exist_ok=True)   
    f = open(redirect, operation[0])
    flag = operation[1]
    
    return f, flag

    
def echo_cmd(arguments, redirect, operation):
    output = " ".join(arguments)
    if redirect:
        f, flag = handle_redirect(redirect, operation)
        if flag == "stdout":
            print(output, file=f)  
            f.close()  
            return True
    print(output)
    return True


def exit_cmd(arguments=None, redirect=None, operation = None):
    return False
     

def type_cmd(arguments, redirect, operation):
    if not arguments:
        return True
    
    target = arguments[0]

    if target in shell_builtins:
        if redirect:
            f, flag = handle_redirect(redirect, operation)
            print(f"{target} is a shell builtin", file=f)
            f.close()
            return True
        else:
            print( f"{target} is a shell builtin")
            return True
        
    for directory in os.environ["PATH"].split(os.pathsep):
            absolute_path = os.path.join(directory, target)
            if os.path.exists(absolute_path) and os.access(absolute_path, os.X_OK):
                    if redirect:
                        f, flag = handle_redirect(redirect, operation)
                        print(f"{target} is {absolute_path}", file=f)
                        f.close()
                        return True
                    else:
                        print(f"{target} is {absolute_path}") 
                        return True
    if redirect:
        f, flag = handle_redirect(redirect, operation)
        print(f"{target}: not found", file=f)
        f.close()
        return True 
    else:
        print(f"{target}: not found") 
        return True


def pwd_cmd(arguments, redirect, operation):
    if redirect:
        f, flag = handle_redirect(redirect, operation)
        print(os.getcwd(), file=f)
        f.close()
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


def auto_complete(text, state):

    all_matches = [builtin for builtin in shell_builtins if builtin.startswith(text)]

    if len(all_matches) == 0:
        for directory in os.environ["PATH"].split(os.pathsep):
            try:
                for file in os.listdir(directory):
                    path = os.path.join(directory, file)
                    if file.startswith(text) and os.access(path, os.X_OK):
                        all_matches.append(file)
            except FileNotFoundError:
                continue

    try:
        return all_matches[state] + " "
    except IndexError:
        return None
   
   
def main():
    readline.set_completer(auto_complete)
    readline.parse_and_bind("tab:complete")
    running = True
    while running:
        sys.stdout.write("$ ") 
        tokens = tokenize_input(input())
        if not tokens:
            continue
        else:
            running = handle_command(tokens)



if __name__ == "__main__":
    main()

