#!/usr/bin/env python3
"""
Price Monitor Pro - Monitor Kursów z Alertami Audio-Wizualnymi
"""

import requests
import json
import os
import time
import winsound
from datetime import datetime
from typing import Dict, List, Optional
from colorama import Fore, Back, Style, init
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.align import Align

init(autoreset=True)
console = Console()

class PriceMonitorPro:
    def __init__(self):
        self.config_file = "monitor_config.json"
        self.data_file = "price_data.json"
        self.config = self.load_config()
        self.monitored_assets = []
        self.price_history = {}
        self.load_data()
        
        self.api_sources = {
            'crypto': 'https://api.coingecko.com/api/v3/simple/price',
            'forex': 'https://api.exchangerate-api.com/v4/latest/'
        }
    
    def load_config(self) -> Dict:
        """Ładuje konfigurację"""
        default_config = {
            "alert_threshold_percent": 5,
            "check_interval_seconds": 60,
            "sound_enabled": True,
            "sound_volume": 1000,
            "sound_frequency": 1000
        }
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                # Merge z defaults - dodaj brakujące klucze
                config = {**default_config, **loaded}
                self.save_config(config)
                return config
        
        self.save_config(default_config)
        return default_config
    
    def save_config(self, config: Dict) -> None:
        """Zapisuje konfigurację"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def load_data(self) -> None:
        """Ładuje dane monitorowanych aktywów"""
        if os.path.exists(self.data_file):
            try:
                data = json.load(open(self.data_file, 'r', encoding='utf-8'))
                self.monitored_assets = data.get('monitored_assets', [])
                self.price_history = data.get('price_history', {})
                
                # Migracja danych
                for asset in self.monitored_assets:
                    if 'alert_change' in asset and 'alert_up' not in asset:
                        asset['alert_up'] = asset.pop('alert_change')
                        asset['alert_down'] = asset['alert_up']
                        asset['last_alert_up'] = asset.pop('last_alert', None)
                        asset['last_alert_down'] = None
                
                self.save_data()
            except json.JSONDecodeError:
                pass
    
    def save_data(self) -> None:
        """Zapisuje dane"""
        data = {
            'monitored_assets': self.monitored_assets,
            'price_history': self.price_history
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def play_alert_sound(self, alert_type: str = "up") -> None:
        """Odgrywa dźwięk alarmu"""
        if not self.config['sound_enabled']:
            return
        
        try:
            freq_up = self.config.get('frequency_up', 1500)
            freq_down = self.config.get('frequency_down', 800)
            
            if alert_type == "up":
                console.print("[bold yellow]🔊 Dźwięk alert wzrostu...[/bold yellow]")
                winsound.Beep(freq_up, 500)
                time.sleep(0.1)
                winsound.Beep(freq_up, 500)
            else:
                console.print("[bold yellow]🔊 Dźwięk alert spadku...[/bold yellow]")
                winsound.Beep(freq_down, 500)
                time.sleep(0.1)
                winsound.Beep(freq_down, 500)
        except Exception as e:
            console.print(f"[red]Błąd dźwięku: {str(e)}[/red]")
    
    def show_alert_popup(self, symbol: str, old_price: float, current_price: float, change_percent: float, alert_type: str) -> None:
        """Wyświetla wizualny alert na ekranie"""
        if alert_type == "up":
            title = f"📈 ALERT WZROSTU: {symbol}"
            color = "green"
            emoji = "📈"
        else:
            title = f"📉 ALERT SPADKU: {symbol}"
            color = "red"
            emoji = "📉"
        
        alert_text = f"""
{emoji} {symbol}
━━━━━━━━━━━━━━━━━━━━━
Zmiana: [bold]{change_percent:+.2f}%[/bold]
${old_price:.4f} → ${current_price:.4f}
Czas: {datetime.now().strftime('%H:%M:%S')}
"""
        
        panel = Panel(
            alert_text,
            title=title,
            border_style=color,
            expand=False,
            padding=(1, 2)
        )
        
        console.print(Align.center(panel))
    
    def add_asset(self, symbol: str, asset_type: str, alert_up: Optional[float] = None, alert_down: Optional[float] = None) -> None:
        """Dodaje aktywo do monitorowania"""
        for asset in self.monitored_assets:
            if asset['symbol'].upper() == symbol.upper():
                console.print(f"[red]✗[/red] Aktywo {symbol} już monitorujesz")
                return
        
        default_threshold = self.config['alert_threshold_percent']
        
        new_asset = {
            'id': len(self.monitored_assets) + 1,
            'symbol': symbol.upper(),
            'type': asset_type.lower(),
            'alert_up': alert_up or default_threshold,
            'alert_down': alert_down or default_threshold,
            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'enabled': True,
            'last_price': None,
            'last_alert_up': None,
            'last_alert_down': None
        }
        
        self.monitored_assets.append(new_asset)
        self.price_history[symbol.upper()] = []
        self.save_data()
        console.print(f"[green]✓[/green] Dodano do monitorowania: [bold]{symbol.upper()}[/bold]")
    
    def remove_asset(self, asset_id: int) -> None:
        """Usuwa aktywo z monitorowania"""
        for i, asset in enumerate(self.monitored_assets):
            if asset['id'] == asset_id:
                removed = self.monitored_assets.pop(i)
                self.save_data()
                console.print(f"[green]✓[/green] Usunięto: [bold]{removed['symbol']}[/bold]")
                return
        console.print(f"[red]✗[/red] Aktywo o ID {asset_id} nie znalezione")
    
    def get_crypto_price(self, symbol: str) -> Optional[float]:
        """Pobiera cenę kryptowaluty"""
        try:
            crypto_ids = {
                'BTC': 'bitcoin', 'ETH': 'ethereum', 'XRP': 'ripple',
                'ADA': 'cardano', 'SOL': 'solana', 'DOGE': 'dogecoin',
                'USDT': 'tether', 'USDC': 'usd-coin', 'BNB': 'binancecoin', 'XLM': 'stellar',
            }
            
            crypto_id = crypto_ids.get(symbol.upper())
            if not crypto_id:
                return None
            
            params = {'ids': crypto_id, 'vs_currencies': 'usd', 'include_market_cap': 'true'}
            
            for attempt in range(3):
                try:
                    response = requests.get(self.api_sources['crypto'], params=params, timeout=5)
                    response.raise_for_status()
                    data = response.json()
                    return data[crypto_id]['usd']
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:
                        wait = (attempt + 1) * 2
                        console.print(f"[yellow]⏳ API limit, czekam {wait}s...[/yellow]")
                        time.sleep(wait)
        except Exception as e:
            pass
        
        return None
    
    def get_forex_price(self, symbol: str) -> Optional[float]:
        """Pobiera kurs walutowy"""
        try:
            if '/' not in symbol:
                return None
            
            base, quote = symbol.split('/')
            response = requests.get(f"{self.api_sources['forex']}{base.upper()}", timeout=5)
            response.raise_for_status()
            data = response.json()
            return data['rates'].get(quote.upper())
        except Exception:
            pass
        
        return None
    
    def get_price(self, symbol: str, asset_type: str) -> Optional[float]:
        """Pobiera cenę instrumentu"""
        if asset_type.lower() == 'crypto':
            return self.get_crypto_price(symbol)
        elif asset_type.lower() == 'forex':
            return self.get_forex_price(symbol)
        return None
    
    def check_price_change(self, asset: Dict, current_price: float) -> None:
        """Sprawdza czy cena zmieniła się i uruchamia alert"""
        symbol = asset['symbol']
        
        if asset['last_price'] is None:
            asset['last_price'] = current_price
            return
        
        old_price = asset['last_price']
        change_percent = ((current_price - old_price) / old_price) * 100
        
        # Alert wzrostu - sprawdza czy zmiana >= progu I czy nie było alerty w ostatnich 30 sekundach
        if change_percent >= asset['alert_up']:
            last_alert = asset.get('last_alert_up')
            if last_alert is None or (datetime.now() - datetime.strptime(last_alert, "%Y-%m-%d %H:%M:%S")).total_seconds() > 30:
                self.show_alert_popup(symbol, old_price, current_price, change_percent, "up")
                self.play_alert_sound("up")
                asset['last_alert_up'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Alert spadku - sprawdza czy zmiana <= -progu I czy nie było alerty w ostatnich 30 sekundach
        elif change_percent <= -asset['alert_down']:
            last_alert = asset.get('last_alert_down')
            if last_alert is None or (datetime.now() - datetime.strptime(last_alert, "%Y-%m-%d %H:%M:%S")).total_seconds() > 30:
                self.show_alert_popup(symbol, old_price, current_price, change_percent, "down")
                self.play_alert_sound("down")
                asset['last_alert_down'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        asset['last_price'] = current_price
    
    def list_assets(self) -> None:
        """Wyświetla listę aktywów"""
        if not self.monitored_assets:
            console.print("[yellow]Brak monitorowanych aktywów[/yellow]")
            return
        
        table = Table(title="Monitorowane Instrumenty")
        table.add_column("ID", style="cyan")
        table.add_column("Symbol", style="bold magenta")
        table.add_column("Typ", style="green")
        table.add_column("Cena", style="yellow")
        table.add_column("Wzrost %", style="cyan")
        table.add_column("Spadek %", style="cyan")
        table.add_column("Status", style="blue")
        
        for asset in self.monitored_assets:
            price_str = f"${asset['last_price']:.2f}" if asset['last_price'] else "N/A"
            status = "✓ Aktywny" if asset['enabled'] else "✗ Wyłączony"
            
            table.add_row(
                str(asset['id']),
                asset['symbol'],
                asset['type'],
                price_str,
                str(asset['alert_up']),
                str(asset['alert_down']),
                status
            )
        
        console.print(table)
    
    def show_asset_details(self, asset_id: int) -> None:
        """Wyświetla szczegóły aktywu"""
        for asset in self.monitored_assets:
            if asset['id'] == asset_id:
                console.print(f"\n[bold cyan]═══════════════════════════[/bold cyan]")
                console.print(f"[bold]Symbol:[/bold] {asset['symbol']}")
                console.print(f"[bold]Typ:[/bold] {asset['type']}")
                console.print(f"[bold]Próg wzrostu:[/bold] [green]{asset['alert_up']}%[/green]")
                console.print(f"[bold]Próg spadku:[/bold] [red]{asset['alert_down']}%[/red]")
                console.print(f"[bold]Aktualna cena:[/bold] [yellow]${asset['last_price']:.4f}[/yellow]" if asset['last_price'] else "[red]Brak danych[/red]")
                console.print(f"[bold]Ostatni alert wzrostu:[/bold] {asset['last_alert_up'] or 'Brak'}")
                console.print(f"[bold]Ostatni alert spadku:[/bold] {asset['last_alert_down'] or 'Brak'}")
                console.print(f"[bold]Data dodania:[/bold] {asset['date_added']}")
                
                if asset['symbol'] in self.price_history and self.price_history[asset['symbol']]:
                    prices = self.price_history[asset['symbol']][-10:]
                    console.print(f"\n[bold]Historia cen (ostatnie 10):[/bold]")
                    for i, record in enumerate(prices, 1):
                        console.print(f"  {i}. ${record['price']:.4f} - {record['timestamp']}")
                
                console.print(f"[bold cyan]═══════════════════════════\n[/bold cyan]")
                return
        
        console.print(f"[red]✗ Aktywo o ID {asset_id} nie znalezione[/red]")
    
    def fetch_all_prices(self) -> None:
        """Pobiera ceny wszystkich aktywów"""
        console.print("\n[bold cyan]🔄 Sprawdzam ceny wszystkich instrumentów...[/bold cyan]\n")
        
        for i, asset in enumerate(self.monitored_assets):
            if not asset['enabled']:
                console.print(f"[yellow]⊘[/yellow] {asset['symbol']}: Wyłączony")
                continue
            
            price = self.get_price(asset['symbol'], asset['type'])
            if price:
                self.check_price_change(asset, price)
                console.print(f"[green]✓[/green] {asset['symbol']}: [bold yellow]${price:.4f}[/bold yellow]")
                
                if asset['symbol'] not in self.price_history:
                    self.price_history[asset['symbol']] = []
                
                self.price_history[asset['symbol']].append({
                    'price': price,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                console.print(f"[red]✗[/red] {asset['symbol']}: Błąd pobierania")
            
            if i < len(self.monitored_assets) - 1:
                time.sleep(1)
        
        self.save_data()
        
        self.save_data()
        console.print("\n[green]✓ Dane zaktualizowane[/green]\n")
    
    def monitor_prices(self, iterations: Optional[int] = None) -> None:
        """Monitoruje ceny w pętli"""
        iteration = 0
        
        try:
            while True:
                if iterations and iteration >= iterations:
                    break
                
                console.print(f"\n[cyan]⏱️  Sprawdzanie cen... ({datetime.now().strftime('%H:%M:%S')})[/cyan]")
                self.fetch_all_prices()
                
                if iterations and iteration >= iterations - 1:
                    break
                
                iteration += 1
                console.print(f"[dim]Następne sprawdzenie za {self.config['check_interval_seconds']} sekund... (CTRL+C aby zatrzymać)[/dim]")
                time.sleep(self.config['check_interval_seconds'])
        
        except KeyboardInterrupt:
            console.print("\n[green]✓ Monitoring zatrzymany[/green]")

def display_main_menu():
    """Wyświetla menu główne"""
    console.clear()
    console.print("[bold cyan]╔══════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║  PRICE MONITOR PRO - Alert Audio     ║[/bold cyan]")
    console.print("[bold cyan]╚══════════════════════════════════════╝[/bold cyan]\n")
    console.print("[bold green]1.[/bold green] Dodaj instrument do monitorowania")
    console.print("[bold green]2.[/bold green] Wyświetl monitorowane instrumenty")
    console.print("[bold green]3.[/bold green] Usuń instrument")
    console.print("[bold green]4.[/bold green] Szczegóły instrumentu")
    console.print("[bold green]5.[/bold green] Pobierz ceny wszystkich")
    console.print("[bold green]6.[/bold green] Monitoring testowy (5 iteracji)")
    console.print("[bold green]7.[/bold green] Monitoring live")
    console.print("[bold green]8.[/bold green] Test alert (dźwięk + ekran)")
    console.print("[bold green]9.[/bold green] Ustawienia")
    console.print("[bold green]0.[/bold green] Wyjście\n")
    console.print("[dim]─" * 40 + "[/dim]")

def settings_menu(monitor: PriceMonitorPro):
    """Menu ustawień"""
    while True:
        console.print("\n[bold cyan]--- Ustawienia ---[/bold cyan]\n")
        console.print(f"[bold]Dźwięk alertów:[/bold] [green]Włączony[/green]" if monitor.config['sound_enabled'] else "[red]Wyłączony[/red]")
        console.print(f"[bold]Interwał sprawdzania:[/bold] {monitor.config['check_interval_seconds']}s")
        console.print(f"[bold]Domyślny próg alertu:[/bold] {monitor.config['alert_threshold_percent']}%")
        console.print(f"[bold]Częstotliwość wzrostu:[/bold] {monitor.config.get('frequency_up', 1500)} Hz")
        console.print(f"[bold]Częstotliwość spadku:[/bold] {monitor.config.get('frequency_down', 800)} Hz\n")
        
        console.print("[bold green]1.[/bold green] Włącz/Wyłącz dźwięk")
        console.print("[bold green]2.[/bold green] Zmień interwał sprawdzania")
        console.print("[bold green]3.[/bold green] Zmień domyślny próg alertu")
        console.print("[bold green]4.[/bold green] Zmień dźwięk alertu wzrostu")
        console.print("[bold green]5.[/bold green] Zmień dźwięk alertu spadku")
        console.print("[bold green]6.[/bold green] Szablony dźwięków")
        console.print("[bold green]0.[/bold green] Powrót\n")
        
        choice = console.input("[bold cyan]Wybierz opcję:[/bold cyan] ").strip()
        
        if choice == "1":
            monitor.config['sound_enabled'] = not monitor.config['sound_enabled']
            status = "Włączony" if monitor.config['sound_enabled'] else "Wyłączony"
            console.print(f"\n[green]✓ Dźwięk {status}[/green]")
            monitor.save_config(monitor.config)
        
        elif choice == "2":
            try:
                interval = int(console.input("Interwał w sekundach: ").strip())
                monitor.config['check_interval_seconds'] = interval
                console.print(f"[green]✓ Interwał zmieniony na {interval}s[/green]")
                monitor.save_config(monitor.config)
            except ValueError:
                console.print("[red]✗ Błędna wartość[/red]")
        
        elif choice == "3":
            try:
                threshold = float(console.input("Domyślny próg (%): ").strip())
                monitor.config['alert_threshold_percent'] = threshold
                console.print(f"[green]✓ Próg zmieniony na {threshold}%[/green]")
                monitor.save_config(monitor.config)
            except ValueError:
                console.print("[red]✗ Błędna wartość[/red]")
        
        elif choice == "4":
            try:
                freq = int(console.input("Częstotliwość Hz (100-10000) [1500]: ").strip() or "1500")
                if 100 <= freq <= 10000:
                    monitor.config['frequency_up'] = freq
                    console.print(f"[green]✓ Testowanie nowego dźwięku...[/green]")
                    winsound.Beep(freq, 500)
                    console.print(f"[green]✓ Dźwięk wzrostu zmieniony na {freq} Hz[/green]")
                    monitor.save_config(monitor.config)
                else:
                    console.print("[red]✗ Częstotliwość musi być pomiędzy 100-10000 Hz[/red]")
            except ValueError:
                console.print("[red]✗ Błędna wartość[/red]")
        
        elif choice == "5":
            try:
                freq = int(console.input("Częstotliwość Hz (100-10000) [800]: ").strip() or "800")
                if 100 <= freq <= 10000:
                    monitor.config['frequency_down'] = freq
                    console.print(f"[green]✓ Testowanie nowego dźwięku...[/green]")
                    winsound.Beep(freq, 500)
                    console.print(f"[green]✓ Dźwięk spadku zmieniony na {freq} Hz[/green]")
                    monitor.save_config(monitor.config)
                else:
                    console.print("[red]✗ Częstotliwość musi być pomiędzy 100-10000 Hz[/red]")
            except ValueError:
                console.print("[red]✗ Błędna wartość[/red]")
        
        elif choice == "6":
            console.print("\n[bold cyan]--- Szablony Dźwięków ---[/bold cyan]\n")
            console.print("[bold green]1.[/bold green] Alarm (wysoki 2000 Hz / niski 500 Hz)")
            console.print("[bold green]2.[/bold green] Syrena (wysoki 3000 Hz / niski 800 Hz)")
            console.print("[bold green]3.[/bold green] Dzwonek (wysoki 1000 Hz / niski 600 Hz)")
            console.print("[bold green]4.[/bold green] Muzyka (wysoki 523 Hz / niski 261 Hz)")
            console.print("[bold green]5.[/bold green] Cichy (wysoki 1500 Hz / niski 800 Hz)")
            console.print("[bold green]0.[/bold green] Powrót\n")
            
            template = console.input("[bold cyan]Wybierz szablon:[/bold cyan] ").strip()
            
            templates = {
                "1": {"up": 2000, "down": 500, "name": "Alarm"},
                "2": {"up": 3000, "down": 800, "name": "Syrena"},
                "3": {"up": 1000, "down": 600, "name": "Dzwonek"},
                "4": {"up": 523, "down": 261, "name": "Muzyka"},
                "5": {"up": 1500, "down": 800, "name": "Cichy"}
            }
            
            if template in templates:
                console.print(f"\n[yellow]🧪 Testowanie szablonu: {templates[template]['name']}...[/yellow]\n")
                
                console.print("[green]Dźwięk wzrostu:[/green]")
                winsound.Beep(templates[template]['up'], 500)
                time.sleep(0.2)
                
                console.print("[red]Dźwięk spadku:[/red]")
                winsound.Beep(templates[template]['down'], 500)
                
                confirm = console.input("\n[bold cyan]Zastosować ten szablon? (t/n):[/bold cyan] ").strip().lower()
                if confirm == 't':
                    monitor.config['frequency_up'] = templates[template]['up']
                    monitor.config['frequency_down'] = templates[template]['down']
                    monitor.save_config(monitor.config)
                    console.print(f"[green]✓ Szablon {templates[template]['name']} zastosowany![/green]")
                else:
                    console.print("[yellow]Anulowano[/yellow]")
            elif template == "0":
                break
            else:
                console.print("[red]✗ Nieznana opcja[/red]")
        
        elif choice == "0":
            break
        
        else:
            console.print("[red]✗ Nieznana opcja[/red]")
        
        console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")

def test_alert(monitor: PriceMonitorPro):
    """Wysyła testowy alert"""
    while True:
        console.print("\n[bold cyan]--- Test Alert ---[/bold cyan]\n")
        
        console.print("[bold green]1.[/bold green] Test wzrostu")
        console.print("[bold green]2.[/bold green] Test spadku")
        console.print("[bold green]0.[/bold green] Powrót\n")
        
        choice = console.input("[bold cyan]Wybierz opcję:[/bold cyan] ").strip()
        
        if choice == "1":
            console.print("\n[yellow]🧪 Uruchamiam test alert wzrostu...[/yellow]\n")
            monitor.show_alert_popup("BTC", 45000, 47350, 5.22, "up")
            monitor.play_alert_sound("up")
        
        elif choice == "2":
            console.print("\n[yellow]🧪 Uruchamiam test alert spadku...[/yellow]\n")
            monitor.show_alert_popup("ETH", 2500, 2425, -3.00, "down")
            monitor.play_alert_sound("down")
        
        elif choice == "0":
            break
        
        else:
            console.print("[red]✗ Nieznana opcja[/red]")
        
        console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")

def main():
    monitor = PriceMonitorPro()
    
    while True:
        display_main_menu()
        choice = console.input("[bold cyan]Wybierz opcję:[/bold cyan] ").strip()
        
        if choice == "1":
            console.print("\n[bold cyan]--- Dodaj instrument ---[/bold cyan]")
            console.print("[dim]Crypto: BTC, ETH, XRP, ADA, SOL, DOGE, USDT, USDC, BNB, XLM[/dim]")
            console.print("[dim]Forex: EUR/USD, GBP/USD, JPY/USD, itp.[/dim]\n")
            
            symbol = console.input("[bold]Symbol:[/bold] ").strip()
            asset_type = console.input("[bold]Typ (crypto/forex):[/bold] ").strip()
            alert_up = console.input("[bold]Próg wzrostu % [5]:[/bold] ").strip()
            alert_down = console.input("[bold]Próg spadku % [5]:[/bold] ").strip()
            
            if symbol and asset_type:
                alert_up_val = float(alert_up) if alert_up else None
                alert_down_val = float(alert_down) if alert_down else None
                monitor.add_asset(symbol, asset_type, alert_up_val, alert_down_val)
            else:
                console.print("[red]✗ Symbol i typ są wymagane![/red]")
            console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")
        
        elif choice == "2":
            console.print()
            monitor.list_assets()
            console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")
        
        elif choice == "3":
            console.print()
            monitor.list_assets()
            try:
                asset_id = int(console.input("\n[bold]Podaj ID instrumentu do usunięcia:[/bold] ").strip())
                monitor.remove_asset(asset_id)
            except ValueError:
                console.print("[red]✗ Błędny ID[/red]")
            console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")
        
        elif choice == "4":
            console.print()
            monitor.list_assets()
            try:
                asset_id = int(console.input("\n[bold]Podaj ID instrumentu:[/bold] ").strip())
                monitor.show_asset_details(asset_id)
            except ValueError:
                console.print("[red]✗ Błędny ID[/red]")
            console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")
        
        elif choice == "5":
            console.print()
            monitor.fetch_all_prices()
            console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")
        
        elif choice == "6":
            console.print("\n[bold cyan]🧪 Monitoring testowy (5 iteracji)...[/bold cyan]")
            monitor.monitor_prices(iterations=5)
            console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")
        
        elif choice == "7":
            console.print("\n[bold green]🚀 Monitoring uruchomiony (CTRL+C aby zatrzymać)[/bold green]")
            try:
                monitor.monitor_prices()
            except KeyboardInterrupt:
                console.print("\n[yellow]Monitoring wstrzymany[/yellow]")
            console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")
        
        elif choice == "8":
            test_alert(monitor)
            console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")
        
        elif choice == "9":
            settings_menu(monitor)
        
        elif choice == "0":
            console.print("[bold yellow]Do widzenia![/bold yellow]")
            break
        
        else:
            console.print("[red]✗ Nieznana opcja[/red]")
            console.input("\n[dim]Naciśnij Enter aby kontynuować...[/dim]")

if __name__ == "__main__":
    main()
