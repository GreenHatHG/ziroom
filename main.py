import datetime
import json
import os
import random
import sys
import time
from pathlib import Path

from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm

from ocr import get_price

project_path = os.path.join(os.path.dirname(__file__))
screenshot_path = os.path.join(project_path, 'screenshot')


def compress_image(input_path, output_path, quality=100):
    """
    压缩图片并保存到指定路径，输出压缩前和压缩后文件大小的信息

    :param input_path: 输入图片的路径
    :param output_path: 压缩后图片的保存路径
    :param quality: 压缩质量，取值范围为0-100，默认为100（无损压缩）
    """
    # 打开图片
    img = Image.open(input_path)

    # 获取原始图片大小
    orig_size = os.path.getsize(input_path) / 1024  # 转换为KB

    # 保存图片时使用无损压缩
    img.save(output_path, optimize=True, quality=quality)

    # 获取压缩后图片的大小
    new_size = os.path.getsize(output_path) / 1024  # 转换为KB

    # 输出压缩前和压缩后文件大小的信息
    print(f"压缩{input_path}: {orig_size:.2f} KB --> {new_size:.2f} KB")


def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.binary_location = '/usr/bin/google-chrome-stable'
    return chrome_options


def web_screenshot(url, save_path=None):
    browser = webdriver.Chrome(options=get_chrome_options())
    width = 1920
    height = 1080
    browser.set_window_size(width, height)

    # 打开网页
    browser.get(url)

    # 等待页面加载完成
    browser.implicitly_wait(10)

    # 截图并保存到本地
    if not save_path:
        png_file = os.path.join(screenshot_path, f"{url.split('/')[-1].replace('.html', '')}.png")
    else:
        png_file = os.path.join(save_path, f"{url.split('/')[-1].replace('.html', '')}.png")

    print(f"screenshot: {png_file}")

    browser.save_screenshot(png_file)

    # 关闭浏览器实例
    browser.quit()


def get_house_info(url):
    driver = webdriver.Chrome(options=get_chrome_options())
    driver.get(url)

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'item')))

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    if '未搜到对应房源，换个搜索条件试试' in soup.text:
        return None

    # 获取房源列表
    house_list = soup.find_all('div', class_='item')
    result = []
    for house in house_list:
        title_elem = house.find('h5', class_='title')
        if title_elem:
            title = title_elem.text.strip()
        else:
            continue

        size_floor, _ = house.find('div', {'class': 'desc'}).find_all('div')
        size = size_floor.text.split('㎡')[0].strip()
        floor = size_floor.text.split('|')[1].strip()
        location = house.find('div', {'class': 'location'}).text.strip()
        link = house.find('a', {'class': 'pic-wrap'})['href']
        link = f"https:{link}"

        print(f'标题： {title}')
        print(f'楼层： {floor}')
        print(f'大小： {size}㎡')
        print(f'位置： {location}')
        print(f'链接： {link}\n')
        result.append({'title': title, 'floor': floor, 'size': size, 'location': location, 'link': link})

    driver.quit()
    return result


def two_bedroom_filter(result):
    new_result = []
    for item in result:
        if str(item['floor']).startswith('1/'):
            continue
        if float(8) > float(item['size']):
            continue
        if '2居室' not in item['title']:
            continue
        # if '北卧' in item['title']:
        #     continue
        new_result.append(item)
    return new_result


def three_bedroom_filter(result):
    new_result = []
    for item in result:
        if str(item['floor']).startswith('1/'):
            continue
        if float(8) > float(item['size']):
            continue
        if '3居室' not in item['title']:
            continue
        if '北卧' in item['title']:
            continue
        new_result.append(item)
    return new_result


