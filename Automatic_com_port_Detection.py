import sys
def find_port():
    if sys.platform.startswith('win'):
        for i in range(1, 256):
            port_name = f"COM{i}"
            try:
                with open(f"\\\\.\\{port_name}", "r+b") as port:
                    return port_name
            except OSError:
                print("An Unexpected error occurred while trying to open the port")
                pass
    else:
        print("Unsupported OS ! .")
        return None

    return None

if __name__ == "__main__":
    port_name = find_port()
    if port_name is None:
        port_name = find_port()

    print("Opening port: " + port_name)