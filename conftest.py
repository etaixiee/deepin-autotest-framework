#!/usr/bin/env python3
# _*_ coding:utf-8 _*_

# SPDX-FileCopyrightText: 2023 UnionTech Software Technology Co., Ltd.

# SPDX-License-Identifier: GPL-2.0-only
# pylint: disable=C0301,R0912,C0413,R0914,W0212,R1702,R0915
# pylint: disable=C0114,W0621,C0411,C0412,R1706,E0401
import sys
from os import environ

environ["DISPLAY"] = ":0"
from setting.globalconfig import SystemPath

for i in SystemPath:
    if i.value not in sys.path:
        sys.path.append(i.value)

from os import walk
from os import popen
from os import system
from os import remove
from os import makedirs
from os.path import exists
from os.path import splitext
from enum import Enum
from time import sleep
from collections import deque
from datetime import datetime
from json import dumps
from re import findall
from shutil import copyfile
from multiprocessing import Process
from concurrent.futures import wait
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import ALL_COMPLETED

import letmego
import allure
import pytest
from _pytest.mark import Mark
from _pytest.terminal import TerminalReporter
from funnylog.conf import setting as log_setting

from setting.globalconfig import GlobalConfig

log_setting.LOG_FILE_PATH = GlobalConfig.REPORT_PATH
log_setting.CLASS_NAME_STARTSWITH = GlobalConfig.CLASS_NAME_STARTSWITH
log_setting.CLASS_NAME_ENDSWITH = GlobalConfig.CLASS_NAME_ENDSWITH
log_setting.CLASS_NAME_CONTAIN = GlobalConfig.CLASS_NAME_CONTAIN

from setting import skipif
from setting.globalconfig import ConfStr
from setting.globalconfig import FixedCsvTitle
from src import logger
from src.plugins.allure_report_extend import AllureReportExtend
from src.plugins import emoji_hooks
from src.cmdctl import CmdCtl
from src.pms._base import write_case_result
from src.pms._base import runs_id_cmd_log
from src.pms.task import Task
from src.pms.suite import Suite
from src.pms.send2pms import Send2Pms
from src.recording_screen import recording_screen

FLAG_FEEL = '=' * 10
LN = "\n"


class LabelType(Enum):
    """用例级别对应报告级别"""
    L1 = allure.severity_level.BLOCKER
    L2 = allure.severity_level.CRITICAL
    L3 = allure.severity_level.NORMAL
    L4 = allure.severity_level.MINOR


def add_mark(item, name: str = "", args: tuple = (), kwargs: dict = None):
    """add mark"""
    item.own_markers.append(Mark(name=name, args=args, kwargs=kwargs))


def write_json(session):
    """write json"""
    return bool(
        session.config.option.send_pms
        and (session.config.option.task_id or session.config.option.suite_id)
    )


def auto_send(session):
    """auto send"""
    return bool(
        session.config.option.send_pms and session.config.option.trigger
    )


def async_send(session):
    """async send"""
    return bool(
        session.config.option.send_pms == ConfStr.ASYNC.value
        and session.config.option.trigger == ConfStr.AUTO.value
    )


def finish_send(session):
    """finish send"""
    return bool(
        session.config.option.send_pms == ConfStr.FINISH.value
        and session.config.option.trigger == ConfStr.AUTO.value
    )


