package amqp

import (
	"github.com/upsilonproject/upsilon-gocommon/pkg/amqp"
	pb "github.com/upsilonproject/upsilon-custodian/gen/amqpproto"
	log "github.com/sirupsen/logrus"
)

func ListenForHeartbeats() {
	db = getDb();

	amqp.ConsumeForever("Heartbeat", func(d amqp.Delivery) {
		d.Message.Ack(true)

		hb := pb.Heartbeat{}

		amqp.Decode(d.Message.Body, &hb)

		log.Infof("Saving HEARTBEAT")

		res, err := db.Query("INSERT INTO nodes (identifier) VALUES (?) ON DUPLICATE KEY UPDATE lastUpdated=now(), instanceApplicationVersion=?", hb.Hostname, hb.Version)

		if err != nil {
			log.Warnf("Insert err: %v", err)
		}

		res.Close()
	})
}
