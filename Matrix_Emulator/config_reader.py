import configparser

config = configparser.ConfigParser()
configfile = open('config.ini')

#settings = config['settings']

#quantity = settings['quantity']
#ordinance = settings['ordinance']
#ordinance_shape = settings['ordinance_shape']
#led_ordinance = settings['led_ordinance']

#print(quantity)
#print(ordinance)
#print(ordinance_shape)
#print(led_ordinance)

print(config.read("config.ini"))