def pytest_addoption(parser):
    """pytest_cmdline_main"""
    parser.addoption(
        "--clean", action="store", default="no", help="是否清理环境&杀进程"
    )
    parser.addoption(
        "--log_level", action="store", default=GlobalConfig.LOG_LEVEL, help="终端日志输出级别"
    )
    parser.addoption(
        "--noskip", action="store", default="", help="skip-xxx标签不生效"
    )
    parser.addoption(
        "--ifixed", action="store", default="", help="fixed-xxx标签不生效"
    )
    parser.addoption(
        "--max_fail", action="store", default="", help="最大失败次数"
    )
    parser.addoption(
        "--record_failed_case", action="store", default="", help="失败录屏从第几次失败开始录制视频"
    )
    parser.addoption(
        "--asan", action="store", default="", help="执行安全测试用例"
    )
    parser.addoption(
        "--send_pms", action="store", default="", help="用例数据回填"
    )
    parser.addoption(
        "--task_id", action="store", default="", help="测试单id"
    )
    parser.addoption(
        "--trigger", action="store", default="", help="数据回填的触发者"
    )
    parser.addoption(
        "--suite_id", action="store", default="", help="pms的测试套件ID"
    )
    parser.addoption(
        "--pms_user", action="store", default="", help="登录pms的账号"
    )
    parser.addoption(
        "--pms_password", action="store", default="", help="登录pms的密码"
    )
    parser.addoption(
        "--top", action="store", default="", help="过程中记录top命令中的值"
    )
    parser.addoption(
        "--duringfail", action="store_true", dest="duringfail", default=False, help="出现错误时立即显示"
    )
    parser.addoption(
        '--repeat', action='store', default=1, type=int, help="用例重复执行的次数"
    )
    parser.addoption(
        '--exportcsv', action='store', default="", help="导出测试用例文件"
    )
    parser.addoption(
        '--line', action='store', default="", help="业务线(CI)"
    )
    parser.addoption(
        '--autostart', action='store', default="", help="用例执行程序注册到开机自启服务"
    )


def pytest_cmdline_main(config):
    """pytest_cmdline_main"""
    # 初始化log配置，以解决allure报告日志格式问题
    log_info = logger(config.option.log_level)
    config.option.log_level = config.option.log_level
    config.option.log_format = log_info.log_format
    config.option.log_date_format = log_info.date_format


def pytest_addhooks(pluginmanager):
    """pytest_addhooks"""
    pluginmanager.add_hookspecs(emoji_hooks)


@pytest.mark.trylast
def pytest_configure(config):
    """pytest_configure"""
    if hasattr(config, "workerinput"):
        return  # xdist worker
    # 获取终端报告器插件
    reporter = config.pluginmanager.getplugin("terminalreporter")
    if config.option.duringfail and reporter:
        custom_reporter = DuringfailingTerminalReporter(reporter)
        # 替换成我们自己的报告插件
        config.pluginmanager.unregister(custom_reporter)
        config.pluginmanager.register(custom_reporter)


def pytest_sessionstart(session):
    """pytest_sessionstart"""
    # 批量执行之前修改主题
    if (
            CmdCtl.run_cmd(
                "gsettings get com.deepin.dde.appearance gtk-theme",
                interrupt=False,
                out_debug_flag=False,
                command_log=False,
            ).strip("'")
            != GlobalConfig.SYS_THEME
    ):
        CmdCtl.run_cmd(
            f"gsettings set com.deepin.dde.appearance gtk-theme {GlobalConfig.SYS_THEME}",
            interrupt=False,
            out_debug_flag=False,
            command_log=False,
        )
    _display = GlobalConfig.DisplayServer.wayland if GlobalConfig.IS_WAYLAND else GlobalConfig.DisplayServer.x11
    logger.info(f"当前系统显示协议为 {_display.title()}.")
    # 设置任务栏方向
    popen("gsettings set com.deepin.dde.dock position bottom")
    # 记录执行开始时间
    session.config.option.start_time = datetime.now()

    user = session.config.option.pms_user
    password = session.config.option.pms_password
    task_id = session.config.option.task_id
    suite_id = session.config.option.suite_id
    if write_json(session):
        session.case_res_path = Send2Pms.case_res_path(task_id or suite_id)
        session.data_send_result_csv = Send2Pms.data_send_result_csv(task_id or suite_id)

    if user and password and async_send(session):
        session.all_thread_task = []
        session.t_executor = ThreadPoolExecutor()

    if not session.config.option.collectonly and session.config.option.top:
        def record_top():
            top_log_path = f"{GlobalConfig.REPORT_PATH}/logs"
            if not exists(top_log_path):
                makedirs(top_log_path)
            system(
                f"{GlobalConfig.top_cmd} | grep ^top -A {int(session.config.option.top) + 6} > "
                f"{top_log_path}/top_{GlobalConfig.TIME_STRING}.log"
            )

        session.p = Process(target=record_top, args=())
        session.p.start()


@pytest.hookimpl(trylast=True)
def pytest_generate_tests(metafunc):
    """pytest_generate_tests"""
    repeat = metafunc.config.option.repeat
    marks = metafunc.definition.get_closest_marker("repeat")
    if marks is not None:
        repeat = int(marks.args[0])
    if repeat > 1:
        metafunc.fixturenames.append("__pytest_repeat_step_number")

        def ids(i, number=repeat):
            return f"{i + 1}-{number}"

        metafunc.parametrize(
            '__pytest_repeat_step_number',
            range(repeat),
            indirect=True,
            ids=ids,
        )


