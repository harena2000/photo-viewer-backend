from channels.generic.websocket import AsyncWebsocketConsumer
import json

class QGISConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("qgis_group", self.channel_name)
        await self.accept()
        print("✅ Frontend connected")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("qgis_group", self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            "qgis_group", {"type": "broadcast_layers", "layers": data.get("layers", [])}
        )

    async def broadcast_layers(self, event):
        await self.send(json.dumps({"layers": event["layers"]}))
