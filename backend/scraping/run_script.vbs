Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "D:\Downloads\Licenta"
WshShell.Run "D:\Downloads\Licenta\.venv\Scripts\python.exe backend\scraping\scraping_automat.py", 0
Set WshShell = Nothing