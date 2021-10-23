#include "sw_uart.h"

due_sw_uart uart;

void setup() {
  Serial.begin(9600);
  sw_uart_setup(&uart, 7, 1, 8, SW_UART_EVEN_PARITY);
}

void loop() {
 send_byte();
 delay(500);
}


void send_byte() {
  sw_uart_write_byte(&uart, 'x');
  Serial.println("enviando x");
}
