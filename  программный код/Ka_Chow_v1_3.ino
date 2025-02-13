/*
АННОТАЦИЯ К СКЕТЧУ.


С перереодичностью 100 мс ( в реальности 150-250 мс) происходит отправка замеров дистанции
Как только приходит сообщение в serial-порт - запскается нужный сценарий

Функции-сценарии и прочее добавлены для будущего использования.

*/


// ПОЯСНЕНИЯ К ЗНАЧКАМ В КОДЕ:
// !!!!! - ЗАМЕРИТЬ ЭКСПЕРИМЕНТАЛЬНО
// ОТЛАДКА!!!!!!!!!!!! - используется для отладки


// скорось от 170 до 255   !!! 
// _____ Гайд по командам _____
//  sonar(); - возвращает показания сонара
//  forward_and_taxiing(speed_r, speed_l); - вперёд с подачей скорости 
//  backward(speed_r, speed_l); - назад с подачей скорости
//  left_90(); - поворачивается на 90 градусов влево
//  right_90(); - поворачивается на 90 градусов вправо
//  turing_back(); - повернуться на 180 градусов
//  releases(); - открыть хват
//  capture(); - закрыть хват
//  stop1(); - останавливает перемещение
//  up(); - шаговый мотор вверх
//  down(); - шаговый мотор вниз
//  moving_to_a_corner(); - переместить предмет в угол (если предмет уже можно схватить) и возвращается в исходную точку
//  detour(); - объезд
//  detour_l(); - объезд c поворотом налево
//  detour_r(); - объезд c поворотом направо


#include <Wire.h> 
#include <stdio.h>
#include <Arduino.h>
#include <Servo.h> // подключаем библиотеку для работы с сервоприводом

// Для управления дравером ЛАРТ
#define direction_R 2 // отвечает за направление правого мотора
#define direction_L 4 // отвечает за направление левого мотора
#define speed_r_port 3 // скорость правой стороны
#define speed_l_port 5 // скорость левой стороны

// Для работы сонара
#define trigPin 7  // Пин для триггера
#define echoPin 6  // Пин для эха
float dist_3[3] = {0.0, 0.0, 0.0}; // Массив для хранения последних измерений
byte i = 0; // Счётчик для массива

// Для управления дравером к шаговому двигателю
#define in1 8
#define in2 9
#define in3 10
#define in4 11

// Для управления дравером к шаговому двигателю
#define servoPin 13

// Инициализация объекта сервопривода (схват)
Servo servo1; 


int entrance_1 = 0;
int entrance_2 = 0;
int entrance_speed_r = 150; // скорость на левые движки
int entrance_speed_l = 150; // скорость на правые движки

// int min_speed = 170;
int min_speed = 68;
// отладка
int speed = 78;
float filteredDist;

float RIGHT = 0.0;
int LEFT = 0;
int DELAY = 0;



// Таймеры
unsigned long time_now = 0;
unsigned long message_timer = 0; // мс, счётчик

// Ававрийная остновка
const unsigned int emergency_timer_timeout = 1000;  // мс, время, через которое происходит аварийная остановка

// Замер дистанции
unsigned int sonar_timer = 0; // мс, счётчик
const unsigned int sonar_timer_timeout = 100; // мс период замера дистанции

// Для работы двуканальной связи по serial-порту
String inputString = "";                // Строка для хранения входящих данных
String input_m[4] = { "", "", "", "" }; // Строка для хранения уже разбитых данных из входящего сообщения
bool stringComplete = false;            // является ли строка полной
bool input_open = false;                // открыта ли строка для записи (записывается ли в данный момент)
String pub_str = "";                    // Строка для сообщения-ответа, которое идёт на raspberry pi

// Функция медианного фильтра из трёх значений
float middle_of_3(float a, float b, float c) {
    if ((a <= b) && (a <= c)) return min(b,c);
    else if ((b <= a) && (b <= c)) return min(a,c);
    else return min(a,b);
}

