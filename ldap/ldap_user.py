from ldap3 import Server, Connection, ALL, MODIFY_REPLACE
import string
import random
import re
import configparser
def accountSearch(conn, user_mail):
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

    return account_list


def accountAdd(conn, user_mail):
    account_list = list()
    account_dn = 'cn={},ou=users,dc=haixue,dc=com'.format(user_mail)
    conn.search(search_base=account_dn,
                search_filter='(objectClass=inetOrgPerson)',
                attributes=['cn', 'givenName'])
    if len(conn.response) < 1:
        conn.add(account_dn, attributes={'objectClass': ['inetOrgPerson', 'pwmUser'],
                                         'sn': user_mail, 'mail': user_mail, 'uid': user_mail,
                                         'cn': user_mail, 'userPassword': user_mail})
        account_list.append(user_mail)

    return account_list


def accountModify(conn, user_mail):
    account_dn = 'cn={},ou=users,dc=haixue,dc=com'.format(user_mail)
    passwd = '134567'
    conn.modify(account_dn, {'userPassword': [(MODIFY_REPLACE, [passwd])]})
    c.unbind()
    return "修改成功"


def accountDel(conn, user_mail):
    account_dn = 'cn={},ou=users,dc=haixue,dc=com'.format(user_mail)
    conn.delete(account_dn)
    if conn.response is None:
        return '删除失败，没有找到该用户'
    else:
        return '删除成功'


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('../config/ldap.cfg')
    admin_password = config['test']['password']
    rand_str = string.ascii_letters + string.digits
    passwd = ''.join(random.sample(rand_str, 8))
    server = Server('192.168.16.227', get_info='ALL')
    mail = 'xrf@haixue.com'
    c = Connection(server, 'cn=admin,dc=haixue,dc=com', admin_password, auto_bind=True)
    res = accountAdd(c,mail)
    if len(res) == 0:
        print("添加失败，用户{}已经存在".format(mail))
    else:
        print(("添加成功，用户名字:{}".format(mail)))
    # res = accountSearch(c, mail)
    # for i in res:
    #     print(i)
    # print('{},新密码为:{}'.format(accountModify(c, mail), passwd))

    # print(accountDel(c, mail))
    # c.unbind()
