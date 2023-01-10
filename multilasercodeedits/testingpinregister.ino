
#define numberofpins 8
#define enpin 33
#define chanA 50
#define chanB 49
#define chanC 48
#define BAUD_RATE_VALUE 230400
#define SERIAL_BUFFER_SIZE 64

float val0;
float val1;
float val2;
float val3;
float val4;
float val5;
float val6;
float val7;

int actualA;
int actualB;
int actualC;

//Communication variables
const char message_length = SERIAL_BUFFER_SIZE;
char message_tracker = 0;
char message[message_length];

char channelnumber = 0;
int outputvalue = 1000;

float pulse1len = 500;
float pulsesep = 1000;
float pulse2len = 100;

//testingloop
unsigned long previoustime = 0;

unsigned long currenttime;

int delaytime;

int loopcounter = 1;

float DACvalue;



void setup() {
  //setting up the serial communication
  Serial.begin(BAUD_RATE_VALUE);
  while(!SerialUSB);
  reset_message_buffer(); 
  //Serial.println("Starting up");
  
  analogWriteResolution(12);
  analogReadResolution(12);

  pinMode(chanA, OUTPUT);
  pinMode(chanB, OUTPUT);
  pinMode(chanC, OUTPUT);
  pinMode(enpin, OUTPUT);
  pinMode(DAC0, OUTPUT);
  pinMode(DAC1, OUTPUT);
  pinMode(A0, INPUT);
  pinMode(A1, INPUT);
  pinMode(A2, INPUT);
  pinMode(A3, INPUT);
  pinMode(A4, INPUT);
  pinMode(A5, INPUT);
  pinMode(A6, INPUT);
  pinMode(A7, INPUT);
  pinMode(A8, OUTPUT);
  pinMode(A9, OUTPUT);
  
  digitalWrite(enpin, HIGH);
  digitalWrite(chanA, HIGH);
  digitalWrite(chanB, LOW);
  digitalWrite(chanC, LOW);
  digitalWrite(enpin, LOW);

  pinMode(47, INPUT);

  //SerialUSB.print(channelnumber);
  //selectChannel(channelnumber);
    
  //analogWrite(DAC0, outputvalue);
  /*selectChannel(channelnumber);
    
  analogWrite(DAC0, outputvalue);*/
  
  
  
}

void loop() {
  // put your main code here, to run repeatedly:
  //before the loop in delay times, send 1000 to channel 0 to kick us off
  //digitalWrite(enpin, HIGH);

  addressDecoderSetup();
  selectChannel(3);


  DACvalue = digitalRead(47);
  SerialUSB.println(DACvalue);

  
  /*selectChannel(0);
  delay(5)
  analogWrite(DAC1, 2000);
  delay(5);
  selectChannel(1);
  delay(5)
  analogWrite(DAC1, 1000);
  delay(5);*/
  
  /*//digitalWrite(enpin, LOW);
  //delay(5);
  DACvalue = analogRead(A7);
  SerialUSB.println(DACvalue);
  delay(10); 
  //digitalWrite(enpin, HIGH);
  selectChannel(1);
  analogWrite(DAC1, 1000);
  //digitalWrite(enpin, LOW);
  //delay(5);
  
  DACvalue = analogRead(A7);
  SerialUSB.println(DACvalue);
  delay(10);*/

  
  /*analogWrite(DAC1, 900);
  DACvalue = analogRead(A0);
  SerialUSB.println(DACvalue);
  delayMicroseconds(10);
  analogWrite(DAC1, 4095);
  DACvalue = analogRead(A0);
  SerialUSB.println(DACvalue);
  delayMicroseconds(10);*/
  /*analogWrite(DAC1, 2000);
  DACvalue = analogRead(A0);
  SerialUSB.println(DACvalue);
  delayMicroseconds(10);*/
 /*for (char i = 0; i < 256; i = i + 1) {
  //SerialUSB.println(50*i);
      delaytime = 100*i;
      
      //do the pulse
      analogWrite(DAC1, 1000);
      delayMicroseconds(5000);
      selectChannel(1); //send signal to channel 1
      delay(100);

      analogWrite(DAC1, 2000);
      selectChannel(2); //send signal back to channel 2
      

      
      
    //pulseChannel(pulse1len, pulse2len, pulsesep);
      delayMicroseconds(delaytime);
      //set the internal values to be the values after this delay time 
      UpdateInternalValues();
      //now want to give opportunities for the readings to happen- ie serialread just checks if python is asking a question
      delay(50);
      SerialRead();
      delay(50);
      SerialRead();
      delay(50);
      SerialRead();
      delay(50);
      SerialRead();
      delay(50);
      SerialRead();

      
    
  }
  
  loopcounter++;*/ }
    

