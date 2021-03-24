# 封装接口
import requests
import json
import jsonpath


class Request:
    # 定义get请求的方法

    def get(self, url, headers=None, params=None):
        result = requests.get(url=url, params=params, headers=headers)
        return result
    # 定义post请求的方法
    def post(self, url, data=None, headers=None, params=None):
        # if data is not None:
        #     data = self.json_dump(data)
        result = requests.post(url=url, json=data, headers=headers, params=params)
        return result

    # 请求参数转换为json
    def json_dump(self, data):
        if data is not None:
            json_data = json.dumps(data, indent=2, ensure_ascii=False)
        else:
            json_data = []
        return json_data

    # 格式化输出的json格式
    def json_format(self, res):
        res_json = res.json()
        json_format = json.dumps(res_json, indent=2, ensure_ascii=False)
        return json_format

    # 定义put请求的方法
    def put(self, url, headers):
        result = requests.put(url=url, data=None, headers=headers)
        return result

    # 定义delete请求的方法
    def delete(self, url, headers, data=None):
        result = requests.delete(url=url, headers=headers, json=data)
        return result

    # 获取文本信息
    def get_text(self, res, key):
        if res is not None:
            try:
                # 将res转换为Json，通过Jsonpath解析获取到指定的key或value的值
                value = jsonpath.jsonpath(res, '$..{0}'.format(key))
                # Jsonpath获取的结果是list，如果失败返回False
                if value:
                    # 将list转化为string
                    if len(value) == 1:
                        return value[0]
                    else:
                        return value
                else:
                    return value
            except Exception as e:
                return e
        else:
            return None
