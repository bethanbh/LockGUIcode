
#define numberofpins 8
#define enpin 33
#define chanA 50
#define chanB 49
#define chanC 48
#define BAUD_RATE_VALUE 230400
#define SERIAL_BUFFER_SIZE 64


volatile uint16_t LOW_THRESHOLD = 3000;// Minimum value of the incoming peak that stops the sampling 
volatile uint16_t HIGH_THRESHOLD = 4000;//Minimum value of the incoming peak that triggers the sampling 
volatile int interruptcount = 0;
volatile int interruptcount6 = 0;
volatile bool A0plug = LOW;
volatile bool A1plug = LOW;
volatile bool A0unplug = LOW;
volatile bool A1unplug = LOW;
//volatile float chnlvalue;


float val0;
float val1;
//float val2;
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

float pulse1len = 5000;
float pulsesep = 1000;
float pulse2len = 5000;
float gap1 = 10000;
float gap2 = 10000;

//testingloop
unsigned long previoustime = 0;
unsigned long currenttime;

unsigned long previoustime2 = 0;
unsigned long currenttime2;

unsigned long starttime;
unsigned long keeptingtrack;

volatile int chnltag;
volatile int chnlvalue;

float DACvalue;

volatile bool flag;

//bool chnlstatus;
//float chnlvalue;

volatile int A0status;
volatile int A1status;

int val;
int val2;

volatile int interruptcounter = 0;

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

  
  
  digitalWrite(enpin, LOW);
  digitalWrite(chanA, LOW);
  digitalWrite(chanB, LOW);
  digitalWrite(chanC, HIGH);


  pinMode(38, OUTPUT);
  pinMode(39, OUTPUT);

  analogWrite(DAC1, 1000);
  analogWrite(A8, 1000);

  addressDecoderSetup();
  ADC_setup();

  starttime = millis();

  SerialUSB.println(interruptcount);
    SerialUSB.println(interruptcount6);
  
}

void loop() {
  // put your main code here, to run repeatedly:
  
  currenttime = millis();


  if ((currenttime == starttime) || (currenttime - previoustime <= pulse1len)){
    digitalWrite(38, HIGH);
  //  SerialUSB.println("peak 1 high");
    }

    if ((currenttime - previoustime > pulse1len) && (currenttime - previoustime - pulse1len <= gap1 )){
      digitalWrite(38, LOW);
    //SerialUSB.println("peak 1 low");
    
  }


    if (((currenttime - previoustime -pulse1len) > gap1) && ((currenttime - previoustime -pulse1len -gap1) <= pulse2len)){
      digitalWrite(39, HIGH);
    //SerialUSB.println("peak 2 high");
  }
      if (((currenttime - previoustime -pulse1len -gap1) > pulse2len) && ((currenttime - previoustime -pulse1len -gap1 -pulse2len) <= gap2)){
      digitalWrite(39, LOW);
    //SerialUSB.println("peak 2 low");
  }
        if (((currenttime - previoustime -pulse1len -gap1 -pulse2len) > gap2)){
      previoustime = currenttime;
  }
    

    if (A1plug){
    SerialUSB.println("A1 plugged in");
    SerialUSB.println(A0status);
    SerialUSB.println(A1status);
    SerialUSB.println(chnltag);
    SerialUSB.println(chnlvalue);
    //SerialUSB.println(interruptcount);
    //SerialUSB.println(interruptcount6);
    A1plug = LOW;
  }
    if (A1unplug){
    SerialUSB.println("A1 unplugged");
    SerialUSB.println(A0status);
    SerialUSB.println(A1status);
    SerialUSB.println(chnltag);
    SerialUSB.println(chnlvalue);
    //SerialUSB.println(interruptcount);
    //SerialUSB.println(interruptcount6);*/
    A1unplug = LOW;
  }

  
     if (A0plug){
    SerialUSB.println("A0 plugged in");
    SerialUSB.println(A0status);
    SerialUSB.println(A1status);
    SerialUSB.println(chnltag);
    SerialUSB.println(chnlvalue);
    //SerialUSB.println(interruptcount);
    //SerialUSB.println(interruptcount6);
    A0plug = LOW;
  }
  
    if (A0unplug){
    SerialUSB.println("A0 unplugged");
    SerialUSB.println(A0status);
    SerialUSB.println(A1status);
    SerialUSB.println(chnltag);
    SerialUSB.println(chnlvalue);
    //SerialUSB.println(interruptcount);
    //SerialUSB.println(interruptcount6);*/
    A0unplug = LOW;
  }



UpdateInternalValues();
SerialRead();

   }
    

