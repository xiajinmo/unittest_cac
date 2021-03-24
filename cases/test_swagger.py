import unittest
from common.RequestHttp import Request
import configparser
from ddt import ddt, file_data
import readConfig


@ddt
class TestSwagger(unittest.TestCase):

    # 测试用例
    # 公共部分提取，作为初始化的内容
    @classmethod
    def setUpClass(cls) -> None:
        # 实例化需要的内容
        conf = configparser.ConfigParser()
        conf.read('../config/config.ini')
        cls.token = None
        cls.ldapUserId = None
        cls.loginToken = None
        cls.kongApiKey = None
        cls.kongSecretKey = None
        cls.userId = None
        cls.url = readConfig.ReadConfig().get_url('url')
        cls.kd = Request()

    # 登录接口，用于获取token、login_token_ldapUserId
    @file_data(r'../data/login_out/login.yaml')
    def test_2_login(self, **kwargs):
        print('——————————测试登录——————————')
        res = self.kd.post(url=kwargs['path'], data=kwargs['data'], headers=kwargs['headers'])
        TestSwagger.token = self.kd.get_text(res.json(), 'token')
        TestSwagger.ldapUserId = self.kd.get_text(res.json(), 'ldapUserId')
        TestSwagger.loginToken = self.kd.get_text(res.json(), 'loginToken')
        TestSwagger.userId = self.kd.get_text(res.json(), 'id')
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
        TestSwagger.kongApiKey = self.kd.get_text(res.json(), 'kongApiKey')
        TestSwagger.kongSecretKey = self.kd.get_text(res.json(), 'kongSecretKey')
        value = self.kd.get_text(res.json(), 'userName')
        print(self.kd.json_format(res))
        print(value[0])
        self.assertEqual(first=kwargs['userName'], second=str(value[0]))
        self.assertIn(kwargs['userName'], value)

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

    @file_data(r'../data/swagger_get_basic.yaml')
    def _test_swagger_get_basic(self, **kwargs):
        print('——————————测试Swagger Get接口—', kwargs['name'], '——————————')
        # 通用get方法的url
        url = self.url + kwargs['path']
        # 通用get方法的headers
        headers = {}
        self.get_headers(headers)
        res = self.kd.get(url=url, headers=headers)
        self.assertEqual('200', str(res.status_code))
        print('状态码：', res.status_code)

    @file_data(r'../data/swagger_get_others.yaml')
    def test_swagger_get_others(self, **kwargs):
        print('——————————测试Swagger Get接口—带参数', kwargs['name'], '——————————')
        # 通用get方法的url
        url = self.url + kwargs['path']
        # 通用get方法的headers
        headers = {}
        params = kwargs['params']
        self.get_headers(headers)
        res = self.kd.get(url=url, headers=headers, params=params)
        self.assertEqual('200', str(res.status_code))
        print('状态码：', res.status_code)


    @file_data(r'../data/login_out/logout.yaml')
    def test_logout(self, **kwargs):
        print('——————————登出云平台——————————')
        url = 'https://dev2.rynnova.com/9093api/loginHistory/logoutSession?id=' + str(self.ldapUserId) + '&type=LOGOUT'
        headers = kwargs['headers']
        headers['x-auth-ldap-user-id'] = str(self.ldapUserId)
        headers['x-auth-token'] = self.token
        headers['x-auth-user-id'] = str(self.ldapUserId)
        res = self.kd.get(url=url, headers=headers)
        print(self.kd.json_format(res))
