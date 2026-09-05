"""
Markov Chain Analysis of Daily Stock Price Movements
Istatistik / Olasiliksal Surecler ders calismasi

Konu : KONTR (Kontrolmatik Teknoloji A.S.) hisse senedinin gunluk
       yuzdesel fiyat degisimleri uzerinden ayrik zamanli bir
       Markov Zinciri modellenmesi.

Calistirma : python markov_analysis.py
Cikti      : Konsol ciktilari + figures/ klasorune kaydedilen grafikler
"""

from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd

# --- Sabitler ve yollar ---------------------------------------------------
# Yollar script'in bulundugu klasore gore cozulur; makineden makineye degismez.
KOK_DIZIN = Path(__file__).resolve().parent
VERI_YOLU = KOK_DIZIN / "data" / "KONTR_gecmis_verileri.csv"
FIGUR_DIZIN = KOK_DIZIN / "figures"

ESIK = 1.0  # Durum ayrimi icin kullanilan yuzdesel esik degeri (%1)

DURUM_ISIMLERI = {1: "1\n(Dusus)", 2: "2\n(Yatay)", 3: "3\n(Yukselis)"}
DURUM_ETIKET = {1: "Dusus", 2: "Yatay", 3: "Yukselis"}


# --- 1. ADIM: VERI OKUMA VE TEMIZLEME -------------------------------------
def veriyi_hazirla(yol: Path) -> pd.DataFrame:
    """CSV'yi okur, 'Fark %' sutununu sayisallastirir ve kronolojik siralar."""
    df = pd.read_csv(yol)

    # "10,00%" -> 10.00  (yuzde isareti kaldirilir, virgul noktaya cevrilir)
    df["Fark %"] = (
        df["Fark %"].astype(str).str.replace("%", "", regex=False).str.replace(",", ".", regex=False).astype(float)
    )

    # Investing.com verisi yeniden eskiye dogru gelir; kronolojik hale getiriyoruz.
    df["Tarih"] = pd.to_datetime(df["Tarih"], format="%d.%m.%Y")
    df = df.sort_values("Tarih").reset_index(drop=True)

    df["Durum"] = df["Fark %"].apply(durum_belirle)
    return df


def durum_belirle(fark: float) -> int:
    """Durum uzayi S = {1, 2, 3} tanimi.

    1 -> Dusus     : Fark % < -1.0
    2 -> Yatay     : -1.0 <= Fark % <= +1.0
    3 -> Yukselis  : Fark % > +1.0
    """
    if fark < -ESIK:
        return 1
    if fark > ESIK:
        return 3
    return 2


# --- Yardimci cizim fonksiyonlari -----------------------------------------
def gecis_diyagrami_ciz(matris: np.ndarray, baslik: str, dosya_adi: str, renk: str) -> None:
    """3x3 bir olasilik matrisini yonlu graf (gecis diyagrami) olarak cizer."""
    plt.figure(figsize=(8, 6))
    G = nx.DiGraph()

    for i in range(3):
        for j in range(3):
            olasilik = matris[i, j]
            if olasilik > 0.001:
                G.add_edge(
                    DURUM_ISIMLERI[i + 1],
                    DURUM_ISIMLERI[j + 1],
                    weight=olasilik,
                    label=f"{olasilik:.3f}",
                )

    pos = nx.circular_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color=renk, edgecolors="black")
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold")
    nx.draw_networkx_edges(
        G, pos, edge_color="gray", arrows=True, arrowsize=20, connectionstyle="arc3, rad=0.1"
    )
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels=nx.get_edge_attributes(G, "label"), label_pos=0.3, font_size=9
    )

    plt.title(baslik)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(FIGUR_DIZIN / dosya_adi, dpi=150)
    plt.show()
    plt.close()


# --- a) Zaman - Durum grafigi ---------------------------------------------
def sik_a_zaman_durum_grafigi(df: pd.DataFrame) -> None:
    plt.figure(figsize=(12, 5))
    plt.plot(df.index + 1, df["Durum"], marker="o", linestyle="-", color="b")
    plt.yticks([1, 2, 3], ["1 (Dusus)", "2 (Yatay)", "3 (Yukselis)"])
    plt.title("Zaman Parametresine Gore Markov Zinciri Durum Grafigi")
    plt.xlabel("Zaman Parametresi T (Gunler)")
    plt.ylabel("Durum Uzayi S")
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(FIGUR_DIZIN / "a_zaman_durum_grafigi.png", dpi=150)
    plt.show()
    plt.close()


