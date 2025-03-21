import py_eureka_client.eureka_client as eureka_client


class EurekaFacade: 
    service_registered = False
    
    def __init__(self, app_name: str, instance_port: int) -> None: 
        """Initializes the facade class """
        if not EurekaFacade.service_registered:
            self.app_name = app_name
            self.instance_port = instance_port
            self.eureka_server="http://host.docker.internal:8761/eureka/"
            self.initEurekaClient()
            EurekaFacade.service_registered = True


    def initEurekaClient(self) -> None:
        """Register this service in Eureka"""
        eureka_client.init(
            eureka_server=self.eureka_server,
            app_name=self.app_name,
            instance_port=self.instance_port,
            instance_host="localhost",
            instance_ip="localhost",
            prefer_same_zone=True,
            should_register=True,
            should_discover=True            
        )
    
eureka_facade = EurekaFacade(app_name="openformsService", instance_port=8001)