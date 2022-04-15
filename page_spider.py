import requests
from lxml import etree
import re
import pandas as pd

#抓取电影信息https://blog.csdn.net/jujudeyueyue/article/details/121193114
#lxml介绍 https://www.cnblogs.com/baowee/p/11364941.html
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
}

cookies = {
    'Cookie': 'bid=AWOYUIKrYws; douban-fav-remind=1; __gads=ID=738bbe658a3a183d-2238a9df1dc800a3:T=1620703677:RT=1620703677:S=ALNI_MZKROUeHHVW9qQRGDn73cDbeWCCig; __utmz=30149280.1620703679.1.1.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; ll="108296"; __utmc=30149280; __utma=30149280.1138384679.1620703679.1633849013.1633853022.3; apiKey=; _pk_ref.100001.2fad=%5B%22%22%2C%22%22%2C1633855761%2C%22https%3A%2F%2Fmovie.douban.com%2Fsubject%2F25845392%2Fcomments%3Fstart%3D220%26limit%3D20%26status%3DP%26sort%3Dnew_score%22%5D; _pk_ses.100001.2fad=*; push_noty_num=0; push_doumail_num=0; __utmv=30149280.24819; _pk_id.100001.2fad=7c075faeee902152.1633855761.1.1633856865.1633855761.; login_start_time=1633856897218; user_data={%22area_code%22:%22+86%22%2C%22number%22:%2217854207497%22%2C%22code%22:%222300%22}; dbcl2="248193763:4+KQgP7f2N8"; vtoken=undefined; last_login_way=phone; ck=kNTl; ap_v=0,6.0; __utmt=1; __utmb=30149280.11.10.1633853022'
}

start = 20
url = 'https://movie.douban.com/subject/25845392/comments?start=20&limit=20&status=P&sort=new_score'
response = requests.get(url=url, headers=headers, cookies=cookies)
tree = etree.HTML(response.text)
div_list = tree.xpath('//*[@id="comments"]/div')

for d in div_list:
    vote_start = d.xpath('.//span[@class="votes vote-count"]/text()')[0]
    vote_user = d.xpath('.//span[@class="comment-info"]/a/text()')[0]
    vote_comment = d.xpath('.//span[@class="short"]/text()')[0]
    print("{} {} {}".format(vote_user,vote_start,vote_comment))
# while start < 500:
#     print(start)
#     # 要爬取的页面网址
#     url = 'https://movie.douban.com/subject/25845392/comments?start=%d&limit=20&status=P&sort=new_score' % start
#     response = requests.get(url=url, headers=headers, cookies=cookies)
#     # 获得该页面的所有信息，是字符串的
#     page_text = response.text

    # # 利用xpath进行解析解析
    # tree = etree.HTML(page_text)
    # # 获得该页面所有评论对应的div标签，这里得到的是一个列表
    # div_list = tree.xpath('//*[@id="comments"]/div')
    #
    # total_data = []
    #
    # # 一页中有20条评论
    # # 对于每条评论的div标签，进行进一步的解析，获取想要得到的字段
    # for div in div_list[:20]:
    #     vote_count = div.xpath('.//span[@class="votes vote-count"]/text()')[0]
    #     name = div.xpath('.//span[@class="comment-info"]/a/text()')[0]
    #     try:
    #         star = re.search('\d', div.xpath('.//span[@class="comment-info"]/span[2]/@class')[0]).group()
    #     except:
    #         star = ' '
    #     time = div.xpath('.//span[@class="comment-info"]/span[@class="comment-time "]/text()')[0].strip('\n').strip(
    #         ' ').strip('\n')
    #     text = div.xpath('./div[2]/p/span/text()')[0]
    #     data = [name, star, vote_count, time, text]
    #     total_data.append(data)
    # print(len(total_data))
    #
    # # 将爬取得到的数据储存起来
    # mydata = pd.DataFrame(total_data, columns=['name', 'star', 'vote_count', 'time', 'text'])
    # if start == 0:
    #     mydata.to_csv('./duanping.csv', index=False, encoding="utf_8_sig")
    # else:
    #     mydata.to_csv('./duanping.csv', index=False, encoding="utf_8_sig", mode='a', header=False)
    # start += 20