// Функция считает длину и отправляет её в serial-порт
void calc_and_pub_dist(){
  float duration, dist; // Переменные для хранения времени и расстояния

  digitalWrite(trigPin, LOW); // Убедимся, что триггер выключен
  delayMicroseconds(2); // Задержка в 2 микросекунды
  digitalWrite(trigPin, HIGH); // Включаем триггер
  delayMicroseconds(10); // Задержка в 10 микросекунд
  digitalWrite(trigPin, LOW); // Выключаем триггер

  duration = pulseIn(echoPin, HIGH); // Получаем время эха
  dist = duration / 58; // Преобразуем время в расстояние в сантиметрах
  
  dist_3[i] = dist;
  i++;
  if (i > 2) i = 0;
  filteredDist = middle_of_3(dist_3[0], dist_3[1], dist_3[2]); 
  pub_str = String(filteredDist); // Формируем сообщение, которое идёт на raspberry pi
  Serial.println(pub_str); // отправка сообщения
}

float mapFloat(float value, float fromLow, float fromHigh, float toLow, float toHigh) {
    return (value - fromLow) * (toHigh - toLow) / (fromHigh - fromLow) + toLow;
}

//Ответ на входное сообщение
void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    if (inChar == '$' or input_open == true) {
      inputString += inChar;
      input_open = true;
    }

    if (inChar == '#') {
      stringComplete = true;
      input_open = false;
    }
  }
}

// принимает 2 скорости (едет вперёд)
void forward_and_taxiing(int speed_r_new, int speed_l_new){ 
  digitalWrite(direction_R, HIGH);
  analogWrite(speed_r_port, min_speed + speed_r_new);
  digitalWrite(direction_L, HIGH);
  analogWrite(speed_l_port, min_speed + speed_l_new + 10);
}

// принимает 2 скорости (едет назад)
void backward(int speed_r_new, int speed_l_new){ 
  digitalWrite(direction_R,LOW);
  analogWrite(speed_r_port,min_speed + speed_r_new);
  digitalWrite(direction_L,LOW);
  analogWrite(speed_l_port,min_speed + speed_l_new + 35);
}

// поворачивается на 90 градусов влево
void left_90(){
  digitalWrite(direction_R, HIGH);
  analogWrite(speed_r_port, 165);
  digitalWrite(direction_L, LOW);
  analogWrite(speed_l_port, 165);
  delay(400);
}

// поворачивается на 90 градусов вправо
void right_90(){ 
  digitalWrite(direction_L, HIGH);
  analogWrite(speed_l_port, 165);
  digitalWrite(direction_R, LOW);
  analogWrite(speed_r_port, 165);
  delay(400);
}


// поворачивается на 45 градусов влево
void left_45(){
  digitalWrite(direction_R, HIGH);
  analogWrite(speed_r_port, 165);
  digitalWrite(direction_L, LOW);
  analogWrite(speed_l_port, 165);
  delay(235);
}

// поворачивается на 45 градусов вправо
void right_45(){ 
  digitalWrite(direction_L, HIGH);
  analogWrite(speed_l_port, 165);
  digitalWrite(direction_R, LOW);
  analogWrite(speed_r_port, 165);
  delay(235);
}

// повернуться на 180 градусов
void turing_back(){ 
  digitalWrite(direction_L, HIGH);
  analogWrite(speed_l_port, 145);
  digitalWrite(direction_R, LOW);
  analogWrite(speed_r_port, 145);
  delay(920);
}

// открыть хват
void releases(){ 
  servo1.write(25);  
}

//закрыть хват
void capture(){ 
  servo1.write(130);
}

void up() { // шаговый мотор вверх
  int dl = 2000; // время задержки между импульсами
    for (int i = 0; i <= 2000; i++) { // !!!!!
      digitalWrite(in1, HIGH); 
      digitalWrite(in2, LOW); 
      digitalWrite(in3, LOW); 
      digitalWrite(in4, HIGH);
      delayMicroseconds(dl);

      digitalWrite(in1, HIGH); 
      digitalWrite(in2, HIGH); 
      digitalWrite(in3, LOW); 
      digitalWrite(in4, LOW);
      delayMicroseconds(dl);

      digitalWrite(in1, LOW); 
      digitalWrite(in2, HIGH); 
      digitalWrite(in3, HIGH); 
      digitalWrite(in4, LOW);
      delayMicroseconds(dl);

      digitalWrite(in1, LOW); 
      digitalWrite(in2, LOW); 
      digitalWrite(in3, HIGH); 
      digitalWrite(in4, HIGH);
      delayMicroseconds(dl);
  }

  digitalWrite(in1, LOW); 
  digitalWrite(in2, LOW); 
  digitalWrite(in3, LOW); 
  digitalWrite(in4, LOW);
}

