import time
from typing import Union, List

import Adafruit_PureIO.smbus as smbus


Write_Address = 0x3E  # i2c address
CNTRBIT = 0x00  # followed by command bytes
CNTRBIT_CO = 0x00  # followed by 1 command byte
CNTRBIT_RS = 0x40  # after last control byte, followed by DDRAM data byte(s)
CLEAR_DISPLAY = 0x01  # Clear display
RETURN_HOME = 0x02  # Cursor home to 00H
ENTRY_MODE_SET = 0x04  # Sets cursor move direction and specifies display shift.
DISPLAY_ON_OFF = 0x08  # display on, cursor on, cursor position on
FUNCTION_SET = 0x20  # DL: interface data is 8/4 bits, N: number of line is 2/1 DH: double height font, IS: instruction table select
SET_DDRAM_ADDRESS = 0x80  # Set DDRAM address in address counter
CURSOR_OR_DISPLAY_SHIFT = 0x10  # Set cursor moving and display shift control bit, and the direction without changing DDRAM data.
SET_CGRAM_ADDRESS = 0x40  # Set CGRAM address in address counter
INTERNAL_OSC_FREQ = 0x10  # BS=1:1/4 bias, BS=0:1/5 bias, F2~0: adjust internal OSC frequency for FR frequency.
POWER_ICON_BOST_CONTR = 0x50  # Ion: ICON display on/off, Bon: set booster circuit on/off, C5,C4: Contrast set
FOLLOWER_CONTROL = 0x60  # Fon: set follower circuit on/off, Rab2~0: select follower amplified ratio.
CONTRAST_SET = 0x70  # C0-C3: Contrast set
LINE_1_ADR = 0x80
LINE_2_ADR = 0xC0

# Various flags and masks

ENTRY_MODE_SET_S = 0x01  # S: Shift of entire display, see data sheet
ENTRY_MODE_SET_ID = 0x02  # I/D : Increment / decrement of DDRAM address (cursor or blink), see  data sheet
DISPLAY_ON_OFF_B = 0x01  # cursor position on
DISPLAY_ON_OFF_C = 0x02  # cursor on
DISPLAY_ON_OFF_D = 0x04  # display on
FUNCTION_SET_IS = 0x01  # IS: instruction table select
FUNCTION_SET_DH = 0x04  # DH: double height font
FUNCTION_SET_N = 0x08  # N: number of line is 2/1
FUNCTION_SET_DL = 0x10  # DL: interface data is 8/4 bits
CURSOR_OR_DISPLAY_SHIFT_RL = 0x04  #
CURSOR_OR_DISPLAY_SHIFT_SC = 0x08  #
INTERNAL_OSC_FREQ_F0 = 0x01  # F2~0: adjust internal OSC frequency for FR frequency.
INTERNAL_OSC_FREQ_F1 = 0x02  # F2~0: adjust internal OSC frequency for FR frequency.
INTERNAL_OSC_FREQ_F2 = 0x04  # F2~0: adjust internal OSC frequency for FR frequency.
INTERNAL_OSC_FREQ_BS = 0x08  # BS=1:1/4 bias (BS=0:1/5 bias)
POWER_ICON_BOST_CONTR_Bon = 0x04  # Ion: ICON display on/off
POWER_ICON_BOST_CONTR_Ion = 0x08  # Bon: set booster circuit on/off
FOLLOWER_CONTROL_Rab0 = 0x01  # Rab2~0: select follower amplified ratio
FOLLOWER_CONTROL_Rab1 = 0x02  # Rab2~0: select follower amplified ratio
FOLLOWER_CONTROL_Rab2 = 0x04  # Rab2~0: select follower amplified ratio
FOLLOWER_CONTROL_Fon = 0x08  # Fon: set follower circuit on/off

CONTRAST_MAX = 0x3F  # limit range max value (0x00 - 0x3F)
CONTRAST_MIN = 0x00  # limit range min value (0x00 - 0x3F)
WRITE_DELAY_MS = 30  # see data sheet
HOME_CLEAR_DELAY_MS = 1200  # see data sheet


