package amqp

import (
	"os"

	log "github.com/sirupsen/logrus"
	"github.com/upsilonproject/upsilon-gocommon/pkg/amqp"
	pb "github.com/upsilonproject/upsilon-gocommon/pkg/amqpproto"
)

func ListenForStartups() {
	amqp.ConsumeForever("Startup", func(d amqp.Delivery) {
		d.Message.Ack(true)

		startup := pb.Startup{}
		amqp.Decode(d.Message.Body, &startup)

		log.WithFields(log.Fields{
			"hostname": startup.Hostname,
		}).Info("Drone startup received")

		gitPull := &pb.GitPullRequest{
			GitUrlAlias: "fabric-config",
		}
		amqp.PublishPb(gitPull)

		startupCommand := os.Getenv("UPSILON_STARTUP_COMMAND")
		if startupCommand != "" {
			execReq := &pb.ExecutionRequest{
				Hostname:    startup.Hostname,
				CommandName: startupCommand,
			}
			amqp.PublishPb(execReq)

			log.WithFields(log.Fields{
				"hostname": startup.Hostname,
				"command":  startupCommand,
			}).Info("Dispatched startup execution request")
		}
	})
}
