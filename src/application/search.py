from src.repo.search_http import SearchHttp
from src.schema.schema import NERResponse


class SearchEngine:
    def __init__(self):
        self.http = SearchHttp()

    async def search(self, ner: NERResponse, limit: int = 4) -> list[dict]:
        params = {
            "district": None,
            "price_range": None,
            "property_type": None,
            "bedrooms": None,
            "square": None,
        }
        if ner.location and ner.location.district:
            params["district"] = ner.location.district.capitalize()

        if ner.price:
            if ner.price.min_price and ner.price.max_price:
                params["price_range"] = f"{ner.price.min_price}-{ner.price.max_price}"
            elif ner.price.min_price:
                params["price_range"] = f"{ner.price.min_price}-{10**9}"
            elif ner.price.max_price:
                params["price_range"] = f"0-{ner.price.max_price}"

        if ner.rooms:
            if ner.rooms.count == 1:
                params["bedrooms"] = "1 СПАЛЬНЯ"
            elif ner.rooms.count == 2:
                params["bedrooms"] = "2 СПАЛЬНЯ"
            elif ner.rooms.count == 3:
                params["bedrooms"] = "3 СПАЛЬНЯ"
            else:
                params["bedrooms"] = "БОЛЕЕ 4 СПАЛЕН"

        if ner.property:
            params["property_type"] = ner.property.value.upper()

        if ner.area:
            if ner.area.min_area and ner.area.max_area:
                params["square"] = f"{ner.area.min_area}-{ner.area.max_area}"
            elif ner.area.min_area:
                params["square"] = f"{ner.area.min_area}-100000"
            elif ner.area.max_area:
                params["square"] = f"0-{ner.area.max_area}"

        print(params)
        return await self.http.search(params=params, limit=limit)

    def format_results(self, results: list[dict]) -> str:
        if not results:
            return "К сожалению, ничего не найдено по заданным параметрам."
        lines = [
            f"🔹 {r['firstBlock']['project_description']}, {r['firstBlock']['square']} м², {r['firstBlock']['priceFrom']} ₽ — {r['fifthBlock']['district']}"
            for r in results
        ]
        return "Вот что я нашёл:<br>" + "<br>".join(lines)
