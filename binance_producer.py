import json
import websocket
from kafka import KafkaProducer

KAFKA_BROKER = 'crypto-kafka:9092'
TOPIC = 'crypto-trades'

producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER],
    key_serializer=lambda k: k.encode('utf-8'),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def on_message(ws, message):
    try:
        payload = json.loads(message)
        data = payload.get('data')
        if not data: return
        
        # Convert short Binance keys into readable field names
        trade_event = {
            'event_time': data.get('E'),
            'symbol': data.get('s'),
            'price': float(data.get('p')),
            'quantity': float(data.get('q')),
            'is_buyer_maker': data.get('m') # True, if the deal was initiated by the seller
        }
        
        producer.send(
            TOPIC, 
            key=trade_event['symbol'], 
            value=trade_event
        )
        print(f"Sent: {trade_event['symbol']} | Price: {trade_event['price']} | Qty: {trade_event['quantity']}")
    except Exception as e:
        print(f"Error processing message: {e}")

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket Closed")
    producer.close()

def on_open(ws):
    print("Connected to Binance WebSocket! Streaming live trades to Kafka...")

if __name__ == "__main__":
    streams = "btcusdt@trade/ethusdt@trade/solusdt@trade/bnbusdt@trade/xrpusdt@trade"
    ws_url = f"wss://stream.binance.com:9443/stream?streams={streams}"
    
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()
