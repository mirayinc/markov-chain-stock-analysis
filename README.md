# Markov Chain Analysis of Daily Stock Price Movements

**KONTR (Kontrolmatik Teknoloji A.Ş. / BİST) — Markov Zinciri ile Günlük Fiyat Hareketi Analizi**

🇹🇷 [Türkçe](#türkçe) · 🇬🇧 [English](#english)

---

<a name="türkçe"></a>

# 🇹🇷 Türkçe

## Proje Hakkında

Bu çalışmada, KONTR (Kontrolmatik Teknoloji A.Ş.) hisse senedinin günlük yüzdesel fiyat değişimleri **ayrık zamanlı, ayrık durumlu bir Markov Zinciri** olarak modellenmiştir.

Temel varsayım Markov özelliğidir: bir günkü piyasa durumu yalnızca bir önceki günün durumuna bağlıdır, daha eski geçmişten bağımsızdır.

Analiz kapsamında bir-adım geçiş matrisi, çok-adımlı geçiş olasılıkları, zincirin yapısal özellikleri (indirgenebilirlik, periyodiklik, yutuculuk) ve denge dağılımı hesaplanmakta; ayrıca yutucu durumlu ayrı bir zincir üzerinde yutulma olasılıkları ve beklenen yutulma süresi incelenmektedir.

## Durum Uzayı (S)

Günlük yüzdesel değişim (`Fark %`) üç duruma indirgenmiştir. %1'lik eşik, finans literatüründe yaygın bir ayrım noktasıdır; bu bandın altındaki hareketler "gürültü" kabul edilip yatay duruma dâhil edilmiştir.

| Durum | Tanım | Koşul |
|---|---|---|
| 1 | Düşüş | `Fark % < -1.0` |
| 2 | Yatay | `-1.0 ≤ Fark % ≤ +1.0` |
| 3 | Yükseliş | `Fark % > +1.0` |

**S = {1, 2, 3}**

Zaman parametresi ayrıktır ve her adım bir iş gününe karşılık gelir: **T = {1, 2, ..., n}**

## Veri

| | |
|---|---|
| Kaynak | [Investing.com – Kontrolmatik Teknoloji geçmiş verileri](https://tr.investing.com/equities/kontrolmatik-teknoloji-enerji-ve-mu-historical-data) |
| Zaman aralığı | 12.01.2026 – 10.04.2026 |
| Gözlem sayısı | 64 iş günü |
| Durum dağılımı | Düşüş: 23 · Yatay: 24 · Yükseliş: 17 |

## Kurulum ve Çalıştırma

```bash
git clone https://github.com/<mirayinc>/markov-chain-stock-analysis.git
cd markov-chain-stock-analysis

pip install -r requirements.txt
python markov_analysis.py
```

Script konsola tüm sayısal sonuçları yazar ve grafikleri `figures/` klasörüne kaydeder.

```
markov-chain-stock-analysis/
├── markov_analysis.py                 # Tüm analizin yapıldığı ana script
├── data/
│   └── KONTR_gecmis_verileri.csv      # Ham veri
├── figures/                           # Script tarafından üretilen grafikler
├── report/
│   └── rapor.docx                      # Yorumların yer aldığı tam rapor
├── requirements.txt
├── .gitignore
└── README.md
```

## Sonuçlar

### a) Zaman–Durum Grafiği

Zincir üç durum arasında sık geçiş yapmaktadır; ardışık günlerde aynı durum uzun süre korunmamaktadır. Yatay durum çoğunlukla düşüş ile yükseliş arasında bir **köprü durum** gibi davranmakta, uç durumlar arasında zaman zaman doğrudan geçişler de gözlenmektedir. Grafiğin düzensiz yapısı, kısa vadeli öngörülebilirliğin düşük olduğunu göstermektedir.

### b) Bir-Adım Geçiş Matrisi (P)

|  | 1 (Düşüş) | 2 (Yatay) | 3 (Yükseliş) |
|---|---|---|---|
| **1 (Düşüş)** | 0.391 | **0.478** | *0.130* |
| **2 (Yatay)** | 0.375 | 0.333 | 0.292 |
| **3 (Yükseliş)** | 0.250 | 0.313 | 0.438 |

- **En yüksek olasılık — P(1→2) = 0.478:** Düşüş yaşanan bir günün ardından hisse en yüksek olasılıkla yatay seyre geçmektedir. Piyasa sert düşüşlerin hemen ardından toparlanmak yerine önce sakinleşme eğilimindedir.
- **En düşük olasılık — P(1→3) = 0.130:** Düşüşten doğrudan yükselişe geçiş, yani ani "V dönüşü" hareketi bu hisse için oldukça nadirdir.
- **Kalıcılık:** En yüksek kendinde kalma olasılığı Yükseliş durumundadır (0.438); hisse yükseliş trendine girdiğinde bunu sürdürme eğilimi en kuvvetli olan durumdur.

### c) P³ ve P¹⁰⁰

**P³** matrisinde satırlar birbirine belirgin biçimde yakınsamıştır; başlangıç durumunun etkisi yalnızca üç adımda büyük ölçüde kaybolmaktadır (örneğin 1→3 geçişi tek adımda %13 iken üç adımda %26.9'a yükselir).

**P¹⁰⁰** matrisinin bütün satırları özdeştir — `[0.3461, 0.3777, 0.2761]`. Bu, zincirin **ergodik** olduğunu ve uzun vadede başlangıç durumundan tamamen bağımsız, tek bir kararlı dağılıma yakınsadığını göstermektedir.

### d) Yapısal İnceleme

| Özellik | Sonuç |
|---|---|
| İndirgenebilirlik | **İndirgenemez** (tüm P elemanları > 0, tek iletişim sınıfı) |
| Kapalı küme | Yalnızca S = {1,2,3}'ün kendisi |
| Yutucu durum | **Yoktur** (en yüksek köşegen değer 0.438 < 1) |
| Periyodiklik | **Yoktur — aperiyodik** (tüm Pᵢᵢ > 0) |

İndirgenemez + aperiyodik ⇒ zincir **ergodiktir**.

### e) Denge Dağılımı

`π·P = π` ve `Σπ = 1` sistemi en küçük kareler yöntemiyle çözülmüştür:

| Durum | π | Yüzde |
|---|---|---|
| 1 — Düşüş | 0.3461 | %34.61 |
| 2 — Yatay | 0.3777 | %37.77 |
| 3 — Yükseliş | 0.2761 | %27.61 |

Uzun vadede hisse zamanının en büyük kısmını (%37.77) yatay durumda geçirmektedir. Düşüş olasılığının yatay ile bu kadar yakın olması hissenin baskılı bir karakteri olduğuna işaret ederken, yükseliş %27.61 ile en az gerçekleşen durumdur. Sonuçlar P¹⁰⁰ matrisiyle birebir örtüşmektedir.

## Yutucu Durumlu İndirgenebilir Zincir

S = {1,2,3,4} için Durum 3 ve 4 yutucu, Durum 1 ve 2 geçici olacak şekilde tanımlanan matris:

|  | D1 | D2 | D3 | D4 |
|---|---|---|---|---|
| **D1** (geçici) | 0.2 | 0.3 | 0.4 | 0.1 |
| **D2** (geçici) | 0.5 | 0.1 | 0.2 | 0.2 |
| **D3** (yutucu) | 0.0 | 0.0 | 1.0 | 0.0 |
| **D4** (yutucu) | 0.0 | 0.0 | 0.0 | 1.0 |

Temel matris `N = (I − Q)⁻¹` ve yutulma olasılıkları `B = N·R` ile hesaplanmıştır.

| Başlangıç | Beklenen yutulma süresi | D3'te yutulma | D4'te yutulma |
|---|---|---|---|
| Durum 1 | 2.11 adım | %73.68 | %26.32 |
| Durum 2 | 2.28 adım | %63.16 | %36.84 |

Zincir **indirgenebilirdir**: {1,2} geçici sınıf, {3} ve {4} ise ayrı birer yutucu kapalı sınıf oluşturur. Durum 1'den başlandığında D3'e geçiş olasılığının daha yüksek olması (0.4) D3'ü baskın yutucu durum yaparken, Durum 2'nin dengeli geçişleri (0.2 / 0.2) D4'te yutulma şansını artırmaktadır.

## Kaynakça

- Investing.com — [Kontrolmatik Teknoloji Enerji ve Mühendislik A.Ş. geçmiş verileri](https://tr.investing.com/equities/kontrolmatik-teknoloji-enerji-ve-mu-historical-data)
- Özel Kadılar, Gamze. *Python ve R Uygulamaları ile Stokastik Süreçler.* Ankara: Seçkin Yayınları, 2. Baskı, 2023.

## Not

Bu depo bir ders çalışması kapsamında hazırlanmıştır. İçerdiği analiz ve yorumlar **yatırım tavsiyesi değildir**; yalnızca eğitim amaçlıdır.

---

<a name="english"></a>

# 🇬🇧 English

## About

This project models the daily percentage price movements of the KONTR (Kontrolmatik Teknoloji A.Ş., Borsa İstanbul) stock as a **discrete-time, discrete-state Markov chain**.

The core assumption is the Markov property: the market state on a given day depends only on the previous day's state and is independent of earlier history.

The analysis computes the one-step transition matrix, multi-step transition probabilities, the chain's structural properties (irreducibility, periodicity, absorption) and the stationary distribution. A separate absorbing chain is also examined for absorption probabilities and expected time to absorption.

## State Space (S)

Daily percentage change is discretised into three states. The 1% threshold is a common cut-off in the finance literature; movements inside that band are treated as noise and assigned to the flat state.

| State | Label | Condition |
|---|---|---|
| 1 | Decline | `Change % < -1.0` |
| 2 | Flat | `-1.0 ≤ Change % ≤ +1.0` |
| 3 | Rise | `Change % > +1.0` |

**S = {1, 2, 3}**

The time parameter is discrete, each step corresponding to one trading day: **T = {1, 2, ..., n}**

## Data

| | |
|---|---|
| Source | [Investing.com – Kontrolmatik Teknoloji historical data](https://tr.investing.com/equities/kontrolmatik-teknoloji-enerji-ve-mu-historical-data) |
| Period | 12.01.2026 – 10.04.2026 |
| Observations | 64 trading days |
| State counts | Decline: 23 · Flat: 24 · Rise: 17 |

## Installation and Usage

```bash
git clone https://github.com/<mirayinc>/markov-chain-stock-analysis.git
cd markov-chain-stock-analysis

pip install -r requirements.txt
python markov_analysis.py
```

The script prints all numerical results to the console and saves the plots into `figures/`.

```
markov-chain-stock-analysis/
├── markov_analysis.py                 # Main analysis script
├── data/
│   └── KONTR_gecmis_verileri.csv      # Raw data
├── figures/                           # Plots generated by the script
├── report/
│   └── rapor.docx                      # Full write-up (in Turkish)
├── requirements.txt
├── .gitignore
└── README.md
```

## Results

### a) Time–State Plot

The chain switches between the three states frequently; the same state rarely persists over consecutive days. The flat state largely acts as a **bridge** between decline and rise, though direct transitions between the extreme states do occur. The irregular shape of the plot indicates low short-term predictability.

### b) One-Step Transition Matrix (P)

|  | 1 (Decline) | 2 (Flat) | 3 (Rise) |
|---|---|---|---|
| **1 (Decline)** | 0.391 | **0.478** | *0.130* |
| **2 (Flat)** | 0.375 | 0.333 | 0.292 |
| **3 (Rise)** | 0.250 | 0.313 | 0.438 |

- **Highest probability — P(1→2) = 0.478:** After a declining day, the stock most likely moves sideways. The market tends to settle down before recovering rather than rebounding immediately.
- **Lowest probability — P(1→3) = 0.130:** A direct move from decline to rise — a sharp "V-shaped" reversal — is rare for this stock.
- **Persistence:** The highest self-transition probability belongs to the rise state (0.438), meaning an upward trend is the most likely one to be sustained.

### c) P³ and P¹⁰⁰

In **P³** the rows have already converged noticeably: the influence of the initial state largely disappears within three steps (the 1→3 transition rises from 13% in one step to 26.9% in three).

All rows of **P¹⁰⁰** are identical — `[0.3461, 0.3777, 0.2761]` — showing that the chain is **ergodic** and converges to a single stationary distribution regardless of the starting state.

### d) Structural Properties

| Property | Result |
|---|---|
| Irreducibility | **Irreducible** (all entries of P > 0, single communicating class) |
| Closed set | Only S = {1,2,3} itself |
| Absorbing state | **None** (largest diagonal entry 0.438 < 1) |
| Periodicity | **None — aperiodic** (all Pᵢᵢ > 0) |

Irreducible + aperiodic ⇒ the chain is **ergodic**.

### e) Stationary Distribution

The system `π·P = π` with `Σπ = 1` is solved via least squares:

| State | π | Percentage |
|---|---|---|
| 1 — Decline | 0.3461 | 34.61% |
| 2 — Flat | 0.3777 | 37.77% |
| 3 — Rise | 0.2761 | 27.61% |

In the long run the stock spends most of its time (37.77%) in the flat state. The decline probability being nearly as high points to a subdued long-run character, while rise is the least frequent state at 27.61%. These figures match the P¹⁰⁰ matrix exactly.

## Reducible Chain with Absorbing States

For S = {1,2,3,4}, states 3 and 4 are absorbing and states 1 and 2 are transient:

|  | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| **S1** (transient) | 0.2 | 0.3 | 0.4 | 0.1 |
| **S2** (transient) | 0.5 | 0.1 | 0.2 | 0.2 |
| **S3** (absorbing) | 0.0 | 0.0 | 1.0 | 0.0 |
| **S4** (absorbing) | 0.0 | 0.0 | 0.0 | 1.0 |

The fundamental matrix `N = (I − Q)⁻¹` and absorption probabilities `B = N·R` give:

| Start | Expected steps to absorption | Absorbed in S3 | Absorbed in S4 |
|---|---|---|---|
| State 1 | 2.11 | 73.68% | 26.32% |
| State 2 | 2.28 | 63.16% | 36.84% |

The chain is **reducible**: {1,2} forms a transient class while {3} and {4} are separate absorbing closed classes. Starting from state 1, the higher transition probability into S3 (0.4) makes it the dominant absorbing state, whereas state 2's balanced transitions (0.2 / 0.2) raise the chance of absorption in S4.

## References

- Investing.com — [Kontrolmatik Teknoloji Enerji ve Mühendislik A.Ş. historical data](https://tr.investing.com/equities/kontrolmatik-teknoloji-enerji-ve-mu-historical-data)
- Özel Kadılar, Gamze. *Stochastic Processes with Python and R Applications.* Ankara: Seçkin Publishing, 2nd ed., 2023.

## Disclaimer

This repository was produced as coursework. The analysis and commentary are **not investment advice** and are provided for educational purposes only.
