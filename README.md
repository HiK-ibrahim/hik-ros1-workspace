# Proje Galeri Satış Danışman Robotu

Bu projede, daha önceden haritası çıkarılıp kaydedilmiş bir alanda TurtleBot3 robotu, kullanıcı arayüzü üzerinden belirlenen konumlara otonom olarak gidebilir.

![image](https://github.com/user-attachments/assets/a1f4846b-65eb-44ee-b87a-68e13c48e320)

<<<<<<< Updated upstream
---
=======
Nasıl Çalıştırılır:
Gerekli kurulumları (Ros neotic - Turtlebot3 ) yaptıktan sonra terminale "roslaunch hik_ortam hik_galeri.launch"  yazılması halinde çalışacaktır.
>>>>>>> Stashed changes

# Proje: Çizgi Takibi ve Haritalandırma (QR Kod ile Başlangıç ve Bitiş Belirleme)

Eğer kaydedilmiş bir harita dosyası (.yaml) varsa, sistem bu haritayı açarak navigasyonu başlatır. Kaydedilmiş harita yoksa, sistem önce **başlangıç QR kodunu** arar, ardından **kırmızı çizgiyi** bulup takip eder.

- **QR kod tespiti** sürekli çalışır ve bitme QR kodunu arar.
- **Bitiş QR kodu** bulunduğunda harita kaydedilir.
- Bir sonraki çalışma için kaydedilen harita kullanılır.

![image](https://github.com/user-attachments/assets/747a09cc-3132-4ecc-bc3d-2dc91d5ba164)

### **Başlangıçta QR Arama**
- Robot, **2 saniye** içinde hedef QR kodu bulamazsa, kendi etrafında **360 derece** dönmeye başlar.
- QR kodu tespit edilirse, **çizgi takip algoritmasına** geçilir.

### **Çizgi Takip Algoritması**
- Robot, ön kameradan gelen görüntüyü **HSV renk uzayına** dönüştürerek kırmızı çizgiyi tespit eder.
- Tespit edilen çizginin **merkez noktasi** hesaplanır ve robot buna göre **yön düzenlemesi** yapar.
- Çizgi kaybolursa **75 derece** saat yönünde dönerek arama yapar. Bulamazsa, ters yönde **150 derece** dönerek çizgiyi bulmaya çalışır.

![image](https://github.com/user-attachments/assets/4fa08578-783a-4663-b3b3-641be8768ab8)

### **Nasıl Çalıştırılır?**
Aşağıdaki komut terminalde çalıştırılmalıdır:
```bash
roslaunch hik_ortam hikQrVeTakipSON.launch
```

---

# Proje: Çizgi Takibi Sırasında Engelden Kaçma ve Frenet Algoritması ile Rota Dönüşü

Bu proje, **çizgi takibi yaparken engel tespit edilirse**, robotun **engel kaçınma algoritması** ile engelden uzaklaşmasını ve sonrasında tekrar rotaya dönmesini sağlar.

![image](https://github.com/user-attachments/assets/34ec162e-ded3-492b-b655-dcce67105abf)

### **Frenet Path Algoritması**
- Robot, daha önceden belirlenmiş bir **x, y koordinat rotasına** göre hareket eder.
- Eğer robot rotadan uzaklaşırsa, **Frenet algoritması** devreye girerek tekrar rotaya dönmeye çalışır.
- Rotaya **sürekli ileri yönde** dönmesini sağlar, yanlışlıkla ters yönde gitmesine izin vermez.

![image](https://github.com/user-attachments/assets/f1745ac4-f7e0-4773-89ad-0fb813d310e7)

### **Koordinat Kaydetme**
Frenet algoritmasına x, y koordinatlarını vermek için:
```bash
rosrun hik_ortam waypoint_saver.py
```
Bu komut, robotun izlediği rotayı kaydeder.

### **Nasıl Çalıştırılır?**
```bash
roslaunch hik_ortam engeldenKacCizgiBul.launch
```



