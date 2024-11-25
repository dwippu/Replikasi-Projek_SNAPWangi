"""
REPLIKASI PROJEK SNAPWANGI

Alur:
1. Import file SHP
2. Ekstrak polygon dari kelurahan yang ditentukan
3. Buat grid untuk mempermudah menentukan lokasi screenshot
    * Lakukan screenshot untuk dua level zoom mengetahui resolusi yang tersedia
    * ukuran grid ditentukan berdasarkan resolusi yang diperoleh
4. Buat screenshot layar berdasarkan grid yang terbentuk
5. Dapatkan nama tempat dengan ocr, sekaligus koordinat pada layar
6. Hapus teks yang merupakan menu dari Google Maps
7. Hapus teks yang berupa nama jalan
8. Ulangi tahapan 4 - 7 untuk setiap grid yan didapat
9. Klik setiap nama tempat yang didapat
10. Dapatkan koordinat POI melalui link
11. Dapatkan detail dari tempat
"""

"""
KONFIKURASI PARAMETER (BISA DISESUAIKAN)
"""
#path shp file
path_shp = "SHPFile Kota Sukabumi/3272.shp"

#pilih kelurahan
kecamatan = "Cikole"
kelurahan = "Cikole"

#folder output
path_output = "output/"


"""
SCRIPT SCRAPING GOOGLE MAPS
"""

# Library for Scrape
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
from a_selenium_click_on_coords import click_on_coordinates

# Visualization
from matplotlib import pyplot as plt
import cv2

# Text Recognition
from paddleocr import PaddleOCR, draw_ocr

# Polygon Manipulation
from shapely.geometry import Polygon, box, Point
from shapely import distance

# Dataframe Management
import geopandas as gpd
import pandas as pd
import numpy as np

# Runtime Monitoring
import time

# I/O
import os
import sys

#windows option
chrome_options = Options()
chrome_options.add_argument("--start-maximized") # windows size
chrome_options.add_experimental_option("detach",True)

#zoom gmaps
zoom1 = 20
zoom2 = 20.5
zoom3 = 21

#test coordinat,
lat_test = -6.9082714
long_test = 106.9384583
#x=long; y=lat

#windows option
chrome_options = Options()
chrome_options.add_argument("--start-maximized") # windows size
chrome_options.add_experimental_option("detach",True)

#zoom gmaps
zoom1 = 20
zoom2 = 20.5
zoom3 = 21

#test coordinat,
lat_test = -6.9082714
long_test = 106.9384583
#x=long; y=lat

def current_time():
    return time.strftime("[%Y/%m/%d %H:%M:%S]")

def calculate_grid_size(x, y, zoom_level):
    x_size = (x/256)*(360/2**zoom_level)
    y_size = (y/256)*(360/2**zoom_level)
    return x_size, y_size

# Fungsi untuk membagi poligon menjadi grid persegi panjang
def create_grid(polygon:gpd.geoseries.GeoSeries, x_size:int, y_size:int):
    minx, miny, maxx, maxy = float(polygon.bounds["minx"]), float(polygon.bounds["miny"]), float(polygon.bounds["maxx"]), float(polygon.bounds["maxy"])  # Mendapatkan batas-batas poligon
    
    # Menentukan jumlah grid yang dibutuhkan dalam arah x dan y
    x1 = -np.inf #int(math.ceil((maxx - minx) / x_size))
    i = 0
    grid = []
    
    # Membuat persegi panjang di dalam area poligon
    while x1 < maxx:
        j = 0
        y1 = -np.inf #int(math.ceil((maxy - miny) / y_size))
        while y1 < maxy:
            # Menentukan koordinat persegi panjang
            x0 = minx + i * x_size * 0.99
            y0 = miny + j * y_size * 0.99
            x1 = x0 + x_size
            y1 = y0 + y_size
            
            # Membuat persegi panjang dengan koordinat tersebut
            rect = box(x0, y0, x1, y1)
            
            # Memeriksa apakah persegi panjang tumpang tindih dengan poligon
            if rect.intersects(polygon.values):
                grid.append(rect)
            j+=1
        i+=1
    
    print(f"{current_time()} INFO: Berhasil membentuk grid sebanyak {len(grid)}")
    return gpd.GeoDataFrame(geometry=grid, crs="EPSG:4326")

def get_centroid(grid_list:gpd):
    grid_list["centroid"] =  grid_list.geometry.centroid
    return grid_list

def get_gmaps_link(lat, long, zoom_level):
    return f"https://www.google.com/maps/@{lat},{long},{zoom_level}z?"

def make_screenshot(driver:webdriver.Chrome, link:str, save_to:str):
    driver.get(link)
    time.sleep(0.5)
    driver.find_element(By.CLASS_NAME,"w6VYqd").click()
    time.sleep(0.2)
    driver.save_screenshot(save_to)

    return save_to

