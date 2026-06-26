import httpx, asyncio, time, json, sys

API = "http://localhost:3000"

async def main():
    async with httpx.AsyncClient() as c:
        # Step 1: Create room
        print("1. Creating room...")
        r = await c.post(f"{API}/api/rooms", json={"topic": "AI 是否应该被严格监管？", "expert_count": 4})
        assert r.status_code == 201, f"Create room failed: {r.text}"
        room = r.json()
        room_id = room["id"]
        print(f"   Room created: {room_id[:12]}... status={room['status']}")

        # Step 2: Generate experts
        print("2. Generating experts...")
        r = await c.post(f"{API}/api/rooms/{room_id}/experts", json={})
        assert r.status_code == 200, f"Generate experts failed: {r.text}"
        data = r.json()
        assert "host" in data and "experts" in data
        print(f"   Host: {data['host']['name']}, Experts: {len(data['experts'])}")

        # Step 3: Start discussion
        print("3. Starting discussion...")
        r = await c.post(f"{API}/api/rooms/{room_id}/start")
        assert r.status_code == 200, f"Start failed: {r.text}"
        print(f"   Started: {r.json()}")

        # Step 4: Wait for completion (poll every 1s, max 30s)
        print("4. Waiting for discussion to complete...")
        for i in range(30):
            await asyncio.sleep(1)
            r = await c.get(f"{API}/api/rooms/{room_id}")
            status = r.json()["status"]
            if status == "finished":
                detail = r.json()
                print(f"   Finished! Transcript: {detail['transcript_count']} lines, Insights: {detail['insight_count']}")
                break
            if i % 3 == 0:
                print(f"   ... status={status}")

        # Step 5: Get summary detail
        print("5. Final state:")
        r = await c.get(f"{API}/api/rooms/{room_id}")
        room = r.json()
        print(f"   Status: {room['status']}")
        print(f"   Topic: {room['topic']}")
        for e in room["experts"]:
            print(f"   - {e['name']} ({e['role']}): {e['stance'][:30]}")

        print("\n✓ All steps passed!")

asyncio.run(main())