def pytest_collection_modifyitems(session):
    """pytest_collection_modifyitems"""
    no_youqu_mark = {}
    csv_path_dict = {}
    for root, _, files in walk(GlobalConfig.APPS_PATH):
        if "NOYOUQUMARK" in files and not no_youqu_mark.get(root):
            no_youqu_mark[root] = True
            continue
        for file in files:
            if file.endswith(".csv") and file != "case_list.csv":
                csv_path_dict[splitext(file)[0]] = f"{root}/{file}"
    if not csv_path_dict:
        return

    user = session.config.option.pms_user
    password = session.config.option.pms_password
    suite_id = session.config.option.suite_id
    task_id = session.config.option.task_id
    containers = {}
    suite_runs_ids = suit_id_deque = task_runs_ids = task_id_deque = None
    skip_index = fixed_index = removed_index = pms_id_index = None

    if suite_id and task_id:
        raise ValueError("suite_id 和 task_id 不能同时存在~")
    if suite_id or task_id:
        if not (user and password):
            raise ValueError("pms_user 或 pms_password 未传入")
    if suite_id:
        suite_runs_ids, suit_id_deque = get_runs_id_deque(
            user, password, Suite, "suite", suite_id
        )
        print(
            f"{LN}测试套件: https://pms.uniontech.com/zentao/testsuite-view-{suite_id}.html"
            f"{LN}关联的用例:{LN}{f'{LN}'.join([runs_id_cmd_log(i) for i in suite_runs_ids])}"
        )
    elif task_id:
        task_runs_ids, task_id_deque = get_runs_id_deque(
            user, password, Task, "task", task_id
        )
        print(
            f"{LN}测试单: https://pms.uniontech.com/testtask-cases-{task_id}.html"
            f"{LN}关联的用例:{LN}{f'{LN}'.join([runs_id_cmd_log(i) for i in task_runs_ids])}"
        )

    for item in session.items[::-1]:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

        if no_youqu_mark:
            continue_flag = False
            for app_abspath in no_youqu_mark:
                if app_abspath in item.fspath.strpath:
                    continue_flag = True
                    break
            if continue_flag:
                continue

        try:
            csv_name, _id = findall(r"test_(.*?)_(\d+)", item.name)[0]
        except IndexError:
            skip_text = f"{item.nodeid} 用例名称缺少用例id, 跳过执行"
            logger.error(skip_text)
            add_mark(item, ConfStr.SKIP.value, (skip_text,), {})
        else:
            csv_path = csv_path_dict.get(csv_name)
            if not csv_path:
                if "asan" not in csv_name:
                    logger.error(f"{csv_name}.csv 文件不存在!")
                continue

            if not containers.get(csv_path):
                with open(csv_path, "r", encoding="utf-8") as _f:
                    txt_list = _f.readlines()
                if not txt_list:
                    continue
                # 通过csv的表头找到对应的索引（排除ID列的索引）
                for index, title in enumerate(txt_list[0].strip().split(",")):
                    if title.strip() == FixedCsvTitle.skip_reason.value:
                        skip_index = index - 1
                    elif title.strip() == FixedCsvTitle.fixed.value:
                        fixed_index = index - 1
                    elif title.strip() == FixedCsvTitle.removed.value:
                        removed_index = index - 1
                    elif title.strip() == FixedCsvTitle.pms_case_id.value:
                        pms_id_index = index - 1

                taglines = [txt.strip().split(",") for txt in txt_list[1:]]
                id_tags_dict = {f"{int(i[0]):0>3}": i[1:] for i in taglines if i[0]}
                # 每个csv文件单独管理一套index
                containers[csv_path] = id_tags_dict
                containers[csv_path][ConfStr.SKIP_INDEX.value] = skip_index
                containers[csv_path][ConfStr.FIXED_INDEX.value] = fixed_index
                containers[csv_path][ConfStr.REMOVED_INDEX.value] = removed_index
                containers[csv_path][ConfStr.PMS_ID_INDEX.value] = pms_id_index
                # 将index重置
                skip_index = fixed_index = removed_index = pms_id_index = None
            # 如果是想通过测试单跑或者测试套件跑用例，但是csv文件里面又没有保存“PMS用例ID”列，直接不跑
            if (task_id or suite_id) and containers[csv_path][
                ConfStr.PMS_ID_INDEX.value
            ] is None:
                session.items.remove(item)
                continue
            tags = containers.get(csv_path).get(_id)
            if tags:
                try:
                    if containers[csv_path][ConfStr.REMOVED_INDEX.value] is not None \
                            and tags[containers[csv_path][ConfStr.REMOVED_INDEX.value]] \
                            .strip('"').startswith(
                        f"{ConfStr.REMOVED.value}-"):
                        session.items.remove(item)
                        continue
                except IndexError as exc:
                    logger.error(
                        f"\ncsv_path:\t{csv_path}\ntags:\t{tags}\n"
                        f"error_tag_index:\t{containers[csv_path][ConfStr.REMOVED_INDEX.value]}"
                    )
                    raise IndexError from exc
                for index, tag in enumerate(tags):
                    if tag:
                        tag = tag.strip('"')
                        # 先处理“跳过原因”列
                        if index == containers[csv_path][ConfStr.SKIP_INDEX.value]:
                            # 标签是以 “skip-” 开头, noskip 用于解除所有的skip
                            if not session.config.option.noskip \
                                    and tag.startswith(f"{ConfStr.SKIP.value}-"):
                                # 标签以 “fixed-” 开头, ifixed表示ignore fixed, 用于忽略所有的fixed
                                # 1. 不给ifixed参数时，只要标记了fixed的用例，即使标记了skip-，也会执行；
                                # 2. 给ifixed 参数时(--ifixed yes)，fixed不生效，仅通过skip跳过用例；
                                try:
                                    if (
                                            not session.config.option.ifixed
                                            and containers[csv_path][ConfStr.FIXED_INDEX.value] is not None
                                            and tags[containers[csv_path][ConfStr.FIXED_INDEX.value]].strip(
                                        '"').startswith(f"{ConfStr.FIXED.value}-")
                                    ):
                                        continue
                                except IndexError:
                                    # 如果访问越界，说明这行没有fixed标签或者标签写错位置了，所以正常跳过
                                    pass
                                add_mark(item, ConfStr.SKIP.value, (tag,), {})
                            elif f"{ConfStr.SKIPIF.value}_" in tag:
                                skip_method, param = tag.split("-", maxsplit=1)
                                if hasattr(skipif, skip_method):
                                    skip_result = getattr(skipif, skip_method)(param)
                                    add_mark(
                                        item,
                                        ConfStr.SKIPIF.value,
                                        (skip_result,),
                                        {"reason": tag},
                                    )
                                else:
                                    logger.error(f"未找到判断是否跳过的自定义方法 <{skip_method}>")
                                    add_mark(
                                        item,
                                        ConfStr.SKIP.value,
                                        (f"未找到判断是否跳过的自定义方法 <{skip_method}>",),
                                        {},
                                    )
                        else:  # 非跳过列
                            # 处理 pms id
                            if containers[csv_path][ConfStr.PMS_ID_INDEX.value] == index:
                                if suite_runs_ids:
                                    if tag not in suit_id_deque:
                                        session.items.remove(item)
                                        continue
                                    add_run_case_id(session, item, tag, suite_runs_ids)
                                elif task_runs_ids:
                                    if tag not in task_id_deque:
                                        session.items.remove(item)
                                        continue
                                    add_run_case_id(session, item, tag, task_runs_ids)

                            # 处理其他自定义标签
                            try:
                                mark_title = txt_list[0].strip().split(",")[index + 1]
                            except IndexError:
                                # 如果写了标签，但是没有对应的表头
                                mark_title = ""
                            add_mark(item, tag, (mark_title,), {})
                    else:  # tag为空
                        # 处理 pmd id 为空的情况
                        if (task_id or suite_id) and containers[csv_path][ConfStr.PMS_ID_INDEX.value] == index:
                            session.items.remove(item)
                            continue
            else:
                if session.config.option.allure_report_dir:
                    # 批量执行时，不执行没有ID的用例。
                    logger.error(f"<{item.name}> csv文件中未标记,强制跳过")
                    session.items.remove(item)

    if session.config.option.autostart:
        for item in session.items[::-1]:
            _reruns = None
            if hasattr(session.config.option, "reruns"):
                _reruns = session.config.option.reruns
            if letmego.read_testcase_running_status(item, reruns=_reruns):
                session.items.remove(item)

    if (suite_id or task_id) and session.items:
        print("\n即将执行的用例:")
        for item in session.items:
            for mark in item.own_markers:
                if mark.args == (FixedCsvTitle.pms_case_id.value,):
                    print(f"case_id: {mark.name}, case_name: {item.name}")
                    break
        print()  # 处理日志换行


