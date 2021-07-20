from sshtunnel import SSHTunnelForwarder
import paramiko


def get_jump_server(host):
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


def exec_host_command_with_tunnel(host, command):
    try:
        with SSHTunnelForwarder(
                (host['jumpserver_ip'], 22),  # 跳板机
                ssh_username=host['jumpserver_user'],
                ssh_pkey="/home/zx_huanglong/.ssh/id_rsa",
                remote_bind_address=(host['host_ip'], 22),  # 远程的服务器
                local_bind_address=('0.0.0.0', 0)  # 开启本地转发端口
        ) as server:
            server.start()  # 开启隧道

            result = exec_ssh_command('127.0.0.1', server.local_bind_port, command)
            server.close()
            return result
    except Exception as e:
        print(e)


def exec_ssh_command(host, port, command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key_file = paramiko.RSAKey.from_private_key_file('/home/mysql/.ssh/id_rsa')
    ssh.connect(host, port=port, username='mysql', pkey=key_file, timeout=20)
    _, stdout, stderr = ssh.exec_command(command)
    out = stdout.readlines()
    err = stderr.readlines()
    if len(err) > 0:
        if err[0].find('No such file or directory'):
            return -2, out
        print(0, 'shell命令执行有误')
        ssh.close()
        return -1, out
    else:
        ssh.close()
        return 1, out


def get_public_key(file):
    with open(file, 'r') as f:
        for item in f.readlines():
            if item:
                public_key = item.strip()
                return public_key


def get_host_info(file):
    with open(file, 'r', encoding='utf8') as f:
        ip_list = []
        for line in f.readlines():
            if 'province' in line:
                province = line.split(':')[1].strip()
                continue
            if not line or '#' in line or 'ip' in line:
                continue
            ip = line.strip()
            ip_list.append(ip)
        return province, ip_list


if __name__ == '__main__':

    public_key_file = 'public_key.txt'
    host_info_file = 'host_info.txt'

    public_key = get_public_key(public_key_file)
    cmd = f"echo '{public_key}'>>/home/mysql/.ssh/authorized_keys"

    province, ip_list = get_host_info(host_info_file)

    for ip in ip_list:
        host = {'province': province, 'host_ip': ip}
        jump_server_info = get_jump_server(host)
        host = dict(jump_server_info, **host)
        exec_host_command_with_tunnel(host=host, command=cmd)