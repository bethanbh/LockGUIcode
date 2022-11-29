 #define SERIAL_BUFFER_SIZE 64 //Arduino DUE SerialUSB buffer size in bytes
//#define USE_PROG_USB
#ifdef USE_PROG_USB
  #define SerialUSB Serial
  #define BAUD_RATE_VALUE 115200
#else
  #define BAUD_RATE_VALUE 230400
#endif
//#define ENABLE_TOGGLE_SWITCH

#define PID_BUFFER 20
#define BUFFER_SIZE  256//Buffer size for each of the 3 peaks 
#define TIME_SIZE 6// There is going to be 6 start time and stop time for sampling. 2 for each peak
// MOVED THESE NEXT TWO TO INTERNAL VARIABLES so that I can modify them from the GUI - AS
//#define LOW_THRESHOLD 100// Minimum value of the incoming peak that stops the sampling 
//#define HIGH_THRESHOLD 180//Minimum value of the incoming peak that triggers the sampling 
/*Change these threshold values to compensate the noise*/
#define THRESHOLD_GAP (HIGH_THRESHOLD-LOW_THRESHOLD)
volatile float CAVITY_REFERENCE = 200000;//t_M that sets the lockpoint for the cavity
#define CAVITY_DACC_OFFSET 2048
#define LASER_DACC_OFFSET 2048
#define HALF_RANGE 2047
float setpoint_change_factor = -341.2;//(beta^-1)*10^6. You can calcuate this using the cavity properties or calibrate through atomic constant measurements like A_{HFS}
float LASER_REFERENCE_MOT = 298500+(4)*22338+(9.9+5.3-1.3-2-4.68-3.2)*setpoint_change_factor;//10^6*r that sets the slave laser setpoint during the 2D MOT stage
volatile float LASER_REFERENCE = 135000; //10^6*r that sets the slave laser setpoint
volatile uint16_t LOW_THRESHOLD = 40;// Minimum value of the incoming peak that stops the sampling 
volatile uint16_t HIGH_THRESHOLD = 160;//Minimum value of the incoming peak that triggers the sampling 

//Define variables that allow for scanning the frequency
volatile uint16_t steps = 1;         // number of steps
volatile uint16_t repeats = 1000;       // number of repeats
volatile float start_frequency  =  0;  // Lower limit of the frequency scan (units of MHz)
volatile float stop_frequency   = 0; // Upper limit of the frequency scan (units of MHz)
volatile uint16_t step_counter =0;//keeps the current step number
volatile uint16_t repeat_counter = 0;//keeps the current repeat number
float frequency_jump = (stop_frequency - start_frequency) / steps; //Units of MHz
boolean jump = LOW;//Determines if the Setpoint jump should be invoked or not
volatile float frequency_changed = 0;


//Define Buffers and variables for storing acquired and processed peak data
uint16_t buf_1[BUFFER_SIZE];//Buffer for M peak
int16_t Length[3];//Keeps track of how many points were acquired for each peak
int16_t derv_buf_1[BUFFER_SIZE];//Buffer for the derivative of M peak
uint16_t buf_2[BUFFER_SIZE];//Buffer for S peak
int16_t derv_buf_2[BUFFER_SIZE];//Buffer for the derivative of S peak
uint16_t buf_3[BUFFER_SIZE];//Buffer for M' peak
int16_t derv_buf_3[BUFFER_SIZE];//Buffer for the derivative of M' peak
int32_t times[TIME_SIZE];//Keeps track of the start and stop time of the DMA acquisition for each peak
int32_t peak_times[3];//The time wrt to the Global digital trigger of the zero-crossing of each peak derivative
boolean flag;//If the program control has entered peakfinder subroutines. HIGH-yes, LOW-no 
volatile int counter;//Enumerates the acquired peak: M(0),S(1),M'(1)