def pytest_collection_finish(session):
    """pytest_collection_finish"""
    session.item_count = len(session.items)
    print(f"用例收集数量:\t{session.item_count}")
    if session.config.option.reruns and not session.config.option.collectonly:
        print(f"失败重跑次数:\t{session.config.option.reruns}")
    if session.config.option.max_fail and not session.config.option.collectonly:
        session.config.option.maxfail = int(float(session.config.option.max_fail) * session.item_count)
        print(f"最大失败次数:\t{session.config.option.maxfail}")
    session.sessiontimeout = 0
    if session.config.option.timeout and not session.config.option.collectonly:
        _min, sec = divmod(int(session.config.option.timeout), 60)
        hour, _min = divmod(_min, 60)
        print(
            f"用例超时时间:\t{session.config.option.timeout}s ({hour}{'小时' if hour else ''}{_min}{'分' if _min else ''}{sec}秒)")
        # sessiontimeout
        _n = 0
        items_timeout = 0
        for item in session.items:
            for mark in item.own_markers:
                if mark.name == "timeout":
                    try:
                        item_timeout = mark.args[0]
                        _n += 1
                    except IndexError:
                        item_timeout = 0
                    items_timeout += item_timeout
                    break
        session.sessiontimeout = ((session.item_count - _n) * session.config.option.timeout) + items_timeout
        _min, sec = divmod(int(session.sessiontimeout), 60)
        hour, _min = divmod(_min, 60)
        print(
            f"会话超时时间:\t{session.sessiontimeout}s ({hour}{'小时' if hour else ''}{_min}{'分' if _min else ''}{sec}秒)"
        )

    # 生成 case_list.csv
    if session.config.option.collectonly:
        execute = []
        execute.append("用例名称," + GlobalConfig.CSV_HEARD + LN)
        for item in session.items:
            node_id = item.nodeid.split("[")[0]
            header = GlobalConfig.CSV_HEARD.split(",")
            case_info = ["" for _ in header]
            case_info.insert(0, node_id)
            for mark in item.own_markers:
                try:
                    index = header.index(mark.args[0]) + 1
                except (ValueError, IndexError):
                    continue
                case_info[index] = mark.name
            # else:
            execute.append(",".join(case_info) + LN)
        # 去重，不改变原有顺序
        execute2 = list(set(execute))
        execute2.sort(key=execute.index)
        if not exists(GlobalConfig.REPORT_PATH):
            makedirs(GlobalConfig.REPORT_PATH)
        with open(f"{GlobalConfig.REPORT_PATH}/{GlobalConfig.CSV_FILE}", "w", encoding="utf-8") as _f:
            _f.writelines(execute2)


