import asyncio
import threading


class ConcurrencySimulation:
    interesting_property: int = 0

    async def task_a(self) -> None:
        while True:
            print("Task A doing stuff...")
            await asyncio.sleep(1)

    async def task_b(self) -> None:
        while True:
            print("Task B doing stuff...")
            await asyncio.sleep(1)

    def run_something_blocking_on_separate_thread(self) -> None:
        t = threading.Thread(target=self.wrap_async_func)
        t.start()

    async def something_blocking(self) -> None:
        while True:
            print(
                f"Doing a blocking thing for {self.interesting_property} times already..."
            )
            self.interesting_property += 1
            await asyncio.sleep(5)

    def wrap_async_func(self) -> None:
        asyncio.run(self.something_blocking())


async def property_query(simulation: ConcurrencySimulation) -> None:
    while True:
        print(f"Interesting property: {simulation.interesting_property}")
        await asyncio.sleep(2)


async def test() -> None:
    sim = ConcurrencySimulation()
    sim.run_something_blocking_on_separate_thread()
    tasks = [
        asyncio.create_task(sim.task_a()),
        asyncio.create_task(sim.task_b()),
        asyncio.create_task(property_query(sim)),
    ]

    await asyncio.gather(*tasks)


asyncio.run(test())
