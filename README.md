## 中文简介

![img](README/xmolo-zx.png)

这是一个能让天猫精灵接入Home Assistant的组件. 通过使用此组件可以实现用语音让天猫精灵控制家里已经连上HA的硬件.

本组件不会上传用户所绑定天猫精灵的手机号和密码到服务器上, 而是将其通过SHA1哈希算法生成token来与阿里平台交互, 账号数据对于服务器透明, 不用担心账号安全问题:

```python
# molo_bot_client.py: get_phonesign(): Line 99
...
hkey = ("molobot:%s:%s" % (phone, password)).encode('utf-8')
self._phone_sign = hashlib.sha1(hkey).hexdigest()
return self._phone_sign
...
```

## 安装MoloBot

### 一键安装

>在终端直接执行下面命令一键安装molobot:
	
```shell
python <(curl "https://raw.githubusercontent.com/haoctopus/molobot/master/auto_install.py" -s -N)
```
	
>等待提示安装成功后手动重启Home Assistant即可。

>若此方法安装失败，请用下面的方法手动安装。有`curl`组件的Windows用户也可以通过`cmd`。

### 手动安装

- [molobot组件](https://github.com/haoctopus/molobot)

>>1、下载`molobot`文件夹，保存在`<homeassistant配置目录>/custom_components/`目录中，若`custom_components`目录不存在则自行创建。

>>2、编辑`<homeassistant配置目录>/custom_components/configuration.yaml`文件，添加如下配置
```yaml
molobot:
  phone: 131xxxxxxxx  # 天猫精灵绑定的手机号
  password: 123456    # 绑定密码
```


- homeassistant配置目录在哪?

>>**Windows用户:** `%APPDATA%\.homeassistant`

>>**Linux-based用户:** 可以通过执行`locate .homeassistant/configuration.yaml`命令，查找到的`.homeassistant`文件夹就是配置目录。

>>**群晖Docker用户:** 进入Docker - 映像 - homeassistant - 高级设置 - 卷, `/config`对应的路径就是配置目录


## 天猫精灵app中配置实例

* 打开天猫`精灵APP`
* 点击`我的`TAB
* 点击`添加智能设备`
* 找到`MoloBot`
* 点击`绑定设备`
* 填写`手机号`和`密码`
* 确认授权，返回我的TAB，智能家居下查看全部

## 高级配置

### 不绑定设备至`天猫精灵`的过滤配置
```yaml
molobot:
  phone: 131********
  password: ******
  filter:
    exclude_domains: #按domain过滤
      - sensor #过滤所有传感器
      - camera #过滤所有摄像头

    exclude_entities: #按设备过滤
      - light.gateway_light_1 #设备1
      - light.gateway_light_2 #设备2
```

### 设备配分组查询或控制
>比如小米传感器支持温度、湿度，在ha中被分为两个设备，但猫精不支持两个相同设备再同一房间，此时可以如下解决
```yaml
molobot:
  phone: 131********
  password: ******
  group:
    - name: test_input #多开关控制，查询时其中一个为关，则状态为关
      entities:
        - input_boolean.notify_home1
        - input_boolean.notify_home2

    - name: sensor #可同时查询温度、湿度
      entities:
        - sensor.humidity_1
        - sensor.temperature_2
```

### 禁止welcome molobot的通知提醒
```yaml
molobot:
  phone: 131********
  password: ******
  disablenotify: true
```

## 备注

__注意，由于天猫精灵本身不支持自定义别名，在绑定成功后请在app中对设备设置位置和别名，否则将不能对这些设备进行操作。例如在“客厅”内有两个“灯”，则这两个灯都不能正常操作，需要改为“卧室”的“灯”和“客厅”的“灯”，或者改为“客厅”的“灯”和“客厅”的“吊灯”，才能正常操作。__

### 支持设备及属性

目前支持的设备类型有: 灯、开关、传感器、风扇、空调、摄像头、播放器、二元选择器.

目前支持的属性: 亮度、颜色、开关、温度、湿度、模式.

	灯支持调整颜色
	空调支持更换模式，自动、制冷、制热、通风、送风、除湿；支持调节温度
	空调、风扇风速支持 自动、低风、中风、高风、最小、最大
	摄像头、播放器、二元选择器 只支持开关

### 相关链接

平台网站：<https://www.molo.cn>

molobot组件：<https://github.com/haoctopus/molobot>

### 联系我们

如果安装和使用过程中遇到任何问题，可以通过以下方式联系我们，我们将在看到反馈后第一时间作出回应:

Email: octopus201806@gmail.com

QQ群: 598514359

****

![img](README/tmall.png)

绑定成功后就能在天猫精灵app中看到HA中绑定的设备.

![img](README/tmall-device.png)

## Description in English

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

__Note that since the Tmall Genie itself does not support custom aliases, please set the location and alias for the device in the app after the binding is successful, otherwise you will not be able to operate on these devices. For example, if there are two "lights" in the "living room", then these two lights can not operate normally, and need to be changed to "bedroom light" and "living room light", or "living room light" and "living room chandelier" can be operated normally.__

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