import json
import base64

def parse_config(file_path):
    configs = []
    with open(file_path, 'r') as f:
        lines = f.readlines()
        entry = {}
        for line in lines:
            line = line.strip()
            if line:
                if line.startswith('- {'):
                    info = json.loads(line[2:])
                    entry = {key: value for key, value in info.items()}
                    configs.append(entry)
                elif line.startswith('- name:'):
                    entry = {'name': line.split(': ')[1]}
                    configs.append(entry)
                else:
                    key, value = line.split(': ')
                    entry[key.strip()] = value.strip()
    return configs


def generate_ss_link(info):
    string = f"{info['cipher']}:{info['password']}@{info['server']}:{info['port']}"
    encoded_string = base64.b64encode(string.encode()).decode()
    return f"ss://{encoded_string}#{info['name']}"


def generate_trojan_link(config):
    trojan_link = f"trojan://{config['password']}@{config['server']}:{config['port']}?sni={config['sni']}#{config['name']}"
    return trojan_link


def base64_encode(string):
    encoded_bytes = base64.b64encode(string.encode('utf-8'))
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string




def main(path):
    configs = parse_config(path)
    res = ''
    for config in configs:
        if config['type'] == 'ss':
            ss = generate_ss_link(config)
            res += ss + '\n'
        if config["type"] == 'trojan':
            tj = generate_trojan_link(config)
            res += tj + '\n'
    print(base64_encode(res))

if __name__ == "__main__":
    path = "link.txt" 
    main(path)