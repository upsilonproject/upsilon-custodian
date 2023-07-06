package amqp

import (
	"github.com/upsilonproject/upsilon-gocommon/pkg/amqp"
	pb "github.com/upsilonproject/upsilon-custodian/gen/amqpproto"
	log "github.com/sirupsen/logrus"
	db "github.com/upsilonproject/upsilon-custodian/internal/db"
)

func exitCodeToKarma(exitCode int64) string {
	switch (exitCode) {
	case 0: return "GOOD";
	default: return "BAD";
	}
}

func ListenForExecutionResults() {
	dbconn := db.GetDb()

	amqp.ConsumeForever("ExecutionResult", func(d amqp.Delivery) {
		d.Message.Ack(true)

		execres := pb.ExecutionResult{}

		amqp.Decode(d.Message.Body, &execres)

		log.Infof("Saving SERVICE_CHECK_RESULT")

		res, err := dbconn.Query("INSERT INTO services (identifier, description, consecutiveCount, node) VALUES (?, '', 0, ?) ON DUPLICATE KEY UPDATE lastUpdated = now(), lastChanged = now() , karma = ?, output =? ", execres.Name, execres.Hostname, exitCodeToKarma(execres.ExitCode), execres.Stdout + execres.Stderr)

		if err != nil {
			log.Warnf("Insert err: %v", err)

		}

		res.Close()

		res, err = dbconn.Query("INSERT INTO service_check_results (service, checked, output, metricProcessed) VALUES (?, now(), ?, 0)", execres.Name, execres.Stdout + execres.Stderr)

		if err != nil {
			log.Warnf("Insert err: %v", err)
		}

		res.Close()
	})
}
