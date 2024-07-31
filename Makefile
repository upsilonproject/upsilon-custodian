default: grpc
	go build

grpc:
	buf generate