# --- b) Bir-adim gecis matrisi (P) ----------------------------------------
def sik_b_gecis_matrisi(df: pd.DataFrame) -> np.ndarray:
    """Ampirik bir-adim gecis matrisini frekans sayimlarindan hesaplar."""
    df = df.copy()
    df["Sonraki_Durum"] = df["Durum"].shift(-1)

    gecis_sayilari = pd.crosstab(df["Durum"], df["Sonraki_Durum"])
    # Hic gozlenmemis bir durum olsa bile matris daima 3x3 kalsin:
    gecis_sayilari = gecis_sayilari.reindex(index=[1, 2, 3], columns=[1.0, 2.0, 3.0], fill_value=0)

    P = gecis_sayilari.div(gecis_sayilari.sum(axis=1), axis=0)

    print("\n--- b) Bir-Adim Gecis Matrisi (P) ---")
    print(P.round(3).to_string())

    P_dizi = P.to_numpy()
    gecis_diyagrami_ciz(P_dizi, "Markov Zinciri Bir-Adim Gecis Diyagrami (b)", "b_P_diyagrami.png", "lightblue")

    # En yuksek / en dusuk gecis olasiliklari
    en_yuksek = np.unravel_index(np.argmax(P_dizi), P_dizi.shape)
    en_dusuk = np.unravel_index(np.argmin(P_dizi), P_dizi.shape)
    print(
        f"En yuksek olasilik : P({en_yuksek[0] + 1}->{en_yuksek[1] + 1}) = {P_dizi[en_yuksek]:.3f} "
        f"({DURUM_ETIKET[en_yuksek[0] + 1]} -> {DURUM_ETIKET[en_yuksek[1] + 1]})"
    )
    print(
        f"En dusuk olasilik  : P({en_dusuk[0] + 1}->{en_dusuk[1] + 1}) = {P_dizi[en_dusuk]:.3f} "
        f"({DURUM_ETIKET[en_dusuk[0] + 1]} -> {DURUM_ETIKET[en_dusuk[1] + 1]})"
    )
    return P_dizi


# --- c) P^3 ve P^100 -------------------------------------------------------
def sik_c_matris_kuvvetleri(P: np.ndarray) -> None:
    P3 = np.linalg.matrix_power(P, 3)
    P100 = np.linalg.matrix_power(P, 100)

    print("\n--- c) P^3 Matrisi (3 Adim Sonraki Olasiliklar) ---")
    print(np.round(P3, 3))
    print("\n--- c) P^100 Matrisi (Kararli Durum) ---")
    print(np.round(P100, 4))

    gecis_diyagrami_ciz(P3, "P^3 Olasilik Matrisi Diyagrami (c)", "c_P3_diyagrami.png", "lightgreen")
    gecis_diyagrami_ciz(P100, "P^100 Olasilik Matrisi Diyagrami (c)", "c_P100_diyagrami.png", "salmon")


# --- d) Surecin teorik incelemesi -----------------------------------------
def sik_d_teorik_inceleme(P: np.ndarray) -> None:
    indirgenemez = bool((P > 0).all())
    kosegen = np.diag(P)
    yutucu_durumlar = [i + 1 for i in range(3) if np.isclose(kosegen[i], 1.0)]
    aperiodik = bool((kosegen > 0).all())

    print("\n--- d) Surecin Teorik Incelemesi ---")
    print("1. Indirgenebilirlik:")
    if indirgenemez:
        print("   Surec INDIRGENEMEZDIR (irreducible). P matrisindeki tum elemanlar sifirdan buyuk")
        print("   oldugundan her durumdan her duruma dogrudan gecis mumkundur; zincir tek bir")
        print("   iletisim sinifindan olusur.")
    else:
        print("   Surec indirgenebilirdir; birden fazla iletisim sinifi vardir.")

    print("2. Kapali Kume:")
    print("   Durum uzayinin tamami S = {1, 2, 3} tek bir kapali kumedir; icinden cikilamayan")
    print("   bir alt grup yoktur.")

    print("3. Yutucu Durum (absorbing state):")
    if yutucu_durumlar:
        print(f"   VARDIR: {yutucu_durumlar}")
    else:
        print(f"   YOKTUR. Yutuculuk icin P_ii = 1 gerekir; en yuksek kosegen deger {kosegen.max():.3f}.")

    print("4. Periyodiklik:")
    if aperiodik:
        print(f"   Surec APERIYODIKTIR (periyot = 1). Tum kosegen elemanlar P_ii > 0 "
              f"({', '.join(f'{d:.3f}' for d in kosegen)}).")
    else:
        print("   En az bir durum icin P_ii = 0; periyodiklik ayrica incelenmelidir.")

    if indirgenemez and aperiodik:
        print("Sonuc: Zincir indirgenemez ve aperiodik oldugundan ERGODIKTIR.")