//Define Servo Loop Variables
const float dT = 0.01;
volatile float cavity_K_i = 0.5;
volatile float cavity_K_p = 1.0;
volatile float laser_K_i = 0.5;
volatile float laser_K_p = 1.0;
volatile float laser_K_d = 0.0;
int32_t cavity_error_signal_current;
int32_t cavity_error_signal_prev;
volatile float laser_error_signal_current;
float laser_error_signal_prev;
float laser_integrator = 0;
volatile uint16_t pid_counter = 0;
int32_t delta_cavity = 0;
float delta_laser = 0;
volatile float average_laser_error_signal = 0;
volatile float sum_laser_error_signal = 0;
int32_t cavity_accumulated_error_signal = 0; // This seems pointless to me - MJ
int32_t cavity_control_signal = 0;
int32_t laser_control_signal = 0;
volatile uint16_t average = 1;
boolean bump = LOW;//I use the bump to indicate if the cavity is locked(HIGH) or not(LOW).

//Define variable for acquiring the Start Time of the SysTick/Global Timer
volatile uint32_t start_time = 0;

//Communication variables
const char message_length = SERIAL_BUFFER_SIZE;
char message_tracker = 0;
char message[message_length];

//EDIT: to stop little jumps in V
int32_t Loop_check = 0;
int32_t Loop_checkF = 0;
int32_t time_master_1_1 = 0;
int32_t time_master_1_2 = 0;
int32_t time_follower_1_1 = 0;
int32_t time_follower_1_2 = 0;
int32_t Loop_checkR = 0;
int32_t time_master_2_1 = 0;
int32_t time_master_2_2 = 0;
int32_t peakcheckF = 0;
int32_t peakcheckR1 = 0;
int32_t peakcheckR2 = 0;

float movingavgF = 0;
float movingavgR1 = 0;
float movingavgR2 = 0;
//end edit

