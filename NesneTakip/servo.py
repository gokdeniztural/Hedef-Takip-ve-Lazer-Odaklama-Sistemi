"""
servo.py — Servo motor sürücüsü
Pi'de GPIO/PWM yönetir, PC'de sessizce pas geçer.
"""

import time
import config


def _angle_to_duty(angle: float) -> float:
    """
    Açıyı PWM duty cycle yüzdesine çevirir.
    Formül: duty = min + (açı / 180) * (max - min)
    SG90: 0°→2.5%  90°→7.5%  180°→12.5%
    """
    return config.SERVO_DUTY_MIN + (angle / 180.0) * (config.SERVO_DUTY_MAX - config.SERVO_DUTY_MIN)


if config.SERVO_ENABLED:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PAN_PIN,  GPIO.OUT)
    GPIO.setup(config.TILT_PIN, GPIO.OUT)

    _pan_pwm  = GPIO.PWM(config.PAN_PIN,  config.SERVO_PWM_FREQ)
    _tilt_pwm = GPIO.PWM(config.TILT_PIN, config.SERVO_PWM_FREQ)
    _pan_pwm.start(0)
    _tilt_pwm.start(0)

    def set_servo(pan: float, tilt: float) -> None:
        """Servo motorları belirtilen açılara götür."""
        _pan_pwm.ChangeDutyCycle(_angle_to_duty(pan))
        _tilt_pwm.ChangeDutyCycle(_angle_to_duty(tilt))
        time.sleep(0.02)        # hareketin tamamlanmasını bekle
        _pan_pwm.ChangeDutyCycle(0)    # titreşimi önlemek için sinyali kes
        _tilt_pwm.ChangeDutyCycle(0)

    def cleanup() -> None:
        """Program kapanırken GPIO'yu temizle."""
        _pan_pwm.stop()
        _tilt_pwm.stop()
        GPIO.cleanup()
        print("[SERVO] GPIO temizlendi.")

else:
    def set_servo(pan: float, tilt: float) -> None:
        """PC modunda: servo komutu yalnızca loglanır."""
        pass

    def cleanup() -> None:
        pass
