# ollama_json_parserInstall 
ollama https://ollama.com/download
install it and in cmd try run using ollama run llama3
now, write code, and see which port it has started, if not the local 11434 that is ollama.
netstat -ano | findstr :11434
$env:OLLAMA_HOST = "127.0.0.1:11500"
ollama start
u can do by using run as admin to cmd, and to vs code.'
now run py main.py 
in ur cmd u will see status code to all request 