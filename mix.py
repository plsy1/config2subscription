import requests
import base64
import random
import string
import json
from urllib.parse import unquote, quote


def add_padding(base64_string):
    """添加适当的 '=' 使得长度是 4 的倍数"""
    return base64_string + "=" * (-len(base64_string) % 4)


def generate_random_string(length=16):
    """生成一个指定长度的随机字符串"""
    letters_and_digits = string.ascii_letters + string.digits
    return "".join(random.choice(letters_and_digits) for _ in range(length))


def decode_vmess(vmess_string):
    """解码 vmess 配置，修改 ps 字段"""
    # 去掉 vmess:// 前缀
    if vmess_string.startswith("vmess://"):
        vmess_base64_string = vmess_string[len("vmess://") :]
    else:
        return None

    # 对 vmess 字符串进行 Base64 解码
    base64_content = base64.b64decode(vmess_base64_string).decode("utf-8")

    # URL 解码（如果需要）
    url_decoded_content = unquote(base64_content)

    # 解析 JSON
    try:
        vmess_data = json.loads(url_decoded_content)
        return vmess_data
    except json.JSONDecodeError as e:
        print(f"JSON 解码失败: {e}")
        return None


def encode_vmess(vmess_data):
    """对 vmess 数据进行 Base64 编码"""
    # 转换为 JSON 字符串
    json_string = json.dumps(vmess_data, separators=(",", ":"))
    # Base64 编码
    base64_content = base64.b64encode(json_string.encode("utf-8")).decode("utf-8")
    return base64_content


def fetch_and_decode_urls(urls, output_file, exclude_keywords=None):
    """获取 URL 内容，解码后过滤并保存到文件"""
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "DNT": "1",
        "Pragma": "no-cache",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "sec-gpc": "1",
    }

    exclude_keywords = exclude_keywords or []  # 默认不排除任何关键词

    with open(output_file, "w") as f:
        for index, url in enumerate(urls):
            try:
                # 获取URL内容
                print(f"处理第 {index + 1} 个 URL: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                # 修复 Base64 字符串的填充
                base64_content = add_padding(response.text)

                # Base64 解码
                decoded_content = base64.b64decode(base64_content).decode("utf-8")
                # URL 解码
                decoded_content = unquote(decoded_content)
                # 将解码后的内容按行处理
                lines = decoded_content.splitlines()
                for line in lines:
                    # 处理 vmess 配置
                    if line.startswith("vmess://"):
                        vmess_data = decode_vmess(line)
                        if vmess_data:
                            if "ps" in vmess_data and any(
                                keyword in vmess_data["ps"]
                                for keyword in exclude_keywords
                            ):
                                continue
                            if "ps" in vmess_data:
                                #random_suffix = generate_random_string()
                                vmess_data["ps"] += f"_00{index+1}"
                            encoded_vmess = encode_vmess(vmess_data)
                            f.write(f"vmess://{encoded_vmess}\n")

                    else:
                        # 处理其他内容
                        if any(keyword in line for keyword in exclude_keywords):
                            continue
                        random_suffix = generate_random_string()
                        f.write(f"{line}_00{index+1}\n")

            except requests.exceptions.RequestException as e:
                print(f"无法获取 {url} 的内容: {e}")
            except base64.binascii.Error as e:
                print(f"无法解码 {url} 的内容: {e}")


def encode_output_to_base64(input_file, output_file):
    """将文件内容编码为 Base64 并保存到另一个文件"""
    with open(input_file, "r") as f:
        content = f.read()

    # 对内容进行 Base64 编码
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    # 将编码后的内容写入到输出文件
    with open(output_file, "w") as f:
        f.write(encoded_content)

    print(f"{input_file} 的内容已编码并保存到 {output_file}")


def read_urls_from_file(file_path):
    """从文件中读取 URL 列表，每行一个链接"""
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


# 从 url.txt 读取链接
urls = read_urls_from_file("url.txt")

# 指定排除的关键词
exclude_keywords = [
    "提交工单",
    "Traffic",
    "网站",
    "Expire",
    "续费",
    "网址",
    "重置",
    "售后",
    "更新",
    "剩余",
    "到期",
    "月节点",
]

# 获取并解码 URL 内容，保存到最终文件
fetch_and_decode_urls(urls, "sub.txt", exclude_keywords)

# 将结果文件进行 Base64 编码
encode_output_to_base64("sub.txt", "sub_base64.txt")
