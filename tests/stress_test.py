import asyncio
import time
import httpx
import math

BASE_URL = "http://localhost:8000"
PURCHASE_URL = f"{BASE_URL}/purchase/"
LOGIN_URL = f"{BASE_URL}/auth/login"

TOTAL_REQUESTS = 1000
CONCURRENCY_LIMIT = 200

# OAuth2PasswordRequestForm expects form-encoded data with 'username' (email) and 'password'
TEST_USER_CREDENTIALS = {
    "username": "test@example.com",
    "password": "securepassword123"
}

PAYLOAD = {
    "product_id": 1,
    "quantity": 1
}

async def get_auth_token(client: httpx.AsyncClient) -> str:
    """Authenticate and fetch a JWT bearer token using form data matching OAuth2PasswordRequestForm."""
    try:
        response = await client.post(
            LOGIN_URL, 
            data=TEST_USER_CREDENTIALS, 
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5.0
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token")
        if not isinstance(token, str) or not token.strip():
            raise ValueError("Login response did not contain a valid access_token")
        return token
    except Exception as e:
        print(f"Failed to authenticate test user: {e}")
        raise

async def send_request(client, semaphore, headers):
    async with semaphore:
        start_time = time.perf_counter()
        try:
            # Expected success status; verify against the actual purchase route.
            response = await client.post(PURCHASE_URL, json=PAYLOAD, headers=headers)
            elapsed = (time.perf_counter() - start_time) * 1000
            return response.status_code, elapsed
        except httpx.RequestError:
            elapsed = (time.perf_counter() - start_time) * 1000
            return "TRANSPORT_ERROR", elapsed

def calculate_percentile(data, percent):
    if not data:
        return 0.0
    data.sort()
    k = (len(data) - 1) * (percent / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return data[int(k)]
    return data[int(f)] * (c - k) + data[int(c)] * (k - f)

async def main():
    limits = httpx.Limits(
        max_connections=CONCURRENCY_LIMIT,
        max_keepalive_connections=CONCURRENCY_LIMIT,
    )
    
    async with httpx.AsyncClient(limits=limits, timeout=httpx.Timeout(10.0)) as client:
        print("Authenticating test user via /auth/login...")
        try:
            token = await get_auth_token(client)
        except Exception:
            print("Aborting benchmark due to authentication failure.")
            return

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
        print(f"Initializing benchmark: {TOTAL_REQUESTS} total requests with concurrency limit {CONCURRENCY_LIMIT}...")
        start_total = time.perf_counter()
        
        tasks = [send_request(client, semaphore, headers) for _ in range(TOTAL_REQUESTS)]
        results = await asyncio.gather(*tasks)
        
        total_duration = time.perf_counter() - start_total

    # Ensure every single request result is accounted for
    assert len(results) == TOTAL_REQUESTS

    # Detailed response classification
    accepted_dispatches = sum(1 for status, _ in results if status == 202)
    bad_requests = sum(1 for status, _ in results if status in [400, 422])
    auth_errors = sum(1 for status, _ in results if status in [401, 403])
    rate_limits = sum(1 for status, _ in results if status == 429)
    not_found = sum(1 for status, _ in results if status == 404)
    server_errors = sum(1 for status, _ in results if isinstance(status, int) and 500 <= status < 600)
    transport_failures = sum(1 for status, _ in results if status == "TRANSPORT_ERROR")
    
    accounted_statuses = {202, 400, 422, 401, 403, 429, 404, "TRANSPORT_ERROR"}
    other_unexpected = sum(1 for status, _ in results if status not in accounted_statuses and not (isinstance(status, int) and 500 <= status < 600))

    latencies = [lat for _, lat in results]
    median_lat = calculate_percentile(latencies, 50)
    p95_lat = calculate_percentile(latencies, 95)
    requests_per_sec = TOTAL_REQUESTS / total_duration if total_duration > 0 else 0

    print("\n================ BENCHMARK RESULTS ================")
    print(f"Total Requests Processed: {TOTAL_REQUESTS}")
    print(f"Accepted Requests (HTTP 202): {accepted_dispatches}")
    print(f"HTTP 400/422 Responses: {bad_requests}")
    print(f"Authentication Errors (401/403): {auth_errors}")
    print(f"Rate Limits (429): {rate_limits}")
    print(f"Not Found (404): {not_found}")
    print(f"Server Errors (HTTP 5xx): {server_errors}")
    print(f"Transport Failures (Network/Timeout): {transport_failures}")
    print(f"Other Unexpected Responses: {other_unexpected}")
    print(f"Total Execution Time: {total_duration:.2f} seconds")
    print(f"Throughput: {requests_per_sec:.2f} requests/sec")
    print(f"Median Latency: {median_lat:.2f} ms")
    print(f"P95 Latency: {p95_lat:.2f} ms")
    print("-----------------------------------------------------")
    print(f"Results Accounted For: {len(results)} / {TOTAL_REQUESTS}")
    print("=====================================================")

if __name__ == "__main__":
    asyncio.run(main())
