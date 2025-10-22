# qgis/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asyncio import sleep

class QGISLayerConsumer(AsyncWebsocketConsumer):
    # Keep track of all connected WebSocket clients
    connected_clients = set()

    async def connect(self):
        """When a client connects"""
        await self.accept()
        QGISLayerConsumer.connected_clients.add(self)
        print(f"✅ Client connected: {self.channel_name}")
        # Optional: Send an initial handshake message
        await self.send(json.dumps({"type": "connection", "status": "connected"}))

    async def disconnect(self, close_code):
        """When a client disconnects"""
        if self in QGISLayerConsumer.connected_clients:
            QGISLayerConsumer.connected_clients.remove(self)
        print(f"❌ Client disconnected: {self.channel_name}")

    async def receive(self, text_data):
        """When QGIS sends a message (usually a layers update)"""
        try:
            data = json.loads(text_data)
            print("📡 Received layers from QGIS:", list(data.keys()))
            print("🛰️ Payload:", data)

            # Prepare the broadcast message
            broadcast = json.dumps({
                "type": "layers_update",
                "source": data.get("source", "qgis"),
                "key": data.get("key", "default"),
                "layers": data.get("layers", [])
            })

            # Broadcast safely to all active clients except sender
            to_remove = []
            for client in list(QGISLayerConsumer.connected_clients):
                if client != self:
                    try:
                        await client.send(broadcast)
                    except Exception as e:
                        print(f"⚠️ Failed to send to {client.channel_name}: {e}")
                        to_remove.append(client)

            # Clean up dead clients
            for c in to_remove:
                QGISLayerConsumer.connected_clients.discard(c)

        except Exception as e:
            print(f"⚠️ Error processing message: {e}")
