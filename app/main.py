import sys


def main():
    sys.stdout.write("$ ")
    user_input = input()
    if user_input is not None:
        print(f"{user_input}: command not found")


if __name__ == "__main__":
    main()

