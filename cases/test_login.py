import unittest
from common.RequestHttp import Request
import configparser
from ddt import ddt, file_data
import readConfig
import collections

class GlobalDict(collections.UserDict):
    """使用继承UserDict"""

    def __missing__(self, key):
        """获取不存在的值时"""
        return None

@ddt
class TestSwagger(unittest.TestCase):
    my_dict = GlobalDict()

    # 登录接口，用于获取token、login_token_ldapUserId
    @file_data(r'../data/login_out/login.yaml')
    def test_2_login(self, **kwargs):
        print('——————————测试登录——————————')
        res = self.kd.post(url=kwargs['path'], data=kwargs['data'], headers=kwargs['headers'])
        GlobalDict.token = self.kd.get_text(res.json(), 'token')
        GlobalDict.ldapUserId = self.kd.get_text(res.json(), 'ldapUserId')
        GlobalDict.loginToken = self.kd.get_text(res.json(), 'loginToken')
        GlobalDict.userId = self.kd.get_text(res.json(), 'id')
        print(self.kd.json_format(res))

    # 个人设置接口，用于获取APIkey
    @file_data(r'../data/getapikey.yaml')
    def test_apikey(self, **kwargs):
        print('——————————测试获取APIKEY——————————')
        url = self.url + 'api/users/'+str(self.userId[0])
        print(url)
        params = kwargs['params']
        headers = {}
        # 将公共头信息传到headers中
        headers['x-auth-login-token'] = self.loginToken
        headers['x-auth-ldap-user-id'] = str(self.ldapUserId)
        headers['x-auth-token'] = self.token
        headers['x-auth-user-id'] = str(self.ldapUserId)
        res = self.kd.get(url=url, params=params, headers=headers)
        GlobalDict.kongApiKey = self.kd.get_text(res.json(), 'kongApiKey')
        GlobalDict.kongSecretKey = self.kd.get_text(res.json(), 'kongSecretKey')
        value = self.kd.get_text(res.json(), 'userName')
        print(self.kd.json_format(res))
        print(value[0])
        self.assertEqual(first=kwargs['userName'], second=str(value[0]))
        # self.assertIn(kwargs['userName'], value)
        self.assertTrue(kwargs['userName'] in res.text)

    def test_get_token(self):
        # 将之前用例中获取的token保存进行调用，但不调用用例执行步骤
        print('——————————测试中间值参数获取——————————')
        print('ldapuserid:', self.ldapUserId)
        print('token:', self.token)
        print('loginToken:', self.loginToken)
        print('kongApiKey:', self.kongApiKey)
        print('kongSecretKey:', self.kongSecretKey)

    # 获取请求头
    def get_headers(self, headers):
        if headers is not None:
            headers['x-auth-login-token'] = self.loginToken
            headers['x-auth-ldap-user-id'] = str(self.ldapUserId)
            headers['x-auth-token'] = self.token
            headers['x-auth-user-id'] = str(self.ldapUserId)
            headers['apikey'] = self.kongApiKey
            headers['secretkey'] = self.kongSecretKey
        return headers

    @file_data(r'../data/login_out/logout.yaml')
    def test_logout(self, **kwargs):
        print('——————————登出云平台——————————')
        url = 'https://uat.rynnova.com/9093api/logoutSession?id=' + str(self.ldapUserId) + '&type=LOGOUT'
        headers = kwargs['headers']
        headers['x-auth-ldap-user-id'] = str(self.ldapUserId)
        headers['x-auth-token'] = self.token
        headers['x-auth-user-id'] = str(self.ldapUserId)
        res = self.kd.get(url=url, headers=headers)
        print(self.kd.json_format(res))
