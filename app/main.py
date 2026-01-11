import sys
import os 
import subprocess

SHELL_BUILTINS = {"echo", "exit", "type", "pwd", "cd"}

def main():
    running = True
    while running:
        sys.stdout.write("$ ")
        tokens = input().split()
        if not tokens:
            continue
        else:
            running = handle_command(tokens)


def handle_command(tokens):
    command, arguments = parse_input(tokens)
    
    if command in SHELL_BUILTINS:
        return run_builtin(command, arguments, tokens)
    else:
        return run_external(command, arguments)
    

def parse_input(tokens):
    command = tokens[0]
    arguments = tokens[1:]
    return command, arguments


def run_builtin(command, arguments, tokens):
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

        
def run_external(command, arguments):
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
    
    path = arguments[0]

    if path[0] == "~":
        os.chdir(os.environ["HOME"])
    elif os.path.exists(path):
        os.chdir(path)
    else: 
        print(f"cd: {path}: No such file or directory")
        

if __name__ == "__main__":
    main()

