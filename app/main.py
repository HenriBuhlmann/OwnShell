import sys

shell_built_in = {"echo", "exit", "type"}

def main():
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
    if command == "echo":
        print(echo(arguments))
        return True
    elif command == "exit":
        return False
    elif command == "type":
        if len(arguments) == 0:
            return True
        else:
            print(type(arguments))
            return True
    else:
        print(f"{command}: command not found")
        return True

def echo(arguments):
    output = " ".join(arguments)
    return output

def type(arguments):
    global shell_built_in
    if arguments[0] in shell_built_in:
        output = f"{arguments[0]} is a shell builtin"
        return output
    else:
        output = f"{arguments[0]}: not found"
        return output








 

if __name__ == "__main__":
    main()

