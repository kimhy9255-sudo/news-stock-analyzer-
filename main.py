import re
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class StockData:
    code: str
    name: str
    theme: str
    role: str            # '핵심부품', '원자재', '완성품', '유통/단순수혜'
    tech_score: int      # 독점/기술력 점수 (1~10)
    trading_volume: int  # 거래대금 (억원)
    is_ma20_above: bool  # 20일선 위 위치 여부 (True/False)

STOCK_DB: List[StockData] = [
    StockData("000001", "A정밀", "방산", "핵심부품", 9, 1200, True),
    StockData("000002", "B소재", "방산", "원자재", 7, 800, True),
    StockData("000003", "C시스템", "방산", "완성품", 8, 2500, False),
    StockData("000004", "D하이텍", "반도체", "핵심부품", 10, 3000, True),
    StockData("000005", "E패키징", "반도체", "완성품", 6, 500, True),
]

IMP_KEYWORDS = {
    "국산화": 3, "세계 최초": 3, "독점": 3, "대규모 수주": 2, 
    "단독": 2, "정부 정책": 2, "MOU": 1, "지분 투자": 1
}

class MaterialAnalyzer:
    def __init__(self, stock_db: List[StockData]):
        self.db = stock_db

    def analyze_news(self, news_text: str):
        print(f"\n[입력 뉴스 분석 중...]\n\"{news_text.strip()}\"\n")
        
        impact_score = sum(score for kw, score in IMP_KEYWORDS.items() if kw in news_text)
        matched_keywords = [kw for kw in IMP_KEYWORDS if kw in news_text]
        
        print(f"▶ 재료 자극도 점수: {impact_score}점 (포착 키워드: {matched_keywords})")

        detected_theme = None
        if any(kw in news_text for kw in ["방산", "무기", "수출"]):
            detected_theme = "방산"
        elif any(kw in news_text for kw in ["반도체", "AI", "부품"]):
            detected_theme = "반도체"
        
        if not detected_theme:
            print("⚠ 관련 테마를 DB에서 찾지 못했습니다.")
            return

        print(f"▶ 포착된 관련 테마: [{detected_theme}]")
        
        candidates = [s for s in self.db if s.theme == detected_theme]
        scored_stocks = []

        role_weights = {"핵심부품": 40, "원자재": 30, "완성품": 20, "유통/단순수혜": 10}

        for stock in candidates:
            role_score = role_weights.get(stock.role, 10)
            tech_score = stock.tech_score * 2
            volume_score = min(20, (stock.trading_volume // 1000) * 10)
            chart_score = 20 if stock.is_ma20_above else 0

            total_score = role_score + tech_score + volume_score + chart_score + impact_score
            
            scored_stocks.append({
                "stock": stock,
                "total_score": total_score,
                "volume": stock.trading_volume,
                "ma_status": "지지(20일선 위)" if stock.is_ma20_above else "저항(20일선 아래)"
            })

        scored_stocks.sort(key=lambda x: x["total_score"], reverse=True)
        self._print_results(scored_stocks)

    def _print_results(self, results: List[Dict]):
        print("\n" + "="*60)
        print(f"{'순위':<4} | {'종목명':<8} | {'구분(역할)':<8} | {'거래대금':<8} | {'차트위치':<12} | {'총점'}")
        print("="*60)
        
        for idx, res in enumerate(results, start=1):
            s = res["stock"]
            rank_label = f"★{idx}순위" if idx == 1 else f" {idx}순위"
            print(f"{rank_label:<4} | {s.name:<8} | {s.role:<8} | {res['volume']}억{'':<4} | {res['ma_status']:<12} | {res['total_score']}점")
        print("="*60 + "\n")

if __name__ == "__main__":
    analyzer = MaterialAnalyzer(STOCK_DB)
    sample_telegram_news = """
    [속보/단독] 정부, 차세대 방산 무기 국산화 독점 사업자 최종 선정. 
    해외 대규모 수주 논의 가속화 전망!
    """
    analyzer.analyze_news(sample_telegram_news)

