import unittest
from common.RequestHttp import Request
import configparser
from ddt import ddt, file_data
import readConfig


@ddt
class TestCase01(unittest.TestCase):

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
        print(self.kd.json_format(res))

    # 个人设置接口，用于获取APIkey
    @file_data(r'../data/getapikey.yaml')
    def test_3_apikey(self, **kwargs):
        print('——————————测试获取APIKEY——————————')
        url = self.url + 'users/' + str(self.userId[0])
        print(url)
        params = kwargs['params']
        headers = {}
        # 将公共头信息传到headers中
        headers['x-auth-login-token'] = self.loginToken
        headers['x-auth-ldap-user-id'] = str(self.ldapUserId)
        headers['x-auth-token'] = self.token
        headers['x-auth-user-id'] = str(self.ldapUserId)
        res = self.kd.get(url=url, params=params, headers=headers)
        print(res.json())
        TestCase01.kongApiKey = self.kd.get_text(res.json(), 'kongApiKey')
        TestCase01.kongSecretKey = self.kd.get_text(res.json(), 'kongSecretKey')

    def test_get_token(self):
        # 将之前用例中获取的token保存进行调用，但不调用用例执行步骤
        print('——————————测试中间值参数获取——————————')
        print('ldapuserid:', self.ldapUserId)
        print('token:', self.token)
        print('loginToken:', self.loginToken)
        print('kongApiKey:', self.kongApiKey)
        print('kongSecretKey:', self.kongSecretKey)

    # 获取请求头
    def _get_headers(self, headers):
        if headers is not None:
            headers['x-auth-login-token'] = self.loginToken
            headers['x-auth-ldap-user-id'] = str(self.ldapUserId)
            headers['x-auth-token'] = self.token
            headers['x-auth-user-id'] = str(self.ldapUserId)
            headers['apikey'] = self.kongApiKey
            headers['secretkey'] = self.kongSecretKey
        return headers

    @file_data(r'../data/company/company.yaml')
    def _test_create_company(self, **kwargs):
        # 创建公司
        create_company = self.usl + ['create_company_path']
        create_company_headers = {}
        self._get_headers(create_company_headers)
        create_company_data = kwargs['data']
        res_company_create = self.kd.post(url=create_company, data=create_company_data,
                                          headers=create_company_headers, params=kwargs['create_params'])
        print(res_company_create.json())

    @file_data(r'../data/department/department.yaml')
    def test_create_department(self, **kwargs):
        # 创建部门
        create_department = self.url + kwargs['create_department_path']
        create_department_headers = {}
        self._get_headers(create_department_headers)
        create_department_data = kwargs['data']
        res_department_create = self.kd.post(url=create_department, data=create_department_data,
                                             headers=create_department_headers, params=kwargs['create_params'])
        print(res_department_create.json())

    @file_data(r'../data/department/resourceDepartments.yaml')
    def _test_change_DptResource(self, **kwargs):
        print('——————————修改部门配额——————————')
        change_DptResource = self.url +'/resourceDepartments/create'
        change_DptResource_headers = {}
        self._get_headers(change_DptResource_headers)
        change_DptResource_data = kwargs['data']
        res_change_DptResource = self.kd.post(url=change_DptResource, data=change_DptResource_data,
                                             headers=change_DptResource_headers)
        print(res_change_DptResource.json())

    @file_data(r'../data/login_out/logout.yaml')
    def test_logout(self, **kwargs):
        print('——————————登出云平台——————————')
        url = kwargs['path'] + str(self.ldapUserId) + '&type=LOGOUT'
        headers = kwargs['headers']
        headers['x-auth-ldap-user-id'] = str(self.ldapUserId)
        headers['x-auth-token'] = self.token
        headers['x-auth-user-id'] = str(self.ldapUserId)
        res = self.kd.get(url=url, headers=headers)
        print(self.kd.json_format(res))
