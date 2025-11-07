# HiklQQBot-CXServerPlugin
# 这是什么
这是基于[HiklQQBot](https://github.com/kldhsh123/hiklqqbot)写的插件，用于查询SCP SL服务器信息得插件
# 安装
把两个Py文件复制到(你的hiklqqbot的目录)/plugins里然后重启机器人就可以了
# 使用
本插件有两个命令，分别是:\
<1>/绑定服务器\
子命令:\
->add,参数:<ServerKey><accountId><Port<可选，不填查询时会显示所有key和id为所填的服务器>>\
->remove,参数:<ServerKey><accountId>,删除所绑定的服务器\
->check,参数:<ServerKey><accountId>,检测该群是否绑定了这个服务器\
<以上命令都需要管理员权限>\
<2>/CX - 查询服务器状态请确保已使用/绑定服务器命令绑定了服务器
# 管理员的添加和删除
命令: /hiklqqbot_admin\
子命令: Add,Remove,Reload\
<1>add: 添加管理员,参数为用户的OpenId,用户发命令时后台日志会显示\
<2>remove: 删除管理员,参数为用户的OpenId\
<3>reload: 重载管理员\
# 缺陷
绑定服务器需要服务器的key和id,所以仅限已经上列表的服务器,也可以使用我另一个项目\
[A2S版本](https://github.com/SL-114514NM/HiklQQBot-CXServerForA2S)\
原理相同，但是使用A2S协议, 可以查询未上列表的服务器
