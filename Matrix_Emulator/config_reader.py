import configparser

config = configparser.ConfigParser()
config.read("config.ini")


quantity = config.get('settings', 'quantity')
ordinance = config.get('settings', 'ordinance')
ordinance_shape = config.get('settings', 'ordinance_shape')
led_ordinance = config.get('settings', 'led_ordinance')

print(quantity)
print(ordinance)
print(ordinance_shape)
print(led_ordinance)