def pytest_runtest_setup(item):
    """pytest_runtest_setup"""
    if hasattr(item, "execution_count"):
        letmego.conf.setting.EXECUTION_COUNT = item.execution_count

    print()  # 处理首行日志换行的问题
    current_item_count = (
        f"[{item.session.items.index(item) + 1}/{item.session.item_count}]"
    )
    try:
        rerun_text = (
            f" | <重跑第{item.execution_count - 1}次>" if item.execution_count > 1 else ""
        )
    except AttributeError:
        rerun_text = ""
    logger.info(
        f"{LN}{FLAG_FEEL} {item.function.__name__} || "
        f"{str(item.function.__doc__).replace(LN, '').replace('    ', '')}{rerun_text} "
        f"{FLAG_FEEL} {current_item_count}"
    )
    try:
        if item.execution_count >= (int(item.config.option.record_failed_case) + 1):
            logger.info("开启录屏")
            item.record = {}
            item.record["object"] = recording_screen(
                f"{item.name}_{item.execution_count}"
            )  # 存放录屏对象
            item.record["image_path"] = next(item.record["object"])  # 录屏文件地址
            sleep(3)  # 等待3秒，优化录屏效果
    except AttributeError:
        pass

    if item.config.option.pms_user and item.config.option.pms_password:
        def send2pms(case_res_path, data_send_result_csv):
            Send2Pms(
                user=item.config.option.pms_user, password=item.config.option.pms_password
            ).send2pms(case_res_path, data_send_result_csv)

        if async_send(item.session):
            task = item.session.t_executor.submit(
                send2pms, item.session.case_res_path, item.session.data_send_result_csv
            )
            item.session.all_thread_task.append(task)


