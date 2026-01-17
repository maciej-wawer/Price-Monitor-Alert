# Price Monitor

**Inteligentny monitor kursów finansowych z alertami audio-wizualnymi**

Monitor kursów kryptowalut i walut forex z automatycznymi alertami dźwiękowymi i wizualnymi. Otrzymaj natychmiastowe powiadomienie gdy cena osiągnie ustawiony próg.

---

## ✨ Funkcje

- **📊 10 kryptowalut** - BTC, ETH, XRP, ADA, SOL, DOGE, USDT, USDC, BNB, XLM
- **💱 Forex** - Wszystkie pary walutowe (EUR/USD, GBP/USD, itp.)
- **🔊 Alerty dźwiękowe** - Natychmiast powiadamia o zmianach
- **📈 Alerty wizualne** - Kolorowe panele (zielone/czerwone)
- **⚙️ Oddzielne progi** - Inne dla wzrostu, inne dla spadku
- **📱 Historia cen** - Śledzenie historii każdego instrumentu
- **🎚️ 6 szablonów dźwięków** - Alarm, Syrena, Dzwonek, Muzyka, Cichy
- **💾 Automatyczne zapisywanie** - Brak utraty danych
- **🎨 Nowoczesny interfejs** - Kolorowy, łatwy w obsłudze

---

## 🛠️ Instalacja (2 minuty)

### Wymagania
- Python 3.7+ (https://www.python.org/downloads/)
- Windows

### Kroki

**1. Otwórz terminal w folderze projektu**

**2. Zainstaluj pakiety:**
```bash
pip install -r requirements.txt
```

**3. Uruchom program:**
```bash
python price_monitor.py
```

---

## 📖 Poradnik szybkiego startu

### Dodaj instrument do monitorowania

```
Wybierz: 1 (Dodaj instrument)
Symbol: BTC
Typ: crypto
Próg wzrostu: 5     ← Alert gdy +5%
Próg spadku: 3      ← Alert gdy -3%
```

### Pobierz aktualne ceny

```
Wybierz: 5 (Pobierz ceny wszystkich)
Program pobierze ceny wszystkich instrumentów
```

### Włącz monitoring

```
Wybierz: 7 (Monitoring live)
Program pracuje w tle
CTRL+C aby zatrzymać
```

### Kiedy przychodzi alert

```
📈 ALERT WZROSTU: BTC
Zmiana: +5.22%
$45,000.00 → $47,350.00
🔊 BEEEP BEEEP! (dźwięk wysoki)
```

---

## 📋 Menu

| Opcja | Funkcja |
|-------|---------|
| 1 | Dodaj instrument |
| 2 | Wyświetl wszystkie |
| 3 | Usuń instrument |
| 4 | Szczegóły i historia |
| 5 | Pobierz ceny ręcznie |
| 6 | Test (5 iteracji) |
| 7 | **Monitoring live** ⭐ |
| 8 | Test alarmu |
| 9 | Ustawienia |
| 0 | Wyjście |

---

## 🎚️ Ustawienia dźwięków

**Szybkie szablony:**
```
Ustawienia → Szablony

1. Alarm - tradycyjny
2. Syrena - głośny
3. Dzwonek - miły
4. Muzyka - melodyjny
5. Cichy - łagodny
```

**Własne ustawienia:**
```
Ustawienia → Zmień dźwięk (Hz)
Podaj częstotliwość: 1000-3000 Hz
```

---

## 💡 Praktyczne scenariusze

### Scenario 1: Inwestor kryptowalut
```
1. Dodaj BTC (próg: 5%)
2. Dodaj ETH (próg: 3%)
3. Uruchom monitoring live
4. Pracuj spokojnie - program Cię powiadomi
```

### Scenario 2: Trader forexu
```
1. Dodaj EUR/USD (próg: 2%)
2. Dodaj GBP/USD (próg: 1.5%)
3. Test alert
4. Monitoring live
```

### Scenario 3: Portfel mieszany
```
1. 3 kryptowaluty
2. 2 pary forex
3. Różne progi dla każdej
4. Monitoring 24/7
```

---

## 🔐 Dane

- ✅ Wszystkie dane przechowywane **lokalnie**
- ✅ Brak przesyłania do chmury
- ✅ Tylko pobieranie cen z publicznych API
- ✅ Pliki: `monitor_config.json`, `price_data.json`

---

## 🌐 Obsługiwane instrumenty

**Kryptowaluty (10):**
```
BTC, ETH, XRP, ADA, SOL, DOGE, USDT, USDC, BNB, XLM
```

**Forex - wszystkie pary:**
```
EUR/USD, GBP/USD, JPY/USD, AUD/USD, CAD/USD, CHF/USD,
PLN/USD, CZK/USD, HUF/USD i wiele innych
```

---

## ⚠️ Uwagi

- Program wymaga **Windows** (ze względu na `winsound`)
- API ma limity: ~50 req/minutę (CoinGecko)
- Minimalna częstotliwość dźwięku: 100 Hz
- Maksymalna częstotliwość dźwięku: 10000 Hz
- Interwał monitoringu: minimum 1 sekunda

---

## 🆘 Problemy?

**Program nie startuje:**
- Upewnij się, że Python 3.7+ jest zainstalowany
- Sprawdź, czy pakiety są zainstalowane: `pip install -r requirements.txt`

**Brak dźwięku:**
- Sprawdź ustawienia (Opcja 9)
- Włącz dźwięk (Opcja 1)
- Przetestuj alert (Opcja 8)

**API error:**
- Połączenie z internetem OK?
- Czekaj, API ma limity

---

## 📞 Informacje

**Wersja:** 1.0  
**Data:** 2026-01-17  
**Licencja:** Proprietary  
**System:** Windows (Python 3.7+)

---

**Gotowy do pracy! 🚀**
