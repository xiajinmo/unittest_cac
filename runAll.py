import os
import common.HTMLTestRunner as HTMLTestRunner
import getpathInfo
import unittest
import time

path = getpathInfo.get_Path()
report_path = os.path.join(path, 'report')


class AllTest:
    def __init__(self):  # 初始化一些参数和数据
        global result_path
        # 报告命名时间格式化
        now = time.strftime("%Y-%m-%d %H")
        # 报告文件完整路径
        result_path = os.path.join(report_path, now + "_测试报告.html")
        # 配置执行哪些测试文件的配置文件路径
        self.caseListFile = os.path.join(path, "CaseList.txt")
        # 断言文件路径
        self.caseFile = os.path.join(path, "cases")
        self.caseList = []

    def set_case_list(self):
        """
        读取CaseList.txt文件中的用例名称，并添加到CaseList元素组
        :return:
        """
        fb = open(self.caseListFile)
        for value in fb.readlines():
            data = str(value)
            # 如果data非空且不以#开头
            if data != '' and not data.startswith("#"):
                # 读取每行数据会将换行转换为\n，去掉每行数据中的\n
                self.caseList.append(data.replace("\n", ""))
        fb.close()

    def set_case_suite(self):
        """
        :return:
        """
        # 通过set_case_list()拿到CaseList元素组
        self.set_case_list()
        test_suite = unittest.TestSuite()
        suite_module = []
        # 从CaseList元素组中循环取出case
        for case in self.caseList:
            # 通过split函数来将aaa/bbb分割字符串，-1取后面，0取前面
            case_name = case.split("/")[-1]
            # 打印出取出来的名称
            print(case_name + ".py")
            # 批量加载用例，第一个参数为用例存放路径，第一个参数为路径文件名
            discover = unittest.defaultTestLoader.discover(self.caseFile, pattern=case_name + '.py', top_level_dir=None)
            # 将discover存入suite_module元素组
            suite_module.append(discover)
            print('suite_module:' + str(suite_module))
        # 判断suite_module元素组是否存在元素
        if len(suite_module) > 0:
            # 如果存在，循环取出元素组内容，命名为suite
            for suite in suite_module:
                # 从discover中取出test_name，使用addTest添加到测试集
                for test_name in suite:
                    test_suite.addTest(test_name)
        else:
            print('else:')
            return None
        # 返回测试集
        return test_suite

    def run(self):
        """
        main
        :return:
        """
        try:
            # 调用set_case_suite获取test_suite
            suit = self.set_case_suite()
            print('try')
            print(str(suit))
            # 判断test_suite是否为空
            if suit is not None:
                print('if-suit')
                # 打开report/report.html测试报告文件，如果不存在就创建
                fp = open(result_path, 'wb')
                # 调用HTMLTestRunner
                runner = HTMLTestRunner.HTMLTestRunner(stream=fp, title='测试报告', description='测试结果')
                runner.run(suit)
            else:
                print("Have no case to test.")
        except Exception as ex:
            print(str(ex))

        finally:
            print("*********TEST END*********")
            fp.close()


if __name__ == '__main__':
    AllTest().run()
