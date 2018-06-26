# LCD_ST7032

Python module for ST7032 LCD controller with I2C interface. 
This module is inspired by https://github.com/olkal/LCD_ST7032

Tested with RaspberryPi 2, Python 3.6 and AQM1602XA-RN-GBW


# usage
```
$ pip install -r requirements.txt
$ pip install lcd_st7032
```

# Hello World

```python
from lcd_st7032 import ST7032

lcd = ST7032()
lcd.write("Hello World!")
```

# LICENSE

MIT