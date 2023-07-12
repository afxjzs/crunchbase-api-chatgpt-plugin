from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
import requests
import json
import os

app = FastAPI()


class Company(BaseModel):
    name: str


@app.post("/search")
async def search_company(company: Company):
    user_key = os.getenv('CRUNCHBASE_API_KEY')
    url = f"https://api.crunchbase.com/api/v4/searches/organizations?user_key={user_key}"
    data = {
        "field_ids": ["name", "short_description", "website_url", "image_url"],
        "query": [
            {
                "type": "predicate",
                "field_id": "identifier",
                "operator_id": "contains",
                "values": [company.name]
            }
        ],
        "limit": 5
    }
    response = requests.post(url, data=json.dumps(data))
    print("\n", data, "\n")
    print(response.json())
    response_data = response.json()
    if response.status_code == 200:
        # Extract the required fields
        extracted_data = []
        for entity in response_data['entities']:
            extracted_entity = {
                'created_at': entity['properties'].get('created_at', None),
                'entity_def_id': entity['properties'].get('entity_def_id', None),
                'facebook': entity['properties'].get('facebook', None),
                'facet_ids': entity['properties'].get('facet_ids', None),
                'identifier': entity['properties'].get('identifier', None),
                'image_id': entity['properties'].get('image_id', None),
                'image_url': entity['properties'].get('image_url', None),
                'linkedin': entity['properties'].get('linkedin', None),
                'location_identifiers': entity['properties'].get('location_identifiers', None),
                'name': entity['properties'].get('name', None),
                'permalink': entity['properties'].get('permalink', None),
                'short_description': entity['properties'].get('short_description', None),
                'stock_exchange_symbol': entity['properties'].get('stock_exchange_symbol', None),
                'stock_symbol': entity['properties'].get('stock_symbol', None),
                'twitter': entity['properties'].get('twitter', None),
                'updated_at': entity['properties'].get('updated_at', None),
                'uuid': entity['properties'].get('uuid', None),
                'website': entity['properties'].get('website', None),
            }
            extracted_data.append(extracted_entity)
        # Convert the extracted data to a JSON string
        extracted_data_json = {'results': extracted_data}
        print("\n", extracted_data_json)

        return extracted_data_json
        # return response.json()
    else:
        raise HTTPException(
            status_code=400, detail="Unable to fetch data from Crunchbase API")


@app.get("/.well-known/ai-plugin.json", include_in_schema=False)
async def read_manifest():
    try:
        with open('./manifest.json', 'r') as file:
            data = json.load(file)
        return JSONResponse(content=data)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="manifest.json not found")


@app.get("/openai.json")
async def get_openapi_json():
    return JSONResponse(get_openapi(
        title="API for Crunchbase ChatGPT Plugin",
        version="0.9.0",
        description="Sample API exposing an enterprise search endpoint using Crunchbase's Basic API as a third-party service",
        routes=app.routes,
    ))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