class ST7032(object):
    DEVICE_ADDR = 0x3e
    MAX_COL = 16

    def __init__(self, bus_num=1):
        self.bus_num = bus_num
        self._contrast = 0x18
        self.display_on_off = DISPLAY_ON_OFF | DISPLAY_ON_OFF_D

        # init
        self._write_instruction(FUNCTION_SET | FUNCTION_SET_DL | FUNCTION_SET_N | FUNCTION_SET_IS)
        self._write_instruction(INTERNAL_OSC_FREQ | INTERNAL_OSC_FREQ_BS | INTERNAL_OSC_FREQ_F2)
        self._write_instruction(POWER_ICON_BOST_CONTR | POWER_ICON_BOST_CONTR_Ion)
        self.setcontrast(self._contrast)
        self._write_instruction(FOLLOWER_CONTROL | FOLLOWER_CONTROL_Fon | FOLLOWER_CONTROL_Rab2)
        self._delay(300)
        self._write_instruction(self.display_on_off)
        self._write_instruction(ENTRY_MODE_SET | ENTRY_MODE_SET_ID)
        self.clear()
        self.home()

    def clear(self):
        self._write_instruction(CLEAR_DISPLAY)
        self._delay(HOME_CLEAR_DELAY_MS * 0.001)

    def home(self):
        self._write_instruction(RETURN_HOME)
        self._delay(HOME_CLEAR_DELAY_MS * 0.001)

    def display(self):
        self.display_on_off |= DISPLAY_ON_OFF_D
        self._write_instruction(self.display_on_off)

    def noDisplay(self):
        self.display_on_off &= ~DISPLAY_ON_OFF_D
        self._write_instruction(self.display_on_off)

    def setCursor(self, line, pos):
        pos = pos if pos < self.MAX_COL else 0
        if line == 0:
            p = LINE_1_ADR + pos
        else:
            p = LINE_2_ADR + pos
        self._write_instruction(SET_DDRAM_ADDRESS | p)

    def cursor(self):
        self.display_on_off |=~ DISPLAY_ON_OFF_C
        self._write_instruction(self.display_on_off)

    def noCursor(self):
        self.display_on_off &= ~DISPLAY_ON_OFF_C
        self._write_instruction(self.display_on_off)

    def blink(self):
        self.display_on_off |= DISPLAY_ON_OFF_B
        self._write_instruction(self.display_on_off)

    def noBlink(self):
        self.display_on_off &= ~DISPLAY_ON_OFF_B
        self._write_instruction(self.display_on_off)

    def setcontrast(self, val:int):
        if val > CONTRAST_MAX:
            val = CONTRAST_MIN
        elif val < CONTRAST_MIN:
            val = CONTRAST_MAX
        self._write_instruction(CONTRAST_SET | (val & 0b00001111))
        self._write_instruction((val >> 4) | POWER_ICON_BOST_CONTR | POWER_ICON_BOST_CONTR_Bon)
        self._contrast = val

    def adjcontrast(self, val:int):
        self.setcontrast(val + self._contrast)

    def getcontrast(self):
        return self._contrast

    def write(self, data:Union[str, List[int]]):
        for c in data[:self.MAX_COL]:
            if type(c) is int:
                self._write_data(c)
            elif type(c) is str:
                self._write_data(ord(c))
            else:
                raise ValueError('require str or int list')

    def _write_instruction(self, cmd:int):
        with smbus.SMBus(self.bus_num) as i2c:
            i2c.write_byte_data(self.DEVICE_ADDR, CNTRBIT_CO, cmd)
        self._delay(WRITE_DELAY_MS * 0.001)

    def _write_data(self, data:int):
        with smbus.SMBus(self.bus_num) as i2c:
            i2c.write_byte_data(self.DEVICE_ADDR, CNTRBIT_RS, data)
        self._delay(WRITE_DELAY_MS * 0.001)

    @staticmethod
    def _delay(milli_secs):
        time.sleep(milli_secs * 0.001)


if __name__ == '__main__':
    lcd = ST7032()
    lcd.write("Hello!")
    lcd.setCursor(1, 0)
    lcd.write([0xba, 0xdd, 0xc6, 0xc1, 0xdc, '!'])
