# import asyncio
# import time

# class Test:
#     def __init__(self) -> None:
#         self.flag = asyncio.Event()
#         self.shutdown = False


#     def excute(self):
#         asyncio.run(self.tasks())

#     async def task1(self):
#         while not self.shutdown:
#             await self.flag.wait()
#             print("task1")
#             self.flag.clear()

#     async def task2(self):
#         while not self.shutdown:
#             print("task2")
#             await asyncio.sleep(1.0)
#             self.flag.set()

    
#     async def task3(self):
#         await asyncio.sleep(10.0)
#         self.shutdown = True

#     async def tasks(self):
#         await asyncio.gather(self.task1(), self.task2(), self.task3())
        

# test = Test()
# print(time.time())
# test.excute()
# print(time.time())