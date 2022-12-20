package amqp

import (
	"github.com/upsilonproject/upsilon-gocommon/pkg/amqp"
	pb "github.com/upsilonproject/upsilon-custodian/gen/amqpproto"
	log "github.com/sirupsen/logrus"
	"fmt"
)

func ListenForReportRequests() {
	db := getDb()

	amqp.Consume("ReportRequest", func(d amqp.Delivery) {
		d.Message.Ack(true)

		rr := pb.ReportRequest{}

		amqp.Decode(d.Message.Body, &rr)

		log.Infof("Serving Report")

		res, err := db.Query("SELECT id, identifier as service, node, karma FROM services ORDER BY karma");

		if err != nil {
			log.Warnf("Insert err: %v", err)
		}

		ret := newReport("id", "service", "node", "karma")

		for res.Next() {
			var id int;
			var identifier string;
			var node string;
			var karma string;

			res.Scan(&id, &identifier, &node, &karma)

			row := &pb.ReportRow {
				Cells: map[string]string {
					"id": fmt.Sprintf("%v", id),
					"service": identifier,
					"node": node,
					"karma": karma,
				},
			}

			ret.Rows = append(ret.Rows, row)
		}
		
		res.Close()

		log.Infof("Report rows: %+v", ret)

		amqp.PublishPb(*ret)
	})
}

func newReport(headers ...string) *pb.ReportResponse {
	ret := &pb.ReportResponse{
		Rows: []*pb.ReportRow {},
		Columns: []*pb.ReportColumn {},
	}

	for _, header := range headers {
		ret.Columns = append(ret.Columns, &pb.ReportColumn {
			Header: header,
		})

	}

	return ret
}