def get_haidian_url(page):
    haidian = {"安宁庄": "611100466",
               "北安河": "611100398",
               "白石桥": "18335761",
               "北太平庄": "18335632",
               "慈寿寺": "200000000025",
               "厂洼": "18335760",
               "定慧寺": "18335634",
               "大钟寺中坤广场": "200000000034",
               "二里庄": "18335757",
               "方恒时尚中心": "200000000033",
               "甘家口": "611100353",
               "公主坟": "18335624",
               "环保科技园": "613001105",
               "海淀北部新区": "611100537",
               "海淀玉泉路": "18335691",
               "花园桥": "200000000024",
               "军博": "18335640",
               "马甸(海淀区)": "611100601",
               "牡丹园": "18335768",
               "马连洼": "611100356",
               "清河": "18335631",
               "上地": "18335633",
               "世纪城": "18335628",
               "四季青": "611100358",
               "双榆树": "611100355",
               "苏州桥": "18335766",
               "田村": "611100357",
               "五道口": "18335636",
               "魏公村": "18335758",
               "五棵松": "18335630",
               "万柳": "18335629",
               "五路居": "200000000031",
               "万寿路": "611100529",
               "西北旺": "611100535",
               "西二旗": "611100314",
               "新街口": "18335653",
               "西山": "18335762",
               "西三旗": "18335746",
               "小西天": "18335754",
               "学院路": "18335627",
               "西直门": "18335654",
               "颐和园": "611100699",
               "圆明园": "611100354",
               "杨庄": "18335695",
               "知春路": "18335639",
               "中关村": "18335623",
               "中航广场": "200000000032",
               "皂君庙": "18335767",
               "紫竹桥": "18335625"}
    location_list = ['安宁庄', '白石桥', '北太平庄', '慈寿寺', '厂洼', '定慧寺', '大钟寺中坤广场', '二里庄',
                     '方恒时尚中心', '甘家口', '公主坟', '海淀玉泉路', '花园桥', '军博', '马甸(海淀区)', '牡丹园',
                     '马连洼', '清河', '上地', '世纪城', '四季青', '双榆树', '苏州桥', '田村', '五道口', '魏公村',
                     '五棵松', '万柳', '五路居', '万寿路', '西北旺', '西二旗', '新街口', '西山', '西三旗', '小西天',
                     '学院路', '西直门', '颐和园', '圆明园', '知春路', '中关村', '中航广场', '皂君庙', '紫竹桥']
    location_url = ''
    for location in location_list:
        location_url += haidian[location]
        location_url += '%7C'
    location_url = location_url[:-3]
    url = f'https://www.ziroom.com/z/d23008618-b{location_url}-r0-p{page}/?cp=0TO2700'
    return url


def get_xichen_url(page):
    xichen = {"安德里北街": "200000000014",
              "安华桥": "200000000015",
              "白纸坊": "18335671",
              "车公庄": "18335657",
              "车公庄地铁站": "200000000012",
              "长椿街": "18335672",
              "地安门": "611100336",
              "达官营": "4403002028",
              "德胜门": "18335652",
              "阜成门": "18335656",
              "广安门": "18335669",
              "官园": "18335658",
              "金融街": "611100342",
              "积水潭": "200000000021",
              "六铺炕": "611100339",
              "马甸(海淀区)": "611100601",
              "马甸(西城区)": "611100603",
              "马连道": "18335670",
              "木樨地": "611100359",
              "牛街": "18335674",
              "前门": "18335673",
              "天宁寺": "611100597",
              "陶然亭": "611100334",
              "湾子": "200000000030",
              "西单": "18335661",
              "新街口": "18335653",
              "西四": "611100340",
              "宣武门": "18335675",
              "西直门": "18335654",
              "右安门内": "611100432",
              "右安门外": "611100431",
              "月坛": "18335655"}
    location_list = ['安德里北街', '安华桥', '车公庄', '车公庄地铁站', '长椿街', '地安门', '达官营', '德胜门', '阜成门',
                     '广安门', '官园', '金融街', '积水潭', '六铺炕', '马甸(海淀区)', '马甸(西城区)', '西单', '新街口',
                     '西四', '宣武门', '西直门', '右安门内', '右安门外', '月坛']
    location_url = ''
    for location in location_list:
        location_url += xichen[location]
        location_url += '%7C'
    location_url = location_url[:-3]
    url = f'https://www.ziroom.com/z/d23008626-b{location_url}-r0-p{page}/?cp=0TO2700'
    return url


