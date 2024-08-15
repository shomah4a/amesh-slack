import datetime
import io

from PIL import Image
import pytz
import requests


JST = pytz.timezone('Asia/Tokyo')


BACKGROUND_URL = 'https://tokyo-ame.jwa.or.jp/map/map050.jpg'
AREA_MASK_URL = 'https://tokyo-ame.jwa.or.jp/map/msk050.png'


def truncate_5min(now: datetime.datetime) -> str:
    now = now - datetime.timedelta(minutes=1)
    minute = (now.minute // 5) * 5

    return now.replace(minute=minute, second=0, microsecond=0)


def resolve_now_url(now: datetime.datetime) -> str:

    truncated = truncate_5min(now).astimezone(JST)

    fmt = truncated.strftime('%Y%m%d%H%M')

    return f'https://tokyo-ame.jwa.or.jp/mesh/050/{fmt}.gif'



def fetch_image(url: str) -> Image:

    res = requests.get(url)
    return Image.open(io.BytesIO(res.content))


def handle_gif_transparency(image: Image) -> Image:
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    data = image.getdata()

    newData = []
    for item in data:
        if item[3] == 0:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    image.putdata(newData)
    return image


def generate_amesh_image(now: datetime.datetime) -> Image:

    background = fetch_image(BACKGROUND_URL)
    now_url = resolve_now_url(now)
    amesh = handle_gif_transparency(fetch_image(now_url))
    area_mask = fetch_image(AREA_MASK_URL).convert('RGBA')

    background.paste(amesh, (0, 0), amesh)
    background.paste(area_mask, (0, 0), area_mask)

    return background


def main():
    now = datetime.datetime.now()

    img = generate_amesh_image(now)

    w, h = img.size
    resized_img = img.resize((w // 2, h // 2), Image.LANCZOS)

    resized_img.save('amesh.jpg', optimize=True)


if __name__ == '__main__':
    main()