void UpdateInternalValues(){
    val0 = adc_get_channel_value(ADC, ADC_CHANNEL_5);
    val1 = adc_get_channel_value(ADC, ADC_CHANNEL_4);
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

  ADC->ADC_EMR |= ADC_EMR_CMPALL;

  //enable the TAG function in EMR so the data is tagged with the channel that it's on (ie on the CHNB bits on ADC_LCDR)
  ADC->ADC_EMR |= ADC_EMR_TAG;

   ADC->ADC_CHER = ADC_CHER_CH4 | ADC_CHER_CH5; 

  //adc_set_comparison_channel(ADC, ADC_CHANNEL_7);
  
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
  if (((adc_get_status(ADC) & ADC_ISR_COMPE) == ADC_ISR_COMPE)) 
 { chnltag = adc_get_tag(ADC);
     chnlvalue = REG_ADC_LCDR & 0x00000FFF;
    NVIC_ClearPendingIRQ(ADC_IRQn); 
    //flag = HIGH;
   
    if (!(ADC->ADC_EMR & 0x01)){
    if (chnlvalue <3000) 
    { 
      
      if (chnltag == 5) 
      {  
        adc_set_comparison_mode(ADC, ADC_EMR_CMPMODE_HIGH);
        adc_enable_channel(ADC, ADC_CHANNEL_4);
        interruptcount++;  
        A0status = 0;
        A0unplug = HIGH;
      }

      if (chnltag == 4) 
      {
        adc_set_comparison_mode(ADC, ADC_EMR_CMPMODE_HIGH);
        adc_enable_channel(ADC, ADC_CHANNEL_5);
        interruptcount6++;
        A1status = 0;
        A1unplug = HIGH;
      }
    }}
    else{
    if (chnlvalue > 4000){
    
      if (chnltag == 5) 
      { 
        adc_disable_channel(ADC, ADC_CHANNEL_4);
        adc_set_comparison_mode(ADC, ADC_EMR_CMPMODE_LOW);
        interruptcount++;
        A0status = 1;
        A0plug = HIGH;
      }
      if (chnltag == 4) 
      {
        adc_disable_channel(ADC, ADC_CHANNEL_5);
        adc_set_comparison_mode(ADC, ADC_EMR_CMPMODE_LOW);
        interruptcount6++;  
        A1status = 1;
        A1plug = HIGH;}
      }
    }
    


    //trying a new approach

   /* if (chnltag == 4){

    if (!(ADC->ADC_EMR & 0x01)){
      
      adc_set_comparison_mode(ADC, ADC_EMR_CMPMODE_HIGH);
        adc_enable_channel(ADC, ADC_CHANNEL_5);
        interruptcount6++;
        A1status = 0;
        A1unplug = HIGH;
    }
    else {
      adc_disable_channel(ADC, ADC_CHANNEL_5);
        adc_set_comparison_mode(ADC, ADC_EMR_CMPMODE_LOW);
        interruptcount6++;  
        A1status = 1;
        A1plug = HIGH;
    }
      
    }

    if (chnltag == 5){
      
      if (!(ADC->ADC_EMR & 0x01)){
        adc_set_comparison_mode(ADC, ADC_EMR_CMPMODE_HIGH);
        adc_enable_channel(ADC, ADC_CHANNEL_4);
        interruptcount++;  
        A0status = 0;
        A0unplug = HIGH;
      }
      else{
        adc_disable_channel(ADC, ADC_CHANNEL_4);
        adc_set_comparison_mode(ADC, ADC_EMR_CMPMODE_LOW);
        interruptcount++;
        A0status = 1;
        A0plug = HIGH;
      }
    }*/

    
    
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
//      SerialUSB.print(delaytime);
      SerialUSB.print(val0,4);
      SerialUSB.print(",");
      SerialUSB.print(val1,4);
      SerialUSB.print(",");
      SerialUSB.print(A0status);
      SerialUSB.print(",");
      SerialUSB.print(A1status);
      SerialUSB.print("\n");
      break;
    
    default:
      //SerialUSB.print("2\n"); // Variable not defined
      return;
  }
  //SerialUSB.print("0\n");
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
  
