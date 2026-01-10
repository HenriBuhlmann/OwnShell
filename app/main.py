import sys
import os 
import subprocess

shell_built_in = {"echo", "exit", "type", "pwd"}

def main():
    # REPL
    status = True
    while status:
        sys.stdout.write("$ ")
        user_input = input().split()
        if len(user_input) == 0:
            continue
        else:
            status = check_command(user_input)

def check_command(user_input):
    command = user_input[0]
    arguments = user_input[1:]
    if command in shell_built_in:
        if command == "echo":
            print(echo(arguments))
            return True
        elif command == "exit":
            return False
        elif command == "type":
            if len(arguments) == 0:
                return True
            else:
                print(type(user_input))
                return True
        elif command == "pwd":
            print(os.getcwd())
            return True
    else:
        path_string = os.environ["PATH"]
        directories = path_string.split(os.pathsep)
        for current_path in directories:
            absolute_path = os.path.join(current_path, command)
            if os.path.exists(absolute_path) and os.access(absolute_path, os.X_OK):
                subprocess.run([command] + arguments)
                return True
        print(f"{command}: command not found")
        return True

        

def echo(arguments):
    output = " ".join(arguments)
    return output

def type(user_input):
    command_type_func = user_input[1]
    global shell_built_in  
    # check if command_type_func is builtin
    if command_type_func in shell_built_in:
        output = f"{command_type_func} is a shell builtin"
        return output
    else:
        # check if command is in directory in $PATH
        path_string = os.environ["PATH"]
        directories = path_string.split(os.pathsep)
        # check each directory 
        for current_path in directories:
            # create absolute path
            absolute_path = os.path.join(current_path, command_type_func)
            # check for existence and execute permission 
            if os.path.exists(absolute_path) and os.access(absolute_path, os.X_OK):
                    output = f"{command_type_func} is {absolute_path}"
                    return output
            else:
                    continue
        output = f"{command_type_func}: not found"
        return output
        
if __name__ == "__main__":
    main()

