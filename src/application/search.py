from src.repo.search_http import SearchHttp
from src.schema.schema import NERResponse


class SearchEngine:
    def __init__(self):
        self.http = SearchHttp()

    async def search(self, ner: NERResponse) -> list[dict]:
        return await self.http.search(data=ner)

    def format_results(self, results: list[dict]) -> str:
        if not results:
            return "К сожалению, ничего не найдено по заданным параметрам."
        lines = [
            f"🔹 {r['title']}, {r['area']} м², {r['price']:,} ₽ — {r['location']}"
            for r in results
        ]
        return "Вот что я нашёл:\n" + "\n".join(lines)
