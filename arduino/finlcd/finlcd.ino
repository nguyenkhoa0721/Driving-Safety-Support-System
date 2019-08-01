#include <ESP8266WiFi.h>
 
const char* ssid = "nk";
const char* password = "07070201";
 
int ledD5 = D5;
int LEDD6 = D6;
WiFiServer server(80);
int valueD5 = LOW;
int valueD6 = LOW; 
void setup() {
  Serial.begin(115200);
  delay(10);
 
 
  pinMode(ledD5, OUTPUT);
  digitalWrite(ledD5, LOW);
  pinMode(LEDD6, OUTPUT);
  digitalWrite(LEDD6, LOW);  
  // Connect to WiFi network
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
 
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected");
 
  // Start the server
  server.begin();
  Serial.println("Server started");
 
  // Print the IP address
  Serial.print("Use this URL : ");
  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println("/");
}
 
void loop() {
  // Check if a client has connected
  WiFiClient client = server.available();
  if (!client) {
    return;
  }
  // Wait until the client sends some data
  Serial.println("new client");
  while(!client.available()){
    delay(1);
  } 
  // Read the first line of the request
  String request = client.readStringUntil('\r');
  Serial.println(request);
  client.flush();
 
  // Match the request
  if (request.indexOf("/LEDD5=ON") != -1) {
    digitalWrite(ledD5, HIGH);
    valueD5 = HIGH;
  } 
  if (request.indexOf("/LEDD5=OFF") != -1){
    digitalWrite(ledD5, LOW);
    valueD5 = LOW;
  }
  if (request.indexOf("/LEDD6=ON") != -1) {
    digitalWrite(LEDD6, HIGH);
    valueD6 = HIGH;
  } 
  if (request.indexOf("/LEDD6=OFF") != -1){
    digitalWrite(LEDD6, LOW);
    valueD6 = LOW;
  }
  // Return the response
  client.println("HTTP/1.1 200 OK");
  client.println("Content-Type: text/html");
  client.println(""); //  do not forget this one
  client.println("<!DOCTYPE HTML>");
  client.println("<html>");

  client.print("{");
  client.print(" \"D5\" :");
  if(valueD5 == HIGH) {
    client.print(" \"On\" ");  
  } else if (valueD5 == LOW){
    client.print(" \"OFF\" ");
  }
  client.print(",");
  client.println("<br>");

  client.print(" \"D6\" :");
  if(valueD6 == HIGH) {
    client.print(" \"On\" ");  
  } else if (valueD6 == LOW) {
    client.print(" \"OFF\" ");
  }
  client.print("}");
  client.println("</html>");
 
  delay(1);
  Serial.println("Client disconnected");
  Serial.println("");
 
}