void down(){ // шаговый мотор вниз
  int dl = 2000; // время задержки между импульсами
    for (int i = 0; i <= 2000; i++) { // !!!!!
      digitalWrite(in1, LOW); 
      digitalWrite(in2, LOW); 
      digitalWrite(in3, HIGH); 
      digitalWrite(in4, HIGH);
      delayMicroseconds(dl);

      digitalWrite(in1, LOW); 
      digitalWrite(in2, HIGH); 
      digitalWrite(in3, HIGH); 
      digitalWrite(in4, LOW);
      delayMicroseconds(dl);

      digitalWrite(in1, HIGH); 
      digitalWrite(in2, HIGH); 
      digitalWrite(in3, LOW); 
      digitalWrite(in4, LOW);
      delayMicroseconds(dl);

      digitalWrite(in1, HIGH); 
      digitalWrite(in2, LOW); 
      digitalWrite(in3, LOW); 
      digitalWrite(in4, HIGH);
      delayMicroseconds(dl);
  } 

  digitalWrite(in1, LOW); 
  digitalWrite(in2, LOW); 
  digitalWrite(in3, LOW); 
  digitalWrite(in4, LOW);
}

// Функция №7 (поставить зелёный цилиндр на площадку старт)
void reverse_capture_1(){
  forward_and_taxiing(40,40);
  delay(560);
  stop1();
  down();
  releases();
  delay(500);
  backward(15,15);
  delay(400);  
  capture(); 
}

// объезд 
void detour(){ 
  forward_and_taxiing(0, 0);
  delay(500);

  left_45();

  forward_and_taxiing(0, 0);
  delay(1500);

  right_90();

  forward_and_taxiing(0, 0);
  delay(1610);
  
  left_45();

  stop1();
  delay(200); 

  backward(0, 0);
  delay(400);

 }
 


/* 
void detour_l(){ // объезд c поворотом налево
  left_90();
  forward_and_taxiing(85,85);
  delay(200); // !!!!!
  right_90();
  forward_and_taxiing(85,85);
  delay(200); // !!!!!
  left_90();
}

void detour_r(){ // объезд c поворотом направо
  right_90();
  forward_and_taxiing(85,85);
  delay(200); // !!!!!
  left_90();
  forward_and_taxiing(85,85);
  delay(200); // !!!!!
  right_90();
}
*/

// останавливает перемещение
void stop1(){ 
  digitalWrite(direction_R,HIGH);
  analogWrite(speed_r_port,0);
  digitalWrite(direction_L,HIGH);
  analogWrite(speed_l_port,0);
}

// останавливает перемещение
void stop_delay(){
  stop1();
  delay(500);
}

// переместить предмет в угол (если предмет уже можно схватить) и возвращается в исходную точку
void moving_to_a_corner(){ // 2
  stop1();
  delay(500);
  releases();
  forward_and_taxiing(0, 0);
    for (;filteredDist > 14.0;){
      calc_and_pub_dist();
      delay(20);
    }
  stop1();
  delay(500);
  capture();
  up();
  left_45();
  forward_and_taxiing(0, 0);
  delay(700);
  stop1();
  down();
  releases();
  delay(700);
  backward(0, 0);
  delay(330);
  stop1();

  digitalWrite(direction_L, HIGH);
  analogWrite(speed_l_port, 165);
  digitalWrite(direction_R, LOW);
  analogWrite(speed_r_port, 165);
  delay(250);

  capture();
  stop1();
  delay(500);
  }

void take_from_a_platform(){ // 1
  releases();
  forward_and_taxiing(0, 0);
    for (;filteredDist > 14.0;){
      calc_and_pub_dist();
      delay(20);
    }
  stop1();
  delay(500);
  capture();
  up();
  forward_and_taxiing(0, 0);
  delay(400);
  turing_back();
}

