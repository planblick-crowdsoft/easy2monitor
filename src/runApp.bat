for /F "tokens=*" %%A in (../.env) do set %%A
python ./server.py