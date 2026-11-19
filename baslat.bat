@echo off
chcp 65001 > nul
echo ========================================================
echo   ARAÇ ÇEKİCİ & OTO KURTARMA WEB SİTESİ BAŞLATILIYOR
echo ========================================================
echo.
echo Tarayıcınızda açmak için aşağıdaki adresi ziyaret edin:
echo   http://127.0.0.1:5000
echo.
echo Yönetici Girişi:
echo   Kullanıcı Adı: admin
echo   Şifre: admin123
echo.
echo Test Üye Girişi:
echo   Kullanıcı Adı: uye
echo   Şifre: 123456
echo ========================================================
python app.py
pause
