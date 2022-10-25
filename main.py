import re
from enum import Enum

import requests


class EType(Enum):
    Heading = 0,
    Cookies = 1
    Forms = 2,
    Parameters = 3,
    Files = 4


cookie = "7ce1376eb6e54b7f98609537f41d209c"
ip = "http://178.154.226.49"

def main():
    req = requests.get(ip, cookies={"user": cookie})
    while True:
        print(req.text[req.text.find("Шаг") + 3:req.text.find("(из")])
        if "href" in req.text:
            address = req.text[req.text.find("href") + 6: req.text.find("ссылке") - 2]
        else:
            address = req.text[req.text.find("<code>") + 6:req.text.find("</code>")]
        contents = parse_content(req.text)
        if "POST" in req.text or "файлы" in req.text:
            req = requests.post(ip + address,
                                cookies=contents[EType.Cookies],
                                headers=contents[EType.Heading],
                                params=contents[EType.Parameters],
                                data=contents[EType.Forms],
                                files=contents[EType.Files])
        elif "GET" in req.text or "Перейдите" in req.text:
            req = requests.get(ip + address,
                               cookies=contents[EType.Cookies],
                               headers=contents[EType.Heading],
                               params=contents[EType.Parameters],
                               data=contents[EType.Forms])
        if "Поздравляем" in req.text:
            print(req.text)
            break


def parse_content(response: str) -> dict:
    contents = {EType.Heading: {}, EType.Cookies: {}, EType.Forms: {}, EType.Parameters: {}, EType.Files: {}}
    headings = parse_table('заголовки', response)
    cookies = parse_table('cookie', response)
    cookies['user'] = f'{cookie}'
    forms = parse_table('формы', response)
    parameters = parse_table('параметры запроса', response)
    files = parse_table('файлы', response)

    if headings:
        contents[EType.Heading] = headings
    if cookies:
        contents[EType.Cookies] = cookies
    if forms:
        contents[EType.Forms] = forms
    if parameters:
        contents[EType.Parameters] = parameters
    if files:
        contents[EType.Files] = files
    return contents


def parse_table(ident: str, response: str) -> dict:
    table_start = response.find(ident)
    if table_start == -1:
        return {}
    table_end = response.find('</table>', table_start)
    table_raw = response[table_start: table_end]
    raw_headings = re.findall(r'<code>\w+.*</code>', table_raw)
    table = {}
    for i in range(0, len(raw_headings) - 1, 2):
        table[raw_headings[i][6: -7]] = raw_headings[i + 1][6: -7]
    return table


if __name__ == "__main__":
    main()
