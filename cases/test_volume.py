import unittest
from common.RequestHttp import Request
import configparser
import time
from ddt import ddt, file_data
import readConfig


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
        cls.url2 = readConfig.ReadConfig().get_url('url2')
        cls.url3 = readConfig.ReadConfig().get_url('url3')
        cls.kd = Request()

    # 登入云平台
    @file_data(r'../data/login_out/login.yaml')
    def test_2_login(self, **kwargs):
        print('——————————登入云平台——————————')
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
        url = self.url + 'users/' + str(self.userId[0])
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

    @file_data(r'../data/volume_data/volume.yaml')
    def test_create_volume(self, **kwargs):
        # 创建虚拟磁盘
        create_volume_url = self.url + kwargs['create_volume_path']
        create_volume_headers = {}
        self.get_headers(create_volume_headers)
        create_volume_data = kwargs['data']
        res_create = self.kd.post(url=create_volume_url, data=create_volume_data, headers=create_volume_headers,
                                  params=kwargs['create_params'])
        print(kwargs['data'])
        print(create_volume_headers)
        print('创建磁盘的状态码结果是：', res_create.status_code)
        print('创建虚拟磁盘成功返回数据：', self.kd.json_format(res_create))
        # # TODO 获取当前zoneUuid
        # 查看虚拟磁盘是否创建成功
        check_volume_url = self.url3 + kwargs['check_volume_path']
        check_volume_headers = {}
        self.get_headers(check_volume_headers)
        res_check = self.kd.get(url=check_volume_url, params=kwargs['check_params'], headers=check_volume_headers)
        # print(self.kd.json_format(res_check))
        print('查询磁盘的状态码结果是：', res_check.status_code)
        print(check_volume_url)
        name = self.kd.get_text(res_check.json(), 'name')
        self.assertIn(kwargs['check_volume_name'], name)
        temp_id = self.kd.get_text(res_check.json(), 'id')
        temp_uuid = self.kd.get_text(res_check.json(), 'uuid')
        temp_zoneId = self.kd.get_text(res_check.json(), 'zoneId')
        temp_domainId = self.kd.get_text(res_check.json(), 'domainId')
        temp_departmentId = self.kd.get_text(res_check.json(), 'departmentId')
        time.sleep(3)
        # # 删除虚拟磁盘
        # # TODO 此处需要删除创建的磁盘id
        # delete_volume_url = self.url + kwargs['delete_volume_path'] + str(temp_id)
        # delete_volume_headers = {}
        # self.get_headers(delete_volume_headers)
        # delete_volume_headers['uuid'] = str(temp_uuid[0])
        # delete_volume_headers['zoneId'] = str(temp_zoneId[0])
        # delete_volume_headers['domainId'] = str(temp_domainId[0])
        # delete_volume_headers['departmentId'] = str(temp_departmentId[0])
        # data = {
        #     "uuid": str(temp_uuid[0]),
        #     "zoneId": str(temp_zoneId[0]),
        #     "domainId": str(temp_domainId[0]),
        #     "departmentId": str(temp_departmentId[0])
        # }
        # res_delete = self.kd.delete(url=delete_volume_url, headers=delete_volume_headers,
        #                             data=data)
        # print(delete_volume_headers)
        # print('删除虚拟磁盘状态码结果：', res_delete.status_code)

    # 登出云平台
    @file_data(r'../data/login_out/logout.yaml')
    def test_logout(self, **kwargs):
        print('——————————登出云平台——————————')
        url = self.url2 + 'loginHistory/logoutSession?id=' + str(self.ldapUserId) + '&type=LOGOUT'
        headers = kwargs['headers']
        headers['x-auth-ldap-user-id'] = str(self.ldapUserId)
        headers['x-auth-token'] = self.token
        headers['x-auth-user-id'] = str(self.ldapUserId)
        res = self.kd.get(url=url, headers=headers)
        print(url)
        print(self.kd.json_format(res))