void selectChannel(int chnl){
//there's gotta be a more efficient way to do this but here we are
  if (chnl == 0){
    REG_PIOD_ODSR = 0x00000000;
  }
  if (chnl == 1){
    REG_PIOD_ODSR = 0x00000001;
  }
  if (chnl == 2){
    REG_PIOD_ODSR = 0x00000002;
  }
  if (chnl == 3){
    REG_PIOD_ODSR = 0x00000003;
  }
  if (chnl == 4){
    REG_PIOD_ODSR = 0x00000004;
  }
  if (chnl == 5){
    REG_PIOD_ODSR = 0x00000005;
  }
  if (chnl == 6){
    REG_PIOD_ODSR = 0x00000006;
  }
  if (chnl == 7){
    REG_PIOD_ODSR = 0x00000007;
  }}
  
  
void addressDecoderSetup(){
  //enable pin 25, and set as output
  PIOD->PIO_PER = PIO_PD0;
  PIOD->PIO_OER = PIO_PD0;
  //enable pin 26, and set as output
  PIOD->PIO_PER = PIO_PD1;
  PIOD->PIO_OER = PIO_PD1;
  //enable pin 27, and set as output
  PIOD->PIO_PER = PIO_PD2;
  PIOD->PIO_OER = PIO_PD2;

  //enable the address decoder pins to have their outputs changed
  REG_PIOD_OWER = 0x00000007;

  pmc_enable_periph_clk(ID_PIOD);

  //also enable and set the INH pin low (35- PC3)
  //slightly concerned that the PIOC_handler function is a whole separate thing in the code and that might mess things up
  PIOC->PIO_PER = PIO_PC3;
  PIOC->PIO_OER = PIO_PC3;
  //want output to be low to enable the chip
  REG_PIOC_CODR = 0x00000008
}
  


/*void selectChannel(int chnl){
  int A = bitRead(chnl, 0);
  int B = bitRead(chnl, 1);
  int C = bitRead(chnl, 2);

  digitalWrite(chanA, A);
  digitalWrite(chanB, B);
  digitalWrite(chanC, C);

  //SerialUSB.print("Channel ");
  //SerialUSB.print(chnl );
  //SerialUSB.print(" (");
  //SerialUSB.print(C);
  //SerialUSB.print(",");
  //SerialUSB.print(B);
  //SerialUSB.print(",");
  //SerialUSB.print(A);
  //SerialUSB.print(")");
  //SerialUSB.println();
  
  actualA = digitalRead(chanA);
  actualB = digitalRead(chanB);
  actualC = digitalRead(chanC);
  
  //SerialUSB.print("ACTUAL ");
  //SerialUSB.print(" (");
  //SerialUSB.print(actualC);
  //SerialUSB.print(",");
  //SerialUSB.print(actualB);
  //SerialUSB.print(",");
  //SerialUSB.print(actualA);
  //SerialUSB.print(")");
  //SerialUSB.println();
  
}*/


void reset_message_buffer()
{
  //SerialUSB.println(message);
  for (int i = 0; i < message_length; i++)
  {
    message[i] = '\0';
  }
  message_tracker = 0;
  //SerialUSB.print("Message after resetting: ");
  //SerialUSB.println(message);
  //SerialUSB.println("got to reset");
}

void message_parser(bool complete_message)
{
  if(complete_message)
  {
    // preprocess
    char action = message[0];
    char variable = message[1];
    //SerialUSB.println("start");
    //SerialUSB.println(action);
    //SerialUSB.println(variable);
    //SerialUSB.println("end");
    switch (action)
    {
      case 'm':   // m for modify
        {
          //SerialUSB.println(message);
          char value_chars[message_tracker-1];
          
          
          for (char i = 0; i < message_tracker-2; i++)
          {
            value_chars[i] = message[i+2];
          }
          value_chars[message_tracker-1] = '\0';
          float value = atof(value_chars);
          //
          
          modify_variable(variable, value);
        }
        break;
      case 'o':   // m for modify
        {
          //SerialUSB.println(message);
          char value_chars[message_tracker-1];
          char chnlnumvalue = message[2];
          
          for (char i = 0; i < message_tracker-2; i++)
          {
            value_chars[i] = message[i+3];
          }
          value_chars[message_tracker-1] = '\0';
          float value = atof(value_chars);
          //
          
          
          modify_variable2(variable, chnlnumvalue, value);
        }
        break;
      case 'p':   // p for print
        print_variable(variable);
        break;
      default: ;
        //SerialUSB.print("1\n"); // command not recognised
    }
  }
  // when done, clear the message buffer so that it's ready for new incoming commands.
  reset_message_buffer();
  clear_SerialUSB_buffer();
  //SerialUSB.println("check values");
  //SerialUSB.println(channelnumber);
  //SerialUSB.println(outputvalue);
}

void clear_SerialUSB_buffer()
{
  while(SerialUSB.available() > 0)
  {
    SerialUSB.read();
  }
}

