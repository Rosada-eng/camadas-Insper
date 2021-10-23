#include "sw_uart.h"
#pragma GCC optimize ("-O3")

void sw_uart_setup(due_sw_uart *uart, int tx, int stopbits, int databits, int paritybit) {
	
	uart->pin_tx     = tx;
	uart->stopbits   = stopbits;
	uart->paritybit  = paritybit;
  uart->databits   = databits;
  pinMode(tx, OUTPUT);
  digitalWrite(tx, HIGH);
}

int calc_even_parity(char data) {
  int ones = 0;

  for(int i = 0; i < 8; i++) {
    ones += (data >> i) & 0x01;
  }

  return ones % 2;
}


void sw_uart_write_byte(due_sw_uart *uart, char data){
  int paridade = calc_even_parity(data);

  // Envia start bit
  digitalWrite(uart->pin_tx, LOW);
  _sw_uart_wait_T(uart);

  // Envia bit a bit
  for (int i = 0; i < 8; i++){
    digitalWrite(uart->pin_tx, (data >> i) & 0x01);
    _sw_uart_wait_T(uart);
  }

  // bit paridade
  digitalWrite(uart->pin_tx, paridade);
  _sw_uart_wait_T(uart);

  // Fim. -> EndBit --> HIGH all
  digitalWrite(uart->pin_tx, HIGH);
  _sw_uart_wait_T(uart); 

}

// MCK 21MHz
void _sw_uart_wait_half_T(due_sw_uart *uart) {
  for(int i = 0; i < 1093; i++)
    asm("NOP");
}

void _sw_uart_wait_T(due_sw_uart *uart) {
  _sw_uart_wait_half_T(uart);
  _sw_uart_wait_half_T(uart);
}
