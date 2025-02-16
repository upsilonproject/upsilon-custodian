package amqp

import (
	"github.com/upsilonproject/upsilon-gocommon/pkg/amqp"
	pb "github.com/upsilonproject/upsilon-gocommon/pkg/amqpproto"
	log "github.com/sirupsen/logrus"
	reports "github.com/upsilonproject/upsilon-custodian/internal/reports"
)

func ListenForReportRequests() {
	amqp.ConsumeForever("ReportRequest", func(d amqp.Delivery) {
		d.Message.Ack(true)

		rr := pb.ReportRequest{}

		amqp.Decode(d.Message.Body, &rr)

		log.Infof("Serving Report")

		ret := reports.Get(rr.IncludeGood)

		log.Infof("Report rows: %+v", ret.Columns)

		amqp.PublishPb(ret)
	})
}
