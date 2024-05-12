class Config():
  SECRET_KEY = 'Ba@345FFa24#3'

class DevelopmentConfig(Config):
  DEBUG = True


config = {
  'development': DevelopmentConfig,
  }

mail_username = 'no-reply@joseluisrizzo.com'
mail_password = 'wAPVB1uMDq'

SECRET_KEY = '34323b759c5cac08a2adf7bf0ed9a53d10940e18946b04627e763aecf1228f14'