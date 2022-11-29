
#define numberofpins 8
#define enpin 33
#define chanA 50
#define chanB 49
#define chanC 48
#define BAUD_RATE_VALUE 230400
#define SERIAL_BUFFER_SIZE 64

volatile uint16_t LOW_THRESHOLD = 3500;// Minimum value of the incoming peak that stops the sampling 
volatile uint16_t HIGH_THRESHOLD = 4000;//Minimum value of the incoming peak that triggers the sampling 
int interruptcount;
int interruptcount6;
volatile bool flag;

int val0;
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

float pulse1len = 2000;
float pulsesep = 1000;
float pulse2len = 100;

//testingloop
unsigned long previoustime = 0;

unsigned long currenttime;

int delaytime;

int loopcounter = 1;

float DACvalue;

bool chnlstatus;
float chnlvalue;

int val;

volatile bool A0plug = LOW;
volatile bool A1plug = LOW;
volatile bool A0unplug = HIGH;
volatile bool A1unplug = HIGH;

volatile int chnlvalue;


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
  digitalWrite(chanB, HIGH);
  digitalWrite(chanC, LOW);
  digitalWrite(enpin, LOW);

  pinMode(47, INPUT);

  analogWrite(DAC1, 1000);
  analogWrite(A8, 1000);

  addressDecoderSetup();
  ADC_setup();
  selectChannel(3);
  
}

