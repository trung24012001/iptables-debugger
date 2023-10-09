
set -x
 
send() {
  curl -X POST \
       -F "title=$(hostname)" \
       "http://127.0.0.1:8000/api/interfaces"
}

send -F "interfaces=helloworld"

