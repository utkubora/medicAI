from manager import Manager

if __name__ == "__main__":
    config_path = "config.json"

    manager = Manager(config_path)
    manager.prepare_data()