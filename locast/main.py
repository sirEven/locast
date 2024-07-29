import asyncio


async def print_some_stuff(name: str) -> None:
    print(f"Start printing stuff for {name}.")
    dots = "."
    for count in range(10):
        print(f"Stuff {count}{dots}")
        dots += "."
        await asyncio.sleep(0.5)
    print(f"Finish printing stuff for {name}.")


async def main():
    await print_some_stuff("Severin")


asyncio.run(main())
