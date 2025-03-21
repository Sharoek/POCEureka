from sanic import Sanic, json
from eurekaclient import EurekaFacade
from sanic.response import text

app = Sanic("Test")


@app.get("/openforms")
async def test_openforms(request):
    result = await EurekaFacade.eureka_facade.pingService("openformsService", "api/v2/ping")
    return text(result)

@app.get("/openzaak")
async def test_openzaak(request):
    result = await EurekaFacade.eureka_facade.pingService("openzaakService", "ping")
    return text(result)


if __name__ == "__main__":
    app.run("0.0.0.0", 8080)