import xml.etree.ElementTree as ET
import json
import re
import requests
import requests
r=requests.post(url='http://ip.taobao.com/service/getIpInfo2.php', data={'ip': '223.104.192.174'})
print(r.json())