import requests
import pandas as pd
from io import StringIO
import logging
import os
from datetime import datetime
from typing import List, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import cloudscraper

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/129.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,"
        "image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://fbref.com/",
}

# Logging konfigürasyonu
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PremierLeagueAnalyzer:
    """Premier League istatistiklerini analiz eden sınıf"""
    
    def __init__(self, cache_dir: str = "data_cache"):
        """
        Analyzer'ı başlatır
        
        Args:
            cache_dir: Verilerin kaydedileceği dizin
        """
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        logger.info(f"Cache dizini: {cache_dir}")
        self.scraper = cloudscraper.create_scraper(
            browser={"browser": "chrome", "platform": "windows", "mobile": False}
        )
    
    def _fetch_html(self, url: str) -> str:
        """
        FBRef HTML içeriğini getirir, 403 durumunda Cloudflare korumasını aşmak için
        cloudscraper yedek stratejisini dener.
        """
        response = requests.get(url, headers=DEFAULT_HEADERS, timeout=10)
        if response.status_code == 403:
            logger.warning("403 hatası alındı, cloudscraper ile tekrar deneniyor...")
            response = self.scraper.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    
    def pull_premier_league_team_passing(self) -> pd.DataFrame:
        """
        FBRef'ten Premier League pas istatistiklerini çeker
        
        Returns:
            DataFrame: Pas istatistikleri
        """
        url = "https://fbref.com/en/comps/9/passing/Premier-League-Stats"
        logger.info(f"FBRef'ten pas istatistikleri indiriliyor: {url}")
        
        try:
            html = self._fetch_html(url)
            df = pd.read_html(StringIO(html))[0]
            
            # Sütunları düzelt
            df.columns = ["_".join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
            
            # Sütun adlarını yeniden adlandır
            rename_dict = {
                "Unnamed: 0_level_0_Squad": "Squad",
                "Unnamed: 1_level_0_# Pl": "Players",
                "Unnamed: 2_level_0_90s": "90s",
                "Unnamed: 17_level_0_Ast": "Ast",
                "Unnamed: 18_level_0_xAG": "xAG",
                "Unnamed: 21_level_0_KP": "KP",
                "Unnamed: 22_level_0_1/3": "1/3",
                "Unnamed: 23_level_0_PPA": "PPA",
                "Unnamed: 24_level_0_CrsPA": "CrsPA",
                "Unnamed: 25_level_0_PrgP": "PrgP"
            }
            
            df = df.rename(columns=rename_dict)
            
            # Verileri cache'e kaydet
            cache_file = os.path.join(self.cache_dir, "passing_stats.csv")
            df.to_csv(cache_file, index=False)
            logger.info(f"Veriler kaydedildi: {cache_file}")
            
            return df
        
        except requests.RequestException as e:
            logger.error(f"İnternetten veri çekeme hatası: {e}")
            raise
        except Exception as e:
            logger.error(f"Veri işleme hatası: {e}")
            raise
    
    def pull_premier_league_team_shooting(self) -> pd.DataFrame:
        """
        FBRef'ten Premier League şut istatistiklerini çeker
        
        Returns:
            DataFrame: Şut istatistikleri
        """
        url = "https://fbref.com/en/comps/9/shooting/Premier-League-Stats"
        logger.info(f"Şut istatistikleri indiriliyor: {url}")
        
        try:
            html = self._fetch_html(url)
            df = pd.read_html(StringIO(html))[0]
            df.columns = ["_".join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
            
            # Squad sütununu al
            squad_col = [col for col in df.columns if 'Squad' in col or 'squad' in col]
            if squad_col:
                df = df.rename(columns={squad_col[0]: "Squad"})
            
            cache_file = os.path.join(self.cache_dir, "shooting_stats.csv")
            df.to_csv(cache_file, index=False)
            logger.info(f"Şut verileri kaydedildi: {cache_file}")
            
            return df
        
        except Exception as e:
            logger.error(f"Şut verileri çekme hatası: {e}")
            raise
    
    def filter_teams(self, df: pd.DataFrame, teams: List[str]) -> pd.DataFrame:
        """
        Belirtilen takımları filtreler
        
        Args:
            df: DataFrame
            teams: Takım adları listesi
            
        Returns:
            DataFrame: Filtrelenen veriler
        """
        filtered = df[df["Squad"].isin(teams)]
        logger.info(f"{len(filtered)} takım bulundu")
        return filtered
    
    def compare_teams(self, df: pd.DataFrame, teams: List[str], 
                     columns: Optional[List[str]] = None) -> None:
        """
        Takımları karşılaştırır ve gösterir
        
        Args:
            df: DataFrame
            teams: Takım adları
            columns: Gösterilecek sütunlar
        """
        df_filtered = self.filter_teams(df, teams)
        
        if df_filtered.empty:
            logger.warning(f"Takımlar bulunamadı: {teams}")
            return
        
        if columns is None:
            columns = ["Squad", "Total_Cmp", "Total_Att", "Total_Cmp%", "Total_TotDist"]
        
        print("\n" + "="*80)
        print(f"STATS | TAKIMLAR KARŞILAŞTIRILDI - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        print(df_filtered[columns].to_string(index=False))
        print("="*80 + "\n")
    
    def export_to_excel(self, df: pd.DataFrame, teams: List[str], 
                       filename: str = "premier_league_analysis.xlsx") -> None:
        """
        Verileri Excel dosyasına kaydeder
        
        Args:
            df: DataFrame
            teams: Takım adları
            filename: Dosya adı
        """
        try:
            df_filtered = self.filter_teams(df, teams)
            filepath = os.path.join(self.cache_dir, filename)
            df_filtered.to_excel(filepath, index=False, engine='openpyxl')
            logger.info(f"Excel dosyası kaydedildi: {filepath}")
        except Exception as e:
            logger.error(f"Excel export hatası: {e}")
    
    def plot_comparison(self, df: pd.DataFrame, teams: List[str], 
                       metric: str = "Total_Cmp%", title: str = None) -> None:
        """
        Takımları görsel olarak karşılaştırır
        
        Args:
            df: DataFrame
            teams: Takım adları
            metric: Karşılaştırılacak metrik
            title: Grafik başlığı
        """
        try:
            df_filtered = self.filter_teams(df, teams)
            
            if df_filtered.empty:
                logger.warning(f"Veri bulunamadı: {teams}")
                return
            
            plt.figure(figsize=(10, 6))
            sns.barplot(data=df_filtered, x="Squad", y=metric, palette="husl")
            
            if title is None:
                title = f"Premier League {metric} Karşılaştırması"
            
            plt.title(title, fontsize=16, fontweight='bold')
            plt.xlabel("Takım", fontsize=12)
            plt.ylabel(metric, fontsize=12)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Grafiği kaydet
            plot_file = os.path.join(self.cache_dir, f"plot_{metric}.png")
            plt.savefig(plot_file, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {plot_file}")
            
            plt.show()
        
        except Exception as e:
            logger.error(f"Grafik oluşturma hatası: {e}")
    
    def get_top_teams(self, df: pd.DataFrame, metric: str = "Total_Cmp%", 
                     top_n: int = 5) -> pd.DataFrame:
        """
        En iyi takımları getirir
        
        Args:
            df: DataFrame
            metric: Metrik adı
            top_n: Kaç takım gösterilecek
            
        Returns:
            DataFrame: En iyi takımlar
        """
        try:
            top_teams = df.nlargest(top_n, metric)[["Squad", metric]]
            logger.info(f"En iyi {top_n} takım {metric} metriğine göre:")
            print("\n" + "="*50)
            print(f"TOP {top_n} TAKIM ({metric})")
            print("="*50)
            print(top_teams.to_string(index=False))
            print("="*50 + "\n")
            return top_teams
        except Exception as e:
            logger.error(f"Top takımları getirme hatası: {e}")
    
    def get_statistics_summary(self, df: pd.DataFrame, teams: List[str]) -> None:
        """
        Takımların istatistik özetini gösterir
        
        Args:
            df: DataFrame
            teams: Takım adları
        """
        df_filtered = self.filter_teams(df, teams)
        
        if df_filtered.empty:
            logger.warning(f"Takımlar bulunamadı: {teams}")
            return
        
        print("\n" + "="*80)
        print("STATISTIK OZETI")
        print("="*80)
        
        for team in teams:
            team_data = df_filtered[df_filtered["Squad"] == team]
            if not team_data.empty:
                print(f"\n{team}:")
                print("-" * 50)
                for col in team_data.columns:
                    value = team_data[col].values[0]
                    print(f"  {col}: {value}")
        
        print("\n" + "="*80 + "\n")


def main():
    """Ana fonksiyon"""
    
    analyzer = PremierLeagueAnalyzer(cache_dir="data_cache")
    
    try:
        # 1. Verileri indir
        df_passing = analyzer.pull_premier_league_team_passing()
        df_shooting = analyzer.pull_premier_league_team_shooting()
        
        # 2. Takımları karşılaştır
        teams = ["Arsenal", "Nott'ham Forest"]
        analyzer.compare_teams(df_passing, teams)
        
        # 3. En iyi takımları göster
        analyzer.get_top_teams(df_passing, metric="Total_Cmp%", top_n=5)
        analyzer.get_top_teams(df_shooting, metric="Standard_Sh", top_n=5)
        
        # 4. Detaylı istatistikler
        analyzer.get_statistics_summary(df_passing, teams)
        
        # 5. Excel'e aktar
        analyzer.export_to_excel(df_passing, teams, "passing_comparison.xlsx")
        
        # 6. Grafik oluştur
        analyzer.plot_comparison(df_passing, teams, metric="Total_Cmp%", 
                                title="Arsenal vs Nottham Forest - Pas Başarı %")
        
        logger.info("Analiz tamamlandı!")
    
    except Exception as e:
        logger.error(f"Program hatası: {e}")
        raise


if __name__ == "__main__":
    main()