void modify_variable2(char variable, char chnlnumvalue, float value)
{
  switch (variable)
  {
    case 'a':
      channelnumber = chnlnumvalue;
      outputvalue = value;
      //SerialUSB.println(channelnumber);
      //seSerialUSB.println(value);
      break;
    default:
      //SerialUSB.print("2\n"); // Variable not defined
      return;
  }
  //SerialUSB.print("0\n");
}

void modify_variable(char variable, float value)
{
  switch (variable)
  {
    case 'a':
      channelnumber = value;
      break;
    case 'b':
      outputvalue = value;
      break;
    //case 'c':
    //  channelnumber = 
    default:
      //SerialUSB.print("2\n"); // Variable not defined
      return;
  }
  //SerialUSB.print("0\n");
}

void print_variable(char variable)
{
  switch (variable)
  {
    case 'a':
      SerialUSB.print(val0,4);
      SerialUSB.print("\n");
      break;
    case 'b':
      SerialUSB.print(val1,4);
      SerialUSB.print("\n");
      break;
    case 'c':
      SerialUSB.print(val2,4);
      SerialUSB.print("\n");
      break;
    case 'd':
      SerialUSB.print(val3,4);
      SerialUSB.print("\n");
      break;
    case 'e':
      SerialUSB.print(val4,4);
      SerialUSB.print("\n");
      break;
    case 'f':
      SerialUSB.print(val5,4);
      SerialUSB.print("\n");
      break;
    case 'g':
      SerialUSB.print(val6,4);
      SerialUSB.print("\n");
      break;
    case 'h':
      SerialUSB.print(val7,4);
      SerialUSB.print("\n");
      break;
    case 'i':
      //channelnumber = 4;
      SerialUSB.print(channelnumber);
      SerialUSB.print("\n");
      break;
    case 'j':
      SerialUSB.print(outputvalue);
      SerialUSB.print("\n");
      break;
     case 'k':
      SerialUSB.print(channelnumber);
      SerialUSB.print("\n");
      SerialUSB.print(val0,4);
      SerialUSB.print(",");
      SerialUSB.print(val1,4);
      SerialUSB.print(",");
      SerialUSB.print(val2,4);
      SerialUSB.print(",");
      SerialUSB.print(val3,4);
      SerialUSB.print(",");
      SerialUSB.print(val4,4);
      SerialUSB.print(",");
      SerialUSB.print(val5,4);
      SerialUSB.print(",");
      SerialUSB.print(val6,4);
      SerialUSB.print(",");
      SerialUSB.print(val7,4);
      SerialUSB.print("\n");
      break;
    case 'l':
      SerialUSB.print(delaytime);
      SerialUSB.print(",");
      SerialUSB.print(val0,4);
      SerialUSB.print(",");
      SerialUSB.print(val1,4);
      SerialUSB.print(",");
      SerialUSB.print(val2,4);
      break;
    
    default:
      //SerialUSB.print("2\n"); // Variable not defined
      return;
  }
  //SerialUSB.print("0\n");
}


void pulseChannel(float pulse1len, float pulse2len, float pulsesep){
  //pulse channel 1 on
  
    
  digitalWrite(chanA, HIGH);

  //SerialUSB.println("channel 1 pulse");
  UpdateInternalValues();
  SerialRead();

  //delay(pulse1len);

  //turn the pulse off
  digitalWrite(chanA, LOW);

  //SerialUSB.println("no pulse");
  
  UpdateInternalValues();
  SerialRead();

  //separation between the two pulses
  //delay(pulsesep);

  //pulse channel 2 on
  digitalWrite(chanB, HIGH);

  //SerialUSB.println("channel 2 pulse");
  
  UpdateInternalValues();
  SerialRead();
    
  //delay(pulse2len);

  //turn the pulse off
  digitalWrite(chanB, LOW);
  
  UpdateInternalValues();
  SerialRead();
}

  
  
void UpdateInternalValues(){
    val0 = analogRead(A0);
    //SerialUSB.println(val0);
    val1 = analogRead(A1);
    //SerialUSB.println(val1);
    val2 = analogRead(A2);
    //SerialUSB.println(val2);
    val3 = analogRead(A3);
    //SerialUSB.println(val3);
    val4 = analogRead(A4);
    //SerialUSB.println(val4);
    val5 = analogRead(A5);
    //SerialUSB.println(val5);
    val6 = analogRead(A6);
    //SerialUSB.println(val6);
    val7 = analogRead(A7);
    //SerialUSB.println(val7);
  }


void SerialRead(){
  
    if (SerialUSB.available() > 0)
  {
    char temp_byte = SerialUSB.read();
    if (temp_byte == '!') // check for msg termination character
    {
      message_parser(true); // successfully received a message, let the parser take care of it
    }
    else
    {
      if (temp_byte != '\n') // for some unknown reason sometimes linefeed characters don't get removed from the input buffer, we just ignore these.
      {
        message[message_tracker++] = temp_byte;
        if (message_tracker > message_length) message_parser(false); // the incoming message appears to be longer than what we expect, likely missed a termination character.
      }
    }

}

}
  
