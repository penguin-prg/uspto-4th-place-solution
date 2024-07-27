ALL_KEYS = ["title", "abstract", "description", "claims"]
KEY2QUERY = {
    "title": "ti",
    "abstract": "ab",
    "claims": "clm",
    "description": "detd",
}

QUERY2KEY = {v: k for k, v in KEY2QUERY.items()}

NUM_CPU = 30
INF = 1e9
