package main

import (
	log "github.com/sirupsen/logrus"
	commonAmqp "github.com/upsilonproject/upsilon-gocommon/pkg/amqp"
	"github.com/upsilonproject/upsilon-custodian/internal/amqp"
	"time"
)

func main() {
	log.Infof("upsilon-custodian")
	log.SetLevel(log.DebugLevel)

	commonAmqp.ConnectionIdentifier = "upsilon-custodian"
	commonAmqp.AmqpHost = "upsilon"
	commonAmqp.AmqpUser = "guest"
	commonAmqp.AmqpPass = "guest"
	commonAmqp.AmqpPort = 5672

	go amqp.ListenForExecutionResults()
	go amqp.ListenForHeartbeats()
	go amqp.ListenForReportRequests()

	for {
		time.Sleep(1 * time.Second)
	}
}