void setup()
{
  //initialise SerialUSB comms
  SerialUSB.begin(BAUD_RATE_VALUE);
  while(!SerialUSB);
  reset_message_buffer(); 

  adc_setup();
  global_digital_interrupt_setup();
  dacc_setup();
  setpoint_change_interrupt_setup();

  peak_times[0] = LASER_REFERENCE/3;
  peak_times[1] = peak_times[0]+LASER_REFERENCE;
  peak_times[2] = peak_times[1]+2*LASER_REFERENCE;
}
void loop()
{

 if (counter == 0 && times[1])  //True when the M peak has been acquired
 //think this is true when counter is 0, and when times[1] exists, or is True (if following python logic)
 //so times is an array of 6 values (start and stop time of each peak)- so I guess this is saying, if your counter is zero, and you have the stop time for your first peak, 
 //you can now do the processing to find the peak centre with that data
  {
    peakfinder_1();// Subroutine to process the M peak
  }


  if (counter == 1 && times[3])  //True when the S peak has been acquired
  //assuming times[3] is where the stop time of middle peak is stored
  {
    peakfinder_2();// Subroutine to process the S peak
  }

  if (counter == 2 && times[5])  //True when the M' peak has been acquired
  //assuming times[5] is where the stop time of end peak is stored
  {
    peakfinder_1();// Subroutine to process the M' peak
  }

  // perform messaging in downtime grabbing one character at a time
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





// Edit: trying to make a moving average function
float movingAverage(float value) {
  const byte nvalues = 10;             // Moving average window size

  static byte current = 0;            // Index for current value
  static byte cvalues = 0;            // Count of values read (<= nvalues)
  static float sum = 0;               // Rolling sum
  static float values[nvalues];

  sum += value;

  // If the window is full, adjust the sum by deleting the oldest value
  if (cvalues == nvalues)
    sum -= values[current];

  values[current] = value;          // Replace the oldest with the latest

  if (++current >= nvalues)
    current = 0;

  if (cvalues < nvalues)
    cvalues += 1;

  return sum/cvalues;
}
//end edit



void reset_message_buffer()
{
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
    switch (action)
    {
      case 'm':   // m for modify
        {
          char value_chars[message_tracker-1];
          for (char i = 0; i < message_tracker-2; i++)
          {
            value_chars[i] = message[i+2];
          }
          value_chars[message_tracker-1] = '\0';
          float value = atof(value_chars);
          modify_variable(variable, value);
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
}

void clear_SerialUSB_buffer()
{
  while(SerialUSB.available() > 0)
  {
    SerialUSB.read();
  }
}

void modify_variable(char variable, float value)
{
  switch (variable)
  {
    case 'a':
      cavity_K_p = value;
      break;
    case 'b':
      cavity_K_i = value;
      break;
    case 'c':
      laser_K_p = value;
      break;
    case 'd':
      laser_K_i = value;
      break;
    case 'e':
      LASER_REFERENCE = value;
      break;
    case 'f':
      LOW_THRESHOLD = value;
      adc_set_comparison_window(ADC, LOW_THRESHOLD, HIGH_THRESHOLD);
      break;
    case 'g':
      HIGH_THRESHOLD = value;
      adc_set_comparison_window(ADC, LOW_THRESHOLD, HIGH_THRESHOLD);
      break;
    case 'h':
      bump = (value == 0) ? LOW : HIGH;
      break;
    case 'i':
      CAVITY_REFERENCE = value;
      break;
    case 'k':
      laser_K_d = value;
      break;
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
      SerialUSB.print(cavity_K_p,4);
      SerialUSB.print("\n");
      break;
    case 'b':
      SerialUSB.print(cavity_K_i,4);
      SerialUSB.print("\n");
      break;
    case 'c':
      SerialUSB.print(laser_K_p,4);
      SerialUSB.print("\n");
      break;
    case 'd':
      SerialUSB.print(laser_K_i,4);
      SerialUSB.print("\n");
      break;
    case 'e':
      SerialUSB.print(LASER_REFERENCE,4);
      SerialUSB.print("\n");
      break;
    case 'f':  //peak times
      SerialUSB.print(peak_times[0]);
      SerialUSB.print("\n");
      break;
    case 'g':
      SerialUSB.print(peak_times[1]);
      SerialUSB.print("\n");
      break;
    case 'h':
      SerialUSB.print(peak_times[2]);
      SerialUSB.print("\n");
      break;
    case 'i':
      SerialUSB.print(peak_times[0]);
      SerialUSB.print('=');
      SerialUSB.print(peak_times[1]);
      SerialUSB.print('=');
      SerialUSB.print(peak_times[2]);
      SerialUSB.print("\n");
      break;
    case 'j':
      SerialUSB.print(LOW_THRESHOLD);
      SerialUSB.print("\n");
      break;
    case 'k':
      SerialUSB.print(HIGH_THRESHOLD);
      SerialUSB.print("\n");
      break;
    case 'l':
      SerialUSB.print(laser_error_signal_current);
      SerialUSB.print("\n");
      break;
    case 'm':
      SerialUSB.print(cavity_error_signal_current);
      SerialUSB.print("\n");
      break;
    case 'n':
      SerialUSB.print(counter);
      SerialUSB.print("\n");
      break;
    case 'o':
      SerialUSB.print(Length[0]);
      SerialUSB.print('=');
      SerialUSB.print(Length[1]);
      SerialUSB.print('=');
      SerialUSB.print(Length[2]);
      SerialUSB.print("\n");
      break;
    case 'p':
      SerialUSB.print(CAVITY_REFERENCE);
      SerialUSB.print("\n");
      break;
    case 'q':
      SerialUSB.print(laser_K_d,4);
      SerialUSB.print("\n");
      break;
    default:
      //SerialUSB.print("2\n"); // Variable not defined
      return;
  }
  //SerialUSB.print("0\n");
}

void setpoint_change_interrupt_setup()
{
  //Enable PB14 - digital pin 53, not sure if it's being used on shield??
  PIOB->PIO_PER = PIO_PB14;
  //Set PB14 as input
  PIOB->PIO_ODR = PIO_PB14;
  //Disable pull-up on both pins
  PIOB->PIO_PUDR = PIO_PB14;
  pmc_enable_periph_clk(ID_PIOB);
  NVIC_DisableIRQ(PIOB_IRQn);
  NVIC_ClearPendingIRQ(PIOB_IRQn);
  NVIC_SetPriority(PIOB_IRQn, -2);
  NVIC_EnableIRQ(PIOB_IRQn);


  PIOB->PIO_AIMER = PIO_PB14;
  //Level Select Register
  PIOB->PIO_ESR = PIO_PB14;
  //Rising Edge/High Level Select Register
  PIOB->PIO_REHLSR = PIO_PB14;
  //Finally enable interrupts 
  PIOB->PIO_IER = PIO_PB14;
}




void adc_setup()
{


  //ADC Configuration
  analogReadResolution(12);
  adc_init(ADC, SystemCoreClock, ADC_FREQ_MAX, ADC_STARTUP_FAST);
  adc_configure_timing(ADC, 0, ADC_SETTLING_TIME_3, 1);
  ADC->ADC_CHER = ADC_CHER_CH6; 
  //channel 6 here is PA24 which is analog in 1- the PD input
  ADC->ADC_MR |= 0x80;
  //this part compares 10000000 to the MD part, bit by bit and if any bits are 1, set the ADC_MR bit to be 1
  //ie sets the 8th bit to be 1- this is the FREERUN bit, so sets the ADC to be free running, doesn't wait for a trigger
  adc_set_comparison_channel(ADC, ADC_CHANNEL_6);
  adc_set_comparison_mode(ADC, ADC_EMR_CMPMODE_HIGH);
  //EMR is the extended mode register
  //CMPMODE - comparsion mode, when HIGH- get and event when converted data is higher than HT
  adc_set_comparison_window(ADC, LOW_THRESHOLD, HIGH_THRESHOLD);
  //yeah these functions are buried in the github for SAM chip/due board- link on OneNOte
  adc_enable_interrupt(ADC, ADC_IER_COMPE);
  //IER is interrupt enable register- enabling the comparsion event interrupt
  adc_start(ADC);
  //ADC Interrupt NVIC Enable
  pmc_enable_periph_clk(ID_ADC);
  NVIC_DisableIRQ(ADC_IRQn);
  NVIC_ClearPendingIRQ(ADC_IRQn);
  NVIC_SetPriority(ADC_IRQn, 0);
  NVIC_EnableIRQ(ADC_IRQn);
  analogWriteResolution(12);
}

void global_digital_interrupt_setup()
{ //Enable PC1- digital pin 33, connected to the trigger
  PIOC->PIO_PER = PIO_PC1;
  //Set PC1 as input
  PIOC->PIO_ODR = PIO_PC1;
  //Disable pull-up on both pins
  PIOC->PIO_PUDR = PIO_PC1;
  pmc_enable_periph_clk(ID_PIOC);
  NVIC_DisableIRQ(PIOC_IRQn);
  NVIC_ClearPendingIRQ(PIOC_IRQn);
  NVIC_SetPriority(PIOC_IRQn, -1);
  NVIC_EnableIRQ(PIOC_IRQn);
 
  //Additional Interrupt Modes Enable Register
  PIOC->PIO_AIMER = PIO_PC1;
  //Edge Select Register
  PIOC->PIO_ESR = PIO_PC1;
  //Falling Edge/Low Level Select Register
  PIOC->PIO_REHLSR = PIO_PC1;
  //Finally enable interrupts
  PIOC->PIO_IER = PIO_PC1;
  //set the interrupt trigger here to be the rising edge of the digital trigger going into PC1 (33)
  //at this point, should do the PIOC handler stuff


  //PC4 - digital pin 36 connected to the weird switchy thing, eventually to PWM and AREF stuff
  PIOC->PIO_PER = PIO_PC4;
  //Set PC4 as input
  PIOC->PIO_ODR = PIO_PC4;
  //Disable pull-up on both pins
  PIOC->PIO_PUDR = PIO_PC4;
  
  //Additional Interrupt Modes Enable Register
  PIOC->PIO_AIMER = PIO_PC4;
  //Level Select Register
  PIOC->PIO_LSR = PIO_PC4;
  //Falling Edge/Low Level Select Register
  PIOC->PIO_FELLSR = PIO_PC4;
  //Finally enable interrupts
  PIOC->PIO_IER = PIO_PC4;
}

void dacc_setup()
{
  //DACC Configuration
  pmc_enable_periph_clk (DACC_INTERFACE_ID) ; // start clocking DAC
  dacc_reset(DACC);
  dacc_set_transfer_mode(DACC, 0);//This allows for WORD transfer from the FIFO rather than HALF-WORD transfer
  //yup, these are the DAC channels :)
  dacc_enable_channel(DACC, 0);
  dacc_enable_channel(DACC, 1);
  //DACC Interrupt NVIC Enable
  NVIC_DisableIRQ(DACC_IRQn);
  NVIC_ClearPendingIRQ(DACC_IRQn);
  NVIC_SetPriority(DACC_IRQn, 0);
  NVIC_EnableIRQ(DACC_IRQn);
}




void ADC_Handler()
{ 
  if (((adc_get_status(ADC) & ADC_ISR_COMPE) == ADC_ISR_COMPE) & start_time != 0) 
  //ADC_ISR - interrupt status register
  //so think this is if the ADC is 1 (on) and also there's been a comparsion error since last ADC_ISR read (ie ADC_ISR_COMPE 1), then let's go
  //if SOMETHING, and also the start_time isn't zero (shouldn't be I think, as gets set as current time in the PIOC handler)- initially gets set as 0 though
  {
    ADC->ADC_EMR ^= 0x01;//toggles the comparision mode register
    //0x01 is 00000001- so compare last bit of EMR to this 1- set EMR bit to 1 if both different, ie if EMR is 0, will be diff to the 1 here, so set to 1 - ie toggle the EMR
    //last bit of EMR is to do with the CMPMODE- swap from LOW to HIGH
    NVIC_ClearPendingIRQ(ADC_IRQn);

    if (!(ADC->ADC_EMR & 0x01))
    //if EMR matches 0x01 bitwise- ie if both got 1, return 1 and don't do this section
    //so if EMP is 1, ie we're in high mode- don't do this part- which feels like the opposite of what we want, because this part is detecting the start times of peaks, where we are doing that HT stuff
    //so maybe I've interpreted this part wrong
    {
      if (times[0] == 0)//if the start time of peak 1 hasn't been measured yet
      {
        times[0] = SysTick->VAL;//Acquires the start time of the DMA acquisition of M peak
        //Think SysTick->VAL gives current time
        //Start the DMA acquisition for the M Peak
        REG_ADC_RPR = (uint32_t) buf_1;
        REG_ADC_RCR = BUFFER_SIZE;
        REG_ADC_PTCR = ADC_PTCR_RXTEN;
      }
      else if (times[2] == 0 && (SysTick->VAL - times[1] > 50 )) 
      //so if the start time of peak 2 is 0 (ie not measured yet) and at least 50 UNITS have passed since the end of peak 1
      {
        times[2] = SysTick->VAL;//Acquires the start time of the DMA acquisition of S peak
        //Start the DMA acquisition for the S Peak
        REG_ADC_RPR = (uint32_t) buf_2;
        REG_ADC_RCR = BUFFER_SIZE;
        REG_ADC_PTCR = ADC_PTCR_RXTEN;

      }
      else if (times[4] == 0 && (SysTick->VAL - times[3] > 50) && times[2] != 0)
      //so if the start time of peak 3 is 0 (ie not measured yet) and at least 50 UNITS have passed since the end of peak 2, and time[2] isn't 0, ie the second peak has been detected
      {
        times[4] = SysTick->VAL;//Acquires the start time of the DMA acquisition of M' peak
        //Start the DMA acquisition for the M' Peak
        REG_ADC_RPR = (uint32_t) buf_3;
        REG_ADC_RCR = BUFFER_SIZE;
        REG_ADC_PTCR = ADC_PTCR_RXTEN;

      }
    }
    else
    {
      if (times[1] == 0)
      //if the end time of peak 1 is 0, ie not measured yet
      {
        times[1] = SysTick->VAL;//Acquires the stop time of the DMA acquisition of M peak
        //Stop the DMA acquisition for the M Peak
        REG_ADC_PTCR = ADC_PTCR_RXTDIS;
        Length[0] = BUFFER_SIZE - REG_ADC_RCR;
      }
      else if (times[3] == 0 && times[2] != 0)
      //if the end time of peak 2 hasn't been measured yet and the start time of peak 2 has been measured
      {
        times[3] = SysTick->VAL;//Acquires the stop time of the DMA acquisition of S peak
         //Stop the DMA acquisition for the S Peak
        REG_ADC_PTCR = ADC_PTCR_RXTDIS;
        Length[1] = BUFFER_SIZE - REG_ADC_RCR;
      }
      else if (times[5] == 0 && times[4] != 0)
      //if the end time of peak 3 hasn't been measured yet and the start time of peak 3 has been measured
      {
        times[5] = SysTick->VAL;//Acquires the stop time of the DMA acquisition of M' peak
         //Stop the DMA acquisition for the M' Peak
        REG_ADC_PTCR = ADC_PTCR_RXTDIS;
        Length[2] = BUFFER_SIZE - REG_ADC_RCR;
       

      }

    }
  }

}



void PIOC_Handler()//Right now I am using the PIOC_handler from the internal functions to work out the interrupt. Will use a typedef function pointer. See WInterrupts.c and Stephen Prata
{
  
  if ((PIOC->PIO_ISR & PIO_PC1) == PIO_PC1) 
  //compare the interrupt status regigter for input/outputs to PC1 bitwise, where 
  //PC1 is digital pin33, digital trigger
  {
    //Setup up the Global Timer or the SysTick Timer
    SysTick->CTRL = 0;
    SysTick->LOAD = 0xFFFFFFFF;
    SysTick->VAL = 0;
    SysTick->CTRL = 0x5;
    while (SysTick->VAL != 0);
    start_time = SysTick->VAL; //set the start_time of the scan to the current time
    
    //Clear all the buffers
    memset(times, 0, sizeof(times));
    //this is where all the times[] values get reset!! so clear it all at the end of the scan, ready to have 0 as the indicator that a peak start/stop time hasn't been measured yet!
    memset(buf_1, 0, sizeof(buf_1));
    memset(buf_2, 0, sizeof(buf_2));
    memset(buf_3, 0, sizeof(buf_3));
    memset(derv_buf_1, 0, sizeof(derv_buf_1));
    memset(derv_buf_2, 0, sizeof(derv_buf_2));
    memset(derv_buf_3, 0, sizeof(derv_buf_3));
    
    counter = 0;
    //reset the counter back to zero
  }


#ifdef ENABLE_TOGGLE_SWITCH //this part actually doesn't apply at the minute, bc ENABLE_TOGGLE_SWITCH isn't defined 
  if ((PIOC->PIO_ISR & PIO_PC4) == PIO_PC4) //PC4 is pin 36 connected to the weird switch
  {
    bump = (HIGH && (!(bump)));
  }
#endif
  //These are the lock signals

  ou
  dacc_set_channel_selection(DACC, 1);
  dacc_write_conversion_data(DACC_INTERFACE, cavity_control_signal + CAVITY_DACC_OFFSET);
  dacc_set_channel_selection(DACC, 0);
  dacc_write_conversion_data(DACC_INTERFACE, laser_control_signal + LASER_DACC_OFFSET);

}




void PIOB_Handler()//This Handler processes TTL signals to perform jump in Slave laser frequency setpoint
//okay, not actually sure what this is doing- think it's to do with scanning the frequency?
{
  
  if ((PIOB->PIO_ISR & PIO_PB14 ) == PIO_PB14) //PB14 is connected to dig pin 53, not sure if actually connected to anything beyond that? 
  {

    if (step_counter <= steps)
    {
      if (!jump)
      {
        LASER_REFERENCE +=  setpoint_change_factor * (start_frequency + step_counter * frequency_jump);
        jump = !jump;
        step_counter++;
      }
      else
      {
        LASER_REFERENCE = LASER_REFERENCE_MOT;
        jump = !jump;
      }

    }

    else
    {

      if (repeat_counter <= repeats)
      {
        LASER_REFERENCE = LASER_REFERENCE_MOT;
        step_counter = 0;
        repeat_counter++;
        jump=LOW;
      }
      
    }
    
  }


}





void peakfinder_1()//Subroutine dedicated to finding the M,M' peaks
{

  flag = HIGH;
  counter++;
  if (counter == 1)//Is this the M peak?
  {
    for (int i = 2; i <= (Length[0] - 3); i++)
    {
      derv_buf_1[i] = (((buf_1[i + 2] << 1) + buf_1[i + 1] - buf_1[i - 1] - (buf_1[i - 2] << 1)) ); //5-point Savitzky-Golay Filter. The denominator doesn't matter when determing zero-crossing.
      if (derv_buf_1[i] <= 0 && flag)
      {
        flag = LOW;
        peak_times[0] = start_time - (times[0] - i * (times[0] - times[1]) / Length[0]) + (float)(derv_buf_1[i] * (times[0] - times[1]) / (Length[0] * (derv_buf_1[i - 1] - derv_buf_1[i]))) ;
       //The line of code uses the method of linear interpolation near the zero crossing to calculate the peaktime

        
      }
    }

  NVIC_SetPendingIRQ(DACC_IRQn); //Software Triggered Interrupt that invokes the DACC Handler to perform Servo Loop calculations
  }
  
 /* if (abs(peakcheckR1-peak_times[0])<2000)
  {
    peak_times[0] = peakcheckR1;
  }*/

      //EDIT:jump stop
  Loop_check +=1;
  if (Loop_check % 2 == 1)
  {
    time_master_1_1 = peak_times[0];
  }
  else
  {
    time_master_1_2 = peak_times[0];
  }
  //END EDIT
  
  
  if (counter == 3)//Is this the M' peak?
  {
    for (int i = 2; i <= (Length[2] - 3); i++)
    {
      derv_buf_3[i] = (((buf_3[i + 2] << 1) + buf_3[i + 1] - buf_3[i - 1] - (buf_3[i - 2] << 1)) );//5-point Savitzky-Golay Filter.The denominator doesn't matter when determing zero-crossing.
      if (derv_buf_3[i] <= 0 && flag)
      {
        flag = LOW;
        peak_times[2] = start_time - (times[4] - i * (times[4] - times[5]) / Length[2]) + (float)(derv_buf_3[i] * (times[4] - times[5]) / (Length[2] * (derv_buf_3[i - 1] - derv_buf_3[i]))) ;
        //The line of code uses the method of linear interpolation near the zero crossing to calculate the peaktime
      }
    }
      
  NVIC_SetPendingIRQ(DACC_IRQn); //Software Triggered Interrupt that invokes the DACC Handler to perform Servo Loop calculations
  }
  
  /*if (abs(peakcheckR2-peak_times[2])<2000)
  {
    peak_times[2] = peakcheckR2;
  }*/
  
        //EDIT:jump stop
  Loop_checkR +=1;
  if (Loop_checkR % 2 == 1)
  {
    time_master_2_1 = peak_times[2];
  }
  else
  {
    time_master_2_2 = peak_times[2];
  }
  //END EDIT
  peakcheckR2 = peak_times[2];
  movingavgR2 = movingAverage(peak_times[2]);

 
}
void peakfinder_2()//Subroutine dedicated to finding the S peak
{
  counter++;
  flag = HIGH;
  //This is the S peak.
  for (int i = 2; i <= (Length[1] - 3); i++)
  {
    derv_buf_2[i] = (((buf_2[i + 2] << 1) + buf_2[i + 1] - buf_2[i - 1] - (buf_2[i - 2] << 1)) ); //5-point Savitzky-Golay Filter.The denominator doesn't matter when determing zero-crossing.
    //of 2.
     if (derv_buf_2[i] <= 0  && flag)
    {
      flag = LOW;
     
      peak_times[1] = start_time - (times[2] - i * (times[2] - times[3]) / Length[1]) + (float)(derv_buf_2[i] * (times[2] - times[3]) / ((derv_buf_2[i - 1] - derv_buf_2[i]) * Length[1])) ;
      //The line of code uses the method of linear interpolation near the zero crossing to calculate the peaktime

    }
  }

 /* if (abs(peakcheckF-peak_times[1])<2000)  
  {
    peak_times[1] = peakcheckF;
  }*/

  DACC_Handler();
  NVIC_SetPendingIRQ(DACC_IRQn);//Software Triggered Interrupt that invokes the DACC Handler to perform Servo Loop calculations
  //why do we call DACC_handler and also have this interrupt?

//EDIT: trying to stop jumping
  Loop_checkF +=1;
  if (Loop_checkF % 2 == 1)
  {
    time_follower_1_1 = peak_times[1];
  }
  else
  {
    time_follower_1_2 = peak_times[1];
  }
  //END EDIT

}


void DACC_Handler()
{

 //Cavity and Slave laser frequency Locking Using the velocity algorithm

  if (!bump)//If the lock is not engaged, do not feedback on the cavity and laser frequency.
  { cavity_control_signal = 0;
    laser_control_signal = 0;
    laser_integrator = 0;
    cavity_error_signal_prev = 0;
  }
  else
  {
    cavity_error_signal_current = CAVITY_REFERENCE - peak_times[0];

    cavity_error_signal_prev += cavity_error_signal_current * dT; // I'm hijacking the _prev variable for the integrator. Cavity won't need a derivative.
    delta_cavity = cavity_K_p*0.001 * (cavity_error_signal_current) + cavity_K_i*0.001 * (cavity_error_signal_prev);
    
     //EDIT
    /*if (abs(time_master_1_1-time_master_1_2)>2000)
    {
      cavity_control_signal += 0;
    }
    //END  */
    
    if (((delta_cavity) > HALF_RANGE) || ((delta_cavity) < -(HALF_RANGE + 1)) || (abs(time_master_1_1-time_master_1_2)>2000) || (abs(time_master_2_1-time_master_2_2)>2000) || (abs(peakcheckR2-movingavgR2)>2000))
    {
      cavity_control_signal += 0;//If the delta_cavity is so large that it will put the control signal outside the rails, do not update the control signal
    }
    else
    {
      cavity_control_signal += delta_cavity;
    }

    
    
    laser_error_signal_current =  LASER_REFERENCE - 1000000 * (float)(peak_times[1] - peak_times[0]) / (peak_times[2] - peak_times[0]);

    laser_integrator += laser_error_signal_current * dT;
    
    delta_laser = laser_K_p*0.001 * (laser_error_signal_current) + (laser_K_i*0.001 * laser_integrator ) + (laser_K_d*0.001 * (laser_error_signal_current - laser_error_signal_prev) / dT);

    /* //EDIT
    if (abs(time_follower_1_1-time_follower_1_2)>2000)
    {
      laser_control_signal += 0; //don't update the laser control signal unless the jump is small- prevent big jumps being an issue
    }
    //END EDIT */


    if (((delta_laser) > HALF_RANGE) || ((delta_laser) < -(HALF_RANGE + 1)) || (abs(time_follower_1_1-time_follower_1_2) > 2000)|| (abs(time_master_2_1-time_master_2_2)>2000)  || (abs(peakcheckR2-movingavgR2)>2000))    
    {
      laser_control_signal += 0;//If the delta_cavity is so large that it will put the control signal outside the rails, do not update the control signal
     }

    else
    {
      laser_control_signal += delta_laser;  // WAS += ORIGINALLY
    }
  }

  cavity_error_signal_prev = cavity_error_signal_current;
  laser_error_signal_prev = laser_error_signal_current;

  frequency_changed = (LASER_REFERENCE - LASER_REFERENCE_MOT) / setpoint_change_factor;

}
