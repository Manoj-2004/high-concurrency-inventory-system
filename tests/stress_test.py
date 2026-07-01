import asyncio
import time

import httpx


BASE_URL = "http://127.0.0.1:8000"

EMAIL = "manoj@example.com"
PASSWORD = "password123"

PRODUCT_ID = 2
QUANTITY = 1
TOTAL_REQUESTS = 100


async def login(client: httpx.AsyncClient) -> str:
    response = await client.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": EMAIL,
            "password": PASSWORD,
        },
    )

    response.raise_for_status()
    return response.json()["access_token"]


async def buy_product(client: httpx.AsyncClient, token: str):
    response = await client.post(
        f"{BASE_URL}/purchase/",
        json={
            "product_id": PRODUCT_ID,
            "quantity": QUANTITY,
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    return response.status_code, response.json()

timeout = httpx.Timeout(120.0)

async def main():
    async with httpx.AsyncClient(timeout=timeout) as client:
        token = await login(client)

        start_time = time.perf_counter()

        tasks = [
            buy_product(client, token)
            for _ in range(TOTAL_REQUESTS)
        ]

        results = await asyncio.gather(*tasks)

        end_time = time.perf_counter()

    success_count = 0
    out_of_stock_count = 0
    other_errors = 0

    for status_code, body in results:
        if status_code == 201:
            success_count += 1
        elif status_code == 400:
            out_of_stock_count += 1
        else:
            other_errors += 1
            print("Unexpected:", status_code, body)

    print("\n===== Stress Test Results =====")
    print(f"Total Requests     : {TOTAL_REQUESTS}")
    print(f"Successful Orders  : {success_count}")
    print(f"Out of Stock       : {out_of_stock_count}")
    print(f"Other Errors       : {other_errors}")
    print(f"Total Time         : {end_time - start_time:.2f} seconds")
    print(f"Requests/Second    : {TOTAL_REQUESTS / (end_time - start_time):.2f}")


if __name__ == "__main__":
    asyncio.run(main())