# pylint: disable=unused-argument
def pytest_runtest_call(item):
    """pytest_runtest_call"""
    logger.info(f"{FLAG_FEEL} case body {FLAG_FEEL}")


def pytest_runtest_teardown(item):
    """pytest_runtest_teardown"""
    logger.info(f"{FLAG_FEEL} teardown {FLAG_FEEL}")
    sessiontimeout = item.session.sessiontimeout
    if sessiontimeout:
        duration = datetime.now() - item.session.config.option.start_time
        if duration.seconds > int(sessiontimeout):
            _min, sec = divmod(duration.seconds, 60)  # 处理时间秒为 XX分XX秒
            hour, _min = divmod(_min, 60)  # 处理时间分为 XX小时xx分xx秒
            raise item.session.Interrupted(f"会话超时（{hour}小时{_min}分{sec}秒）,用例强制终止!")


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """pytest_runtest_makereport"""
    out = yield
    report = out.get_result()
    if report.when == "setup":
        for mark in item.own_markers:
            if mark.name == "parametrize":
                continue
            if mark.args[0] == FixedCsvTitle.case_level.value:
                try:
                    allure.dynamic.severity(LabelType[mark.name].value)
                except KeyError:
                    allure.dynamic.severity(LabelType.L3.value)
            elif mark.args[0] == FixedCsvTitle.pms_case_id.value:
                # if mark.name:
                testcase_url = f"https://pms.uniontech.com/testcase-view-{mark.name}.html"
                allure.dynamic.testcase(testcase_url)
                logger.info(testcase_url)
            else:
                allure.dynamic.tag(mark.name)
    if report.when == "call":
        logger.info(f"运行结果: {str(report.outcome).upper()}")
        if write_json(item.session):
            # 只要是需要数据回填（无论是自动还是手动）,都需要写json结果.
            write_case_result(item, report)

        if item.config.option.autostart:
            letmego.write_testcase_running_status(item)
    try:
        if item.execution_count >= (int(item.config.option.record_failed_case) + 1):
            if report.when == "call":  # 存放录屏当次测试结果
                item.record["result"] = report.outcome
                try:
                    # 记录断言的模板图片
                    item.record["template"] = call.excinfo.value.args[0].args[1:]
                except (IndexError, KeyError, AttributeError):
                    # 记录ocr识别区域图片
                    try:
                        pic = call.excinfo.value.args[0][1]
                        if isinstance(pic, tuple):
                            item.record["ocr"] = call.excinfo.value.args[0][1]
                    except (IndexError, AttributeError, TypeError):
                        # 非ocr断言
                        pass
            elif report.when == "teardown":
                try:
                    sleep(3)
                    # 调用生成器保存视频
                    next(item.record["object"])
                except StopIteration:
                    # 录屏时测试结果为passed，则删除视频
                    if item.record.get("result") == ConfStr.PASSED.value:
                        try:
                            remove(item.record["image_path"])
                        except FileNotFoundError:
                            pass
                    else:
                        if exists(GlobalConfig.SCREEN_CACHE):
                            screen_png = f"{splitext(item.record['image_path'])[0]}.png"
                            copyfile(GlobalConfig.SCREEN_CACHE, screen_png)
                            allure.attach.file(
                                screen_png,
                                name="屏幕截图",
                                attachment_type=allure.attachment_type.PNG,
                            )
                            try:
                                for index, tem in enumerate(item.record["template"]):
                                    template = f"{splitext(item.record['image_path'])[0]}_template_{index}.png"
                                    CmdCtl.run_cmd(f"cp {tem} {template}")
                                    allure.attach.file(
                                        template,
                                        name="模板图片",
                                        attachment_type=allure.attachment_type.PNG,
                                    )
                            except KeyError:
                                # 非图像识别错误
                                pass
                            try:
                                template = f"{splitext(item.record['image_path'])[0]}_ocr_.png"
                                CmdCtl.run_cmd(f"cp {item.record['ocr']} {template}")
                                allure.attach.file(
                                    template,
                                    name="OCR识别区域",
                                    attachment_type=allure.attachment_type.PNG,
                                )
                            except KeyError:
                                # ocr 识别区域
                                pass
                        allure.attach.file(
                            item.record["image_path"],
                            name="用例视频",
                            attachment_type=allure.attachment_type.MP4,
                        )
                    logger.info(
                        "结束录屏! "
                        f"{'重跑用例测试成功，删除视频录像' if item.record.get('result') == ConfStr.PASSED.value else ''}"
                    )
    except (AttributeError, KeyError):
        pass


