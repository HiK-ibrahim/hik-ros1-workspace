![image](https://github.com/user-attachments/assets/a1f4846b-65eb-44ee-b87a-68e13c48e320)

Başlangıçta QR Arama:

Algoritma başlangıçta 2 saniye içersinde  hedef qr kodu okuyamaz ise kendi etrafında 360 derece dönmeye başlar.Eğer başlangıç qrkodu okunur ise çizgi takip etme algoritmasına geçilir.


Çizgi Takip Etme:

Algoritma, robotun önündeki görüntüyü alarak, kırmızı rengindeki çizgiyi tanımak için bir renk filtresi uygular. Bu işlem, görüntüyü HSV renk uzayına dönüştürüp, kırmızı renk aralığını filtreler.
Elde edilen maskeden çizginin merkezi noktası hesaplanır. Eğer çizgi tespit edilirse:
Robotun yönünü, çizginin merkezinin görüntüdeki orta noktasıyla karşılaştırarak ayarlar.
Eğer çizgi merkezden sola veya sağa kaymışsa, robotun dönüş hızını bu hataya göre belirler ve robotu düz ilerlemeye teşvik eder.

Çizgi Kaybolduğunda Arama:
Eğer çizgi kaybolursa robot çizgiyi aramak için belirli bir yönde dönmeye başlar (ilk başta saat yönünde) bu dönme hareketi 75 derece ile sınırlandırılır ve 75 derece dönme hareketi yaparken çizgi hala bulunamadıysa ters yönde (75+75) 150 derece dönme dönerek çizgiyi bulmaya çalışır.




