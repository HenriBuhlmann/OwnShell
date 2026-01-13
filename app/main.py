import sys
import os 
import subprocess

SHELL_BUILTINS = {"echo", "exit", "type", "pwd", "cd"}

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
    current_token  = ""
    token_list  = []
    inside_single_quote = False
    inside_double_quotes = False
    escaped = False
    for char in input_line:
        if inside_single_quote:
            if char == "'":
                inside_single_quote = not inside_single_quote
            else:
                current_token += char
        elif inside_double_quotes:
            if char == "\\":
                if escaped:
                    current_token += char
                    escaped = False
                else:
                    escaped = True
            elif char == '"':
                if escaped:
                    current_token += char
                    escaped = False
                else:
                    inside_double_quotes = not inside_double_quotes
            elif escaped:
                current_token += "\\"
                current_token += char
                escaped = False
            else:
                current_token += char
        elif escaped:
            current_token += char
            escaped = False
        else:
            if char == " ":
                if not current_token :
                    continue
                else:
                    token_list .append(current_token )
                    current_token  = ""
            elif char == "'":
                inside_single_quote = not inside_single_quote
            elif char == '"':
                inside_double_quotes = not inside_double_quotes   
            elif char == "\\":
                escaped = True             
            else:
                current_token += char
    if current_token:
        token_list.append(current_token )
    return token_list 


def handle_command(tokens):
    command, arguments = parse_input(tokens)
    
    if command in SHELL_BUILTINS:
        return execute_builtin(command, arguments, tokens)
    else:
        return execute_external(command, arguments)
    

def parse_input(tokens):
    command = tokens[0]
    arguments = tokens[1:]
    return command, arguments


def execute_builtin(command, arguments, tokens):
    if command == "echo":
        print(echo_cmd(arguments))
        return True
    
    if command == "exit":
        return False
    
    if command == "type":
        if arguments:
            print(type_cmd(tokens))
        return True
        
    if command == "pwd":
        print(pwd_cmd())
        return True
    
    if  command == "cd":
        cd_cmd(arguments)
        return True

        
def execute_external(command, arguments):
    for directory in os.environ["PATH"].split(os.pathsep):
        absolute_path = os.path.join(directory, command)
        if os.path.exists(absolute_path) and os.access(absolute_path, os.X_OK):
            subprocess.run([command] + arguments)
            return True
        
    print(f"{command}: command not found")
    return True


def echo_cmd(arguments):
    return " ".join(arguments)
     

def type_cmd(tokens):
    target = tokens[1]

    if target in SHELL_BUILTINS:
        return f"{target} is a shell builtin"

    for directory in os.environ["PATH"].split(os.pathsep):
            absolute_path = os.path.join(directory, target)
            if os.path.exists(absolute_path) and os.access(absolute_path, os.X_OK):
                    return f"{target} is {absolute_path}"
            
    return f"{target}: not found"
        

def pwd_cmd():
    return os.getcwd()


def cd_cmd(arguments):
    if not arguments:
        return
    
    if len(arguments) >= 2:
        print("cd: too many arguments")
        return
    
    path = arguments[0]

    if path == "~":
        os.chdir(os.environ["HOME"])
    elif os.path.exists(path):
        os.chdir(path)
    else: 
        print(f"cd: {path}: No such file or directory")
        

if __name__ == "__main__":
    main()

