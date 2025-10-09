import json
from channels.generic.websocket import AsyncWebsocketConsumer

class QGISLayerConsumer(AsyncWebsocketConsumer):
    connected_clients = set()

    async def connect(self):
        await self.accept()
        QGISLayerConsumer.connected_clients.add(self)
        print("✅ Client connected yes :", self.channel_name)

    async def disconnect(self, close_code):
        QGISLayerConsumer.connected_clients.discard(self)
        print("❌ Client disconnected:", self.channel_name)

    async def receive(self, text_data):
        """Handle messages from QGIS plugin"""
        try:
            data = json.loads(text_data)
            print("📡 Received layers from QGIS:", list(data.keys()))
            print("Mety tsara ve : ", data)

            # Broadcast to all connected clients (like Next.js)
            for client in list(QGISLayerConsumer.connected_clients):
                if client != self:
                    await client.send(text_data)

        except Exception as e:
            print(f"⚠️ Error processing message: {e}")
