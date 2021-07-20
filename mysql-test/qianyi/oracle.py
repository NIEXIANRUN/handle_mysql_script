#coding=utf-8
#backup status
#tablespce useage
#disk usage
#asm diskgroup usage
import cx_Oracle,pymysql
from sshtunnel import SSHTunnelForwarder
import paramiko, base64
from heapq import merge


def get_insp_hosts():
    db = pymysql.connect(host="dbmonitor-1e296.zjjpt-lycore.svc.cs1-ly.hpc", user='inspection', password="e9IQzSVv5FZ0yfPh",database="inspection", port=20001 )
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("select id,direct_ip,province,host_ip,vip,sid as ORACLE_SID,service_name,inst_port as port ,username,password from instances where province!='总部' and maintenance='是'") 
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data


def get_jumpserver(host):
    jumpservers=[
    {"province":"山东","jumpserver_ip":"172.20.28.29","jumpserver_user":"dbops"},
    {"province":"辽宁","jumpserver_ip":"172.20.12.24 ","jumpserver_user":"dbops"},
    {"province":"湖北","jumpserver_ip":"172.20.32.26","jumpserver_user":"dbops"},
    {"province":"江西","jumpserver_ip":"172.20.26.29 ","jumpserver_user":"dbops"},
    {"province":"山西","jumpserver_ip":"172.20.10.28","jumpserver_user":"dbops"},
    {"province":"吉林","jumpserver_ip":"172.20.14.43","jumpserver_user":"dbops"},
    {"province":"云南","jumpserver_ip":"172.20.44.86","jumpserver_user":"dbops"},
    {"province":"内蒙","jumpserver_ip":"172.20.54.61","jumpserver_user":"dbops"},
    {"province":"河北","jumpserver_ip":"172.20.8.31","jumpserver_user":"dbops"},
    {"province":"浙江","jumpserver_ip":"172.20.20.23","jumpserver_user":"dbops"},
    {"province":"安徽","jumpserver_ip":"172.20.22.24","jumpserver_user":"dbops"},
    {"province":"福建","jumpserver_ip":"172.20.24.76","jumpserver_user":"dbops"},
    {"province":"海南","jumpserver_ip":"172.20.38.40","jumpserver_user":"dbops"},
    {"province":"黑龙江","jumpserver_ip":"172.20.16.25","jumpserver_user":"dbops"},
    {"province":"宁夏","jumpserver_ip":"172.20.56.29","jumpserver_user":"dbops"},
    {"province":"四川","jumpserver_ip":"172.20.40.105","jumpserver_user":"dbops"},
    {"province":"天津","jumpserver_ip":"172.20.2.25","jumpserver_user":"dbops"},
    {"province":"广西","jumpserver_ip":"172.20.52.31","jumpserver_user":"dbops"},
    {"province":"贵州","jumpserver_ip":"172.20.42.23","jumpserver_user":"dbops"},
    {"province":"青海","jumpserver_ip":"172.20.50.64","jumpserver_user":"dbops"},
    {"province":"甘肃","jumpserver_ip":"172.20.48.25","jumpserver_user":"dbops"},
    {"province":"河南","jumpserver_ip":"172.20.30.86","jumpserver_user":"dbops"},
    {"province":"江苏 ","jumpserver_ip":"172.20.18.87","jumpserver_user":"dbops"},
    {"province":"重庆","jumpserver_ip":"172.20.6.46","jumpserver_user":"dbops"},
    {"province":"北京","jumpserver_ip":"172.20.0.67","jumpserver_user":"dbops"},
    {"province":"广东","jumpserver_ip":"172.20.36.190","jumpserver_user":"dbops"},
    {"province":"陕西","jumpserver_ip":"172.20.46.65","jumpserver_user":"dbops"},
    {"province":"湖南","jumpserver_ip":"172.20.34.73","jumpserver_user":"dbops"},
    {"province":"新疆","jumpserver_ip":"172.20.58.58","jumpserver_user":"dbops"},
    {"province":"上海","jumpserver_ip":"172.20.4.61","jumpserver_user":"dbops"},
    ]
    for j in jumpservers:
        if j["province"]==host['province']:
            return j


def get_insp_items():
    db = pymysql.connect(host="dbmonitor-1e296.zjjpt-lycore.svc.cs1-ly.hpc", user='inspection', password="e9IQzSVv5FZ0yfPh",database="inspection", port=20001 )
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("select item_name,item_sql from insp_items limit 1") 
    data = cursor.fetchall()
    cursor.close()
    db.close()
    return data