def get_image_resolution(image_path:str):
    img = cv2.imread(image_path)
    y,x,z = img.shape 
    return x, y #x=lat; y=long

def detect_text(image_path, bin=False, inv=False, link_map=""):
    # Path
    font_path = "C:/Windows/Fonts/arial.ttf"

    # Initialize OCR
    ocr = PaddleOCR(use_angle_cls= True, lang = "en", ocr_version='PP-OCRv4', vis_font_path=font_path)

    # Perform OCR
    result = ocr.ocr(image_path, cls=True, bin=bin, inv=inv)

    # Visualization
    # Get the bounding box and corresponding text
    boxes = [line[0] for line in result[0]]
    txts = [line[1][0] for line in result[0]]
    scores = [line[1][1] for line in result[0]]

    boxes_centroid = [Polygon(line).centroid for line in boxes]
    source = link_map

    return pd.DataFrame({'text': txts, 'scores': scores, 'boxes': boxes, 'centroid':boxes_centroid, 'source':source})

def save_image_with_boxes(image_path, boxes, save_to:str):
    # Load the image
    image = cv2.imread(image_path)

    image_with_boxes = draw_ocr(image, boxes)

    # Convert the image from BGR to RGB (OpenCV loads images in BGR)
    image_with_boxes = cv2.cvtColor(image_with_boxes, cv2.COLOR_BGR2RGB)

    plt.savefig(save_to)

def cleaning_text(df_text):
    exclude_list = ["disimpan", "disimpar", "i", "google", "atm", "museum", "an atm", "hotel", "googl", "rekomendasi aktivitas", "transportasi umum", "itn atm", "area ini", "terbaru", "login", "+", "y1 restoran", "restoran", "apotek", "telusuri google maps", "tidak ada info lalu lintas", "lapisan", "lapisar", "lapisa", "+|", "gogle"]
    exclude_specified_position = [Point(1799, 30), Point(35,37), Point(35,112.5), Point(33,184), Point(1885,809), Point(1858,31), Point(549,36), Point(644,36)]
    df_text["text"] = df_text["text"].str.lower()
    df_text["text"] = df_text["text"].str.strip()

    # Hapus Menu Google, 
    df_text = df_text[~df_text["text"].isin(exclude_list)]
    for i, r in df_text.iterrows():
        for j in exclude_specified_position:
            if distance(j, r["centroid"])<5:
                df_text.drop(index=i, inplace=True)
                break
    
    # Hapus nama jalan
    df_text = df_text[~df_text['text'].str.startswith('jl')]
    df_text = df_text[~df_text['text'].str.startswith('ji')]
    df_text = df_text[~df_text['text'].str.startswith('gg')]

    #hapus lainnya
    df_text = df_text[~df_text['text'].str.startswith('lalin')]
    df_text = df_text[~df_text['text'].str.startswith('tidak ada')]
    df_text = df_text[~df_text['text'].str.startswith('telusuri google')]
    
    df_text.reset_index(inplace=True, drop=True)

    return df_text

def collect_place(destination, df):
    if "text" not in destination.columns:
        destination["text"] = []

    df = df[~(df["text"].isin(destination["text"]))]
    destination = pd.concat([destination, df], ignore_index=True, axis=0)
    destination.reset_index(drop=True, inplace=True)
    
    return destination

def get_point_coor(link):
    # batas untuk memotong
    first = link.find("!3d")+3
    last = link.find("!16")
    
    # potong    
    tag = link[first:last].split("!4d")
    if len(tag) == 2:
        return tag
    else:
        return "Galat", "Galat"
    
def add_column(df):
    col = ["latitude", "longitude", "nama", "kategori", "telp", "alamat", "website", "last_review", "date_last_review", "last_review_rating", "link", "keterangan"]
    for i in col:
        if i not in df.columns:
            df[f"{i}"] = None

    return df

