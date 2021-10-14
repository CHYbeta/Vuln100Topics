import datetime
import json
import os

import dateutil.parser
import requests


def query_20topics(zsxq_access_token):
    topic_datas = []
    top20_url = "https://api.zsxq.com/v2/groups/555848225184/topics"
    params = {
        "scope": "all",
        "count": "20"
    }
    cookies = {
        "abtest_env": "product",
        "zsxq_access_token": zsxq_access_token
    }

    headers = {
        "Sec-Ch-Ua": "\"Chromium\";v=\"94\", \"Google Chrome\";v=\"94\", \";Not A Brand\";v=\"99\"",
        "X-Version": "2.9.0",
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Sec-Ch-Ua-Platform": "\"macOS\"",
        "Origin": "https://wx.zsxq.com",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://wx.zsxq.com/",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }

    resp = requests.get(top20_url, headers=headers, params=params, cookies=cookies)
    resp_json = json.loads(resp.text)
    topics = resp_json["resp_data"]["topics"]

    for topic in topics:
        topic_id = topic["topic_id"]
        topic_url = "https://wx.zsxq.com/dweb2/index/topic_detail/{topic_id}".format(topic_id=topic_id)
        topic_type = topic["type"]
        create_time = dateutil.parser.parse(topic["create_time"])

        if topic_type == "talk":
            topic_auther = topic["talk"]["owner"]["name"]
            topic_talk = topic["talk"]
            topic_first_filename = topic_talk.get("files")[0]["name"].strip() if topic_talk.get("files") else "无"
            topic_origin_text = topic_talk.get("text")[:100].strip() if topic_talk.get("text") else "无"
            topic_text = topic_origin_text[
                         : topic_origin_text.index("\n")] if "\n" in topic_origin_text else topic_origin_text
            topic_article_title = topic_talk.get("article").get("title").strip() if topic_talk.get("article") else "无"

            topic_data = {
                "topic_id": topic_id,
                "topic_url": topic_url,
                "topic_type": topic_type,
                "topic_auther": topic_auther,
                "topic_text": topic_text,
                "topic_article_title": topic_article_title,
                "topic_first_filename": topic_first_filename,
                "create_time": create_time
            }
            topic_datas.append(topic_data)
        elif topic_type == "q&a":
            topic_question = topic["question"]
            topic_auther = topic_question["owner"]["name"]
            topic_text = topic_question["text"][:100].strip() if topic_question.get("text") else ""

            topic_data = {
                "topic_id": topic_id,
                "topic_url": topic_url,
                "topic_type": topic_type,
                "topic_auther": topic_auther,
                "topic_text": topic_text,
                "topic_article_title": "无",
                "topic_first_filename": "无",
                "create_time": create_time
            }

            topic_datas.append(topic_data)
    return topic_datas


def generate_readme(topic_datas):
    markdown_prefix = "# [漏洞百出](https://public.zsxq.com/groups/555848225184.html) Topics 20\n\n"
    markdown_prefix += "星球最新20条Topic - 更新于 {time}\n\n".format(
        time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    markdown_content_header = "|作者|内容|发表时间|\n|:---:|:---|:---|\n"
    markdown_content_topic = ""
    for topic_data in topic_datas:
        markdown_content_topic += "|" + topic_data["topic_auther"] + "|"
        markdown_content_topic += "星球链接: [{topic_id}]({topic_url})".format(topic_id=topic_data["topic_id"],
                                                                           topic_url=topic_data[
                                                                               "topic_url"]) + " <br />"
        markdown_content_topic += "简要内容: " + topic_data["topic_text"] + "<br />"
        markdown_content_topic += "文章标题: " + topic_data["topic_article_title"] + "<br />"
        markdown_content_topic += "首个文件: " + topic_data["topic_first_filename"] + "|"
        markdown_content_topic += topic_data["create_time"].strftime("%Y-%m-%d %H:%M:%S") + "|\n"

    markdwon_all = markdown_prefix + markdown_content_header + markdown_content_topic
    f = open("README.md", "w")
    f.write(markdwon_all)
    f.close()


if __name__ == "__main__":
    zsxq_access_token = os.environ.get("ZSXQ_TOKEN")
    generate_readme(query_20topics(zsxq_access_token))
