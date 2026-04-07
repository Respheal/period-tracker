$ ./scripts/prestart.sh

$ openssl genrsa -out private.pem 2048 $ openssl rsa -in private.pem -out public.pem -pubout

To update the openapi.json:

python -c "import api.main; import json; print(json.dumps(api.main.app.openapi()))" > ../frontend/openapi.json
