from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
from django.shortcuts import render, HttpResponse, redirect, HttpResponseRedirect
import string
import random
from django.contrib import messages
from email.mime.text import MIMEText
from deploy_tools import settings
import smtplib


def sendMail(user_mail, passwd):
    title = 'LDAP账号开通通知'  # 邮件主题
    content = '''
    您好！LDAP账号已开通：
         账号：{}
         密码：{}
    可登录pwm.h.highso.com.cn修改密码
    VPN文档：https://www.tapd.cn/20094431/markdown_wikis/?#1120094431001039777
    跳板机文档：https://www.tapd.cn/20094431/markdown_wikis/?#1120094431001036383
    常用后台地址：https://www.tapd.cn/20094431/markdown_wikis/?#1120094431001042688
    '''.format(user_mail, passwd)
    message = MIMEText(content, 'plain', 'utf-8')  # 内容, 格式, 编码
    message['From'] = settings.mail_user
    message['To'] = user_mail
    message['Subject'] = title

    try:
        smtpObj = smtplib.SMTP_SSL(settings.mail_host, 465)  # 启用SSL发信, 端口一般是465
        smtpObj.login(settings.mail_user, settings.mail_pass)  # 登录验证
        smtpObj.sendmail(settings.sender, user_mail, message.as_string())  # 发送
        print("mail has been send successfully.")
    except smtplib.SMTPException as e:
        print(e)


def testHttp(request):
    conn = Connection(settings.ldap_host, settings.ldap_user, settings.ldap_password, auto_bind=True)
    user_mail = 'xierongfei@haixue.com'
    account_list = list()
    if len(user_mail) == 0:
        account_dn = 'ou=users,dc=haixue,dc=com'
    else:
        account_dn = 'cn={},ou=users,dc=haixue,dc=com'.format(user_mail)
    conn.search(search_base=account_dn,
                search_filter='(objectClass=inetOrgPerson)',
                attributes=['cn', 'givenName'])
    if len(conn.response) > 0:
        search_result = conn.response
        for u in range(len(search_result)):
            account_list.append(search_result[u]['attributes']['cn'][0])
    return render(request, "xrf-test.html", {"account_list": account_list})


def accountSearch(request):
    if request.method == 'POST' and request.POST.get('submit') == 'search':
        user_mail = request.POST.get('input')
    else:
        user_mail = ''
    conn = Connection(settings.ldap_host, settings.ldap_user, settings.ldap_password, auto_bind=True)

    account_list = list()
    print(user_mail)
    if user_mail is '':
        print("---------")
        account_dn = 'ou=users,dc=haixue,dc=com'
    else:
        account_dn = 'cn={},ou=users,dc=haixue,dc=com'.format(user_mail)
    conn.search(search_base=account_dn,
                search_filter='(objectClass=inetOrgPerson)',
                attributes=['cn', 'givenName'])
    if len(conn.response) > 0:
        search_result = conn.response
        for u in range(len(search_result)):
            account_list.append(search_result[u]['attributes']['cn'][0])

    return render(request, "ldap-account.html", {"account_list": account_list})


def accountAdd(request):
    if request.method == 'POST' and request.POST.get('submit') == 'add':
        user_mail = request.POST.get('input')
    else:
        user_mail = ''
    conn = Connection(settings.ldap_host, settings.ldap_user, settings.ldap_password, auto_bind=True)
    account_dn = 'cn={},ou=users,dc=haixue,dc=com'.format(user_mail)
    rand_str = string.ascii_letters + string.digits
    passwd = ''.join(random.sample(rand_str, 8))
    conn.search(search_base=account_dn,
                search_filter='(objectClass=inetOrgPerson)',
                attributes=['cn', 'givenName'])
    if len(conn.response) < 1:
        conn.add(account_dn, attributes={'objectClass': ['inetOrgPerson', 'pwmUser'],
                                         'sn': user_mail, 'mail': user_mail, 'uid': user_mail,
                                         'cn': user_mail, 'userPassword': passwd})
        res = ("{} 用户添加成功!密码:{}".format(user_mail, passwd))
        sendMail(user_mail, passwd)

    else:
        res = "{} 用户已经存在".format(user_mail)

    conn.unbind()
    messages.error(request, res)
    return HttpResponseRedirect("/ldap/account/index")


def accountModify(request):
    conn = Connection(settings.ldap_host, settings.ldap_user, settings.ldap_password, auto_bind=True)
    user_mail = request.GET.get('mail')
    account_dn = 'cn={},ou=users,dc=haixue,dc=com'.format(user_mail)
    rand_str = string.ascii_letters + string.digits
    passwd = ''.join(random.sample(rand_str, 8))
    conn.modify(account_dn, {'userPassword': [(MODIFY_REPLACE, [passwd])]})
    conn.unbind()
    res = ("{}修改成功!新密码:{}".format(user_mail, passwd))
    # return render(request, "xrf-test.html")
    messages.error(request, res)
    return HttpResponseRedirect("/ldap/account/index")


def accountDel(request):
    conn = Connection(settings.ldap_host, settings.ldap_user, settings.ldap_password, auto_bind=True)
    user_mail = request.GET.get('mail')
    account_dn = 'cn={},ou=users,dc=haixue,dc=com'.format(user_mail)
    conn.delete(account_dn)
    conn.unbind()
    res = "删除成功"
    # return render(request, "xrf-test.html")
    messages.error(request, res)
    return HttpResponseRedirect("/ldap/account/index")