# --- e) Denge (durağan) dagilimi ------------------------------------------
def sik_e_denge_dagilimi(P: np.ndarray) -> np.ndarray:
    """pi * P = pi ve sum(pi) = 1 sistemini en kucuk kareler ile cozer."""
    A = P.T - np.eye(3)
    A = np.append(A, [[1, 1, 1]], axis=0)
    b = np.array([0, 0, 0, 1])

    pi, *_ = np.linalg.lstsq(A, b, rcond=None)

    print("\n--- e) Denge Dagilimi ---")
    for i, deger in enumerate(pi, start=1):
        print(f"Durum {i} ({DURUM_ETIKET[i]:<9}) : {deger:.4f}  (%{deger * 100:.2f})")
    print(f"Kontrol toplami: {pi.sum():.4f}")
    return pi


# --- 2. SORU: Yutucu durumlu indirgenebilir zincir -------------------------
def soru_2() -> None:
    """S = {1,2,3,4}; 3 ve 4 yutucu, 1 ve 2 gecici durumlar."""
    P = np.array(
        [
            [0.2, 0.3, 0.4, 0.1],
            [0.5, 0.1, 0.2, 0.2],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ]
    )
    Q = P[:2, :2]  # Gecici -> Gecici
    R = P[:2, 2:]  # Gecici -> Yutucu

    print("\n\n=== 2. SORU ===")
    print("Tanimlanan bir-adim gecis matrisi P:")
    print(P)
    print("\nQ matrisi (Gecici -> Gecici):")
    print(Q)
    print("\nR matrisi (Gecici -> Yutucu):")
    print(R)

    N = np.linalg.inv(np.eye(2) - Q)  # Temel matris
    beklenen_sure = N.sum(axis=1)
    B = N @ R  # Yutulma olasiliklari

    print("\n--- Temel Matris N = (I - Q)^-1 ---")
    print(np.round(N, 4))

    print("\n--- Beklenen Yutulma Suresi ---")
    for i, sure in enumerate(beklenen_sure, start=1):
        print(f"Durum {i}'den baslayan bir surec ortalama {sure:.2f} adimda yutulmaktadir.")

    print("\n--- Yutulma Olasiliklari (B = N * R) ---")
    for i in range(2):
        print(f"Durum {i + 1}'den baslayan bir surecin:")
        print(f"  -> Durum 3'te yutulma olasiligi: %{B[i, 0] * 100:.2f}")
        print(f"  -> Durum 4'te yutulma olasiligi: %{B[i, 1] * 100:.2f}")


# --- Ana akis --------------------------------------------------------------
def main() -> None:
    FIGUR_DIZIN.mkdir(exist_ok=True)

    df = veriyi_hazirla(VERI_YOLU)
    print("=== 1. SORU ===")
    print(f"Gozlem sayisi          : {len(df)}")
    print(f"Zaman araligi          : {df['Tarih'].min():%d.%m.%Y} - {df['Tarih'].max():%d.%m.%Y}")
    print("Durum frekanslari      :")
    print(df["Durum"].value_counts().sort_index().rename(DURUM_ETIKET).to_string())

    sik_a_zaman_durum_grafigi(df)
    P = sik_b_gecis_matrisi(df)
    sik_c_matris_kuvvetleri(P)
    sik_d_teorik_inceleme(P)
    sik_e_denge_dagilimi(P)

    soru_2()


if __name__ == "__main__":
    main()