def pytest_report_teststatus(report, config):
    """pytest_report_teststatus"""
    # 在 setup 和 teardown 阶段处理 error 和 skip
    if report.when in ("setup", "teardown"):
        if report.failed:
            short, verbose = config.hook.pytest_emoji_error(
                config=config,
                head_line=report.head_line
            )
            return "error", short, verbose
        if report.skipped:
            short, verbose = config.hook.pytest_emoji_skipped(
                config=config,
                head_line=report.head_line
            )
            return "skipped", short, verbose
    # 在用例执行阶段处理 passed skipped failed
    if report.when == "call":
        short = verbose = ""
        if report.passed:
            short, verbose = config.hook.pytest_emoji_passed(
                config=config,
                head_line=report.head_line
            )
        elif report.skipped:
            short, verbose = config.hook.pytest_emoji_skipped(
                config=config,
                head_line=report.head_line
            )
        elif report.failed:
            short, verbose = config.hook.pytest_emoji_failed(
                config=config,
                head_line=report.head_line
            )
        return report.outcome, short, verbose
    return None


def pytest_sessionfinish(session):
    """pytest_sessionfinish"""
    if session.config.option.allure_report_dir:
        AllureReportExtend.environment_info(session)
        terminalreporter = session.config.pluginmanager.get_plugin("terminalreporter")
        execute = {}
        for _, items in terminalreporter.stats.items():
            for item in items:
                default_result = {"result": "blocked", "longrepr": "None"}
                try:
                    if item.outcome == ConfStr.PASSED.value:
                        default_result["result"] = "pass"
                    elif item.outcome == ConfStr.SKIPPED.value:
                        default_result["result"] = "skip"
                    elif item.outcome == ConfStr.RERUN.value:
                        continue
                    else:
                        default_result["result"] = "fail"
                    item_name = item.nodeid.split("[")[0]
                    if not execute.get(item_name) or (
                            item.outcome != ConfStr.PASSED.value
                            and execute.get(item_name).get("result") == "pass"
                    ):
                        execute[item_name] = default_result
                except AttributeError:
                    pass
        if execute:
            with open(
                    f"{GlobalConfig.ROOT_DIR}/ci_result.json", "w", encoding="utf-8"
            ) as _f:
                _f.write(dumps(execute, indent=2, ensure_ascii=False))

    if session.config.option.pms_user and session.config.option.pms_password:
        def send2pms(case_res_path, data_send_result_csv):
            Send2Pms(
                user=session.config.option.pms_user,
                password=session.config.option.pms_password,
            ).send2pms(case_res_path, data_send_result_csv)

        if async_send(session):
            wait(session.all_thread_task, return_when=ALL_COMPLETED)
            send2pms(session.case_res_path, session.data_send_result_csv)
            session.t_executor.shutdown()

        if finish_send(session):
            send2pms(session.case_res_path, session.data_send_result_csv)

    if not session.config.option.collectonly and session.config.option.top:
        session.p.terminate()
        system(
            f"ps -aux | grep '{GlobalConfig.top_cmd}' | "
            "cut -c 9-15 | xargs kill -9 > /dev/null 2>&1"
        )
        session.p.close()

    if exists(GlobalConfig.TMPDIR):
        # 清理临时模板图片
        CmdCtl.run_cmd(
            f"echo '{GlobalConfig.PASSWORD}' | sudo -S rm -rf {GlobalConfig.TMPDIR}",
            interrupt=False,
            out_debug_flag=False,
            command_log=False
        )


