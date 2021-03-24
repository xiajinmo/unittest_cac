import json
import unittest
from common.RequestHttp import Request
from common.HTMLTestRunner import HTMLTestRunner
import configparser
from ddt import ddt, file_data
import readConfig
import time
import jsonpath


@ddt
class TestCase01(unittest.TestCase):
    """
        date:{
            key:value,
            key1:{
                key1-1:value1-1
                key1-2:{
                    key1-1-1:value1-1-1
                }
            }
            key2:{
                key2-1:value2-1
            }
        }
    """

    # 封装字典对象赋值行为
    def assignment(self, kwargs):
        for key, value in kwargs.items():
            if type(value) in dict:
                self.assignment(value)
            else:
                if value:
                    pass
                else:
                    kwargs[key] = getattr(self, key)
        print(kwargs)
        return kwargs

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
        TestCase01.token = self.kd.get_text(res.json(), 'token')
        TestCase01.ldapUserId = self.kd.get_text(res.json(), 'ldapUserId')
        TestCase01.loginToken = self.kd.get_text(res.json(), 'loginToken')
        TestCase01.userId = self.kd.get_text(res.json(), 'id')
        # fp = open("D:\sherry\config\config.ini", 'w')
        # fp.writelines(TestCase01.token)
        # fp.writelines(TestCase01.ldapUserId)
        # fp.writelines(TestCase01.loginToken)
        # fp.close()
        print(self.kd.json_format(res))

    # 个人设置接口，用于获取APIkey
    @file_data(r'../data/getapikey.yaml')
    def test_3_apikey(self, **kwargs):
        print('——————————测试获取APIKEY——————————')
        url = self.url + 'api/users/'+str(self.userId[0])
        params = kwargs['params']
        headers = {}
        # 将公共头信息传到headers中
        headers['x-auth-login-token'] = self.loginToken
        headers['x-auth-ldap-user-id'] = str(self.ldapUserId)
        headers['x-auth-token'] = self.token
        headers['x-auth-user-id'] = str(self.ldapUserId)
        res = self.kd.get(url=url, params=params, headers=headers)
        TestCase01.kongApiKey = self.kd.get_text(res.json(), 'kongApiKey')
        TestCase01.kongSecretKey = self.kd.get_text(res.json(), 'kongSecretKey')
        value = self.kd.get_text(res.json(), 'userName')
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

    @file_data(r'../data/addresspool.yaml')
    def test_some_get(self, **kwargs):
        print('——————————测试状态—', kwargs['name'], '——————————')
        url = self.url + kwargs['path']
        headers = {}
        self.get_headers(headers)
        res = self.kd.get(url=url, headers=headers)
        self.assertEqual('200', str(res.status_code))
        print('状态码：', res.status_code)
        # print(self.kd.json_format(res))

    @file_data(r'../data/test.yaml')
    def _test_1_api_demo(self, **kwargs):
        # 接口测试用例
        url = self.url + kwargs['path']
        headers = kwargs['headers']
        headers['x-auth-login-token'] = self.loginToken
        res = self.kd.get(url=url, headers=headers)
        # self.assertEqual('<Response [200]>', str(res))
        print(res.status_code)
        print(res.json())
        # value = kd.get_text(res.text, 'description')
        # self.assertEqual(first=kwargs['description'], second=value)

    @file_data(r'../data/network.yaml')
    def test_create_network(self, **kwargs):
        print('——————————测试创建网络——————————')
        url_create = self.url + kwargs['path_create']
        headers = {}
        self.get_headers(headers)
        data = kwargs['data']
        res_create = self.kd.post(url=url_create, data=data, headers=headers)
        print(self.kd.json_format(res_create))

        print('——————————测试网络是否创建成功——————————')
        headers_check = kwargs['headers_check']
        self.get_headers(headers_check)
        url_check = self.url + kwargs['path_check']
        params_check = kwargs['params_check']
        res_check = self.kd.get(url=url_check, params=params_check, headers=headers_check)
        print(self.kd.json_format(res_check))

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


if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestCase01))  # 使用makeSuite方法添加所有的测试方法
    fp = open(r"D:\sherry\report\report.html", "wb")
    runner = HTMLTestRunner(stream=fp, title="测试报告", description="测试结果")
    runner.run(suite)
    fp.close()
