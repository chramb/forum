from configparser import ConfigParser


def config(filename="../config/config.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    options = {}
    if parser.has_section(section):
        params = parser.items(section)
        for p in params:
            options[p[0]] = p[1]
    else:
        raise Exception(f"Section{section} is not found in {filename} file.")
    return options
