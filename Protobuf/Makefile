default:
	protoc --python_out="./build" "protobufs/request.proto"
	protoc --python_out="./build" "protobufs/response.proto"

client:
	python client.py

server:
	python server.py
