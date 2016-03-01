default:
	protoc --python_out="./build" "request.proto"
	protoc --python_out="./build" "response.proto"

client:
	python client.py

server:
	python server.py
