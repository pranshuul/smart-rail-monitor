#include <WiFi.h>
#include <PubSubClient.h>
#include <BluetoothSerial.h>

// Wi‑Fi & MQTT settings
typedef const char* cstr;
cstr ssid           = "Pranshul's OnePlus Twelve";
cstr password       = "t4eccvfn";
cstr mqtt_server    = "mqtt.thingspeak.com";
int mqtt_port       = 1883;
cstr mqtt_user      = "3GDTO22V308LUSY5";
cstr mqtt_pass      = "";

// MQTT topics for separate streams
cstr ts_publish_topic      = "channels/2925813/publish";
cstr sensor_alert_topic    = "rail/alerts/sensor";  // sensor-only alerts\;
cstr ml_alert_sub_topic    = "rail/alerts/ml";      // ML-only alerts subscription

// Pins
define trigPin1   2
#define echoPin1   15
#define trigPin2   12
#define echoPin2   13
#define irSensor1  34
#define irSensor2  35
#define buzzerPin  25
#define redLED     32
#define greenLED   33

WiFiClient espClient;
PubSubClient client(espClient);
BluetoothSerial SerialBT;
volatile bool ml_alert = false;

long getDistance(int trigPin,int echoPin) {
  digitalWrite(trigPin,LOW); delayMicroseconds(2);
  digitalWrite(trigPin,HIGH); delayMicroseconds(10);
  digitalWrite(trigPin,LOW);
  long duration=pulseIn(echoPin,HIGH);
  return (duration*0.034)/2;
}

void callback(char* topic,byte* payload,unsigned int length) {
  // Only ML topic triggers
  if (String(topic)==String(ml_alert_sub_topic)) {
    String msg;
    for(unsigned int i=0;i<length;i++) msg+=(char)payload[i];
    ml_alert=(msg=="1");
    Serial.print("ML alert: "); Serial.println(msg);
  }
}

void setup(){
  Serial.begin(115200);
  SerialBT.begin("ESP32_BT");
  pinMode(trigPin1,OUTPUT); pinMode(echoPin1,INPUT);
  pinMode(trigPin2,OUTPUT); pinMode(echoPin2,INPUT);
  pinMode(irSensor1,INPUT); pinMode(irSensor2,INPUT);
  pinMode(buzzerPin,OUTPUT);
  pinMode(redLED,OUTPUT); pinMode(greenLED,OUTPUT);

  WiFi.begin(ssid,password);
  while(WiFi.status()!=WL_CONNECTED){ delay(500); Serial.print("."); }
  Serial.println("\nWiFi connected");

  client.setServer(mqtt_server,mqtt_port);
  client.setCallback(callback);
  while(!client.connected()){
    if(client.connect("ESP32Client",mqtt_user,mqtt_pass)){
      Serial.println("MQTT connected");
      client.subscribe(ml_alert_sub_topic);
    } else { delay(1000); Serial.print("Retry MQTT"); }
  }
}

void loop(){
  client.loop();  // check for ML messages

  long d1 = getDistance(trigPin1,echoPin1);
  long d2 = getDistance(trigPin2,echoPin2);
  int ir1 = digitalRead(irSensor1);
  int ir2 = digitalRead(irSensor2);

  bool sensor_alert = (ir1==1)||(ir2==1)||(d1>6)||(d1<=2)||(d2>6)||(d2<=2);
  bool combined_alert = sensor_alert || ml_alert;

  // Physical signaling
  digitalWrite(redLED, combined_alert);
  digitalWrite(greenLED,!combined_alert);
  digitalWrite(buzzerPin, combined_alert);

  // Publish sensor data to ThingSpeak
  String ts_payload = String("field1=") + d1 +
                   "&field2=" + d2 +
                   "&field3=" + ir1 +
                   "&field4=" + ir2 +
                   "&field5=" + (sensor_alert?"1":"0") +
                   "&field6=" + (ml_alert?"1":"0");
  client.publish(ts_publish_topic, ts_payload.c_str());

  // Publish sensor-only alert to its own topic
  client.publish(sensor_alert_topic, sensor_alert?"1":"0");

  // Bluetooth output
  SerialBT.println(ts_payload);

  delay(1500);
}
