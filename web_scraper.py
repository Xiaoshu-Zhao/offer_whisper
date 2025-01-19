import requests
from bs4 import BeautifulSoup
import time
import json
import random
from datetime import datetime
from fake_useragent import UserAgent
import logging

def scrape_webpage(url):
    # 添加请求头，模拟浏览器访问
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # 发送 GET 请求获取网页内容
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 检查请求是否成功
        response.encoding = response.apparent_encoding  # 设置正确的编码
        
        # 使用 Beautiful Soup 解析网页
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 提取主要信息
        # 1. 页面标题
        title = soup.title.string if soup.title else "无标题"
        
        # 2. 所有段落文本
        paragraphs = [p.text.strip() for p in soup.find_all('p') if p.text.strip()]
        
        # 3. 所有链接
        links = [{'text': a.text.strip(), 'href': a.get('href')} 
                for a in soup.find_all('a') if a.get('href')]
        
        # 4. 主要文章内容（假设在 article 或 main 标签中）
        main_content = ""
        article = soup.find(['article', 'main'])
        if article:
            main_content = article.text.strip()
        
        return {
            'title': title,
            'paragraphs': paragraphs,
            'links': links,
            'main_content': main_content
        }
        
    except requests.RequestException as e:
        print(f"爬取过程中出现错误: {e}")
        return None

def scrape_tencent_jobs():
    # 设置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 初始化数据存储
    all_jobs = []
    
    try:
        # 创建 Session 对象以复用连接
        session = requests.Session()
        
        # 设置基础 headers
        base_headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Connection': 'keep-alive',
            'Referer': 'https://careers.tencent.com/search.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        
        page_index = 1
        while True:
            # 生成当前时间戳
            timestamp = int(datetime.now().timestamp() * 1000)
            
            # 构建URL
            url = (
                f"https://careers.tencent.com/tencentcareer/api/post/Query?"
                f"timestamp={timestamp}&countryId=&cityId=&bgIds=&productId="
                f"&categoryId=40001001,40001002,40001003,40001004,40001005,40001006"
                f"&parentCategoryId=&attrId=1&keyword=&pageIndex={page_index}"
                f"&pageSize=20&language=zh-cn&area=cn"
            )
            
            # 随机生成 User-Agent
            ua = UserAgent()
            headers = base_headers.copy()
            headers['User-Agent'] = ua.random
            
            # 添加随机延时
            sleep_time = random.uniform(2, 5)
            time.sleep(sleep_time)
            
            try:
                response = session.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # 检查返回数据
                if not data.get('Code') == 200:
                    logger.warning(f"页面 {page_index} 请求异常: {data}")
                    break
                
                posts = data.get('Data', {}).get('Posts', [])
                if not posts:
                    break
                
                # 处理当前页数据
                all_jobs.extend(posts)
                logger.info(f"成功获取第 {page_index} 页数据，共 {len(posts)} 条职位信息")
                
                # 判断是否还有下一页
                count = data.get('Data', {}).get('Count', 0)
                if len(all_jobs) >= count:
                    break
                
                page_index += 1
                
            except requests.exceptions.RequestException as e:
                logger.error(f"请求异常: {e}")
                break
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析异常: {e}")
                break
        
        # 保存数据到文件
        if all_jobs:
            filename = f"腾讯招聘信息_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"获取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"总职位数: {len(all_jobs)}\n\n")
                
                for i, job in enumerate(all_jobs, 1):
                    f.write(f"职位 {i}:\n")
                    f.write(f"职位名称: {job.get('RecruitPostName', '无')}\n")
                    f.write(f"职位类别: {job.get('CategoryName', '无')}\n")
                    f.write(f"所在地: {job.get('LocationName', '无')}\n")
                    f.write(f"职责: {job.get('Responsibility', '无')}\n")
                    f.write(f"要求: {job.get('Requirement', '无')}\n")
                    f.write(f"发布时间: {job.get('LastUpdateTime', '无')}\n")
                    f.write("-" * 50 + "\n")
            
            logger.info(f"数据已保存到文件: {filename}")
            return filename
        
    except Exception as e:
        logger.error(f"发生未知错误: {e}")
    
    return None

def main():
    # 示例使用
    # url = 'http://47.109.69.35/index.php/2024/04/06/面试日记-4-4（收集他人的）/'
    url = 'https://talent.taotian.com/off-campus/position-list?lang=zh&search=%E6%9D%AD%E5%B7%9E'
    
    result = scrape_webpage(url)
    
    if result:
        # 创建一个txt文件，使用文章标题作为文件名
        filename = f"{result['title'].replace('/', '_').replace(':', '_')}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"页面标题: {result['title']}\n\n")
            
            f.write("主要段落:\n")
            for i, p in enumerate(result['paragraphs'], 1):
                f.write(f"{i}. {p}\n")
            
            f.write("\n找到的链接:\n")
            for i, link in enumerate(result['links'], 1):
                f.write(f"{i}. {link['text']} -> {link['href']}\n")
            
            if result['main_content']:
                f.write("\n主要内容:\n")
                f.write(result['main_content'])
        
        print(f"爬取结果已保存到文件: {filename}")

    # 添加腾讯招聘信息爬取
    print("开始爬取腾讯招聘信息...")
    result_file = scrape_tencent_jobs()
    if result_file:
        print(f"腾讯招聘信息已保存到: {result_file}")
    else:
        print("爬取腾讯招聘信息失败")

if __name__ == "__main__":
    main() 