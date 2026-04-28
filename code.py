from PIL import Image
import numpy as np

def transform_img(img_path):
    img = Image.open(img_path).convert('RGB')
    img_array = np.array(img)
    height, width, _ = img_array.shape
    
    # Koordinat matrisleri
    x_coords, y_coords = np.meshgrid(np.arange(width), np.arange(height))
    
    # Gri tonu hesapla (0.299R + 0.587G + 0.114B)
    gray_array = (0.299 * img_array[:,:,0] + 0.587 * img_array[:,:,1] + 0.114 * img_array[:,:,2]) / 255.0
    
    # [X, Y, Gri, R, G, B] yapısını kur
    pixel_matrix = np.zeros((height, width, 6), dtype=np.float32)
    pixel_matrix[:, :, 0] = x_coords
    pixel_matrix[:, :, 1] = y_coords
    pixel_matrix[:, :, 2] = gray_array
    pixel_matrix[:, :, 3:] = img_array
    
    return pixel_matrix.reshape(-1, 6), (height, width)

# Dosya yolları
source = "appleman.png"
target = "neon_wallpaper.jpg"

print("Computation has started.")

# Dönüşümleri yap
source_list, source_dims = transform_img(source)
target_list, target_dims = transform_img(target)

# 1. Boyut eşitleme (Kısa olanın boyutuna göre kırpma)
min_len = min(len(source_list), len(target_list))
source_list = source_list[:min_len]
target_list = target_list[:min_len]

# 2. Gri değerlerine (indeks 2) göre sıralama
# argsort kullanarak dizinleri alıyoruz ki tüm satırı buna göre dizelim
source_sorted = source_list[source_list[:, 2].argsort()]
target_sorted = target_list[target_list[:, 2].argsort()]

# 3. Konum Transferi:
# Target piksellerinin renklerini, Source piksellerinin orijinal konumlarına atıyoruz
# Target'ın renklerini (RGB) ve Source'un konumlarını (X, Y) birleştiriyoruz
final_pixels = np.zeros((min_len, 5), dtype=np.float32) 
final_pixels[:, 0:2] = source_sorted[:, 0:2] # Source'un X, Y koordinatları
final_pixels[:, 2:5] = target_sorted[:, 3:6] # Target'ın R, G, B renkleri

# 4. Fotoğrafı Yeniden İnşa Etme
# Kaynak görselin boyutlarında boş bir tuval oluştur
result_img_array = np.zeros((source_dims[0], source_dims[1], 3), dtype=np.uint8)

# Pikselleri koordinatlarına göre yerleştir
# X ve Y koordinatlarını integer'a çevirmeyi unutma
for p in final_pixels:
    x, y = int(p[0]), int(p[1])
    result_img_array[y, x] = p[2:5].astype(np.uint8)

# Sonucu kaydet ve göster
result_img = Image.fromarray(result_img_array)
result_img_name = f"{source.split(".")[0]}_to_{target.split(".")[0]}.png"
result_img.save(result_img_name)
print(f"{target} image is transformed into {source}, creating {result_img_name}")