def get_places_detail(driver, df_result):
    df_result = add_column(df_result)
    for i, data in df_result.iterrows():
        
        if not pd.isna(data["nama"]):
            continue
        
        # buka lagi webnya
        driver.get(data["source"])
        time.sleep(0.6)
        
        try:
            driver.find_element(By.CLASS_NAME,"w6VYqd").click()
        except:
            time.sleep(0.2)
            pass
        
        # Klik nama tempat
        try: 
            click_on_coordinates(driver,int(round(data["centroid"].x, 0)),int(round(data["centroid"].y,0)))
        except:
            time.sleep(1)
            continue
        time.sleep(2.5)

        # Periksa apakah tampilan detail tempat telah muncul, jika tidak ada maka beri isian "Na" untuk semua kolom dan lanjut ke baris berikutnya
        if len(driver.find_elements(By.CLASS_NAME, 'ZKCDEc')) == 0:
            continue
        time.sleep(0.5)
        
        # Ambil nama tempat dan kegiatan usaha
        name_element = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf.lfPIob')
        df_result["nama"][i] = name_element.text
        category_element = driver.find_elements(By.CSS_SELECTOR, 'button.DkEaL ')
        if (len(category_element) != 0):
            df_result["kategori"][i] = category_element[0].text

        # Ambil link kemudian ekstrak koordinat dari POI kemudian periksa apakah telah ada yang sama pada baris sebelumnya, jika ada buang dan lanjut pada baris selanjutnya
        url = driver.current_url
        lat, long = get_point_coor(url)
        if ((df_result['latitude'] == lat) & (df_result['longitude'] == long)).any():
            df_result.drop(index=i, inplace=True)
            continue
        df_result["latitude"][i] = lat
        df_result["longitude"][i] = long
        df_result["link"][i] = url

        # Ambil email, nomor telp., alamat, website
        identity_element = driver.find_elements(By.CLASS_NAME, "CsEnBe")
        for element in identity_element:
            identity = str(element.get_attribute("aria-label"))          
            if identity.startswith("Telepon"):
                df_result["telp"][i] = identity
            elif identity.startswith("Alamat"):
                df_result["alamat"][i] = identity
            elif identity.startswith("Situs Web"):
                df_result["website"][i] = identity

        try:
            df_result["keterangan"][i] = driver.find_element(By.CLASS_NAME, "aSftqf").text
        except:
            pass

        # Ambil Last Review
        try:
            driver.find_element(By.XPATH, f'//*[@aria-label="Ulasan untuk {name_element.text}"]').click()
            time.sleep(0.8)
            driver.find_element(By.XPATH, '//*[@aria-label="Urutkan ulasan"]').click()
            time.sleep(0.5)
            filter = driver.find_elements(By.XPATH, '//*[@class="fxNQSd"]')
            filter[1].click()
            time.sleep(0.5)
            
            #scroll dulu biar muncul        
            scrollable_div = driver.find_element(By.CSS_SELECTOR, "div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde")
            driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
            time.sleep(1)
        except:
            continue

        try:
            review_element = driver.find_elements(By.CLASS_NAME, "jftiEf")
            review_element = review_element[0]
        except:
            continue
        try:
            df_result["last_review"][i] = review_element.find_element(By.CLASS_NAME, "wiI7pd").text
        except:
            pass
        try:
            df_result["date_last_review"][i] = review_element.find_element(By.CLASS_NAME, "rsqaWe").text
        except:
            pass
        try:
            df_result["last_review_rating"][i] = review_element.find_element(By.CLASS_NAME, "kvMYJc").get_attribute("aria-label")
        except:
            pass
        
    return df_result

def save(df, path:str):
    if not path.endswith(".csv"):
        path = path+"csv.csv"
    
    df.to_csv(path)

def cleaning_data(df):
    # drop baris yang tidak gagal didapat
    df = df[~df["nama"].isna()]
    df.reset_index(drop=True, inplace=True)
    return df    

def filter_place(df, polygon, drop = True):
    df["intersect"] = None
    for i, data in df.iterrows():
        point = Point(data["longitude"], data["latitude"])
        if (point.intersects(polygon.values)):
            df["intersect"][i] = True
        else:
            df["intersect"][i] = False
    
    if drop:
        df = df[df["intersect"]==True]
        df.reset_index(drop=True, inplace=True)
        df.drop("intersect", axis = 1)
    
    df = df.drop(['text', 'scores', 'boxes', 'centroid', 'source'], axis = 1)

    return df

# EXECUT
# Nama folder yang ingin diperiksa atau dibuat
folder_name = ["screenshoot", "ocr_result", f"[SHPFile] Unit usaha kelurahan {kelurahan} dan sekitarnya", f"[SHPFile] Unit usaha kelurahan {kelurahan}"]

# Memeriksa apakah folder ada
for i in folder_name:
    if not os.path.exists(path_output+i):
        # Membuat folder jika belum ada
        os.makedirs(path_output+i)
sys.stdout = open(f'{path_output}log.txt', 'w')

# Hitung Waktu
start_time = time.time()

print(f'{current_time()} INFO: Memulai proses Scrapping')
#initiate browser
driver = webdriver.Chrome(options=chrome_options)

# first screenshoot
path_first_screenshoot = make_screenshot(driver, get_gmaps_link(lat_test, long_test, zoom1), f"{path_output}/screenshoot_zoom_1.png")

# Periksa ukuran resolusi gambar
res_x, res_y = get_image_resolution(path_first_screenshoot)

# Import SHP
geo_df_kota = gpd.read_file(path_shp)
geo_df_kota.head()
geo_kelurahan = geo_df_kota[(geo_df_kota["WADMKC"]==kecamatan) & (geo_df_kota["WADMKD"]==kelurahan)]["geometry"]

