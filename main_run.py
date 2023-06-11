from morsel import Morsel
import uasyncio as asyncio

def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)

async def main():
    set_global_exception()  # Debug aid
    morsel = Morsel()
    await morsel.run()
try:
    asyncio.run(main())
finally:
    asyncio.new_event_loop()  # Clear retained state