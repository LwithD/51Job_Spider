from bs4 import BeautifulSoup
import re,json
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
import urllib.request
import urllib.error
import MySQLdb

#初始化变量
findJobName = re.compile(r'class="jname at">(.*?)</span>')

# chrome_options = Options()
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')

# baseurl = r"https://search.51job.com/list/000000,000000,0100%252c7800%252c7300%252c7900%252c7500,01%252c40,9,99,+,2,1.html?lang=c&postchannel=0000&workyear=01&cotype=99&degreefrom=04&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare="
# baseurl = r"https://search.51job.com/list/030200%252c080200%252c080400%252c080500%252c090200,000000,0000,00,9,99,python,2,1.html?lang=c&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare="


header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
    }




def askurl(url):
    
    req = urllib.request.Request(url=url,headers = header)
    try:
        response = urllib.request.urlopen(req)
        html = response.read().decode("gbk")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html

def post_salary(item_salary):
    if item_salary == "":
        return 0
    suffix = re.findall(r"[\u4e00-\u9fa5]*/.+",item_salary)[0]
    # print (suffix)
    Prefix = re.findall("[0-9]*-?[0-9]*",item_salary)[0]
    # print(Prefix)
    if "-" in Prefix:
        bottom_salary = float(re.findall("(.+)-",Prefix)[0])
        top_salary = float(re.findall("-(.+)",Prefix)[0])
        salary = bottom_salary + (top_salary-bottom_salary) * 0.4
    else:
        salary = float(Prefix)
    if suffix[0] == "万":
        salary = salary * 10000
    elif suffix[0] == "千":
        salary = salary * 1000
        
    if suffix[-1] == "年":
        salary = salary / 12
    if suffix[-1] == "天":
        salary = salary * 21.75  #劳动法月计薪天数

    return salary


def getJson(html):
    # job51 = open("51job.html",'r',encoding="gbk")
    # job51 = BeautifulSoup(html,"html.parser")
    data = re.findall(r"\"engine_search_result\":(.+?),\"jobid_count\"",html)
    jsonObj = json.loads(data[0])
    return jsonObj
    # for item in joblist.select(".e"):
    #     data = []  # 保存一部电影的所有信息
    #     item = str(item)
    #     job_name = re.findall(findJobName, item)[0]
    #     data.append(job_name)
    #     datalist.append(data)
    # print(datalist)


def save2DB(Json):
    db = MySQLdb.connect("localhost", "root", "a6277741230", "51job", charset='gbk' )
    cursor = db.cursor()
    for item in Json:
        sql = """INSERT INTO hangzhou_job(id,
            job_name, company, salary, city, trade, companytype_text)
            VALUES (0,'{}', '{}', {}, '{}', '{}','{}')""".format(item['job_name'],item['company_name'],post_salary(item['providesalary_text']),item['workarea_text'],item['companyind_text'],item['companytype_text'])
        try:
   # 执行sql语句
            cursor.execute(sql)
   # 提交到数据库执行
            db.commit()
        except:
   # Rollback in case there is any error
            db.rollback()

    # 关闭数据库连接
    db.close()


def main():
    for i in range(1,11):
        baseurl = r"https://search.51job.com/list/080200,000000,7800%252c7300%252c0100%252c2700%252c7500,00,9,99,+,2,{}.html?lang=c&postchannel=0000&workyear=01&cotype=99&degreefrom=04&jobterm=99&companysize=99&ord_field=0&dibiaoid=0&line=&welfare=".format(i)
        html = askurl(baseurl)
        json = getJson(html)
        save2DB(json)
        print("第{}页爬取成功".format(i))



if __name__ == "__main__":
    main()
