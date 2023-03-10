module github.com/upsilonproject/upsilon-custodian

go 1.18

require (
	github.com/go-sql-driver/mysql v1.6.0
	github.com/sirupsen/logrus v1.9.0
	github.com/upsilonproject/upsilon-gocommon v0.0.0-00010101000000-000000000000
	google.golang.org/protobuf v1.28.1
)

require (
	github.com/doug-martin/goqu/v9 v9.18.0 // indirect
	github.com/streadway/amqp v1.0.0 // indirect
	github.com/teris-io/shortid v0.0.0-20201117134242-e59966efd125 // indirect
	golang.org/x/sys v0.0.0-20220715151400-c0bba94af5f8 // indirect
)

replace github.com/upsilonproject/upsilon-gocommon => /home/xconspirisist/sandbox/Development/upsilon/upsilon-gocommon