def run_insp_host_with_tunnel(host):
    username=host['username']
    password=host['password']
    if host['vip'] is not None:
        ip=host['vip']
    else:
        ip=host['host_ip']
    try:
        with SSHTunnelForwarder(
                (host['jumpserver_ip'], 22),  # 跳板机
                ssh_username=host['jumpserver_user'],
                ssh_pkey="/home/zx_huanglong/.ssh/id_rsa",
                remote_bind_address=(ip, int(host['port'])),  # 远程的服务器
                local_bind_address=('0.0.0.0', 0)  # 开启本地转发端口
                ) as server:
            server.start()  # 开启隧道
            print(server.local_bind_port)
            if host['service_name'] is None:
                tns=cx_Oracle.makedsn('127.0.0.1',str(server.local_bind_port),sid=host['ORACLE_SID'])
            else:
                tns=cx_Oracle.makedsn('127.0.0.1',str(server.local_bind_port),service_name=host['service_name'])
            conn = cx_Oracle.connect(username,password,tns)
            cursor = conn.cursor()
            items=get_insp_items()  
            for item in items:        
                sql = item['item_sql']
                cursor.execute(sql)
                row=cursor.fetchall()
                if len(row)>0:
                    save_insp_data(host['id'], item['item_name'], row[0][0])
                else:
                    save_insp_data(host['id'], item['item_name'], None)
            cursor.close()
            conn.close()
        server.close()
    except Exception as e:
        print(e)


def save_insp_data(instance_id,item_name,insp_result): 
    db = pymysql.connect(host="dbmonitor-1e296.zjjpt-lycore.svc.cs1-ly.hpc", user='inspection', password="e9IQzSVv5FZ0yfPh",database="inspection", port=20001 )
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("insert into insp_results(instance_id,item_name,item_result) values ('%s','%s','%s')" % (instance_id,item_name,insp_result))        
    db.commit()
    cursor.close()
    db.close() 
def save_insp_disk_usage(instance_id,data): 
    db = pymysql.connect(host="dbmonitor-1e296.zjjpt-lycore.svc.cs1-ly.hpc", user='inspection', password="e9IQzSVv5FZ0yfPh",database="inspection", port=20001 )
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    sql="insert into insp_disk_usage(filesystem,size,used,avail,use_percent,mountedon,instance_id) values (%s,%s,%s,%s,%s,%s,%s)"
    data=tuple(data)+(instance_id,)
    cursor.execute(sql,data)        
    db.commit()
    cursor.close()
    db.close()      
def exec_host_command_with_tunnel(host,command):
    try:
        with SSHTunnelForwarder(
                    (host['jumpserver_ip'], 22),  # 跳板机
                    ssh_username=host['jumpserver_user'],
                    ssh_pkey="/home/zx_huanglong/.ssh/id_rsa",
                    remote_bind_address=(host['host_ip'], 22),  # 远程的服务器
                    local_bind_address=('0.0.0.0', 0)  # 开启本地转发端口
                    ) as server:
            server.start()  # 开启隧道
            
            result= exec_ssh_command('127.0.0.1',server.local_bind_port,command)        
            server.close()
            return result
    except Exception as e:
        print(e)
def exec_host_command(host,command):
    if host.has_key('jumpserver_ip'):
        result=exec_host_command_with_tunnel(host,command)
    else:       
        result=exec_ssh_command(host['jumpserver_ip'],22,command)        
    return  result
def exec_ssh_command(ip,port,command):
        key =paramiko.RSAKey.from_private_key_file('/home/zx_huanglong/.ssh/id_rsa')
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, port=port,username='oracle', password='')
        stdin, stdout, stderr = client.exec_command(command,timeout=10)
        result=stdout.readlines()
        client.close()
        return result
def get_disk_usage(host):
    print("checking disk usage of %s ...." % host['host_ip'])
    result=exec_host_command(host, 'df -kP')
    if result is not None:
        for i in range(len(result)):
            if i>=1:
                r=result[i]
                if len(r.split())==6:
                    save_insp_disk_usage(host['id'],r.split())
                else:
                    print(host['host_ip'],r.split())
        print("sucessced")
    else:
        print("check disk usage of %s failed!" % host['host_ip'])
def run_insp_host(host):
    try:
        username=host['username']
        password=host['password']
        
        if host['service_name'] is None:
            tns=cx_Oracle.makedsn(host['direct_ip'],host['port'],sid=host['ORACLE_SID'])  
        else:
            tns=cx_Oracle.makedsn(host['direct_ip'],host['port'],service_name=host['service_name'])        
        conn = cx_Oracle.connect(username,password,tns)
        cursor = conn.cursor()
        items=get_insp_items()  
        for item in items:        
            sql = item['item_sql']
            cursor.execute(sql)
            row=cursor.fetchall()
            if len(row)>0:
                save_insp_data(host['id'], item['item_name'], row[0][0])
            else:
                save_insp_data(host['id'], item['item_name'], None)
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
def insp_all_host_disk_usage():
    hosts=get_insp_hosts()
    for host in hosts:
        jumpserver=get_jumpserver(host)
        host=dict(jumpserver,**host)
        get_disk_usage(host)
        
def insp_all_instance_sql_item():
    hosts=get_insp_hosts()
    for host in hosts:
        print('---------------------',host['province'], host['host_ip'], host['port'],host['ORACLE_SID'],'---------------------')
        jumpserver=get_jumpserver(host)
        if jumpserver is not None:
            host=dict(jumpserver,**host)
        else:
            print('未找到对应跳板机信息')
        if host['direct_ip'] is not None:
            run_insp_host(host)
        elif host.has_key('jumpserver_ip'):
            run_insp_host_with_tunnel(host)
        else:
            run_insp_host(host)
insp_all_host_disk_usage()
#insp_all_instance_sql_item()