# pylint: disable=unused-argument
def pytest_emoji_passed(config, head_line):
    """pytest_emoji_passed"""
    # 笑脸
    return (
        f"【 {datetime.now()} {head_line} || 😃 】\n",
        f"【 {datetime.now()} {head_line} || PASSED 😃 】\n"
    )


# pylint: disable=unused-argument
def pytest_emoji_failed(config, head_line):
    """pytest_emoji_failed"""
    # 哭笑不得
    return (
        f"【 {datetime.now()} {head_line} || 😰 】\n",
        f"【 {datetime.now()} {head_line} || FAILED 😰 】\n"
    )


# pylint: disable=unused-argument
def pytest_emoji_skipped(config, head_line):
    """pytest_emoji_skipped"""
    # 翻白眼儿
    return (
        f"【 {datetime.now()} {head_line} || 🙄 】\n",
        f"【 {datetime.now()} {head_line} || SKIPPED 🙄 】\n"
    )


# pylint: disable=unused-argument
def pytest_emoji_error(config, head_line):
    """pytest_emoji_error"""
    # 哭哭
    return (
        f"【 {datetime.now()} {head_line} || 😡 】\n",
        f"【 {datetime.now()} {head_line} || ERROR 😡 】\n"
    )


class DuringfailingTerminalReporter(TerminalReporter):
    """测试过程中立即显示报错"""

    def __init__(self, reporter):
        TerminalReporter.__init__(self, reporter)
        self._tw = reporter._tw

    def pytest_collectreport(self, report):
        """pytest_collectreport"""
        # 立即显示收集过程中发生的错误。
        TerminalReporter.pytest_collectreport(self, report)
        if report.failed:
            if self.isatty:
                self.rewrite("")
            self.print_failure(report)

    def pytest_runtest_logreport(self, report):
        """pytest_runtest_logreport"""
        # 立刻显示运行测试期间发生的故障和错误
        TerminalReporter.pytest_runtest_logreport(self, report)
        if report.failed and not hasattr(report, "wasxfail"):
            if self.verbosity <= 0:
                self._tw.line()
            self.print_failure(report)

    def summary_failures(self):
        """summary_failures"""
        # 防止显示错误摘要，因为我们已经错误发生后立即显示错误。

    def summary_errors(self):
        """summary_errors"""

    def print_failure(self, report):
        """print_failure"""
        if self.config.option.tbstyle != "no":
            if self.config.option.tbstyle == "line":
                line = self._getcrashline(report)
                self.write_line(line)
            else:
                msg = self._getfailureheadline(report)
                if report.when == "collect":
                    msg = "ERROR collecting " + msg
                elif report.when == "setup":
                    msg = "ERROR at setup of " + msg
                elif report.when == "teardown":
                    msg = "ERROR at teardown of " + msg
                self.write_sep("_", msg)
                if not self.config.getvalue("usepdb"):
                    self._outrep_summary(report)


def get_runs_id_deque(user, password, class_obj, func, _id):
    """get_runs_id_deque"""
    if not (user and password):
        raise ValueError("缺少PMS用户名或密码")
    runs_ids = getattr(class_obj(user, password), f"get_{func}_data")(_id)
    if not runs_ids:
        raise ValueError
    id_deque = deque()
    for i in runs_ids:
        id_deque.append(i.get("case_id"))
        id_deque.append(i.get("from_case_id"))
    return runs_ids, id_deque


def add_run_case_id(session, item, tag, runs_ids):
    """add_run_case_id"""
    if auto_send(session):
        # 需要回填数据的时候才做
        for i in runs_ids:
            _case_id = i.get("case_id")
            _from_case_id = i.get("from_case_id")
            _run_case_id = i.get("run_case_id")
            if tag in (_case_id, _from_case_id):
                add_mark(item, _run_case_id, ("run_case_id",), {})
                add_mark(item, _from_case_id, ("from_case_id",), {})
                break


@pytest.fixture
def __pytest_repeat_step_number(request):
    """__pytest_repeat_step_number"""
    marker = request.node.get_closest_marker("repeat")
    repeat = marker and marker.args[0] or request.config.option.repeat
    if repeat > 1:
        return request.param
    return None