# x2_size, y2_size = calculate_grid_size(res_x,res_y,zoom2)

# make grid maps
print(f'{current_time()} INFO: Menghitung jumlah grid untuk tingkat zoom {zoom1}')
x1_size, y1_size = calculate_grid_size(res_x,res_y,zoom1)
grid1 = create_grid(geo_kelurahan,x1_size,y1_size)

print(f'{current_time()} INFO: Menghitung jumlah grid untuk tingkat zoom {zoom3}')
x3_size, y3_size = calculate_grid_size(res_x,res_y,zoom3)
grid3 = create_grid(geo_kelurahan,x3_size,y3_size)

# centroid of each grid
grid1 = get_centroid(grid1)
print(f'{current_time()} INFO: Selesai mendapatkan titik tengah tiap grid pada tingkat zoom {zoom1}')
grid3 = get_centroid(grid3)
print(f'{current_time()} INFO: Selesai mendapatkan titik tengah tiap grid pada tingkat zoom {zoom3}')

# Initiate Dataframe hasil
df_result = pd.DataFrame()

# looping zoom 1
for i in range(len(grid1)):
    l = get_gmaps_link(round(grid1['centroid'][i].y,7), round(grid1['centroid'][i].x,7),zoom1)
    img = make_screenshot(driver, l,f"{path_output}screenshoot/zoom1_{i+1}.png")
    
    result = detect_text(img, link_map=l)
    save_image_with_boxes(img,result['boxes'],f"{path_output}ocr_result/zoom1_{i+1}.png")
    clean_result = cleaning_text(result)
    df_result = collect_place(df_result, clean_result)

save(df_result, f"{path_output}hasil OCR tingkat zoom {zoom1}.csv")

print(f'{current_time()} INFO: Mengambil detail tempat')
df_result = get_places_detail(driver, df_result)
save(df_result, f"{path_output}hasil scrapping detail tingkat zoom {zoom1}.csv")

end_time = time.time()
elapsed_time = end_time - start_time
print(f'{current_time()} INFO: Waktu eksekusi sampai looping 1: {elapsed_time // 3600} jam {(elapsed_time % 3600) // 60} menit {elapsed_time % 60} detik')

# looping zoom 3
for i in range(len(grid3)):
    l = get_gmaps_link(round(grid3['centroid'][i].y,7), round(grid3['centroid'][i].x,7),zoom3)
    img = make_screenshot(driver, l,f"{path_output}screenshoot/zoom3_{i+1}.png")
    
    result = detect_text(img, link_map=l)
    save_image_with_boxes(img,result['boxes'],f"{path_output}ocr_result/zoom3_{i+1}.png")
    clean_result = cleaning_text(result)
    df_result = pd.concat([df_result, clean_result], ignore_index=True, axis=0)

df_result = get_places_detail(driver, df_result)
save(df_result, f"{path_output}hasil scrapping dengan tambahan tingkat zoom {zoom3}.csv")
print(f'{current_time()} INFO: Berhasil menyimpan hasil {path_output}hasil scrapping dengan tambahan tingkat zoom {zoom3}.csv')

driver.quit()

end_time = time.time()
elapsed_time = end_time - start_time
print(f'{current_time()} INFO: Waktu eksekusi sampai looping 2: {elapsed_time // 3600} jam {(elapsed_time % 3600) // 60} menit {elapsed_time % 60} detik')
sys.stdout.flush()

df_result_final = cleaning_data(df_result)
df_result_final_kelurahan = filter_place(df_result_final, geo_kelurahan, drop=False)
df_result_final_kelurahan_filtered = filter_place(df_result_final, geo_kelurahan, drop=True)

df_result_final = cleaning_data(df_result)
df_result_final_kelurahan = filter_place(df_result_final, geo_kelurahan, drop=False)
df_result_final_kelurahan_filtered = filter_place(df_result_final, geo_kelurahan, drop=True)

df_result_final_kelurahan['geometry'] = df_result_final_kelurahan.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
gpd.GeoDataFrame(df_result_final_kelurahan, geometry="geometry").set_crs("EPSG:4326", allow_override=True, inplace=True).to_file(f'{path_output}[SHPFile] Unit usaha kelurahan {kelurahan} dan sekitarnya/Unit usaha kelurahan {kelurahan} dan sekitarnya.shp')

df_result_final_kelurahan_filtered['geometry'] = df_result_final_kelurahan_filtered.apply(lambda row: Point(row['longitude'], row['latitude']), axis=1)
gpd.GeoDataFrame(df_result_final_kelurahan_filtered, geometry="geometry").set_crs("EPSG:4326", allow_override=True, inplace=True).to_file(f'{path_output}[SHPFile] Unit usaha kelurahan {kelurahan}/Unit usaha kelurahan {kelurahan}.shp')

sys.stdout.close()