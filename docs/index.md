comments: true
![](https://pic.imgdb.cn/item/64f05326661c6c8e54fe9bf4.png)

有趣（YouQu）
================

```shell
# =============================================
# Attribution : Chengdu Test Department
# Time        : 2022/4/1
# Author      : Mikigo
# =============================================
```



><p>
><span id="busuanzi_container_site_pv">
>本站总访问量
><span id="busuanzi_value_site_pv">
></span>
>次
></span>    
></p>



欢迎在浏览器访问【[公网文档](https://linuxdeepin.github.io/deepin-autotest-framework/)】

统信公司内网还可以访问【[内网文档](http://youqu-dev.uniontech.com/)】，文档内容一样，访问速度更快哦~~

一、简介
------------

有趣（YouQu）是深度科技设计和开发的一个自动化测试基础框架，采用结构分层的设计理念，支持多元化元素定位和断言、用例标签化管理和执行、强大的日志和报告输出等特色功能，同时完美兼容X11、Wayland显示协议，环境部署简单，操作易上手。

### 爱上 “有趣” 的 17 个理由

1. 核心库提供了统一的接口，编写方法时只需要导入一个包就可以使用到核心库提供的所有功能；
2. 公共库封装了很多常用模块的相关方法，比如：任务栏的操作、桌面的操作、右键菜单的操作等等；
3. 除了常用的属性定位、图像识别以外，我们还提供基于 `UI` 的元素定位方案，其使用简单且高效，效果一定能惊讶到你；
4. 对属性定位的方法进行了二次封装，将编写属性定位的方法变得简单而优雅；
5. 对图像识别定位技术进行功能升级，除了支持单个坐标返回，还支持同一界面下多个相同元素返回多个坐标的功能；
6. 提供用例标签化管理、批量跳过和批量条件跳过的功能，你想不到一个 `csv` 文件原来能干这么多事情；
7. 提供了功能强大的执行器入口，让你可以方便的在本地执行任何用例集的用例，其丰富的自定义配置项，满足你对执行器所有的幻想；
8. 提供远程执行的功能，可以控制多台机器并行跑，或者分布式跑，这种付费功能现在免费给你用；
9. 提供自动输出日志的功能，你再也不用为每个方法单独写输出日志的代码，一切我们给你搞定了，日志输出不仅内容丰富，颜值也绝对在线，我们还自己设计了一款终端输出主题叫《五彩斑斓的黑》；
10. 提供了一键部署自动化测试环境的功能，连代码编辑器都给你装好了，让你再也不用为环境部署而烦恼；
11. 提供了自动生成多种报告的功能，你想输出什么报告形式都行，而且我们在报告中还加入了失败录屏和失败截图的功能；
12. 对断言进行了二次封装，提供更友好化的错误提示，让定位问题精准高效；
13. 不仅支持单条用例超时控制，而且还支持动态控制用例批量执行的总时间，确保 `CI` 环境下能顺畅运行；
14. 支持本地文件测试套执行、`PMS` 测试套执行、标签化执行方案，满足你各种场景下的执行需求；
15. 支持基于深度学习的 `OCR` 功能，可定位可断言，中文识别的天花板；
16. 完美兼容 `Wayland`  和 `X11`，真正做到一套代码，随处执行；
17. 支持多种方式的数据回填功能，其中异步回填的方案，完美解决了数据回填的耗时问题；

【[视频介绍](https://doc.uniontech.com/file/gXqmeOpjg4uGpRqo)】


二、安装使用
-------

基础框架：https://github.com/linuxdeepin/deepin-autotest-framework

从 PyPI 安装:

```shel
sudo pip3 install youqu
```

创建项目:

```shell
youqu-startproject youqu
```

安装依赖:

```sh
cd youqu
bash env.sh
```

> 注意，如果你的测试机密码不是 1 ，那你需要在全局配置文件 `globalconfig.ini` 里面将 `PASSWORD` 配置项修改为当前测试机的密码。

应用库：`https://gerrit.uniontech.com/admin/repos/autotest_ +  app_name`

链接后面的应用名称中间以下划线连接，比如音乐：https://gerrit.uniontech.com/admin/repos/autotest_deepin_music

```shell
cd apps/
```

将应用库拉到基础框架下 `apps` 目录下，像这样：

```shell
youqu
├── apps
│   ├── autotest_deepin_music  # 应用库
...
```

**应用库的名称不可以修改**。

三、运行
-------

### 1. 工作空间

基础框架工程目录建议放在 `~` 目录下，放在其他目录也可以运行，但是在自动化用例执行过程中可能需要做环境清理，放在其他目录存在代码被删除的风险。

如果你的机器上不同目录下存在多个 YouQu 工程，那么在运行之前，请先执行 env.sh 校正相关环境。

### 2. 执行器

在项目根目录下有一个 `manage.py` ，它是一个执行器入口，提供了本地执行、远程执行等的功能。

使用系统命令 `youqu` 来执行：

```shell
youqu manage.py run -a deepin-music
```

#### 2.1. 本地执行

```shell
youqu manage.py run
```

##### 2.1.1. 配置文件

通过配置文件配置参数

在配置文件 `setting/globalconfig.ini` 里面支持配置对执行的一些参数进行配置，常用的如：

```ini
;=============================== CASE CONFIG ===================================
[case]
;执行的应用名称
;为空表示执行 apps/ 目录下所有应用的用例
APP_NAME =

;执行包含关键词的用例
KEYWORDS =

;执行包含用例标签的用例
TAGS =
;1、KEYWORDS 和 TAGS 都为空表示执行 APP_NAME 的所有用例
;2、KEYWORDS 和 TAGS 都支持逻辑组合，即 and/or/not 的表达式, e.g. TAGS = L1 or smoke

;本地文件测试套，将要执行的用例写入指定的 csv 文件
;默认为空，从基础框架根目录开始：e.g. CASE_FILE = case_list.txt
;如果这里有值，APP_NAME KEYWORDS TAGS 的配置均不生效
CASE_FILE =

;=============================== RUNNER CONFIG ===================================
[runner]
;最大失败用例数量的占比
;比如：总执行用例数为100, 若 MAX_FAIL = 0.5,则失败用例数达到50就会终止测试。
MAX_FAIL = 0.5

;单条用例的超时时间，如果一条用例的执行时间超时，这条用例会被停止，后续用例继续执行。
;单位为秒
; 这是一个全局统一配置，如果某条用例需要单独配置超时时间，可以在用例中这样写：
;@pytest.mark.timeout(500)
;def test_xxx_001():
;    ...
;会话（所有用例执行的）超时是根据全局超时配置和用例单独超时配置自动计算的；
CASE_TIME_OUT = 200

;失败用例重跑次数
RERUN = 1

;失败录屏从第几次开始录制视频。
;比如 RECORD_FAILED_CASE = 1 ，表示用例第1次执行失败之后开始录屏。
;注意，用例失败重跑的次数不能小于失败录屏次数，即 RERUN >= RECORD_FAILED_CASE
RECORD_FAILED_CASE = 1

;批量执行时，终端输出的日志级别 DEBUG/INFO/ERROR
LOG_LEVEL = INFO

;yes 每条用例执行之后进行环境清理
CLEAN_ALL = yes

;检查测试机分辨率
RESOLUTION = 1920x1080

;不跳过用例，csv文件里面标记了 skip-xxx的用例不跳过
NOSKIP = no

;ignore fixed
;no，只要标记了fixed的用例，即使标记了skip-，也会执行；
;yes，fixed不生效，仅通过skip跳过用例；
IFIXED = no

;要安装deb包的路径
;e.g : ~/Downloads/ 安装下载目录下的deb包，如果是远程执行，会自动拷贝到远程并安装。
DEB_PATH =

;DEBUG 模式执行用例，只收集不执行用例，也不做设备分辨率的检查。
DEBUG = no

;记录top命令查询的系统资源占用情况，TOP = 3 表示记录前3个进程。
TOP =

;指定用例执行次数
REPEAT =

;默认在所有测试完成之后输出报错信息.
;yes, 测试过程中立即显示报错
DURING_FAIL = no

;=============================== REPORT CONFIG ===================================
[report]
;用例执行完后生成的测试报告格式
;目前支持 allure, xml, json （支持同时生成）
REPORT_FORMAT = allure, xml, json

;指定报告生成的路径（相对项目根目录下）
ALLURE_REPORT_PATH = report/
XML_REPORT_PATH = report/
JSON_REPORT_PATH = report/

;=============================== GLOBAL CONFIG ===================================
[globalconfig]
;测试机的密码
PASSWORD = 1

;图像识别重试次数
IMAGE_MATCH_NUMBER = 1

;图像识别重试每次间隔等待时间
IMAGE_MATCH_WAIT_TIME = 1

;图像识别匹配度
IMAGE_RATE = 0.9

;截取当前屏幕实时图像保存路径，用于图像识别坐标
SCREEN_CACHE = /tmp/screen.png

;截取屏幕上指定区域图片，保存临时图片的路径
TMPDIR = /tmp/tmpdir

;系统主题
SYS_THEME = deepin

;OCR服务端地址（不可随意修改）
OCR_SERVER_HOST = http://youqu-dev.uniontech.com:8890

;OpenCV服务端地址
OPENCV_SERVER_HOST = http://youqu-dev.uniontech.com:8889

;=============================== PMS CONFIG ===================================
;PMS相关配置，包含以下几个方面：
;1.PMS测试套执行
;2.自动从PMS爬取数据并同步本地CSV文件
;3.PMS数据回填
[pms]
;PMS的用户名: ut001234
PMS_USER =

;PMS的密码
PMS_PASSWORD =

;PMS测试套的ID
;在PMS上查看用例“套件”链接: https://pms.uniontech.com/testsuite-view-495.html
;测试套ID为: 495
SUITE_ID =

;数据回填必须关联PMS测试单
;在PMS上查看测试单链接: https://pms.uniontech.com/testtask-cases-20747.html
;测试单ID为: 20747
TASK_ID =

;将测试结果数据回填到PMS
;为空: 表示不回填,不会在每条用例执行完之后生成json结果文件;
;async: 表示逐条异步回填,后面一条执行开始时通过子线程对前一条用例的执行结果进行回填，如此实现时间效率最大化;
;finish: 表示所有用例执行完成之后逐个回填(PMS不支持并发);
SEND_PMS =

;数据回填的触发者
;auto: 框架自动回填,配合SEND_PMS配置使用,你可以选择在不同的阶段进行数据回填;
;hand: 手动回填,每条用例仍然会生成json文件,但框架不会进行数据回填,需要你可以在你想要发送的时间点手动触发回填;
TRIGGER = auto

;PMS回填的重试次数
;如果接口请求失败,会进行重试
SEND_PMS_RETRY_NUMBER = 2

[csv_link_pms_lib]
;caselib: 用例库
;testcase: 产品库用例
CASE_FROM = caselib

[csv_link_pms_id]
;同步PMS数据到本地CSV文件，必须要配置的配置项
;key是本地CSV文件的文件名称;
;value是对应PMS上的模块ID;
;比如要同步音乐的数据, 首先需要将配置 APP_NAME = deepin-music，
;CSV文件名称为music.csv，其在PMS上的用例为: https://pms.uniontech.com/caselib-browse-81.html
;因此应该配置为: music = 81
;这样才能将PMS与本地CSV文件建立联系。
;如果你的应用分了很多模块,只需要将对应的信息依次配置好就行了。
music =


[export_csv]
;导出的csv文件名称，默认 case_list.csv
CSV_FILE = case_list.csv

;exportcsv 命令导出 case_list.csv 文件时配置的字段名，用例名称默认存在第一列，无需添加
CSV_HEARD = 用例级别,用例类型,测试级别,是否跳过
```

配置完成之后，直接在命令行执行 `manage.py` 就好了。

```shell
youqu manage.py run
```

##### 2.1.2. 命令行参数

通过命令行参数配置参数

以下为 `youqu manage.py run` 提供的一些参数选项：

```coffeescript
  -a APP, --app APP     应用名称：deepin-music 或 autotest_deepin_music 或
                        apps/autotest_deepin_music
  -k KEYWORDS, --keywords KEYWORDS
                        用例的关键词,支持and/or/not逻辑组合
  -t TAGS, --tags TAGS  用例的标签,支持and/or/not逻辑组合
  --rerun RERUN         失败重跑次数
  --clean {yes,}        清理环境
  --report_formats REPORT_FORMATS
                        测试报告格式
  --max_fail MAX_FAIL   最大失败率
  --log_level LOG_LEVEL
                        日志输出级别
  --timeout TIMEOUT     单条用例超时时间
  --resolution RESOLUTION
                        检查分辨率
  --debug DEBUG         调试模式
  --noskip {yes,}       csv文件里面标记了skip跳过的用例不生效
  --ifixed {yes,}       fixed不生效，仅通过skip跳过用例
  --send_pms {,async,finish}
                        数据回填
  --task_id TASK_ID     测试单ID
  --trigger {,auto,hand}
                        触发者
  -f CASE_FILE, --case_file CASE_FILE
                        根据文件执行用例
  --deb_path DEB_PATH   需要安装deb包的本地路径
  --pms_user PMS_USER   pms 用户名
  --pms_password PMS_PASSWORD
                        pms 密码
  --suite_id SUITE_ID   pms 测试套ID
  --pms_info_file PMS_INFO_FILE
                        pms 信息文件
  --top TOP             过程中记录top命令中的值
  --lastfailed          仅执行上次失败用例
  --duringfail          测试过程中立即显示报错
  --repeat REPEAT       指定用例执行次数
  --project_name PROJECT_NAME
                        工程名称（写入json文件）
  --build_location BUILD_LOCATION
                        构建地区（写入json文件）
  --line LINE           执行的业务线（写入json文件）
```

在一些 CI 环境下使用命令行参数会更加方便：

```shell
youqu manage.py run --app deepin-music --keywords "xxx" --tags "xxx"
```

**命令行参数优先级是高于配置文件的，也就是说通过命令行参数指定了对应的参数，配置文件中不管是否配置均不生效。**

--app 入参还支持 `autotest_xxx` 和 `apps/autotest_xxx` 两种写法，方便在输入命令的过程中使用补全，下面的远程执行功能同样支持。

#### 2.2. 远程执行

```shell
youqu manage.py remote
```

远程执行同样通过配置文件 `setting/globalconfig.ini` 进行用例相关配置；

需要重点说一下远程执行时的测试机信息配置，在配置文件 `setting/remote.ini`  里面配置测试机的用户名、IP、密码。

```ini
;=============================== CLIENT LIST =====================================
; 测试机配置列表
;[client{number}]     ;测试机别名，有多少台测试机就写多少个 client，别名必须包含 client 字符，且不能重复。
;user =               ;测试机 user
;ip =                 ;测试机 ip
;password = 1         ;测试机的密码, 可以不配置此项，默认取 CLIENT_PASSWORD 的值；
                      ;如果你所有测试机密码都相同，那么只需要配置 CLIENT_PASSWORD 就可以了
;=================================================================================

[client1]
user = uos
ip = 10.8.15.xx

[client2]
user = uos
ip = 10.8.15.xx

[client3]
user = uos
ip = 10.8.11.xx
```

有多少台机器就像这样挨着写就行了。

然后在命令行：

```shell
youqu manage.py remote
```

这样运行是从配置文件去读取相关配置。

如果你不想通过配置文件，你仍然通过命令行参数进行传参，

以下为 `python3 manage.py remote` 提供的一些参数选项：

```coffeescript
  -a APP, --app APP     应用名称：deepin-music 或 autotest_deepin_music 或
                        apps/autotest_deepin_music
  -c CLIENTS, --clients CLIENTS
                        远程机器的user@ip:password,多个机器用'/'连接,如果password不传入,默认取
                        setting/remote.ini 中 CLIENT_PASSWORD
                        的值,比如：uos@10.8.13.33:1 或 uos@10.8.13.33
  -k KEYWORDS, --keywords KEYWORDS
                        用例的关键词,支持and/or/not逻辑组合
  -t TAGS, --tags TAGS  用例的标签,支持and/or/not逻辑组合
  -s {yes,no,}, --send_code {yes,no,}
                        发送代码到测试机（不含report目录）
  -e, --build_env       搭建测试环境,如果为yes，不管send_code是否为yes都会发送代码到测试机.
  -p CLIENT_PASSWORD, --client_password CLIENT_PASSWORD
                        测试机密码（全局）
  -y PARALLEL, --parallel PARALLEL
                        yes:表示所有测试机并行跑，执行相同的测试用例，no
                        :表示测试机分布式执行，服务端会根据收集到的测试用例自动分配给各个测试机执行。
  --rerun RERUN         失败重跑次数
  --clean {yes,}        清理环境
  --report_formats REPORT_FORMATS
                        测试报告格式
  --log_level LOG_LEVEL
                        日志输出级别
  --timeout TIMEOUT     单条用例超时时间
  --debug DEBUG         调试模式
  --noskip {yes,}       csv文件里面标记了skip跳过的用例不生效
  --ifixed {yes,}       fixed不生效，仅通过skip跳过用例
  --send_pms SEND_PMS   数据回填
  --task_id TASK_ID     测试单ID
  --deb_path DEB_PATH   需要安装deb包的本地路径
```

在命令行这样运行：

```shell
youqu manage.py remote -a deepin-music -c uos@10.8.13.33/uos@10.8.13.34 -k "xxx" -t "xxx"
```

所有用例执行完之后会在 `report` 目录下回收各个测试机执行的测试报告。

配置文件其他相关配置项详细说明，请查看配置文件中的注释内容。

#### 2.3. PMS 数据回填

测试单关联的用例，自动化测试对应的去跑这些关联的用例，并且将执行的结果回填的测试用例的状态里面。

PMS 数据回填主要有三种方式：

（1）异步回填

在用例执行的过程中，采用异步的方式去进行数据回填，直白的讲就是，第二条用例开始跑的时候，通过子线程去做第一条用例的数据回填，如此循环，直到所有用例执行结束；

这种方案的时间效率最高的，因为理论上用例的执行时间是大于数据回填的接口请求时间的，也就是说，当用例执行完之后，数据回填也完成了。

使用方法，在 `globalconfig.ini` 里面配置以下参数：（以下涉及到的参数配置都是在配置文件里面进行配置）

```ini
PMS_USER = PMS账号
PMS_PASSWORD = PMS密码
SEND_PMS = async
TASK_ID = 测试单ID
TRIGGER = auto
APP_NAME = 这个参数可填可不填，但是填了可以提高用例的执行速度，因为在用例收集阶段可以指定到具体的应用库。（下同）
```

（2）用例执行完之后回填

等所有用例执行完之后，再逐个进行回填的接口请求，此方案时间效率比较低。

使用方法：

```ini
PMS_USER = PMS账号
PMS_PASSWORD = PMS密码
SEND_PMS = finish
TASK_ID = 测试单ID
TRIGGER = auto
APP_NAME = 
```

（3）手动回填

所有用例执行完之后不做回填的接口请求，后续手动将结果进行回填请求。

用例执行时配置：

```ini
PMS_USER = PMS账号
PMS_PASSWORD = PMS密码
SEND_PMS = finish
TASK_ID = 测试单ID
TRIGGER = hand
APP_NAME = 
```

后续手动回填方法：

```shell
youqu manage.py pms --send2task yes
```

##### 可能遇到的问题

由同学可能会发现，怎么回填一次之后，后面想再次回填就不生效了；

这是因为为了应对前面提到的多种数据回填的方式，在 `report` 目录下会由 `pms_xxx` 开头的目录，记录了用例的执行结果和回填情况，如果这条用例之前已经回填过了，后续就不会再此触发回填了；

如果你想重新做回填，你可以把 `report/pms_xxx` 目录删掉，这样就可以重新做数据回填了；

#### 2.4. 导出 CSV 文件

框架提供导出指定标签用例的功能：

```shell
youqu manage.py exportcsv -a deepin-album -t CICD
```

表示导出 `deepin-album` 的用例中标记了 `CICD` 标签的用例，导出 `CSV` 文件的字段格式已经适配了 `CICD` 的要求。

#### 2.5. 脚手架新建 APP 工程

新建一个 APP 工程：

```shell
youqu manage.py startapp autotest_deepin_some  
```

这样在 `apps` 目录下会创建一个子项目工程 `autotest_deepin_some`，同时新建好工程模板目录和模板文件：

```shell
apps
└── autotest_deepin_some
    ├── case
    │   ├── assert_res
    │   │   └── readme
    │   ├── base_case.py
    │   └── __init__.py
    ├── config.ini
    ├── config.py
    ├── conftest.py
    ├── control
    ├── deepin_some_assert.py
    ├── deepin_some.csv
    ├── __init__.py
    └── widget
        ├── base_widget.py
        ├── case_res
        │   └── readme
        ├── deepin_some_widget.py
        ├── __init__.py
        ├── other.ini
        ├── other_widget.py
        ├── pic_res
        │   └── readme
        └── ui.ini
```

`autotest_deepin_some` 是你的工程名称，比如：`autotest_deepin_music` ；

在此基础上，你可以快速的开始你的 AT 项目。

#### 2.6. 用例标签自动同步

用于自动同步 `PMS` 用例标签数据至本地 `CSV` 文件，主要通过以下几个配置来控制：

```ini
APP_NAME =  # 指定要同步的应用名称
PMS_USER =  # PMS的用户名
PMS_PASSWORD =  # PMS的密码
```

在 `[csv_link_pms_id]` 节点下指定 `csv` 文件名与 `PMS` 用例模块的对应关系，比如：

```ini
[csv_link_pms_id]
;同步PMS数据到本地CSV文件，必须要配置的配置项
;key是本地CSV文件的文件名称;
;value是对应PMS上的模块ID;
;比如要同步音乐的数据, 首先需要将配置 APP_NAME = deepin-music，
;CSV文件名称为music.csv，其在PMS上的用例为: https://pms.uniontech.com/testcase-browse-53.html
;因此应该配置为: music = 53
;这样才能将PMS与本地CSV文件建立联系。
;如果你的应用分了很多模块,只需要将对应的信息依次配置好就行了。
music = 53
```

将以上信息配置好之后，在命令行执行：

```shell
youqu manage.py pms --pms2csv yes
```

每次执行时原 `csv` 文件会自动备份在 `report/csv_back` 目录下，因此你不用担心脚本执行导致你的数据丢失。