from utils.fundamental_scraper_demo import FundamentalScraperDemo
from utils.gpt_analyzer_trade_demo import GPTAnalyzerTradeDemo

def demo_trade(symbol="XAUUSD"):
    try:
        fundamentals = FundamentalScraperDemo.fetch_news(symbol)
        print("✅ News fondamentales récupérées\n", fundamentals)
    except Exception as e:
        print("❌ Erreur scraping :", e)
        return

    trade = {
        'symbol': symbol,
        'signal': 1,
        'entry': 2050,
        'stop_loss': 2040,
        'take_profit': 2060
    }

    gpt = GPTAnalyzerTradeDemo()
    result = gpt.analyze_trade_with_fundamentals(trade, fundamentals)

    print("\n=== Résultat GPT ===")
    print("Résumé fondamental :", result['gpt_summary'])
    print("Confirmation trade :", result['gpt_confirmation'])

if __name__ == "__main__":
    demo_trade("XAUUSD")
