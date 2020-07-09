import configparser

config = configparser.ConfigParser()
config['settings'] = {'resolution': '230x368', 'color': 'blue'}

configfile = open('config.ini', 'w')
config.write(configfile)