def get_chaoyang_url(page):
    chaoyang = {"CBD": "18335735",
                "朝青": "18335729",
                "成寿寺": "611100332",
                "常营": "611100328",
                "朝阳公园": "18335739",
                "朝阳郊区": "613000370",
                "朝阳门": "18335622",
                "朝阳门外": "611100448",
                "慈云寺": "100000000006",
                "安定门": "18335647",
                "奥林匹克公园": "611100323",
                "安贞": "18335704",
                "北工大": "611100330",
                "北京朝阳站": "200000000016",
                "北苑": "611100412",
                "百子湾": "18335715",
                "东坝": "18335780",
                "东大桥": "611100326",
                "定福庄": "18335724",
                "豆各庄": "18335713",
                "东湖渠": "200000000027",
                "东四十条": "100000000009",
                "大山子": "611100320",
                "大望路": "611100329",
                "东直门": "18335644",
                "垡头": "611100322",
                "方庄": "18335676",
                "高碑店": "611100325",
                "甘露园": "18335726",
                "国贸": "18335736",
                "广渠门": "18335666",
                "工体": "18335779",
                "管庄": "18335723",
                "国展": "18335734",
                "华彩国际": "200000000028",
                "呼家楼": "18335742",
                "欢乐谷": "611100333",
                "红领巾公园": "100000000005",
                "红庙": "18335743",
                "和平里": "18335641",
                "华威桥": "18335718",
                "惠新西街": "611100324",
                "建国门外": "611100446",
                "劲松": "18335737",
                "金台路": "100000000004",
                "酒仙桥": "18335710",
                "健翔桥": "611100481",
                "来广营": "18335721",
                "亮马桥": "1100006187",
                "利泽西园": "200000000029",
                "马甸(朝阳区)": "611100602",
                "马甸(海淀区)": "611100601",
                "牡丹园": "18335768",
                "南沙滩": "611100318",
                "农展馆": "611100327",
                "潘家园": "611100368",
                "十八里店": "18335716",
                "首都机场": "18335738",
                "石佛营": "18335728",
                "四惠": "18335727",
                "孙河": "200000000023",
                "双井": "611100316",
                "十里堡": "18335741",
                "十里河": "18335717",
                "三里屯": "611100698",
                "双桥": "18335714",
                "芍药居": "18335707",
                "三元桥": "18335709",
                "团结湖": "18335730",
                "土桥": "4403002021",
                "甜水园": "611100319",
                "太阳宫": "18335740",
                "望京": "18335711",
                "西坝河": "611100321",
                "燕莎": "18335722",
                "亚运村": "18335706",
                "亚运村小营": "611100315",
                "中央别墅区": "18335770"}
    location_list = ['安定门', '奥林匹克公园', '安贞', '东直门', '和平里', '惠新西街', '健翔桥',
                     '马甸(朝阳区)', '马甸(海淀区)', '牡丹园', '南沙滩', '芍药居', '三元桥', '太阳宫', '望京', '西坝河',
                     '亚运村', '亚运村小营']
    location_url = ''
    for location in location_list:
        location_url += chaoyang[location]
        location_url += '%7C'
    location_url = location_url[:-3]
    url = f'https://www.ziroom.com/z/d23008613-b{location_url}-r0-p{page}/?cp=0TO2700'
    return url


def deduplicate_dicts_by_key(dicts_list, key):
    """
    根据指定的键（key）去重一个包含字典的列表。
    """
    return [dict(t) for t in {tuple(d.items()) for d in dicts_list if key in d}]


def read_result_file(result_file):
    with open(result_file, "r") as f:
        dict_json = f.readline().strip()
        house_info = json.loads(dict_json)
    house_info = deduplicate_dicts_by_key(house_info, 'link')
    return house_info


def screenshot_two_bedroom_from_file(result_file):
    house_info = read_result_file(result_file)
    house_info = two_bedroom_filter(house_info)
    if not os.path.exists(screenshot_path):
        os.makedirs(screenshot_path)
    for item in tqdm(house_info, file=sys.stdout):
        web_screenshot(item['link'])
        time.sleep(random.randint(2, 5))


def screenshot_three_bedroom_from_file(result_file):
    house_info = read_result_file(result_file)
    house_info = three_bedroom_filter(house_info)
    path = os.path.join(screenshot_path, 'three_bedroom')
    if not os.path.exists(path):
        os.makedirs(path)
    for item in tqdm(house_info, file=sys.stdout):
        web_screenshot(item['link'], save_path=path)
        time.sleep(random.randint(2, 5))


def crawl_rooms():
    house_info = []
    now = datetime.datetime.now()
    time_str = now.strftime("%y%m%d%H")
    result_file = os.path.join(project_path, f'result_{time_str}.txt')
    for i in range(1, 100):
        print(f"=========================start haidian:{i} page=========================")
        url = get_haidian_url(i)
        result = get_house_info(url)
        if result is None:
            break
        house_info += result
        time.sleep(random.randint(2, 5))
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(house_info))

    for i in range(1, 100):
        print(f"=========================start xichen:{i} page=========================")
        url = get_xichen_url(i)
        result = get_house_info(url)
        if result is None:
            break
        house_info += result
        time.sleep(random.randint(2, 5))
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(house_info))

    for i in range(1, 100):
        print(f"=========================start chaoyang:{i} page=========================")
        url = get_chaoyang_url(i)
        result = get_house_info(url)
        if result is None:
            break
        house_info += result
        time.sleep(random.randint(2, 5))
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(house_info))

    return result_file, time_str


if __name__ == '__main__':
    result_file, time_str = crawl_rooms()
    screenshot_two_bedroom_from_file(result_file)
    screenshot_three_bedroom_from_file(result_file)

    print("remove old image")
    for path in tqdm(list(Path(screenshot_path).rglob('*.png')), file=sys.stdout):
        if '_' in str(path.name):
            os.remove(str(path.absolute()))

    for path in tqdm(list(Path(screenshot_path).rglob('*.png')), file=sys.stdout):
        absolute_path = str(path.absolute())
        compress_image(absolute_path, absolute_path)
        price = get_price(absolute_path)
        new_name = os.path.join(os.path.dirname(absolute_path), f"{price}_{time_str}_{path.name}")
        print(f"rename: {new_name}")
        os.rename(absolute_path, new_name)
    # result_file = "result_23041511.txt"
    # analyze_three_bedroom_from_file(result_file)
