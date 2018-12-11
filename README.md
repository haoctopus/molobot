## **【中文简介】**

![img](README/xmolo-zx.png)

这是一个能让天猫精灵接入Home Assistant的组件. 通过使用此组件可以实现用语音让天猫精灵控制家里已经连上HA的硬件.

本组件不会上传用户所绑定天猫精灵的手机号和密码到服务器上, 而是将其通过SHA1哈希算法生成token来与阿里平台交互, 账号数据对于服务器透明, 不用担心账号安全问题:

```python
# molo_bot_client.py: get_phonesign(): Line 93
...
hkey = ("molobot:%s:%s" % (phone, password)).encode('utf-8')
self._phone_sign = hashlib.sha1(hkey).hexdigest()
return self._phone_sign
...
```

**【一键安装】**

在终端直接执行下面命令一键安装molobot:

```shell
python <(curl "https://raw.githubusercontent.com/haoctopus/molobot/master/auto_install.py" -s -N)
```

等待提示安装成功后手动重启Home Assistant即可。

若此方法安装失败，请用下面的方法手动安装。有`curl`组件的Windows用户也可以通过`cmd`。

**【安装软件】**

- [molobot组件](https://github.com/haoctopus/molobot)

下载`molobot`文件夹，保存在`<homeassistant配置目录>/custom_components/`目录中，若`custom_components`目录不存在则自行创建。

- homeassistant配置目录在哪?

**Windows用户:** `%APPDATA%\.homeassistant`

**Linux-based用户:** 可以通过执行`locate .homeassistant/configuration.yaml`命令，查找到的`.homeassistant`文件夹就是配置目录。

**群晖Docker用户:** 进入Docker - 映像 - homeassistant - 高级设置 - 卷, `/config`对应的路径就是配置目录

![img](README/docker.png)

**【HA中配置实例】**

```yaml
molobot:
  phone: 131xxxxxxxx  # 天猫精灵绑定的手机号
  password: 123456    # 绑定密码
```

**【天猫精灵app中配置实例】**

打开天猫精灵app - 我的 - 添加智能设备 - 找到MoloBot - 绑定设备 - 账户配置 - 填写手机号和密码:

![img](README/tmall.png)

绑定成功后就能在天猫精灵app中看到HA中绑定的设备.

![img](README/tmall-device.png)

**【支持设备及属性】**

目前支持的设备类型有: 灯, 开关, 传感器.

目前支持的属性: 亮度, 颜色, 开关, 温度, 湿度.

**【相关链接】**

平台网站：<https://www.molo.cn>

molobot组件：<https://github.com/haoctopus/molobot>

**【联系我们】**

如果安装和使用过程中遇到任何问题，可以通过以下方式联系我们，我们将在看到反馈后第一时间作出回应:

Email: octopus201806@gmail.com

QQ群: 598514359

****

## **【Description in English】**

![img](README/xmolo-zx.png)

This is a component that allows the Tmall Genie to access Home Assistant. By using this component, you can use the voice to let the Tmall Genie control the devices that has connected to the HA.

This component does not upload the phone number and password binds to the Tmall Genie to server. Instead, it generates a token through the SHA1 hash algorithm to interact with the Aligenie platform. The account data is transparent to the server, so there is no need to worry about account security:

```python
# molo_bot_client.py: get_phonesign(): Line 93
...
hkey = ("molobot:%s:%s" % (phone, password)).encode('utf-8')
self._phone_sign = hashlib.sha1(hkey).hexdigest()
return self._phone_sign
...
```

**【One-key install】**

If you are Linux-based user, run the command below to install molobot automatically:

```shell
python <(curl "https://raw.githubusercontent.com/haoctopus/molobot/master/auto_install.py" -s -N)
```

Wait untill installation success, and restart your Home Assistant.

If this not working, please install molobot manually according to the next section. For Windows user with `curl` component, run the command line in `cmd`.

**【Installation】**

- [molobot component](https://github.com/haoctopus/molobot)

Download `molobot` folder and put it under `homeassistant configuration directory/custom_components/`. If `custom_components` doesn't exist, create one.

- Where is homeassistant configuration directory?

**Windows user:** `%APPDATA%\.homeassistant`

**Linux-based user:** Run command line `locate .homeassistant/configuration.yaml`. The `.homeassistant` folder in the returning result is the configuration directory.

**Synology NAS Docker user:** Go to Docker - Images - Homeassistant - Advanced settings - Volumes, the path corresponding to `/config` is the configuration directory.

![img](README/docker.png)

**【Configuration】**

```yaml
molobot:
  phone: 131xxxxxxxx  # phone number binds to the Tmall Genie
  password: 123456    # binding password
```

**【Tmall Genie app configuration】**

Open Tmall Genie app - 我的 - 添加智能设备 - 找到MoloBot - 绑定设备 - 账户配置 - 填写手机号和密码:

![img](README/tmall.png)

After the binding is successful, you can see the device bound in HA in the Tmall Genie app.

![img](README/tmall-device.png)

**【Supported devices and attributes】**

Currently supported device types: lights, switches, sensors.

Currently supported attributes: brightness, color, switch, temperature, humidity.

**【Reference link】**

Platform link：<https://www.molo.cn>

molobot component：<https://github.com/haoctopus/molobot>

**【Contact us】**

Please contact us if you have any questions about installation and using molobot. We will respond as soon as we see the feedback.

Email: octopus201806@gmail.com

QQGroup: 598514359