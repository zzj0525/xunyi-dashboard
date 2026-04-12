import requests
import csv
from datetime import datetime
from zoneinfo import ZoneInfo
import time
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOKEN_FULL = os.environ.get("XUNYI_TOKEN")

if not TOKEN_FULL:
    raise Exception("请在环境变量中设置 XUNYI_TOKEN (GitHub Secrets 中配置)")

members = {
    198331: "王橹杰",
    198334: "张函瑞",
    198330: "张桂源",
    198332: "杨博文",
    198335: "陈奕恒",
    198333: "左奇函",
    198336: "陈浚铭",
}

HEADERS = {
    "Host": "api.xunyee.cn",
    "token": TOKEN_FULL.replace("Bearer ", ""),
    "content-type": "application/x-www-form-urlencoded",
    "Authorization": TOKEN_FULL,
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.70(0x18004634) NetType/WIFI Language/zh_CN",
    "Referer": "https://servicewechat.com/wx6959ba05bf03effa/112/page-frame.html"
}

CSV_FILE = "xunyi_likes_summary.csv"


def now_cn():
    return datetime.now(ZoneInfo("Asia/Shanghai"))


def fetch_person_info(person_id):
    url = f"https://api.xunyee.cn/xunyee/vcuser_person/person_info?person={person_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                return data.get("data", {}).get("check", 0)
        return None
    except Exception as e:
        print(f"person_info 请求失败 {person_id}: {e}")
        return None


def fetch_fans_check(person_id):
    url = f"https://api.xunyee.cn/xunyee/vcuser_person/fans_check?person={person_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("code") == 0:
                fans_data = data.get("data", {})
                return {
                    "fans_count": fans_data.get("fans_count", 0),
                    "check1": fans_data.get("check1", 0),
                    "check2": fans_data.get("check2", 0),
                    "check3": fans_data.get("check3", 0)
                }
        return None
    except Exception as e:
        print(f"fans_check 请求失败 {person_id}: {e}")
        return None


def save_to_csv(records):
    file_exists = False
    try:
        with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
            file_exists = True
    except FileNotFoundError:
        pass

    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["时间", "练习生", "总点赞量", "粉丝数", "点赞1次人数", "点赞2次人数", "点赞3次人数"])
        for row in records:
            writer.writerow(row)


def main():
    collect_time = now_cn().strftime("%Y-%m-%d %H:%M:%S")
    print(f"开始采集 {collect_time}")

    results = []
    for pid, name in members.items():
        print(f"正在获取 {name} (ID: {pid})...")
        total_likes = fetch_person_info(pid)
        fans_data = fetch_fans_check(pid)

        if total_likes is not None and fans_data is not None:
            print(
                f"  ✅ {name}: 总点赞={total_likes}, 粉丝数={fans_data['fans_count']}, 1次={fans_data['check1']}, 2次={fans_data['check2']}, 3次={fans_data['check3']}"
            )
            results.append((
                collect_time,
                name,
                total_likes,
                fans_data["fans_count"],
                fans_data["check1"],
                fans_data["check2"],
                fans_data["check3"]
            ))
        else:
            print("  ❌ 失败")
        time.sleep(1)

    if results:
        save_to_csv(results)
        print(f"✅ 数据已保存到 {CSV_FILE}")
    else:
        print("⚠️ 没有成功获取任何数据")


if __name__ == "__main__":
    main()
