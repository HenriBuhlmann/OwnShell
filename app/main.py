import sys


def main():

    while True:
        sys.stdout.write("$ ")
        user_input = input().split()
        if len(user_input) == 0:
            continue
        else:
            command = user_input[0]
            arguments = user_input[1:]
        if command == "exit":
            break
        elif command == "echo":
            print(" ".join(arguments))
        else:
            print(f"{command}: command not found")       
        
        

      
        
if __name__ == "__main__":
    main()