void special(){ // 4
  right_45();
  forward_and_taxiing(0, 0);
  delay(600);
  stop1();
  down();
  releases();
  delay(500);
  backward(0, 0);
  delay(500);

  left_45();
  stop1();
  calc_and_pub_dist();
  delay(500);

  forward_and_taxiing(0, 0);
    for (;filteredDist > 14.0;){
    calc_and_pub_dist();
    delay(RIGHT);
  }
  stop1();
  delay(500);
  capture();
  up();
  backward(0, 0);
  delay(300);

  left_45();
  forward_and_taxiing(0, 0);
  delay(800);
  stop1();
  down();
  releases();


  delay(500);
  backward(0, 0);
  delay(330);
  stop1();

  digitalWrite(direction_L, HIGH);
  analogWrite(speed_l_port, 165);
  digitalWrite(direction_R, LOW);
  analogWrite(speed_r_port, 165);
  delay(470);

  stop1();
  delay(1500);

  forward_and_taxiing(0, 0);
    for (;filteredDist > 14.0;){
    calc_and_pub_dist();
    delay(RIGHT);
  }
  stop1();
  
  capture();
  up();
  delay(500);
  backward(0, 0);
  delay(300);

  left_45();  

  forward_and_taxiing(0, 0);
  delay(400);
  

}

void turn_normalizing(float x){

  int del = 25;

  if (x < 0){
    digitalWrite(direction_R, HIGH);
    analogWrite(speed_r_port, 165);
    digitalWrite(direction_L, LOW);
    analogWrite(speed_l_port, 165);
    delay(del);
    stop1();

  }
  else if (x > 0) {
    digitalWrite(direction_L, HIGH);
    analogWrite(speed_l_port, 165);
    digitalWrite(direction_R, LOW);
    analogWrite(speed_r_port, 165);
    delay(del);
    stop1();
  }
  else{
    stop1();
  }
}



void setup() {
  Serial.begin(115200);  // Начинаем работу с последовательным портом

  inputString.reserve(150); // Резервирование в 150 символов для объекта-строки "inputString"

  pinMode(trigPin, OUTPUT); // Установка trigPin как выход
  pinMode(echoPin, INPUT); // Установка echoPin как вход

  servo1.attach(servoPin); // Инициализация servo-привода на 13 pin'e
  capture();

  pinMode(direction_R,OUTPUT);
  pinMode(direction_L,OUTPUT);
  pinMode(speed_r_port,OUTPUT);
  pinMode(speed_l_port,OUTPUT);
    
  pinMode(in1, OUTPUT);
  pinMode(in2, OUTPUT);
  pinMode(in3, OUTPUT);
  pinMode(in4, OUTPUT);
}