void loop() {
  // put your main code here, to run repeatedly:
  

  currenttime = millis();
  chnlvalue = REG_ADC_LCDR & 0x00000FFF;

  if (currenttime - previoustime >= pulse1len){
    previoustime = currenttime;
    //SerialUSB.println(digitalRead(A0));
    //SerialUSB.println(digitalRead(chanA));
    if (adc_get_channel_value(ADC, ADC_CHANNEL_7) < 4000){
      digitalWrite(chanA, HIGH);
      SerialUSB.println("go high");
      SerialUSB.println(adc_get_channel_value(ADC, ADC_CHANNEL_7));
    } else{
      digitalWrite(chanA, LOW);
      SerialUSB.println("go low");
      SerialUSB.println(adc_get_channel_value(ADC, ADC_CHANNEL_7));
    }
  }


         if (A0plug){
    SerialUSB.println("Interrupt triggered: HT");
    SerialUSB.println(adc_get_channel_value(ADC, ADC_CHANNEL_7));

    A0plug = LOW;
  }
    if (A0unplug){
    SerialUSB.println("Interrupt triggered: LT");
    SerialUSB.println(adc_get_channel_value(ADC, ADC_CHANNEL_7));

    A0unplug = LOW;
  }



if (flag){
  SerialUSB.println("woah interrupt!");
  flag = LOW;
}
  
    //delay(200);
    //this is the part we essentially want to happen all the time   
   //UpdateInternalValues();
   //val0 = analogRead(A0);
   //SerialUSB.println(val0);
   // SerialRead();
    


/*
  SerialUSB.println("status");
  chnlstatus = adc_get_channel_status(ADC, ADC_CHANNEL_0);
  SerialUSB.print("Ch 0:");
  SerialUSB.println(chnlstatus);
  chnlstatus = adc_get_channel_status(ADC, ADC_CHANNEL_1);
  SerialUSB.print("Ch 1:");
  SerialUSB.println(chnlstatus);
  chnlstatus = adc_get_channel_status(ADC, ADC_CHANNEL_2);
  SerialUSB.print("Ch 2:");
  SerialUSB.println(chnlstatus);
  chnlstatus = adc_get_channel_status(ADC, ADC_CHANNEL_3);
  SerialUSB.print("Ch 3:");
  SerialUSB.println(chnlstatus);
  chnlstatus = adc_get_channel_status(ADC, ADC_CHANNEL_4);
  SerialUSB.print("Ch 4:");
  SerialUSB.println(chnlstatus);
  chnlstatus = adc_get_channel_status(ADC, ADC_CHANNEL_5);
  SerialUSB.print("Ch 5:");
  SerialUSB.println(chnlstatus);
  chnlstatus = adc_get_channel_status(ADC, ADC_CHANNEL_6);
  SerialUSB.print("Ch 6:");
  SerialUSB.println(chnlstatus);
  chnlstatus = adc_get_channel_status(ADC, ADC_CHANNEL_7);
  SerialUSB.print("Ch 7:");
  SerialUSB.println(chnlstatus);

  SerialUSB.println("value");
  chnlvalue = adc_get_channel_value(ADC, ADC_CHANNEL_0);
  SerialUSB.print("Ch 0:");
  SerialUSB.println(chnlvalue);
  chnlvalue = adc_get_channel_value(ADC, ADC_CHANNEL_1);
  SerialUSB.print("Ch 1:");
  SerialUSB.println(chnlvalue);
  chnlvalue = adc_get_channel_value(ADC, ADC_CHANNEL_2);
  SerialUSB.print("Ch 2:");
  SerialUSB.println(chnlvalue);
chnlvalue = adc_get_channel_value(ADC, ADC_CHANNEL_3);
  SerialUSB.print("Ch 3:");
  SerialUSB.println(chnlvalue);
chnlvalue = adc_get_channel_value(ADC, ADC_CHANNEL_4);
  SerialUSB.print("Ch 4:");
  SerialUSB.println(chnlvalue);
chnlvalue = adc_get_channel_value(ADC, ADC_CHANNEL_5);
  SerialUSB.print("Ch 5:");
  SerialUSB.println(chnlvalue);
chnlvalue = adc_get_channel_value(ADC, ADC_CHANNEL_6);
  SerialUSB.print("Ch 6:");
  SerialUSB.println(chnlvalue);
chnlvalue = adc_get_channel_value(ADC, ADC_CHANNEL_7);
  SerialUSB.print("Ch 7:");
  SerialUSB.println(chnlvalue);



  SerialUSB.println("tag");
  SerialUSB.println(adc_get_tag(ADC));

  if (interruptcount6 == 1){
    SerialUSB.println("Not plugged in, A1");
  }
  if (interruptcount == 3){
    SerialUSB.println("Not plugged in, A0");
  }
  if (interruptcount6 == 0){
    SerialUSB.println("Plugged in, A1");
  }
  if (interruptcount == 2){
    SerialUSB.println("plugged in, A0");
  }*/

  //delay(50);
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
  REG_PIOC_CODR = 0x00000008;
}


  
void ADC_setup(){
  //ADC Configuration
  analogReadResolution(12);
  adc_init(ADC, SystemCoreClock, ADC_FREQ_MAX, ADC_STARTUP_FAST);
  adc_configure_timing(ADC, 0, ADC_SETTLING_TIME_3, 1);
  ADC->ADC_MR |= 0x80;

  //want to enable the use of sequence registers
 // ADC->ADC_MR |= ADC_MR_USEQ;

  //enable the TAG function in EMR so the data is tagged with the channel that it's on (ie on the CHNB bits on ADC_LCDR)
  ADC->ADC_EMR |= ADC_EMR_TAG;

  //need to set the sequence register first I think?
  //ADC->ADC_SEQR1 = 0x00000076; //aiming for this to sample channel 6 and 7 (which are A0 and A1)

  //so then to enable these channels, need to enable channel 0 and 1 in the CHER (bc in 0 and 1 position in the SEQR register)
 // ADC->ADC_CHER = 0x00000003; 
  //channel 6 (A1) is technically CH0 here- 7 (A0) is CH1


   ADC->ADC_CHER = ADC_CHER_CH7; //| ADC_CHER_CH6; 

  adc_set_comparison_channel(ADC, ADC_CHANNEL_7);
  //don't want just one comparsion channel, we want to compare on all activated channels
  //ADC->ADC_EMR |= ADC_EMR_CMPALL;
  //hoping this sets it to be all channels


  
  //now is the question of whether this applies to all of the channels
  adc_set_comparison_mode(ADC, ADC_EMR_CMPMODE_LOW);
  //EMR is the extended mode register
  //CMPMODE - comparsion mode, when HIGH- get and event when converted data is higher than HT
  adc_set_comparison_window(ADC, LOW_THRESHOLD, HIGH_THRESHOLD);
  //yeah these functions are buried in the github for SAM chip/due board- link on OneNOte
  adc_enable_interrupt(ADC, ADC_IER_COMPE);
  //IER is interrupt enable register- enabling the comparsion event interrupt*/
  adc_start(ADC);
  //ADC Interrupt NVIC Enable
  pmc_enable_periph_clk(ID_ADC);
  NVIC_DisableIRQ(ADC_IRQn);
  NVIC_ClearPendingIRQ(ADC_IRQn);
  NVIC_SetPriority(ADC_IRQn, 0);
  NVIC_EnableIRQ(ADC_IRQn);
  analogWriteResolution(12);
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




void ADC_Handler()
{ 
  if ((adc_get_status(ADC) & ADC_ISR_COMPE) == ADC_ISR_COMPE) 
 {
     flag = HIGH;
    ADC->ADC_EMR ^= 0x01;//toggles the comparision mode register
    //0x01 is 00000001- so compare last bit of EMR to this 1- set EMR bit to 1 if both different, ie if EMR is 0, will be diff to the 1 here, so set to 1 - ie toggle the EMR
    //last bit of EMR is to do with the CMPMODE- swap from LOW to HIGH
    NVIC_ClearPendingIRQ(ADC_IRQn);

    if (!(ADC->ADC_EMR & 0x01)) // this case applies when triggering event was a HT crossing
    { 
       // SerialUSB.println("Interrupt triggered: HT");  
      interruptcount = HIGH;
      A0plug = HIGH;
      }
      else 
      {
      //SerialUSB.println("Interrupt triggered: LT");  
      interruptcount = LOW;  
      A0unplug = HIGH;
      }
      
    }
    
  }







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
  
