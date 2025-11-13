from os import path

from sunrise.sunrise import spin_node

if __name__ == "__main__":
    spin_node(path.join("sunrise", "config", "sunrise.json"))