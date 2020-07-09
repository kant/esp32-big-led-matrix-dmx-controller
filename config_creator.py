import configparser

config = configparser.ConfigParser()
config['settings'] = {'quantity': '4', 'ordinance': '0;1;2;3', 'ordinance_shape': 'rectangle', 'led_ordinance': 'TLS', }

configfile = open('Matrix_Emulator\\config.ini', 'w')
config.write(configfile)
