import requests
def get_stream(link):
    url="https://api.vidssave.com/api/contentsite_api/media/parse"
    headers = {
        "origin": "https://vidssave.com",
        "referer": "https://vidssave.com/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36"
    }
    data={
        "auth": "20250901majwlqo",
        "domain": "api-ak.vidssave.com",
        "origin": "source",
        "referer": "https://vidssave.com/",
        "link": f"{link}"
    }

    response = requests.post(url, headers=headers,data=data,timeout=5)
    download_link=None
    size=None
    a=response.json()["data"]
    for items in a["resources"]:
        if items["quality"]=="48KBPS":
            download_link=items["download_url"]
            size=items["size"]
            break
    if download_link and size:
        return{
            "stream": download_link,
            "size": size
        }
    else:
        return None
