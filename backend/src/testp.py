import httpx
import csv
from datetime import datetime

API_URL = "http://localhost:8000"

TEST_QUERIES = [
    "3 bedroom house built in 1990 with 2 bathrooms and a 2 car garage in NridgHt",
    "small house in OldTown with 1 bathroom and 1 fireplace average kitchen",
    "luxury home built in 2005 with excellent quality 3 full baths and 3 car garage in StoneBr",
    "2 bed house good basement quality built in 1980 in Edwards with 1200 sqft living area",
    "nice 2500 sqft home in CollgCr built 2000 remodeled 2015 excellent kitchen 2 full baths"
]

ALL_FIELDS = [
    "overall_qual", "gr_liv_area", "garage_cars", "total_bsmt_sf",
     "first_flr_sf", "year_built", "year_remod_add",
    "full_bath", "neighborhood", "kitchen_qual", "bsmt_qual"
]

results = []

for query in TEST_QUERIES:
    response = httpx.post(
        f"{API_URL}/predict",
        json={"query": query},
        timeout=30
    )
    data = response.json()
    features = data["extracted_features"]

    extracted_count = sum(1 for f in ALL_FIELDS if features.get(f) is not None)
    missing = features.get("missing_fields", [])
    confidence = features.get("confidence")

    result = {
        "timestamp": datetime.now().isoformat(),
        "query": query[:60],
        "extracted": extracted_count,
        "total": len(ALL_FIELDS),
        "missing": ', '.join(missing),
        "confidence": confidence,
        "predicted_price": data.get("predicted_price"),
    }
    results.append(result)

    print(f"\nQuery: {query[:60]}...")
    print(f"  Extracted: {extracted_count}/{len(ALL_FIELDS)}")
    print(f"  Missing:   {missing}")
    print(f"  Confidence:{confidence}")
    print(f"  Price:     ${data.get('predicted_price', 0):,.0f}" if data.get('predicted_price') else "  Price: N/A")

# Save log
#with open("prompt_version_log.csv", "w", newline="") as f:
   # writer = csv.DictWriter(f, fieldnames=results[0].keys())
    #writer.writeheader()
    #writer.writerows(results)

#print("\n✅ Log saved to prompt_version_log.csv")

#avg = sum(r["extracted"] for r in results) / len(results)
#print(f"\nAvg fields extracted: {avg:.1f}/{len(ALL_FIELDS)}")