package amqp

import (
	"github.com/upsilonproject/upsilon-gocommon/pkg/amqp"
	pb "github.com/upsilonproject/upsilon-custodian/gen/amqpproto"
	"github.com/doug-martin/goqu/v9"
	log "github.com/sirupsen/logrus"
	"fmt"
)

func ListenForReportRequests() {
	db := getDb()

	amqp.ConsumeForever("ReportRequest", func(d amqp.Delivery) {
		d.Message.Ack(true)

		rr := pb.ReportRequest{}

		amqp.Decode(d.Message.Body, &rr)

		log.Infof("Serving Report")

		sql := reportRequestToSql(&rr)

		res, err := db.Query(sql);

		if err != nil {
			log.Warnf("Query err: %v", err)
		}

		ret := newReport("id", "service", "node", "karma", "lastUpdated")
		ret.Columns[4].Type = "timestamp"

		for res.Next() {
			var id int;
			var identifier string;
			var node string;
			var karma string;
			var lastUpdated string;

			err := res.Scan(&id, &identifier, &node, &karma, &lastUpdated)

			if err != nil {
				log.Errorf("scanf: %s", err)
			}

			row := &pb.ReportRow {
				Cells: map[string]string {
					"id": fmt.Sprintf("%v", id),
					"service": identifier,
					"node": node,
					"karma": karma,
					"lastUpdated": lastUpdated,
				},
			}

			ret.Rows = append(ret.Rows, row)
		}
		
		res.Close()

		log.Infof("Report rows: %+v", ret.Columns)

		amqp.PublishPb(ret)
	})
}

func reportRequestToSql(rr *pb.ReportRequest) string {
	//"SELECT id, identifier as service, node, karma, lastUpdated FROM services ORDER BY karma");

	builder := getGoqu().From("services").Select("id", goqu.C("identifier").As("serivce"), "node", "karma", "lastUpdated");

	if !rr.IncludeGood {
		builder = builder.Where(goqu.C("karma").Neq("good"))
	}

	sql, _, err := builder.ToSQL();

	if err != nil {
		log.Errorf("report sql prep error: %v", err)
	} else {
		log.Debugf("report sql: %s", sql);
	}

	return sql
}

func newReport(headers ...string) *pb.ReportResponse {
	ret := &pb.ReportResponse{
		Rows: []*pb.ReportRow {},
		Columns: []*pb.ReportColumn {},
	}

	for _, header := range headers {
		ret.Columns = append(ret.Columns, &pb.ReportColumn {
			Type: "string",
			Header: header,
		})

	}

	return ret
}

