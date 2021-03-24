import unittest
from common.RequestHttp import Request
import configparser
from ddt import ddt, file_data
import readConfig
import json


@ddt
class TestVolume(unittest.TestCase):

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
        TestVolume.token = self.kd.get_text(res.json(), 'token')
        TestVolume.ldapUserId = self.kd.get_text(res.json(), 'ldapUserId')
        TestVolume.loginToken = self.kd.get_text(res.json(), 'loginToken')
        TestVolume.userId = self.kd.get_text(res.json(), 'id')
        print(self.kd.json_format(res))

    # 个人设置接口，用于获取APIkey
    @file_data(r'../data/getapikey.yaml')
    def test_3_apikey(self, **kwargs):
        print('——————————测试获取APIKEY——————————')
        url = self.url + 'api/users/' + str(self.userId[0])
        params = kwargs['params']
        headers = {}
        # 将公共头信息传到headers中
        headers['x-auth-login-token'] = self.loginToken
        headers['x-auth-ldap-user-id'] = str(self.ldapUserId)
        headers['x-auth-token'] = self.token
        headers['x-auth-user-id'] = str(self.ldapUserId)
        res = self.kd.get(url=url, params=params, headers=headers)
        TestVolume.kongApiKey = self.kd.get_text(res.json(), 'kongApiKey')
        TestVolume.kongSecretKey = self.kd.get_text(res.json(), 'kongSecretKey')
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
            headers['Content-Type'] = 'application/json'
        return headers

    @file_data(r'../data/resource_norm_data/other_price.yaml')
    def test_edit_other_price(self, **kwargs):
        # 编辑其他定价信息公共接口URL、Header
        edit_miscellaneous = self.url + kwargs['edit_miscellaneous']
        edit_miscellaneous_header = {}
        self.get_headers(edit_miscellaneous_header)
        # 编辑私有镜像定价
        template_price_data = kwargs['template_price_data']
        res_template_price = self.kd.post(url=edit_miscellaneous, data=template_price_data,
                                          headers=edit_miscellaneous_header)
        print('编辑私有镜像定价的状态码结果是：', res_template_price.status_code)
        # 检查镜像编辑结果
        template_price_url = self.url + kwargs['template_url']
        check_template_price = self.kd.get(url=template_price_url, params=kwargs['params'],
                                           headers=edit_miscellaneous_header)
        print('输入查询结果', check_template_price)
        print('输入查询结果类型', type(check_template_price))
        check_text = self.kd.get_text(check_template_price)
        print(check_text)
        
        # print('输入查询结果', print(self.kd.json_format(check_template_price)))
        # 编辑虚拟磁盘备份定价
        disk_backup_price_data = kwargs['disk_backup_price_data']
        res_disk_backup_price = self.kd.post(url=edit_miscellaneous, data=disk_backup_price_data,
                                             headers=edit_miscellaneous_header)
        print('编辑虚拟磁盘备份定价的状态码结果是：', res_disk_backup_price.status_code)
        # 编辑公网IP定价
        publicip_price_data = kwargs['publicip_price_data']
        res_publicip_price = self.kd.post(url=edit_miscellaneous, data=publicip_price_data,
                                          headers=edit_miscellaneous_header)
        print('编辑公网IP定价的状态码结果是：', res_publicip_price.status_code)
        # 编辑虚拟机快照定价
        snapshot_price_data = kwargs['snapshot_price_data']
        res_snapshot_price = self.kd.post(url=edit_miscellaneous, data=snapshot_price_data,
                                          headers=edit_miscellaneous_header)
        print('编辑虚拟机快照定价的状态码结果是：', res_snapshot_price.status_code)

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
