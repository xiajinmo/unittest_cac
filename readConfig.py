import os
import configparser
import getpathInfo

path = getpathInfo.get_Path()
config_path = os.path.join(path, 'config/config.ini')
config = configparser.ConfigParser()
config.read(config_path, encoding='utf-8')


class ReadConfig():

    def get_url(self, name):
        value = config.get('DEFAULT', name)
        return value


if __name__ == '__main__':
    print('HTTP中的url值为：', ReadConfig().get_url('url'))
