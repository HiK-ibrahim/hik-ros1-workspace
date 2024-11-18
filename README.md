1. Proje Galeri Satış Danışman Robotu

Bu projede daha önceden haritası çıkarılıp kaydedilmiş bir alanda turtlebot3 robotumuz istenen konumlara kullanıcı arayüzü üzerinden seçerek  otonom olarak gidebiliyor.

![image](https://github.com/user-attachments/assets/a1f4846b-65eb-44ee-b87a-68e13c48e320)

Nasıl Çalıştırılır:
Gerekli kurulumları (Ros neotic - Turtlebot3 -Pyqt5- python3) yapılır. 
Terminale "roslaunch hik_ortam hik_galeri.launch"  yazılması halinde çalışacaktır.


2. Proje Çizgi izleme ve haritalandırma (qr kod okunarak başlangıç ve bitiş belirlendi)
Eğer kaydedilmiş bir harita dosyası (.yaml) var ise o haritayı açarak navigasyon başlatır. Kaydedilmiş harita yoksa Başlangıç Qr'ını arar, ardından çizgi arar(kırmızı) ve kırmızı çizgiyi takip eder. Bu çizgi takibi sırasında qr-detection görevi bitiş Qr'ını bulabilmek için çalışmasını sürdürür. Çizginin sonunda bitiş Qr ı bulunduğunda harita kaydedilir. Bir sonraki çalışmada eğer harita var ise bu harita ile işlem yapılır.
![image](https://github.com/user-attachments/assets/747a09cc-3132-4ecc-bc3d-2dc91d5ba164)





Başlangıçta QR Arama:

Algoritma başlangıçta 2 saniye içersinde  hedef qr kodu okuyamaz ise kendi etrafında 360 derece dönmeye başlar.Eğer başlangıç qrkodu okunur ise çizgi takip etme algoritmasına geçilir.


Çizgi Takip Etme:

Algoritma, robotun önündeki görüntüyü alarak, kırmızı rengindeki çizgiyi tanımak için bir renk filtresi uygular. Bu işlem, görüntüyü HSV renk uzayına dönüştürüp, kırmızı renk aralığını filtreler.
Elde edilen maskeden çizginin merkezi noktası hesaplanır. Eğer çizgi tespit edilirse:
Robotun yönünü, çizginin merkezinin görüntüdeki orta noktasıyla karşılaştırarak ayarlar.
Eğer çizgi merkezden sola veya sağa kaymışsa, robotun dönüş hızını bu hataya göre belirler ve robotu düz ilerlemeye teşvik eder.

Çizgi Kaybolduğunda Arama:
Eğer çizgi kaybolursa robot çizgiyi aramak için belirli bir yönde dönmeye başlar (ilk başta saat yönünde) bu dönme hareketi 75 derece ile sınırlandırılır ve 75 derece dönme hareketi yaparken çizgi hala bulunamadıysa ters yönde (75+75) 150 derece dönme dönerek çizgiyi bulmaya çalışır.
![image](https://github.com/user-attachments/assets/4fa08578-783a-4663-b3b3-641be8768ab8)

Nasıl Çalıştırılır:
Terminale "roslaunch hik_ortam hikQrVeTakipSON.launch"  yazılması halinde çalışacaktır.

3.Proje-Çizgi takibi sırasında çıkan engelden kaçınca ve tekrar çizgiyi bulabilmek için Frenet ile rotaya dönüş 

Çizgi takibi yapar iken engel tespit edilirse (Lidar sensörüile) bu engelden kaçış algoritmasıdır.
![image](https://github.com/user-attachments/assets/34ec162e-ded3-492b-b655-dcce67105abf)


Frenet Path -
Bu algoritma daha önceden çizilmiş bir rotanın (x,y) koordinatlarını alır , aracımız bu rotadan uzaklaştığı zaman rotaya tekrar ulaşmasını hedefler.
Bu algoritma 2. planda çalışır.(Rotadan uzun süre çıkılmış ve rota bulunamıyorsa aktif edilir.)
Frenet çalışır iken rota mantığı izlenmiştir, verilen koordinatlardan hep ilerdeki koordinata yönlendirecek şekilde ayarlanmıştır. Bu sayede istenmeyen ters yöne gitme durumuna izin vermeyecektir. 
 
![image](https://github.com/user-attachments/assets/f1745ac4-f7e0-4773-89ad-0fb813d310e7)

Frenet algoritmasına x,y koordinatlarını verebilmek için "/waypoint_saver.py" kodunu terminalde çalıştırıp aracınızın izlediği rotayı kaydedebilirsiniz.

Nasıl Çalıştırılır:
roslaunch hik_ortam engeldenKacCizgiBul.launch







