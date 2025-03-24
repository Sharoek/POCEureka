import py_eureka_client.eureka_client as eureka_client
from sanic.response import json  # Sanic's JSON response

class EurekaFacade: 
    def __init__(self, app_name: str, instance_port: int) -> None: 
        """Initializes the facade class with appropiate a"""
        self.app_name = app_name
        self.instance_port = instance_port
        self.eureka_server="http://localhost:8761/eureka/"
        self.initEurekaClient()


    def initEurekaClient(self) -> None:
        """Register this service in Eureka"""
        eureka_client.init(
            eureka_server=self.eureka_server,
            app_name=self.app_name,
            instance_port=self.instance_port
        )
        
    async def pingService(self, service: str, path: str):
        response = await eureka_client.do_service_async(service, path)
        return response

eureka_facade = EurekaFacade(app_name="CLIENTSERVICE", instance_port=8080)