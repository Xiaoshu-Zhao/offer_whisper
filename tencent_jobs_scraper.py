import json
import requests
import time

def get_tencent_jobs(city: str = "", career_category: str = "", key_word: str = "", new_grad: bool = False):
    """
    获取腾讯招聘信息
    :param city: 城市名称
    :param career_category: 职位类别
    :param key_word: 关键词
    :param new_grad: 是否为应届生
    """

    # 获取当前时间戳（毫秒级）
    current_timestamp = int(time.time() * 1000)
    
    # API URL
    url = f"https://careers.tencent.com/tencentcareer/api/post/Query"

    category_dict = {
        "技术": "40001001,40001002,40001003,40001004,40001005,40001006",
        "产品": "40003001,40003002,40003003",
    }
    
    # 请求参数, 分页查询所有职位
    params = {
        "timestamp": current_timestamp,
        "countryId": "",
        "cityId": "",
        "bgIds": "",
        "productId": "",
        "categoryId": category_dict[career_category],
        "parentCategoryId": "",
        "attrId": "2" if new_grad else "1",
        "keyword": key_word,
        "pageIndex": "1",
        "pageSize": "10",
        "language": "zh-cn",
        "area": "cn"
    }
    
    try:
        # 发送GET请求
        response = requests.get(url, params=params)
        # 确保请求成功
        response.raise_for_status()
        # 返回JSON数据
        return response.json()
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    jobs = get_tencent_jobs(career_category="技术", key_word="大模型")
    """把整个jobs数据写入json文件"""
    with open("tencent_jobs.json", "w") as f:
        json.dump(jobs, f, ensure_ascii=False)
    if jobs and jobs.get("Code") == 200:
        print(f"Successfully retrieved {jobs['Data']['Count']} jobs") 