void loop() {

  // Обработка входящего сообщения
  if (stringComplete) {
    // Обновление времени, когда было полученно последнее сообщение
    message_timer = millis();

    // В этом блоке происходит деление исходной строки, полученной из serial-порта на числа в формате строк (массивы char)
    unsigned int i = 0;
    // Обработка 1 числа
    for (i = 1; i < inputString.length() - 1; i++) {
      input_m[0] += inputString[i];
      if (inputString[i] == ';') break;
    }

    // Обработка 2 числа
    for (i = i + 1; i < inputString.length() - 1; i++) {
      input_m[1] += inputString[i];
      if (inputString[i] == ';') break;
    }

    // Обработка 3 числа
    for (i = i + 1; i < inputString.length() - 1; i++) {
      input_m[2] += inputString[i];
      if (inputString[i] == ';') break;
    }

    // Обработка 4 числа
    for (i = i + 1; i < inputString.length() - 1; i++) {
      input_m[3] += inputString[i];
      if (inputString[i] == ';') break;
    }

    // Выделение места для "развертки" массива из массивов
    char str0[input_m[0].length()];
    char str1[input_m[1].length()];
    char str2[input_m[2].length()];
    char str3[input_m[3].length()];

    // "Развертка" массива из массивов
    for (i = 0; i < input_m[0].length(); i++) { str0[i] = input_m[0][i]; }
    for (i = 0; i < input_m[1].length(); i++) { str1[i] = input_m[1][i]; }
    for (i = 0; i < input_m[2].length(); i++) { str2[i] = input_m[2][i]; }
    for (i = 0; i < input_m[3].length(); i++) { str3[i] = input_m[3][i]; }

    // Сброс буфера
    input_m[0] = "";
    input_m[1] = "";
    input_m[2] = "";
    input_m[3] = "";
    inputString = "";
    stringComplete = false;

    // Перобразование чисел-строк в числа-int и числа-float
    char function_to_move = (char)atof(str0);
    char function_to_grab = (char)atof(str1);
    float speed_to_right_wheels = (float)atof(str2);
    float speed_to_left_wheels = (float)atof(str3);



    RIGHT = (int)function_to_grab;
    LEFT = (int)speed_to_right_wheels;
    DELAY = (int)speed_to_left_wheels;    

    
    if ((function_to_move == 0) && (function_to_grab == 0)){
      speed_to_right_wheels = mapFloat(speed_to_right_wheels, 0.0, 1.0, 0.0, 255.0-(float)min_speed); // 85 - max_speed - min_speed !!!!!
      speed_to_left_wheels = mapFloat(speed_to_left_wheels, 0.0, 1.0, 0.0, 255.0-(float)min_speed);
      forward_and_taxiing((int)speed_to_right_wheels, (int)speed_to_left_wheels);

    }

    switch (function_to_grab) {
      case 1:
        take_from_a_platform();
        break;
      case 2:
        moving_to_a_corner();
        break;
      case 3:
        special();
        break;
      case 4:
        capture();
        up();
        break;
      }


        
    switch (function_to_move) {
      case 1:
        stop_delay();
        forward_and_taxiing(0, 0);
        delay(1500);
        right_90();
        stop_delay();
        forward_and_taxiing(0, 0);
        delay(400);
        stop_delay();
        break;

      case 2:
        stop_delay();
        forward_and_taxiing(0, 0);
        delay(1500);
        left_90();
        stop_delay();
        forward_and_taxiing(0, 0);
        delay(400);
        stop_delay();
        break;

      /*
      case 3:
        detour();
        break;
      */
      case 4:
        stop_delay();
        turing_back();
        stop_delay();
        break;
      

      /*
      case 5:
        detour_r();
        break;

      case 6:
        detour_l();
        break;
      */

      /*
      case 7:
        reverse_capture_1();
        break;
      */

      // Отладочная ветвь №1 НАЧАЛО
      case 8:
        // Нужен для обработки функции
        special();
        stop1();
        break;

      case 9:
        // Нужен для обработки функции
        RIGHT = function_to_grab;
        LEFT = speed_to_right_wheels;
        DELAY = speed_to_left_wheels;
        releases();
        delay(1500);
        capture();
        stop1();
        break;

      case 10:
      //   // Нужен для обработки функции
      //   RIGHT = function_to_grab;
      //   LEFT = speed_to_right_wheels;
      //   DELAY = speed_to_left_wheels;
      //   releases();
      //   forward_and_taxiing(0, 0);
      //   for (; filteredDist > LEFT;) {
      //     calc_and_pub_dist();
      //     delay(RIGHT);
      //   }
      //   stop1();
      //   delay(500);
      //   capture();
      //   break;
      // // Отладочная ветвь №1 КОНЕЦ
        right_45();

      case 11:
        turn_normalizing(speed_to_right_wheels);
        break;

      // Отладочная ветвь №2 НАЧАЛО
      case 12:
        up();
        break;

      case 13:
        turing_back();
        break;
        
      case 20:
        left_45();
        break;
    // Отладочная ветвь №2 КОНЕЦ
    } 
  }

  time_now = millis();


  // Расчёт и отправка значений с сонара
  if (time_now - sonar_timer > sonar_timer_timeout){  
    sonar_timer = millis();
    calc_and_pub_dist();
  }

  // Аварийная останвка, если он не получает сообщения 1 сек
  if (time_now - message_timer > emergency_timer_timeout){
    stop1();
  }

}
