# Premier League Predict

Python tabanlı bu mini araç, FBRef üzerinde yer alan Premier League takım istatistiklerini indirip aynı anda birkaç farklı çıktıya dönüştürerek hızlı analiz yapmanızı sağlar. Varsayılan senaryoda Arsenal ve Nott'ham Forest için pas & şut metriklerini indirir, iki takımı karşılaştırır, lig genelinde en iyi takımları listeler, özet tablolar basar, Excel’e export eder ve görselleştirir.

## Özellikler
- **HTTP katmanı** – FBRef verileri doğrudan `requests` ile indirilir; 403/Cloudflare engeli olduğunda `cloudscraper` devreye girer.
- **Veri ön işleme** – FBRef’in çok seviyeli kolon yapısı düzleştirilir ve anlaşılır isimler atanır.
- **Özelleştirilebilir filtre** – `teams` listesine istediğiniz kulüpleri ekleyip sadece o satırlar üzerinde çalışabilirsiniz.
- **Karşılaştırma & sıralamalar** – Konsolda seçilen takımların kritik pas metrikleri gösterilir, ayrıca lig genelinde seçtiğiniz metrik için ilk `n` takım listelenir.
- **İstatistik özeti** – Her takımın tüm kolonları döngüyle yazdırılarak hızlı inceleme yapılabilir.
- **Çıktılar** – `data_cache/` altında CSV, Excel, PNG formatlarında kayıt tutulur. Excel çıktısı `openpyxl` motoru ile üretilir.

## Gereksinimler
- Python 3.10+
- Bağımlılıklar:
  - `requests`
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `cloudscraper`
  - `openpyxl`

Hızlı kurulum için:

```bash
pip install requests pandas matplotlib seaborn cloudscraper openpyxl
```

## Kullanım
1. Depoyu klonlayın veya dosyaları indirin.
2. Terminalde proje klasörüne geçin. Windows’ta masaüstü yolunda Türkçe karakterler varsa kısa yol (`MASAST~1`) kullanmak daha kolaydır:
   ```powershell
   cd C:\Users\<kullanıcı>\OneDrive\MASAST~1\Premier League Predict
   ```
3. Script’i çalıştırın:
   ```bash
   python Pr_league_predict_version2.py
   ```
4. Çalışma tamamlandığında:
   - Konsola takım karşılaştırmaları, top 5 listeleri ve özetler yazılır.
   - `data_cache/` klasörüne:
     - `passing_stats.csv` & `shooting_stats.csv`
     - `passing_comparison.xlsx`
     - `plot_Total_Cmp%.png`
     kaydedilir.

## Özelleştirme
- Farklı takımlar analiz etmek için `main()` içindeki `teams` listesini düzenleyin.
- Top sıralamasında kullanılan metrikleri `get_top_teams` çağrılarına girilen `metric` argümanı belirler.
- Grafikteki metrik `plot_comparison(..., metric="Total_Cmp%")` satırından değiştirilebilir.

## Bilinen notlar
- FBRef, Cloudflare tarafından korunuyor; eğer ülkenize/ISP’nize göre erişim tamamen engellenirse `cloudscraper` da hata verebilir.
- Seaborn 0.14 ile birlikte `palette` parametresi uyarı veriyor; ileride `hue` kullanacak şekilde güncelleyebilirsiniz.

Katkı vermek veya yeni metrikler eklemek için issue açmanız yeterli. İyi analizler! 🚀

